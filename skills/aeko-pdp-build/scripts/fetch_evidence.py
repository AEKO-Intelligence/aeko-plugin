#!/usr/bin/env python3
"""Bounded web evidence fetcher. Usage: fetch_evidence.py [--mode page|site] [--content-only] [--image-dir DIR] <URL>"""

from __future__ import annotations

import gzip
import hashlib
import json
import mimetypes
import os
import re
import ssl
import sys
import time
from html.parser import HTMLParser
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin, urlsplit, urlunsplit
from urllib.request import (
    HTTPRedirectHandler,
    HTTPSHandler,
    ProxyHandler,
    Request,
    build_opener,
)


SCHEMA = "aeko_fetch_evidence/v2"
MAX_BODY_BYTES = 6_000_000
MAX_SITE_RESOURCE_BYTES = 2_000_000
MAX_ASSET_BYTES = 8_000_000
MAX_ASSET_TOTAL_BYTES = 48_000_000
MAX_ASSET_COUNT = 50
PER_REQUEST_SECONDS = 6.0
TOTAL_SECONDS = 90.0
MAX_REDIRECTS = 5

BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0 Safari/537.36"
)
CRAWLER_UAS = {
    "GPTBot": "GPTBot/1.0",
    "ClaudeBot": "ClaudeBot/1.0",
    "OAI-SearchBot": "OAI-SearchBot/1.0",
    "PerplexityBot": "PerplexityBot/1.0",
    "Google-Extended": "Google-Extended",
    "CCBot": "CCBot/2.0",
    "Googlebot": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
}
VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param",
    "source", "track", "wbr",
}
TEXT_EXCLUDED_TAGS = {"script", "style", "noscript", "template", "svg"}
IMAGE_EXCLUDED_TOKENS = {
    "board", "cookie", "footer", "header", "nav", "paginate", "pagination", "progress", "qna",
    "question", "recommendation", "related", "relation", "review", "scroll", "sns", "social",
}
IMAGE_EXCLUDED_EXACT = {"bottom_bottom", "scroll_sns_icon", "top_top"}
LAZY_ATTRIBUTES = ("ec-data-src", "data-src", "data-original", "data-lazy")
DETAIL_SECTION_IDS = {
    "prddetail": "detail",
    "prdinfo": "platform_boilerplate",
    "prdreview": "reviews",
    "p_review": "reviews",
    "prdqna": "qna",
}
GLOBAL_BOUNDARY_IDS = {
    "footer", "progresspaybar", "progresspaybarbackground", "progresspaybarview",
    "layoutdimmed", "multi_option",
}
START_TAG_RE = re.compile(r"<(?:div|section|article|main|footer)\b[^>]*>", re.IGNORECASE)
ATTR_RE = re.compile(
    r"([:\w-]+)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))",
    re.IGNORECASE,
)
WIDGET_HEADING_RE = re.compile(
    r"(?:함께\s*구매|관련\s*상품|이\s*상품과\s*함께|frequently\s+bought|you\s+may\s+also\s+like|recently\s+viewed)",
    re.IGNORECASE,
)
PRICE_TOKEN_RE = re.compile(
    r"(?:[$€£¥₩]\s?\d[\d,.]*|\d[\d,.]*\s?(?:원|krw|usd|eur|jpy))",
    re.IGNORECASE,
)
POLICY_HEADING_RE = re.compile(
    r"(?:상품\s*결제\s*(?:정보|안내)|결제\s*(?:정보|안내)|배송\s*(?:정보|안내)|상품\s*배송\s*정보|"
    r"교환\s*(?:및|/)\s*반품|반품\s*(?:및|/)\s*교환|환불\s*안내|서비스\s*문의|고객\s*지원|"
    r"payment\s*(?:information|details)|shipping\s*(?:information|delivery|policy)|delivery\s*information|"
    r"exchanges?\s*(?:&|and)\s*returns?|returns?\s*(?:and|&)\s*refunds?|return\s*policy|refund\s*policy|"
    r"customer\s*service|service\s*inquir(?:y|ies)|support|contact\s*us)",
    re.IGNORECASE,
)
CHROME_RE = re.compile(
    r"(?:상품\s*정보|구매\s*정보|상품\s*후기|상품\s*문의|product\s*info|reviews?|q\s*&\s*a)",
    re.IGNORECASE,
)
PROMO_RE = re.compile(
    r"(?:membership|installment|coupon|benefit|promotion|promo|event|banner|무이자|할부|멤버십|쿠폰|혜택)",
    re.IGNORECASE,
)
BACKGROUND_RE = re.compile(r"background(?:-image)?\s*:[^;]*url\((['\"]?)(.*?)\1\)", re.IGNORECASE)


class Node:
    def __init__(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
        parent: "Node | None",
        order: int,
        start_tag: str,
    ) -> None:
        self.tag = tag.lower()
        self.attrs_list = [(key.lower(), value or "") for key, value in attrs]
        self.attrs = dict(self.attrs_list)
        self.parent = parent
        self.order = order
        self.start_tag = start_tag
        self.items: list[Node | str] = []


class PDPParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("document", [], None, 0, "")
        self.stack = [self.root]
        self.nodes: list[Node] = []
        self.order = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.order += 1
        node = Node(tag, attrs, self.stack[-1], self.order, self.get_starttag_text() or f"<{tag}>")
        self.stack[-1].items.append(node)
        self.nodes.append(node)
        if tag.lower() not in VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if self.stack[-1].tag == tag.lower() and tag.lower() not in VOID_TAGS:
            self.stack.pop()

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == lowered:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        self.stack[-1].items.append(data)


def compact_text(value: str) -> str:
    return " ".join(value.split())


def tag_attrs(raw_tag: str) -> dict[str, str]:
    return {
        match.group(1).lower(): next(
            (value for value in match.groups()[1:] if value is not None), ""
        )
        for match in ATTR_RE.finditer(raw_tag)
    }


def classify_text_segment(
    section_kind: str,
    module_name: str,
    text: str,
    product_name: str,
) -> tuple[str, dict[str, Any]]:
    lowered_module = module_name.lower()
    price_tokens = PRICE_TOKEN_RE.findall(text)
    widget_heading = bool(WIDGET_HEADING_RE.search(text))
    dense_price_run = len(price_tokens) >= 3 and len(text) / max(1, len(price_tokens)) < 100
    other_product_run = bool(
        len(price_tokens) >= 3
        and product_name
        and compact_text(product_name).lower() not in text.lower()
    )
    signals: dict[str, Any] = {
        "widget_heading": widget_heading,
        "dense_price_run": dense_price_run,
        "other_product_run": other_product_run,
        "price_token_count": len(price_tokens),
    }

    chrome_matches = CHROME_RE.findall(text)
    if any(token in lowered_module for token in ("tab", "tap", "nav", "menu", "pagination")):
        signals["chrome_label_count"] = len(chrome_matches)
        return "chrome", signals
    if any(token in lowered_module for token in ("review", "snap_widget")):
        return "reviews", signals
    if any(token in lowered_module for token in ("qna", "question")):
        return "qna", signals
    if any(token in lowered_module for token in ("customer", "service", "support", "cscenter")):
        return "support", signals
    if section_kind in {"platform_boilerplate", "reviews", "qna", "support"}:
        return section_kind, signals
    if sum((widget_heading, dense_price_run, other_product_run)) >= 2:
        return "merchandising_widget", signals
    if POLICY_HEADING_RE.search(text):
        return "platform_boilerplate", signals
    if len(chrome_matches) >= 3 and len(text) < 300:
        signals["chrome_label_count"] = len(chrome_matches)
        return "chrome", signals
    return "product_copy", signals


def node_text(node: Node, limit: int | None = None) -> str:
    parts: list[str] = []

    def collect(current: Node) -> None:
        if current.tag in TEXT_EXCLUDED_TAGS:
            return
        for item in current.items:
            if isinstance(item, str):
                text = compact_text(item)
                if text:
                    parts.append(text)
            else:
                collect(item)

    collect(node)
    joined = " ".join(parts)
    return joined if limit is None else joined[:limit]


def positional_text_segments(
    root: Node,
    section_kind: str,
    product_name: str,
    start_index: int = 1,
) -> list[dict[str, Any]]:
    raw: list[tuple[str, str, str]] = []

    def section(node: Node) -> str:
        current: Node | None = node
        while current:
            if current.attrs.get("id"):
                return f"#{current.attrs['id']}"
            if current is root:
                break
            current = current.parent
        return f"#{root.attrs['id']}" if root.attrs.get("id") else root.tag

    def module(node: Node) -> str:
        current = node
        while current.parent and current.parent is not root:
            current = current.parent
        suffix = f"#{current.attrs['id']}" if current.attrs.get("id") else ""
        classes = ".".join(current.attrs.get("class", "").split()[:3])
        return f"{current.tag}{suffix}{'.' + classes if classes else ''}"

    def collect(node: Node) -> None:
        if node.tag in TEXT_EXCLUDED_TAGS:
            return
        for item in node.items:
            if isinstance(item, str):
                text = compact_text(item)
                if text:
                    raw.append((section(node), module(node), text))
            else:
                collect(item)

    collect(root)
    output: list[dict[str, Any]] = []
    for section_name, module_name, text in raw:
        if output and output[-1]["section"] == section_name and output[-1]["module"] == module_name:
            output[-1]["text"] += " " + text
        else:
            output.append(
                {
                    "source_id": f"text_segment_{start_index + len(output):03d}",
                    "section": section_name,
                    "module": module_name,
                    "text": text,
                }
            )
    for segment in output:
        classification, signals = classify_text_segment(
            section_kind,
            segment["module"],
            segment["text"],
            product_name,
        )
        segment["classification"] = classification
        segment["classification_signals"] = signals
    return output


def raw_contents(node: Node) -> str:
    parts: list[str] = []

    def render(item: Node | str) -> None:
        if isinstance(item, str):
            parts.append(item)
            return
        parts.append(item.start_tag)
        for child in item.items:
            render(child)
        if item.tag not in VOID_TAGS:
            parts.append(f"</{item.tag}>")

    for child in node.items:
        render(child)
    return "".join(parts)


def descendants(node: Node) -> Iterable[Node]:
    for item in node.items:
        if isinstance(item, Node):
            yield item
            yield from descendants(item)


def attr_tokens(node: Node) -> set[str]:
    value = " ".join([node.attrs.get("id", ""), node.attrs.get("class", "")]).lower()
    return set(re.findall(r"[a-z0-9_-]+", value))


def has_excluded_ancestor(node: Node, root: Node) -> bool:
    current = node.parent
    while current and current is not root:
        tokens = attr_tokens(current)
        if tokens & IMAGE_EXCLUDED_EXACT or any(
            any(blocked in token for blocked in IMAGE_EXCLUDED_TOKENS) for token in tokens
        ):
            return True
        current = current.parent
    return False


def choose_detail_root(parser: PDPParser) -> tuple[Node, str, bool]:
    priorities = ("prddetail", "productdetail", "product-detail", "product_detail")
    for wanted in priorities:
        for node in parser.nodes:
            if node.attrs.get("id", "").lower() == wanted:
                return node, f"#{node.attrs['id']}", False
    for wanted in priorities[2:]:
        for node in parser.nodes:
            classes = node.attrs.get("class", "").lower().split()
            if wanted in classes:
                return node, f"{node.tag}.{wanted}", False
    for tag in ("main", "article", "body"):
        for node in parser.nodes:
            if node.tag == tag:
                return node, tag, True
    return parser.root, "document", True


def bounded_detail_region(html: str) -> dict[str, Any] | None:
    landmarks: list[dict[str, Any]] = []
    for match in START_TAG_RE.finditer(html):
        raw_tag = match.group(0)
        attrs = tag_attrs(raw_tag)
        tag_name_match = re.match(r"<\s*([a-z0-9]+)", raw_tag, re.IGNORECASE)
        landmarks.append(
            {
                "start": match.start(),
                "end": match.end(),
                "tag": tag_name_match.group(1).lower() if tag_name_match else "",
                "id": attrs.get("id", ""),
                "class": attrs.get("class", ""),
            }
        )

    start_landmark = next(
        (item for item in landmarks if item["id"].lower() == "prddetail"),
        None,
    )
    if not start_landmark:
        return None

    boundary = next(
        (
            item
            for item in landmarks
            if item["start"] > start_landmark["start"]
            and (
                item["tag"] == "footer"
                or item["id"].lower() in GLOBAL_BOUNDARY_IDS
                or item["id"].lower().startswith("footer")
            )
        ),
        None,
    )
    region_end = boundary["start"] if boundary else len(html)
    section_landmarks = [
        item
        for item in landmarks
        if start_landmark["start"] <= item["start"] < region_end
        and item["id"].lower() in DETAIL_SECTION_IDS
    ]
    if not section_landmarks or section_landmarks[0]["id"].lower() != "prddetail":
        section_landmarks.insert(0, start_landmark)

    sections: list[dict[str, Any]] = []
    for index, item in enumerate(section_landmarks):
        end = section_landmarks[index + 1]["start"] if index + 1 < len(section_landmarks) else region_end
        sections.append(
            {
                "id": item["id"],
                "kind": DETAIL_SECTION_IDS.get(item["id"].lower(), "detail"),
                "start": item["start"],
                "end": end,
                "html": html[item["start"]:end],
            }
        )
    return {
        "start": start_landmark["start"],
        "end": region_end,
        "html": html[start_landmark["start"]:region_end],
        "end_marker": (
            f"{boundary['tag']}#{boundary['id']}" if boundary and boundary["id"] else boundary["tag"]
            if boundary
            else "end_of_document"
        ),
        "sections": sections,
    }


def parse_fragment_root(fragment: str, wanted_id: str = "") -> Node:
    parser = PDPParser()
    parser.feed(fragment)
    if wanted_id:
        matched = next(
            (node for node in parser.nodes if node.attrs.get("id", "").lower() == wanted_id.lower()),
            None,
        )
        if matched:
            return matched
    return parser.nodes[0] if parser.nodes else parser.root


def parse_fragment_document(fragment: str) -> Node:
    parser = PDPParser()
    parser.feed(fragment)
    return parser.root


def detail_slice_text_segments(
    fragment: str,
    product_name: str,
    start_index: int,
) -> list[dict[str, Any]]:
    parser = PDPParser()
    parser.feed(fragment)
    output: list[dict[str, Any]] = []
    for item in parser.root.items:
        if not isinstance(item, Node):
            continue
        output.extend(
            positional_text_segments(
                item,
                "detail",
                product_name,
                start_index + len(output),
            )
        )
    return output


def parse_srcset(raw: str) -> list[str]:
    candidates: list[tuple[float, str]] = []
    for index, part in enumerate(raw.split(",")):
        fields = part.strip().split()
        if not fields:
            continue
        weight = float(index)
        if len(fields) > 1:
            descriptor = fields[-1].lower()
            try:
                if descriptor.endswith("w"):
                    weight = float(descriptor[:-1])
                elif descriptor.endswith("x"):
                    weight = float(descriptor[:-1]) * 10000
            except ValueError:
                pass
        candidates.append((weight, fields[0]))
    return [url for _, url in sorted(candidates)]


def resolve_asset(base_url: str, candidate: str) -> tuple[str | None, str | None]:
    cleaned = candidate.strip().strip("'\"")
    if not cleaned:
        return None, "empty candidate"
    if cleaned.lower().startswith("data:"):
        return cleaned, None
    resolved = urljoin(base_url, cleaned)
    parsed = urlsplit(resolved)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return None, f"unsupported asset URL: {cleaned}"
    return resolved, None


def image_sources(node: Node) -> list[dict[str, str]]:
    nodes = [node]
    if node.tag == "picture":
        nodes.extend(child for child in descendants(node) if child.tag in {"source", "img"})
    found: list[dict[str, str]] = []
    for item in nodes:
        for attr in (*LAZY_ATTRIBUTES, "src", "srcset"):
            raw = item.attrs.get(attr, "").strip()
            if not raw:
                continue
            values = parse_srcset(raw) if attr == "srcset" else [raw]
            found.extend({"attribute": attr, "value": value} for value in values)
    return found


def choose_image_source(
    sources: list[dict[str, str]], base_url: str
) -> tuple[str | None, str | None, str]:
    lazy = [item for item in sources if item["attribute"] in LAZY_ATTRIBUTES]
    if lazy:
        resolved = [(item, *resolve_asset(base_url, item["value"])) for item in lazy]
        unique = {url for _, url, error in resolved if url and not error}
        if len(unique) != 1:
            attrs = ", ".join(item["attribute"] for item, _, _ in resolved)
            return None, attrs or None, "ambiguous lazy-load attributes"
        item, url, error = next(row for row in resolved if row[1] in unique)
        return url, item["attribute"], "resolved" if not error else error or "unresolved"
    srcsets = [item for item in sources if item["attribute"] == "srcset"]
    if srcsets:
        item = srcsets[-1]
        url, error = resolve_asset(base_url, item["value"])
        return url, "srcset", "resolved" if not error else error or "unresolved"
    plain = [item for item in sources if item["attribute"] == "src"]
    if plain:
        item = plain[0]
        url, error = resolve_asset(base_url, item["value"])
        return url, "src", "resolved" if not error else error or "unresolved"
    if sources:
        item = sources[0]
        url, error = resolve_asset(base_url, item["value"])
        return url, item["attribute"], "resolved" if not error else error or "unresolved"
    return None, None, "no supported source attribute"


def nearest_context(node: Node, root: Node) -> str:
    current = node.parent
    while current and current is not root:
        text = node_text(current, 120)
        if text:
            return text
        current = current.parent
    return ""


def image_context_classification(node: Node, root: Node) -> str:
    current: Node | None = node.parent
    while current and current is not root:
        tokens = attr_tokens(current)
        joined = " ".join(tokens)
        if any(token in joined for token in ("recommend", "related", "relation", "cross-sell", "recent")):
            return "merchandising_widget"
        if any(token in joined for token in ("review", "snap_widget")):
            return "reviews"
        if any(token in joined for token in ("qna", "question")):
            return "qna"
        if any(token in joined for token in ("support", "service", "cscenter")):
            return "support"
        if any(token in joined for token in ("nav", "menu")):
            return "chrome"
        current = current.parent
    context = nearest_context(node, root)
    widget_signals = (
        bool(WIDGET_HEADING_RE.search(context)),
        len(PRICE_TOKEN_RE.findall(context)) >= 3,
    )
    return "merchandising_widget" if all(widget_signals) else "product_media"


def enumerate_images(root: Node, base_url: str, product_name: str) -> list[dict[str, Any]]:
    components: list[Node] = []
    picture_nodes: set[int] = set()
    for node in descendants(root):
        if node.tag == "picture":
            components.append(node)
            picture_nodes.add(id(node))
        elif node.tag == "img":
            parent = node.parent
            inside_picture = False
            while parent and parent is not root:
                if id(parent) in picture_nodes or parent.tag == "picture":
                    inside_picture = True
                    break
                parent = parent.parent
            if not inside_picture:
                components.append(node)
        elif node.attrs.get("style") and BACKGROUND_RE.search(node.attrs["style"]):
            components.append(node)

    output: list[dict[str, Any]] = []
    for index, node in enumerate(components, 1):
        if node.tag in {"img", "picture"}:
            sources = image_sources(node)
        else:
            match = BACKGROUND_RE.search(node.attrs.get("style", ""))
            sources = [{"attribute": "style.background-image", "value": match.group(2)}] if match else []
        resolved, chosen_attr, resolution = choose_image_source(sources, base_url)
        alt_node = node
        if node.tag == "picture":
            alt_node = next((child for child in descendants(node) if child.tag == "img"), node)
        alt = alt_node.attrs.get("alt", "")
        context = nearest_context(node, root)
        promo_haystack = " ".join([resolved or "", alt, context[:200]])
        product_related = bool(product_name and compact_text(product_name).lower() in promo_haystack.lower())
        promo_signals = {
            "asset_or_text_vocabulary": bool(PROMO_RE.search(promo_haystack)),
            "no_current_product_identity": not product_related,
        }
        output.append(
            {
                "source_id": f"detail_image_{index:03d}",
                "tag": node.tag,
                "dom_order": node.order,
                "source_candidates": sources,
                "chosen_attribute": chosen_attr,
                "resolved_url": resolved,
                "resolution": resolution,
                "alt": alt,
                "context_text": context,
                "classification": image_context_classification(node, root),
                "promo_signals": promo_signals,
                "promo_banner_candidate": all(promo_signals.values()),
            }
        )
        output[-1]["eligible_for_product_facts"] = bool(
            output[-1]["classification"] == "product_media"
            and not output[-1]["promo_banner_candidate"]
        )
    return output


def extract_product_name(jsonld: list[dict[str, Any]]) -> str:
    for block in jsonld:
        try:
            value = json.loads(block["raw"])
        except (TypeError, ValueError):
            continue
        stack = [value]
        while stack:
            item = stack.pop()
            if isinstance(item, dict):
                types = item.get("@type", [])
                if not isinstance(types, list):
                    types = [types]
                if "Product" in types and compact_text(str(item.get("name", ""))):
                    return compact_text(str(item["name"]))
                stack.extend(item.values())
            elif isinstance(item, list):
                stack.extend(item)
    return ""


def link_evidence(node: Node, final_url: str) -> dict[str, Any]:
    """Preserve a link element's complete ordered attributes plus resolved href."""
    return {
        "source_id": f"head:link:{node.order}",
        "href": urljoin(final_url, node.attrs.get("href", "")),
        "rel_tokens": node.attrs.get("rel", "").lower().split(),
        "attributes": [
            {"name": name, "value": value} for name, value in node.attrs_list
        ],
    }


def parse_document(
    html: str,
    final_url: str,
    x_robots: list[str],
    include_detail_root: bool = True,
) -> dict[str, Any]:
    parser = PDPParser()
    parser.feed(html)
    head = next((node for node in parser.nodes if node.tag == "head"), None)
    title_node = next((node for node in descendants(head) if node.tag == "title"), None) if head else None
    meta_robots: list[dict[str, Any]] = []
    canonical: list[dict[str, Any]] = []
    alternates: list[dict[str, Any]] = []
    og_tags: list[dict[str, Any]] = []
    for node in descendants(head) if head else []:
        if node.tag == "meta":
            name = node.attrs.get("name", "")
            prop = node.attrs.get("property", "")
            if name.lower() == "robots" or name.lower().endswith("bot"):
                meta_robots.append(
                    {"source_id": f"head:meta:{node.order}", "name": name, "content": node.attrs.get("content", "")}
                )
            if prop.lower().startswith("og:"):
                og_tags.append(
                    {"source_id": f"head:meta:{node.order}", "property": prop, "content": node.attrs.get("content", "")}
                )
        if node.tag == "link" and "canonical" in node.attrs.get("rel", "").lower().split():
            canonical.append(link_evidence(node, final_url))
        if node.tag == "link" and "alternate" in node.attrs.get("rel", "").lower().split():
            alternate = link_evidence(node, final_url)
            alternate["hreflang"] = node.attrs.get("hreflang", "")
            alternate["media"] = node.attrs.get("media", "")
            alternates.append(alternate)

    jsonld: list[dict[str, Any]] = []
    for node in parser.nodes:
        if node.tag == "script" and node.attrs.get("type", "").lower().split(";", 1)[0].strip() == "application/ld+json":
            jsonld.append(
                {
                    "source_id": f"jsonld_block_{len(jsonld) + 1:03d}",
                    "dom_order": node.order,
                    "raw": raw_contents(node),
                }
            )

    product_name = extract_product_name(jsonld)
    if not include_detail_root:
        return {
            "head": {
                "title": node_text(title_node) if title_node else "",
                "meta_robots": meta_robots,
                "x_robots_tag": x_robots,
                "canonical": canonical,
                "alternates": alternates,
                "og_tags": og_tags,
            },
            "jsonld_blocks": jsonld,
            "product_identity": {"jsonld_name": product_name},
            "detail_root": None,
        }
    bounded = bounded_detail_region(html)
    if bounded:
        detail_section = bounded["sections"][0]
        detail_root = parse_fragment_document(detail_section["html"])
        selector = f"#{detail_section['id']}"
        fallback = False
        images = enumerate_images(detail_root, final_url, product_name)
        text_segments: list[dict[str, Any]] = []
        for section_data in bounded["sections"]:
            if section_data["kind"] == "detail":
                text_segments.extend(
                    detail_slice_text_segments(
                        section_data["html"],
                        product_name,
                        len(text_segments) + 1,
                    )
                )
            else:
                section_root = parse_fragment_root(section_data["html"], section_data["id"])
                text_segments.extend(
                    positional_text_segments(
                        section_root,
                        section_data["kind"],
                        product_name,
                        len(text_segments) + 1,
                    )
                )
        detail_html = bounded["html"]
        boundary = {
            "method": "raw_semantic_landmarks",
            "start_marker": selector,
            "end_marker": bounded["end_marker"],
            "start_byte": bounded["start"],
            "end_byte": bounded["end"],
        }
    else:
        detail_root, selector, fallback = choose_detail_root(parser)
        images = enumerate_images(detail_root, final_url, product_name)
        text_segments = positional_text_segments(detail_root, "detail", product_name)
        detail_html = raw_contents(detail_root)
        boundary = {
            "method": "parsed_dom_fallback",
            "start_marker": selector,
            "end_marker": None,
            "start_byte": None,
            "end_byte": None,
        }
    classification_counts: dict[str, int] = {}
    for image in images:
        classification = image["classification"]
        classification_counts[classification] = classification_counts.get(classification, 0) + 1
    text_classes = (
        "product_copy", "platform_boilerplate", "merchandising_widget", "chrome",
        "reviews", "qna", "support",
    )
    classified_text = {
        classification: "\n".join(
            segment["text"]
            for segment in text_segments
            if segment["classification"] == classification
        )
        for classification in text_classes
    }
    return {
        "head": {
            "title": node_text(title_node) if title_node else "",
            "meta_robots": meta_robots,
            "x_robots_tag": x_robots,
            "canonical": canonical,
            "alternates": alternates,
            "og_tags": og_tags,
        },
        "jsonld_blocks": jsonld,
        "product_identity": {"jsonld_name": product_name},
        "detail_root": {
            "selector": selector,
            "fallback": fallback,
            "tag": detail_root.tag,
            "dom_order": detail_root.order,
            "boundary": boundary,
            "html_sha256": hashlib.sha256(detail_html.encode("utf-8")).hexdigest(),
            "text_segments": text_segments,
            "machine_readable_character_count": len(
                "\n".join(segment["text"] for segment in text_segments)
            ),
            "text_classification_character_counts": {
                classification: len(value)
                for classification, value in classified_text.items()
            },
            "image_component_count": len(images),
            "image_classification_counts": classification_counts,
            "product_fact_eligible_image_count": sum(
                1 for image in images if image["eligible_for_product_facts"]
            ),
            "image_components": images,
        },
    }


def headers_list(message: Any) -> list[dict[str, str]]:
    return [{"name": name, "value": value} for name, value in message.items()]


def compact_probe(response: dict[str, Any]) -> dict[str, Any]:
    keep_headers = {"content-type", "location", "server", "x-via"}
    return {
        "status": response.get("status"),
        "final_url": response.get("final_url"),
        "headers": [
            header for header in response.get("headers", []) if header["name"].lower() in keep_headers
        ],
        "redirects": response.get("redirects", []),
        "error": response.get("error"),
        "elapsed_ms": response.get("elapsed_ms"),
    }


def ssl_context() -> ssl.SSLContext:
    system_bundle = "/etc/ssl/cert.pem"
    if os.path.isfile(system_bundle):
        return ssl.create_default_context(cafile=system_bundle)
    return ssl.create_default_context()


class SameHostRedirects(HTTPRedirectHandler):
    def __init__(self, host: str) -> None:
        self.host = host.lower().rstrip(".")
        self.history: list[dict[str, Any]] = []

    def redirect_request(self, req: Request, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> Request:
        resolved = urljoin(req.full_url, newurl)
        parsed = urlsplit(resolved)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.hostname.lower().rstrip(".") != self.host
            or parsed.username
            or parsed.password
        ):
            raise URLError("cross-host or unsafe redirect blocked")
        if len(self.history) >= MAX_REDIRECTS:
            raise URLError("redirect cap exceeded")
        self.history.append({"status": code, "from": req.full_url, "to": resolved})
        return super().redirect_request(req, fp, code, msg, headers, resolved)


def decode_body(raw: bytes, headers: Any) -> tuple[str, str]:
    if headers.get("Content-Encoding", "").lower() == "gzip":
        raw = gzip.decompress(raw)
    content_type = headers.get("Content-Type", "")
    match = re.search(r"charset\s*=\s*['\"]?([^;\s'\"]+)", content_type, re.IGNORECASE)
    candidates = [match.group(1)] if match else []
    candidates.extend(["utf-8", "cp949", "euc-kr"])
    for encoding in candidates:
        try:
            return raw.decode(encoding), encoding
        except (LookupError, UnicodeDecodeError):
            continue
    return raw.decode("utf-8", errors="replace"), "utf-8-replace"


def fetch(
    url: str,
    user_agent: str,
    allowed_host: str,
    deadline: float,
    body_cap: int = 0,
) -> dict[str, Any]:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        return {"status": None, "final_url": None, "headers": [], "error": "total time cap exceeded"}
    redirector = SameHostRedirects(allowed_host)
    opener = build_opener(ProxyHandler({}), redirector, HTTPSHandler(context=ssl_context()))
    request = Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.1",
            "Accept-Encoding": "identity",
            "Cache-Control": "no-cache",
        },
        method="GET",
    )
    started = time.monotonic()
    response: Any = None
    try:
        response = opener.open(request, timeout=max(0.25, min(PER_REQUEST_SECONDS, remaining)))
    except HTTPError as error:
        response = error
    except (OSError, URLError, ValueError) as error:
        return {
            "status": None,
            "final_url": None,
            "headers": [],
            "redirects": redirector.history,
            "error": str(error),
            "elapsed_ms": round((time.monotonic() - started) * 1000),
        }

    try:
        raw = response.read(body_cap + 1) if body_cap else b""
        truncated = bool(body_cap and len(raw) > body_cap)
        if truncated:
            raw = raw[:body_cap]
        body, encoding = decode_body(raw, response.headers) if body_cap else ("", None)
        return {
            "status": int(response.status),
            "final_url": response.geturl(),
            "headers": headers_list(response.headers),
            "redirects": redirector.history,
            "error": None,
            "elapsed_ms": round((time.monotonic() - started) * 1000),
            "bytes_read": len(raw),
            "body_sha256": hashlib.sha256(raw).hexdigest() if body_cap else None,
            "body_truncated": truncated,
            "encoding": encoding,
            "body": body,
        }
    except (OSError, ValueError) as error:
        return {
            "status": int(response.status),
            "final_url": response.geturl(),
            "headers": headers_list(response.headers),
            "redirects": redirector.history,
            "error": f"body read failed: {error}",
            "elapsed_ms": round((time.monotonic() - started) * 1000),
        }
    finally:
        response.close()


def validate_image_dir(raw: str) -> str:
    if not os.path.isabs(raw):
        raise ValueError("--image-dir must be an absolute caller-supplied temporary directory")
    if os.path.islink(raw) or not os.path.isdir(raw):
        raise ValueError("--image-dir must already exist as a non-symlink directory")
    if os.listdir(raw):
        raise ValueError("--image-dir must be empty so no existing file can be overwritten")
    return os.path.realpath(raw)


def asset_extension(url: str, content_type: str) -> str:
    mime = content_type.split(";", 1)[0].strip().lower()
    guessed = mimetypes.guess_extension(mime) if mime.startswith("image/") else None
    if guessed:
        return ".jpg" if guessed in {".jpe", ".jpeg"} else guessed
    suffix = os.path.splitext(urlsplit(url).path)[1].lower()
    return suffix if re.fullmatch(r"\.[a-z0-9]{1,5}", suffix) else ".img"


def fetch_asset(
    url: str,
    source_id: str,
    allowed_host: str,
    image_dir: str,
    deadline: float,
    remaining_total_bytes: int,
) -> dict[str, Any]:
    parsed = urlsplit(url)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.hostname.lower().rstrip(".") != allowed_host
        or parsed.username
        or parsed.password
    ):
        return {
            "status": "skipped",
            "local_path": None,
            "error": "asset is not on the exact page host",
            "bytes_written": 0,
        }
    if remaining_total_bytes <= 0:
        return {
            "status": "skipped",
            "local_path": None,
            "error": "total asset byte cap reached",
            "bytes_written": 0,
        }
    remaining_time = deadline - time.monotonic()
    if remaining_time <= 0:
        return {
            "status": "skipped",
            "local_path": None,
            "error": "total time cap exceeded",
            "bytes_written": 0,
        }

    redirector = SameHostRedirects(allowed_host)
    opener = build_opener(ProxyHandler({}), redirector, HTTPSHandler(context=ssl_context()))
    request = Request(
        url,
        headers={
            "User-Agent": BROWSER_UA,
            "Accept": "image/avif,image/webp,image/png,image/jpeg,image/gif,image/*;q=0.8,*/*;q=0.1",
            "Accept-Encoding": "identity",
            "Cache-Control": "no-cache",
        },
        method="GET",
    )
    started = time.monotonic()
    response: Any = None
    try:
        response = opener.open(
            request,
            timeout=max(0.25, min(PER_REQUEST_SECONDS, remaining_time)),
        )
    except HTTPError as error:
        response = error
    except (OSError, URLError, ValueError) as error:
        return {
            "status": "failed",
            "http_status": None,
            "local_path": None,
            "error": str(error),
            "bytes_written": 0,
            "elapsed_ms": round((time.monotonic() - started) * 1000),
        }

    try:
        http_status = int(response.status)
        content_type = response.headers.get("Content-Type", "")
        if http_status < 200 or http_status >= 300:
            return {
                "status": "failed",
                "http_status": http_status,
                "local_path": None,
                "error": f"HTTP {http_status}",
                "bytes_written": 0,
                "elapsed_ms": round((time.monotonic() - started) * 1000),
            }
        if not content_type.lower().startswith("image/"):
            return {
                "status": "failed",
                "http_status": http_status,
                "local_path": None,
                "error": f"non-image Content-Type: {content_type or 'missing'}",
                "bytes_written": 0,
                "elapsed_ms": round((time.monotonic() - started) * 1000),
            }
        cap = min(MAX_ASSET_BYTES, remaining_total_bytes)
        raw = response.read(cap + 1)
        if len(raw) > cap:
            return {
                "status": "failed",
                "http_status": http_status,
                "local_path": None,
                "error": "asset byte cap exceeded",
                "bytes_written": 0,
                "elapsed_ms": round((time.monotonic() - started) * 1000),
            }
        extension = asset_extension(response.geturl(), content_type)
        local_path = os.path.join(image_dir, source_id + extension)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(local_path, flags, 0o600)
        with os.fdopen(descriptor, "wb") as output:
            output.write(raw)
        return {
            "status": "fetched",
            "http_status": http_status,
            "final_url": response.geturl(),
            "content_type": content_type,
            "local_path": local_path,
            "error": None,
            "bytes_written": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "elapsed_ms": round((time.monotonic() - started) * 1000),
        }
    except (OSError, ValueError) as error:
        return {
            "status": "failed",
            "http_status": int(response.status),
            "local_path": None,
            "error": str(error),
            "bytes_written": 0,
            "elapsed_ms": round((time.monotonic() - started) * 1000),
        }
    finally:
        response.close()


def fetch_product_images(
    images: list[dict[str, Any]],
    host: str,
    image_dir: str,
    deadline: float,
) -> dict[str, Any]:
    fetched = 0
    bytes_written = 0
    attempted = 0
    for image in images:
        if not image.get("eligible_for_product_facts"):
            image["asset_fetch"] = {
                "status": "skipped",
                "local_path": None,
                "error": "non-product or store-wide promotional component",
                "bytes_written": 0,
            }
            continue
        if attempted >= MAX_ASSET_COUNT:
            image["asset_fetch"] = {
                "status": "skipped",
                "local_path": None,
                "error": "asset count cap reached",
                "bytes_written": 0,
            }
            continue
        resolved = image.get("resolved_url")
        if not resolved or resolved.lower().startswith("data:"):
            image["asset_fetch"] = {
                "status": "skipped",
                "local_path": None,
                "error": "no fetchable resolved URL",
                "bytes_written": 0,
            }
            continue
        attempted += 1
        result = fetch_asset(
            resolved,
            image["source_id"],
            host,
            image_dir,
            deadline,
            MAX_ASSET_TOTAL_BYTES - bytes_written,
        )
        image["asset_fetch"] = result
        if result["status"] == "fetched":
            fetched += 1
            bytes_written += result["bytes_written"]
    return {
        "requested": True,
        "directory": image_dir,
        "attempted_count": attempted,
        "fetched_count": fetched,
        "bytes_written": bytes_written,
        "eligible_count": sum(1 for image in images if image.get("eligible_for_product_facts")),
        "skipped_or_failed_count": len(images) - fetched,
    }


def validate_url(raw: str) -> tuple[str, str]:
    parsed = urlsplit(raw)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("URL scheme must be http or https")
    if not parsed.hostname:
        raise ValueError("URL must include a host")
    if parsed.username or parsed.password:
        raise ValueError("URL credentials are not allowed")
    path = quote(parsed.path or "/", safe="/%:@!$&'()*+,;=-._~")
    query = quote(parsed.query, safe="=&?/:;+,%@[]!$'()*-._~")
    target = urlunsplit((parsed.scheme, parsed.netloc, path, query, ""))
    return target, parsed.hostname.lower().rstrip(".")


def origin_resource(target: str, path: str) -> str:
    parsed = urlsplit(target)
    return urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))


def response_without_body(response: dict[str, Any]) -> tuple[dict[str, Any], str]:
    body = response.pop("body", "")
    return response, body


def probe_resources(
    resources: dict[str, str],
    browser_responses: dict[str, dict[str, Any]],
    host: str,
    deadline: float,
) -> dict[str, Any]:
    probes: dict[str, Any] = {}
    for name, user_agent in CRAWLER_UAS.items():
        resource_probes: dict[str, Any] = {}
        edge_block = False
        for resource_name, url in resources.items():
            response = fetch(url, user_agent, host, deadline)
            resource_probes[resource_name] = compact_probe(response)
            edge_block = edge_block or bool(
                browser_responses[resource_name].get("status") == 200
                and response.get("status") == 403
            )
        probes[name] = {
            "user_agent": user_agent,
            "resources": resource_probes,
            "edge_block_suspected": edge_block,
        }
    return probes


def base_payload(
    mode: str,
    input_url: str,
    image_dir: str | None = None,
    content_only: bool = False,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "mode": mode,
        "input_url": input_url,
        "limits": {
            "max_body_bytes": MAX_BODY_BYTES,
            "max_site_resource_bytes": MAX_SITE_RESOURCE_BYTES,
            "max_asset_bytes": MAX_ASSET_BYTES,
            "max_asset_total_bytes": MAX_ASSET_TOTAL_BYTES,
            "max_asset_count": MAX_ASSET_COUNT,
            "per_request_seconds": PER_REQUEST_SECONDS,
            "total_seconds": TOTAL_SECONDS,
            "max_redirects": MAX_REDIRECTS,
        },
        "safety": {
            "network_read_only": True,
            "temporary_local_writes": bool(image_dir),
            "temporary_write_directory": image_dir,
            "cookies": False,
            "credentials": False,
            "cross_host_redirects": False,
            "discovered_url_fetches": bool(image_dir),
            "asset_fetches": bool(image_dir),
            "asset_scope": "resolved product-image components on the exact page host only" if image_dir else None,
            "overwrites_existing_files": False,
            "content_only": content_only,
            "crawler_probes_suppressed": content_only,
        },
    }


def emit(payload: dict[str, Any], exit_code: int = 0) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
    raise SystemExit(exit_code)


def main() -> None:
    started = time.monotonic()
    args = sys.argv[1:]
    mode = "page"
    image_dir_raw: str | None = None
    content_only = False
    positional: list[str] = []
    index = 0
    while index < len(args):
        if args[index] == "--mode" and index + 1 < len(args):
            mode = args[index + 1]
            index += 2
        elif args[index] == "--image-dir" and index + 1 < len(args):
            image_dir_raw = args[index + 1]
            index += 2
        elif args[index] == "--content-only":
            content_only = True
            index += 1
        elif args[index].startswith("--"):
            positional = []
            break
        else:
            positional.append(args[index])
            index += 1
    if (
        mode not in {"page", "site"}
        or len(positional) != 1
        or (image_dir_raw and mode != "page")
        or (content_only and mode != "page")
    ):
        emit(
            {
                "schema": SCHEMA,
                "fatal_error": (
                    "usage: fetch_evidence.py [--mode page|site] [--content-only] "
                    "[--image-dir EXISTING_EMPTY_ABSOLUTE_DIR] <http-or-https-url>; "
                    "--content-only and --image-dir are page-mode only"
                ),
            },
            2,
        )
    raw_url = positional[0]
    try:
        target_url, host = validate_url(raw_url)
    except ValueError as error:
        emit({"schema": SCHEMA, "mode": mode, "fatal_error": str(error)}, 2)
    image_dir: str | None = None
    if image_dir_raw:
        try:
            image_dir = validate_image_dir(image_dir_raw)
        except ValueError as error:
            emit({"schema": SCHEMA, "mode": mode, "fatal_error": str(error)}, 2)

    deadline = started + TOTAL_SECONDS
    robots_url = origin_resource(target_url, "/robots.txt")

    if mode == "site":
        resources = {
            "target": target_url,
            "robots_txt": robots_url,
            "llms_txt": origin_resource(target_url, "/llms.txt"),
            "sitemap_xml": origin_resource(target_url, "/sitemap.xml"),
        }
        browser_responses: dict[str, dict[str, Any]] = {}
        raw_bodies: dict[str, str] = {}
        for resource_name, resource_url in resources.items():
            cap = MAX_BODY_BYTES if resource_name == "target" else MAX_SITE_RESOURCE_BYTES
            response = fetch(resource_url, BROWSER_UA, host, deadline, cap)
            browser_responses[resource_name], raw_bodies[resource_name] = response_without_body(response)

        probes = probe_resources(resources, browser_responses, host, deadline)
        target_response = browser_responses["target"]
        x_robots = [
            header["value"]
            for header in target_response.get("headers", [])
            if header["name"].lower() == "x-robots-tag"
        ]
        parsed = (
            parse_document(
                raw_bodies["target"],
                target_response.get("final_url") or target_url,
                x_robots,
                include_detail_root=False,
            )
            if raw_bodies["target"]
            else {
                "head": {
                    "title": "",
                    "meta_robots": [],
                    "x_robots_tag": x_robots,
                    "canonical": [],
                    "alternates": [],
                    "og_tags": [],
                },
                "jsonld_blocks": [],
                "product_identity": {"jsonld_name": ""},
                "detail_root": None,
            }
        )
        site_resources = {
            name: {
                "url": resources[name],
                "response": browser_responses[name],
                "raw": raw_bodies[name],
                "crawler_probes": {
                    crawler: result["resources"][name] for crawler, result in probes.items()
                },
            }
            for name in resources
        }
        payload = {
            **base_payload(mode, target_url),
            "site_resources": site_resources,
            **parsed,
            "crawler_probes": probes,
            "elapsed_ms": round((time.monotonic() - started) * 1000),
        }
        emit(payload)

    resources = {"target": target_url} if content_only else {"target": target_url, "robots_txt": robots_url}
    document_response = fetch(target_url, BROWSER_UA, host, deadline, MAX_BODY_BYTES)
    robots_response = (
        {
            "status": None,
            "final_url": None,
            "headers": [],
            "redirects": [],
            "error": None,
            "body": "",
            "skipped": "content-only mode",
        }
        if content_only
        else fetch(robots_url, BROWSER_UA, host, deadline, MAX_SITE_RESOURCE_BYTES)
    )
    browser_responses = {"target": document_response}
    if not content_only:
        browser_responses["robots_txt"] = robots_response
    probes = {} if content_only else probe_resources(resources, browser_responses, host, deadline)

    document_response, html = response_without_body(document_response)
    robots_response, robots_text = response_without_body(robots_response)
    x_robots = [
        header["value"]
        for header in document_response.get("headers", [])
        if header["name"].lower() == "x-robots-tag"
    ]
    parsed = parse_document(html, document_response.get("final_url") or target_url, x_robots) if html else {
        "head": {
            "title": "",
            "meta_robots": [],
            "x_robots_tag": x_robots,
            "canonical": [],
            "alternates": [],
            "og_tags": [],
        },
        "jsonld_blocks": [],
        "product_identity": {"jsonld_name": ""},
        "detail_root": None,
    }
    asset_fetch = {
        "requested": False,
        "directory": None,
        "attempted_count": 0,
        "fetched_count": 0,
        "bytes_written": 0,
        "eligible_count": (
            parsed["detail_root"].get("product_fact_eligible_image_count", 0)
            if parsed.get("detail_root")
            else 0
        ),
        "skipped_or_failed_count": 0,
    }
    if image_dir and parsed.get("detail_root"):
        asset_fetch = fetch_product_images(
            parsed["detail_root"]["image_components"],
            host,
            image_dir,
            deadline,
        )
    payload = {
        **base_payload(mode, target_url, image_dir, content_only),
        "robots_url": robots_url,
        "document": {"response": document_response},
        "robots_txt": {"response": robots_response, "text": robots_text},
        **parsed,
        "asset_fetch": asset_fetch,
        "crawler_probes": probes,
        "elapsed_ms": round((time.monotonic() - started) * 1000),
    }
    emit(payload)


if __name__ == "__main__":
    main()

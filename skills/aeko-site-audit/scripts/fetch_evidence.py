#!/usr/bin/env python3
"""Read-only raw web evidence fetcher. Usage: fetch_evidence.py [--mode page|site] <URL>"""

from __future__ import annotations

import gzip
import hashlib
import json
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


def positional_text_segments(root: Node) -> list[dict[str, Any]]:
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
                    "source_id": f"text_segment_{len(output) + 1:03d}",
                    "section": section_name,
                    "module": module_name,
                    "text": text,
                }
            )
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


def enumerate_images(root: Node, base_url: str, product_name: str) -> list[dict[str, Any]]:
    components: list[Node] = []
    picture_nodes: set[int] = set()
    for node in descendants(root):
        if has_excluded_ancestor(node, root):
            continue
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
                "promo_signals": promo_signals,
                "promo_banner_candidate": all(promo_signals.values()),
            }
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


def parse_document(html: str, final_url: str, x_robots: list[str]) -> dict[str, Any]:
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
            canonical.append(
                {"source_id": f"head:link:{node.order}", "href": urljoin(final_url, node.attrs.get("href", ""))}
            )
        if node.tag == "link" and "alternate" in node.attrs.get("rel", "").lower().split():
            alternates.append(
                {
                    "source_id": f"head:link:{node.order}",
                    "hreflang": node.attrs.get("hreflang", ""),
                    "href": urljoin(final_url, node.attrs.get("href", "")),
                }
            )

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
    detail_root, selector, fallback = choose_detail_root(parser)
    images = enumerate_images(detail_root, final_url, product_name)
    detail_html = raw_contents(detail_root)
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
            "html_sha256": hashlib.sha256(detail_html.encode("utf-8")).hexdigest(),
            "text_segments": positional_text_segments(detail_root),
            "image_component_count": len(images),
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


def base_payload(mode: str, input_url: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "mode": mode,
        "input_url": input_url,
        "limits": {
            "max_body_bytes": MAX_BODY_BYTES,
            "max_site_resource_bytes": MAX_SITE_RESOURCE_BYTES,
            "per_request_seconds": PER_REQUEST_SECONDS,
            "total_seconds": TOTAL_SECONDS,
            "max_redirects": MAX_REDIRECTS,
        },
        "safety": {
            "read_only": True,
            "cookies": False,
            "credentials": False,
            "cross_host_redirects": False,
            "discovered_url_fetches": False,
            "asset_fetches": False,
        },
    }


def emit(payload: dict[str, Any], exit_code: int = 0) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
    raise SystemExit(exit_code)


def main() -> None:
    started = time.monotonic()
    args = sys.argv[1:]
    mode = "page"
    if len(args) == 3 and args[0] == "--mode" and args[1] in {"page", "site"}:
        mode = args[1]
        raw_url = args[2]
    elif len(args) == 1:
        raw_url = args[0]
    else:
        emit(
            {
                "schema": SCHEMA,
                "fatal_error": "usage: fetch_evidence.py [--mode page|site] <http-or-https-url>",
            },
            2,
        )
    try:
        target_url, host = validate_url(raw_url)
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
            parse_document(raw_bodies["target"], target_response.get("final_url") or target_url, x_robots)
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
                **({"raw": raw_bodies[name]} if name != "target" else {}),
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

    resources = {"target": target_url, "robots_txt": robots_url}
    document_response = fetch(target_url, BROWSER_UA, host, deadline, MAX_BODY_BYTES)
    robots_response = fetch(robots_url, BROWSER_UA, host, deadline, MAX_SITE_RESOURCE_BYTES)
    browser_responses = {"target": document_response, "robots_txt": robots_response}
    probes = probe_resources(resources, browser_responses, host, deadline)

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
    payload = {
        **base_payload(mode, target_url),
        "robots_url": robots_url,
        "document": {"response": document_response},
        "robots_txt": {"response": robots_response, "text": robots_text},
        **parsed,
        "crawler_probes": probes,
        "elapsed_ms": round((time.monotonic() - started) * 1000),
    }
    emit(payload)


if __name__ == "__main__":
    main()

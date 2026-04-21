---
name: aeo-audit-local
description: >
  Audit local content files for AI citability. Scans a directory of HTML,
  Markdown, and text files, scores each for AI engine citability, then
  produces a master scorecard with aggregated findings and prioritized
  recommendations. Use when a user wants to evaluate their local content
  library for AEO readiness.
argument-hint: <directory-path>
allowed-tools: aeko_scan_content_directory, aeko_read_content_file, aeko_audit_content_file, aeko_save_content
---

# AEO Local Content Audit — Batch Citability Analysis

You are performing a batch AEO audit on local content files in a directory.

## Step 1: Scan the directory

Call `aeko_scan_content_directory` with the user-provided directory path (or let it default to `AEKO_CONTENT_DIR`).

Note the total file count, types, and sizes. If no files are found, inform the user and suggest checking the path or extensions.

## Step 2: Prioritize files

From the scan results, prioritize files for auditing:

1. **HTML files** first (most relevant for web content optimization)
2. **Markdown files** next (common for blog/docs content)
3. **Other text files** last (CSV, JSON, TXT)

Select up to **20 files** for auditing. If there are more than 20 eligible files, prioritize by:
- Newest modification date
- Larger word count (more content to analyze)
- HTML/MD over other types

Tell the user which files you're auditing and why.

## Step 3: Audit each file

For each selected file, call `aeko_audit_content_file` with the file path and language (if known).

Collect results: file name, type, word count, citability score, grade, and top issue.

If any file fails to score (e.g., backend unreachable), note it as "N/A" and continue with remaining files.

## Step 4: Build master scorecard

Present results as a markdown table:

```
| # | File | Type | Words | Score | Grade | Top Issue |
|---|------|------|-------|-------|-------|-----------|
| 1 | product-page.html | .html | 850 | 72/100 | C | Weak answer blocks |
| 2 | about.md | .md | 1,200 | 81/100 | B | Low statistical density |
```

Sort by score (lowest first) to highlight files needing the most work.

## Step 5: Aggregate findings

Calculate and present:

- **Average citability score** across all audited files
- **Score distribution**: how many A/B/C/D/F grades
- **Overall grade** based on the average

### Common patterns across files

Identify recurring issues. For example:
- "6 of 12 files scored below 50 on Answer Block Quality"
- "Most files lack statistical data — average Statistical Density: 28/100"
- "HTML files score 15 points higher than Markdown on average"

### Dimension averages

| Dimension | Average | Min | Max |
|-----------|---------|-----|-----|
| Answer Block Quality | XX | XX | XX |
| Self-Containment | XX | XX | XX |
| Structural Readability | XX | XX | XX |
| Statistical Density | XX | XX | XX |
| Uniqueness Signals | XX | XX | XX |

## Step 6: Prioritized recommendations

Group recommendations by severity and impact:

### Critical (fix first)
Issues that appear across many files and have the largest score impact.
Provide specific, actionable advice with examples from the audited files.

### High
Issues in key files (product pages, landing pages) that are dragging scores down.

### Medium
Common patterns that would lift the overall average with consistent fixes.

### Quick Wins
Changes that are easy to implement and would improve multiple files at once.

## Step 7: Offer to save the report

Ask the user if they'd like to save the full audit report.

If yes, call `aeko_save_content` with filename `aeo-local-audit-YYYY-MM-DD.md` and the complete report content.

Also suggest next steps:
- Use `/aeo-optimize` on specific low-scoring HTML files
- Use `/create-blog-article` to rewrite low-scoring content
- Use `/generate-jsonld` to add structured data to HTML files

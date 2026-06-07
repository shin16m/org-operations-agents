#!/usr/bin/env python3
"""Publish team markdown artifacts as human-readable static HTML.

Usage:
  python tools/publish_artifact_html.py --dry-run
  python tools/publish_artifact_html.py --publish
  python tools/publish_artifact_html.py --file output/development/requirements/foo.md

Style SSOT: output/ux/specs/*-artifact-html-style.md · output/_shared/artifact.css
"""
from __future__ import annotations

import argparse
import html
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS_SRC = ROOT / "output/_shared/artifact.css"
HTML_OUT = ROOT / "output/development/html"
CSS_OUT = HTML_OUT / "_shared"

ARTIFACT_SOURCES: list[tuple[str, Path, str]] = [
    ("要件定義書", ROOT / "output/development/requirements", "requirements"),
    ("ソフト設計書", ROOT / "output/development/design", "design"),
    ("機能仕様書", ROOT / "output/development/specs", "specs"),
    ("プロダクト取説", ROOT / "output/development/docs", "docs"),
    ("UX仕様", ROOT / "output/ux/specs", "ux-specs"),
    ("UXデザイン", ROOT / "output/ux/design-system", "ux-design"),
]

SKIP_NAMES = {"README.md"}


def slugify(name: str) -> str:
    stem = Path(name).stem
    return re.sub(r"[^\w\-]+", "-", stem, flags=re.UNICODE).strip("-") or "doc"


def md_to_html(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    in_code = False
    in_table = False
    list_type: str | None = None

    def close_list() -> None:
        nonlocal list_type
        if list_type:
            out.append(f"</{list_type}>")
            list_type = None

    def close_table() -> None:
        nonlocal in_table
        if in_table:
            out.append("</tbody></table>")
            in_table = False

    while i < len(lines):
        line = lines[i]

        if line.strip().startswith("```"):
            close_list()
            close_table()
            if in_code:
                out.append("</code></pre>")
                in_code = False
            else:
                lang = line.strip()[3:].strip()
                cls = f' class="language-{html.escape(lang)}"' if lang else ""
                out.append(f"<pre><code{cls}>")
                in_code = True
            i += 1
            continue

        if in_code:
            out.append(html.escape(line))
            i += 1
            continue

        if "|" in line and line.strip().startswith("|"):
            close_list()
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(re.match(r"^:?-+:?$", c.replace(" ", "")) for c in cells):
                i += 1
                continue
            if not in_table:
                out.append('<table><thead><tr>')
                for j, c in enumerate(cells):
                    out.append(f'<th scope="col">{inline_md(c)}</th>')
                out.append("</tr></thead><tbody>")
                in_table = True
            else:
                out.append("<tr>")
                for c in cells:
                    out.append(f"<td>{inline_md(c)}</td>")
                out.append("</tr>")
            i += 1
            continue

        close_table()

        m = re.match(r"^(#{1,4})\s+(.+)$", line)
        if m:
            close_list()
            level = len(m.group(1))
            text = m.group(2).strip()
            anchor = re.sub(r"[^\w\-]", "", slugify(text).lower()) or f"h{level}"
            out.append(f'<h{level} id="{anchor}">{inline_md(text)}</h{level}>')
            i += 1
            continue

        if line.startswith(">"):
            close_list()
            out.append(f"<blockquote><p>{inline_md(line.lstrip('> ').strip())}</p></blockquote>")
            i += 1
            continue

        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.+)$", line)
        if m:
            kind = "ol" if m.group(2)[0].isdigit() else "ul"
            if list_type != kind:
                close_list()
                out.append(f"<{kind}>")
                list_type = kind
            out.append(f"<li>{inline_md(m.group(3))}</li>")
            i += 1
            continue

        close_list()

        if not line.strip():
            i += 1
            continue

        out.append(f"<p>{inline_md(line.strip())}</p>")
        i += 1

    close_list()
    close_table()
    if in_code:
        out.append("</code></pre>")

    return "\n".join(out)


def inline_md(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def extract_title(md: str, fallback: str) -> str:
    for line in md.splitlines():
        m = re.match(r"^#\s+(.+)$", line.strip())
        if m:
            return m.group(1).strip()
    return fallback


def build_toc(body_html: str) -> str:
    items: list[str] = []
    for m in re.finditer(r'<h([2-3]) id="([^"]+)">([^<]+)</h\1>', body_html):
        level = int(m.group(1))
        anchor = m.group(2)
        title = m.group(3)
        indent = "  " * (level - 2)
        items.append(f'{indent}<li><a href="#{anchor}">{title}</a></li>')
    if not items:
        return ""
    return '<nav class="toc" aria-label="目次"><h2>目次</h2><ul>\n' + "\n".join(items) + "\n</ul></nav>"


def render_page(
    *,
    title: str,
    badge: str,
    body_html: str,
    source_path: Path,
) -> str:
    toc = build_toc(body_html)
    rel_css = "../_shared/artifact.css"
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} — org-ops 成果物</title>
  <link rel="stylesheet" href="{rel_css}">
</head>
<body>
  <header class="doc-header">
    <span class="badge">{html.escape(badge)}</span>
    <h1>{html.escape(title)}</h1>
    <div class="doc-meta">
      <span>source: {html.escape(source_path.as_posix())}</span>
      <span>更新: {updated}</span>
    </div>
  </header>
  {toc}
  <main class="doc-body">
    {body_html}
  </main>
  <footer class="doc-footer">
    org-operations-agents · 読み取り専用 · publish_artifact_html.py
  </footer>
</body>
</html>
"""


def collect_sources() -> list[tuple[str, Path, str]]:
    found: list[tuple[str, Path, str]] = []
    for badge, directory, subdir in ARTIFACT_SOURCES:
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.md")):
            if path.name in SKIP_NAMES:
                continue
            found.append((badge, path, subdir))
    manual = ROOT / "output/development/docs/product-manual.md"
    if manual.is_file() and not any(p == manual for _, p, _ in found):
        found.append(("プロダクト取説", manual, "docs"))
    return found


def publish_one(badge: str, src: Path, subdir: str) -> Path:
    md = src.read_text(encoding="utf-8")
    title = extract_title(md, src.stem)
    body = md_to_html(md)
    page = render_page(title=title, badge=badge, body_html=body, source_path=src.relative_to(ROOT))
    out_dir = HTML_OUT / subdir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{slugify(src.name)}.html"
    out_path.write_text(page, encoding="utf-8")
    return out_path


def write_index(entries: list[dict]) -> Path:
    rows = []
    for e in sorted(entries, key=lambda x: (x["badge"], x["title"])):
        rows.append(
            f'<tr><td><span class="badge">{html.escape(e["badge"])}</span></td>'
            f'<td><a href="{html.escape(e["href"])}">{html.escape(e["title"])}</a></td>'
            f'<td><code>{html.escape(e["source"])}</code></td></tr>'
        )
    body = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>成果物索引 — org-ops</title>
  <link rel="stylesheet" href="_shared/artifact.css">
</head>
<body>
  <header class="doc-header">
    <span class="badge">索引</span>
    <h1>各チーム成果物（HTML）</h1>
    <div class="doc-meta"><span>生成: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}</span></div>
  </header>
  <main class="doc-body">
    <p>markdown 成果物のヒューマン可読 HTML 一覧です。<code>python tools/publish_artifact_html.py --publish</code> で再生成できます。</p>
    <table>
      <thead><tr><th scope="col">種別</th><th scope="col">タイトル</th><th scope="col">ソース</th></tr></thead>
      <tbody>
        {"".join(rows)}
      </tbody>
    </table>
  </main>
  <footer class="doc-footer">org-operations-agents · 読み取り専用</footer>
</body>
</html>
"""
    index_path = HTML_OUT / "index.html"
    index_path.write_text(body, encoding="utf-8")
    return index_path


def copy_css() -> None:
    if not CSS_SRC.is_file():
        raise SystemExit(f"ERROR: missing CSS {CSS_SRC}")
    CSS_OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CSS_SRC, CSS_OUT / "artifact.css")


def cmd_publish(*, dry_run: bool) -> int:
    sources = collect_sources()
    if dry_run:
        for badge, path, subdir in sources:
            print(f"  {badge:12} {path.relative_to(ROOT)} -> html/{subdir}/")
        print(f"DRY_RUN  count={len(sources)}  out={HTML_OUT.relative_to(ROOT)}")
        return 0

    copy_css()
    entries: list[dict] = []
    for badge, path, subdir in sources:
        out = publish_one(badge, path, subdir)
        rel_href = out.relative_to(HTML_OUT).as_posix()
        md = path.read_text(encoding="utf-8")
        entries.append({
            "badge": badge,
            "title": extract_title(md, path.stem),
            "href": rel_href,
            "source": path.relative_to(ROOT).as_posix(),
        })
        print(f"OK  {path.relative_to(ROOT)} -> {out.relative_to(ROOT)}")

    index = write_index(entries)
    print(f"OK  index -> {index.relative_to(ROOT)}  count={len(entries)}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Publish markdown artifacts as HTML")
    p.add_argument("--publish", action="store_true", help="Generate HTML under output/development/html/")
    p.add_argument("--dry-run", action="store_true", help="List targets only")
    p.add_argument("--file", type=Path, help="Convert a single markdown file")
    args = p.parse_args()

    if args.file:
        path = args.file if args.file.is_absolute() else ROOT / args.file
        if not path.is_file():
            print(f"ERROR: not found {path}", file=sys.stderr)
            return 1
        copy_css()
        badge = "単一"
        for b, directory, subdir in ARTIFACT_SOURCES:
            try:
                path.relative_to(directory)
                badge = b
                break
            except ValueError:
                continue
        out = publish_one(badge, path, "single")
        print(f"OK  {out.relative_to(ROOT)}")
        return 0

    if args.dry_run:
        return cmd_publish(dry_run=True)
    if args.publish:
        return cmd_publish(dry_run=False)

    p.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Generate a print-ready HTML version of the GTA6 vocabulary guide."""
import markdown
from pathlib import Path

ROOT = Path(__file__).parent
md_text = (ROOT / "README.md").read_text(encoding="utf-8")

body = markdown.markdown(
    md_text,
    extensions=["tables", "fenced_code", "sane_lists"],
)

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GTA6 英文速成教材 · 核心词汇清单</title>
<style>
  :root {{
    --ink: #1a1a1a;
    --accent: #c8102e;
    --muted: #666;
    --line: #e5e0da;
    --bg-soft: #faf7f2;
  }}
  * {{ box-sizing: border-box; }}
  html {{ -webkit-text-size-adjust: 100%; }}
  body {{
    margin: 0 auto;
    max-width: 820px;
    padding: 32px 40px 80px;
    font-family: -apple-system, "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
    color: var(--ink);
    line-height: 1.7;
    font-size: 15.5px;
    background: #fff;
  }}
  h1 {{
    font-size: 26px;
    line-height: 1.3;
    margin: 0 0 6px;
    letter-spacing: .5px;
  }}
  h1 + blockquote {{
    margin: 0 0 8px;
    color: var(--muted);
    border: none;
    padding: 0;
  }}
  h2 {{
    font-size: 20px;
    margin: 40px 0 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--accent);
  }}
  h3 {{
    font-size: 17px;
    margin: 26px 0 8px;
    color: var(--accent);
  }}
  p {{ margin: 8px 0; }}
  strong {{ color: #111; }}
  blockquote {{
    margin: 8px 0;
    padding: 6px 14px;
    border-left: 3px solid var(--accent);
    background: var(--bg-soft);
    border-radius: 0 6px 6px 0;
    color: #333;
  }}
  table {{
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;
    font-size: 14px;
  }}
  th, td {{
    border: 1px solid var(--line);
    padding: 7px 10px;
    text-align: left;
    vertical-align: top;
  }}
  th {{ background: var(--bg-soft); font-weight: 600; }}
  hr {{ border: none; border-top: 1px solid var(--line); margin: 30px 0; }}
  hr + hr {{ display: none; }}
  em {{ color: var(--muted); }}
  /* word entries: bold head line followed by blockquote example */
  p > strong:only-child {{ display: inline; }}

  @page {{ size: A4; margin: 18mm 16mm; }}
  @media print {{
    body {{ max-width: none; padding: 0; font-size: 12.5pt; }}
    h2 {{ page-break-after: avoid; }}
    h3 {{ page-break-after: avoid; }}
    blockquote {{ page-break-inside: avoid; }}
    table {{ page-break-inside: auto; }}
    tr {{ page-break-inside: avoid; }}
    a {{ color: inherit; text-decoration: none; }}
  }}
</style>
</head>
<body>
{body}
</body>
</html>
"""

(ROOT / "index.html").write_text(html, encoding="utf-8")
print(f"Wrote index.html ({len(html)} bytes)")

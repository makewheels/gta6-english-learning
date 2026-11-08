#!/usr/bin/env python3
"""从 vocab.json 生成 index.html（网页版）和 README.md（GitHub 版）。
用法：改 vocab.json 后运行 `python3 generate.py`，两个文件一起更新。"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
data = json.loads((ROOT / "vocab.json").read_text(encoding="utf-8"))

AUDIO_BASE = "https://dict.youdao.com/dictvoice?type=2&audio="


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def md_inline(s: str) -> str:
    """把 **粗体** 转成 <strong>，其余转义。"""
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return s


# ---------------- 生成 README.md ----------------

def render_readme() -> str:
    out = []
    out.append(f"# {data['title']}")
    out.append("")
    out.append(f"> {data['subtitle']}")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## 使用说明")
    out.append("")
    for n in data["notes"]:
        out.append(f"- {n}")
    out.append("")
    out.append("---")
    out.append("")

    for pi, part in enumerate(data["parts"]):
        out.append(f"# {part['title']}")
        out.append("")
        part_short = re.sub(r"^第[一二三四五六七八九十]+部分\s*[·•]\s*", "", part["title"])
        for sec in part["sections"]:
            # 若 section 标题与 part 短标题相同，则不重复输出 heading
            if sec["title"] != part_short:
                head = sec["title"] + (f"（{sec['en']}）" if sec.get("en") else "")
                out.append(f"## {head}")
                out.append("")
            kind = sec.get("kind", "words")
            if kind == "words":
                for n, w in enumerate(sec["words"], 1):
                    out.append(f"**{n}. {w['word']}** {w['ipa']}（{w['pos']}）{w['meaning']}")
                    out.append(f"> {w['ex_en']}")
                    out.append(f"> {w['ex_zh']}")
                    out.append("")
            elif kind == "table":
                hdr = "| " + " | ".join(sec["headers"]) + " |"
                sep = "|" + "|".join(["---"] * len(sec["headers"])) + "|"
                out.append(hdr)
                out.append(sep)
                for row in sec["rows"]:
                    out.append("| " + " | ".join(row) + " |")
                out.append("")
                if sec.get("note"):
                    out.append(sec["note"])
                    out.append("")
            elif kind == "bullets":
                for it in sec["items"]:
                    out.append(f"- {it}")
                out.append("")
            out.append("---")
            out.append("")

    out.append(f"*{data['footer']}*")
    out.append("")
    return "\n".join(out)


# ---------------- 生成 index.html ----------------

def render_html() -> str:
    # 目录与正文
    toc_items = []   # (href, label, part_label)
    body_parts = []
    sec_counter = 0

    for pi, part in enumerate(data["parts"]):
        part_short = re.sub(r"^第[一二三四五六七八九十]+部分\s*[·•]\s*", "", part["title"])
        secs_html = []
        for sec in part["sections"]:
            sec_counter += 1
            sid = f"sec-{sec_counter}"
            head = sec["title"] + (f" <span class='en'>（{esc(sec['en'])}）</span>" if sec.get("en") else "")
            kind = sec.get("kind", "words")
            inner = ""
            if kind == "words":
                cards = []
                for w in sec["words"]:
                    spk = (f'<button class="spk" data-w="{esc(w["word"])}" title="点击发音" '
                           f'aria-label="点击发音 {esc(w["word"])}">🔊</button>')
                    cards.append(
                        f'<div class="word"><div class="head">{spk}'
                        f'<span class="wt">{esc(w["word"])}</span> '
                        f'<span class="ipa">{esc(w["ipa"])}</span> '
                        f'<span class="pos">{esc(w["pos"])}</span> '
                        f'<span class="zh">{esc(w["meaning"])}</span></div>'
                        f'<div class="ex"><span class="en">{esc(w["ex_en"])}</span><br>'
                        f'<span class="zh2">{esc(w["ex_zh"])}</span></div></div>'
                    )
                inner = "\n".join(cards)
            elif kind == "table":
                ths = "".join(f"<th>{esc(h)}</th>" for h in sec["headers"])
                trs = []
                for row in sec["rows"]:
                    tds = []
                    for ci, cell in enumerate(row):
                        # 第一列若是英文词，加发音按钮
                        if ci == 0 and re.search(r"[A-Za-z]", cell):
                            tds.append(
                                f'<td><button class="spk" data-w="{esc(cell)}" title="点击发音">🔊</button> '
                                f'{esc(cell)}</td>'
                            )
                        else:
                            tds.append(f"<td>{esc(cell)}</td>")
                    trs.append("<tr>" + "".join(tds) + "</tr>")
                inner = (f'<table><thead><tr>{ths}</tr></thead>'
                         f'<tbody>{"".join(trs)}</tbody></table>')
                if sec.get("note"):
                    inner += f'<p class="note">{md_inline(sec["note"])}</p>'
            elif kind == "bullets":
                inner = "<ul>" + "".join(f"<li>{md_inline(it)}</li>" for it in sec["items"]) + "</ul>"
            secs_html.append(f'<section class="sec" id="{sid}"><h2>{head}</h2>{inner}</section>')
            toc_items.append((sid, sec["title"], part_short))
        body_parts.append(
            f'<section class="part" id="part-{pi}">'
            f'<h1 class="part-title">{esc(part["title"])}</h1>'
            f'{"".join(secs_html)}</section>'
        )

    toc_html = "".join(
        f'<a href="#{sid}" class="toc-link"><span class="toc-part">{esc(part_label)}</span>'
        f'<span class="toc-label">{esc(label)}</span></a>'
        for sid, label, part_label in toc_items
    )

    notes_html = "".join(f"<li>{md_inline(n)}</li>" for n in data["notes"])

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(data['title'])}</title>
<style>
  :root {{
    --accent:#c8102e; --ink:#1a1a1a; --muted:#777; --line:#e8e2d9; --bg:#fff; --bg-soft:#faf6f0;
  }}
  * {{ box-sizing:border-box; }}
  html {{ -webkit-text-size-adjust:100%; scroll-behavior:smooth; }}
  body {{
    margin:0; color:var(--ink); background:var(--bg);
    font-family:-apple-system,"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Segoe UI",sans-serif;
    line-height:1.75; font-size:16px;
  }}
  /* 目录侧栏 */
  #toc {{
    position:fixed; top:0; left:0; bottom:0; width:250px; overflow-y:auto;
    background:var(--bg-soft); border-right:1px solid var(--line); padding:20px 16px;
    z-index:40; transform:translateX(-100%); transition:transform .25s ease;
  }}
  #toc.open {{ transform:translateX(0); }}
  #toc .toc-title {{ font-weight:700; font-size:17px; margin-bottom:10px; color:var(--accent); }}
  #toc a {{ display:block; text-decoration:none; color:var(--ink); padding:5px 8px; border-radius:6px; font-size:14px; }}
  #toc a:hover {{ background:#efe7db; }}
  #toc .toc-part {{ display:block; font-size:11.5px; color:var(--muted); }}
  #toc .toc-label {{ font-weight:500; }}
  #toc-toggle {{
    position:fixed; top:12px; left:12px; z-index:50; border:1px solid var(--line);
    background:var(--bg); border-radius:8px; padding:7px 12px; cursor:pointer; font-size:14px; box-shadow:0 1px 4px rgba(0,0,0,.08);
  }}
  /* 主内容 */
  main {{ padding:28px 22px 70px; max-width:860px; margin:0 auto; }}
  .doc-header h1 {{ font-size:25px; margin:0 0 4px; line-height:1.35; }}
  .doc-header .subtitle {{ color:var(--muted); margin:0 0 14px; }}
  .notes-box {{ background:var(--bg-soft); border:1px solid var(--line); border-radius:10px; padding:12px 16px; margin:14px 0 26px; font-size:14px; }}
  .notes-box ul {{ margin:0; padding-left:20px; }}
  .notes-box li {{ margin:3px 0; }}
  .part-title {{ font-size:21px; margin:38px 0 6px; padding-bottom:8px; border-bottom:3px solid var(--accent); }}
  .sec h2 {{ font-size:17px; margin:24px 0 10px; color:var(--accent); }}
  .sec h2 .en {{ font-weight:400; color:var(--muted); font-size:.85em; }}
  /* 单词卡片 */
  .word {{ padding:9px 0; border-bottom:1px dashed var(--line); }}
  .word:last-child {{ border-bottom:none; }}
  .word .head {{ font-size:16px; }}
  .word .wt {{ font-weight:700; font-size:1.08em; }}
  .word .ipa {{ color:var(--muted); font-size:.92em; margin:0 4px; }}
  .word .pos {{ color:var(--accent); font-size:.82em; margin-right:4px; }}
  .word .ex {{ margin:4px 0 0 6px; padding:4px 0 4px 12px; border-left:3px solid var(--accent); }}
  .word .ex .en {{ color:#333; }}
  .word .ex .zh2 {{ color:var(--muted); font-size:.9em; }}
  .note {{ font-size:14px; color:#444; }}
  /* 发音按钮 */
  .spk {{ background:none; border:none; cursor:pointer; font-size:15px; padding:0 3px; vertical-align:middle; }}
  .spk:hover {{ transform:scale(1.15); }}
  /* 表格 */
  table {{ border-collapse:collapse; width:100%; margin:10px 0; font-size:14.5px; }}
  th,td {{ border:1px solid var(--line); padding:7px 9px; text-align:left; vertical-align:top; }}
  th {{ background:var(--bg-soft); font-weight:600; white-space:nowrap; }}
  footer {{ margin-top:36px; color:var(--muted); font-size:13px; border-top:1px solid var(--line); padding-top:14px; }}
  /* 桌面：侧栏展开 */
  @media (min-width: 900px) {{
    #toc {{ transform:translateX(0); }}
    #toc-toggle {{ display:none; }}
    main {{ margin-left:250px; max-width:820px; padding:34px 40px 80px; }}
  }}
  /* 打印 */
  @page {{ size:A4; margin:16mm 14mm; }}
  @media print {{
    #toc, #toc-toggle {{ display:none !important; }}
    main {{ margin:0; max-width:none; padding:0; font-size:12pt; }}
    .word, .sec, table, tr {{ page-break-inside:avoid; }}
    .part-title {{ page-break-after:avoid; }}
    .spk {{ display:none; }}  /* 打印不显示发音按钮 */
  }}
</style>
</head>
<body>
<button id="toc-toggle" aria-label="目录">☰ 目录</button>
<nav id="toc" aria-label="目录">
  <div class="toc-title">目录</div>
  {toc_html}
</nav>
<main>
  <header class="doc-header">
    <h1>{esc(data['title'])}</h1>
    <p class="subtitle">{esc(data['subtitle'])}</p>
    <div class="notes-box"><strong>使用说明</strong><ul>{notes_html}</ul></div>
  </header>
  {''.join(body_parts)}
  <footer>{esc(data['footer'])}</footer>
</main>
<script>
  (function(){{
    var toc = document.getElementById('toc');
    var btn = document.getElementById('toc-toggle');
    btn.addEventListener('click', function(){{ toc.classList.toggle('open'); }});
    toc.addEventListener('click', function(e){{
      if (e.target.tagName === 'A') toc.classList.remove('open');
    }});
    // 点击发音
    document.addEventListener('click', function(e){{
      var b = e.target.closest('.spk');
      if (!b) return;
      var w = b.getAttribute('data-w');
      var a = new Audio('{AUDIO_BASE}' + encodeURIComponent(w));
      a.play().catch(function(){{ alert('发音加载失败，请检查网络'); }});
    }});
  }})();
</script>
</body>
</html>
"""


(ROOT / "index.html").write_text(render_html(), encoding="utf-8")
(ROOT / "README.md").write_text(render_readme(), encoding="utf-8")
print("已生成 index.html 和 README.md")

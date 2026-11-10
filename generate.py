#!/usr/bin/env python3
"""从 vocab.json 生成 index.html（网页版）和 README.md（项目说明与 Pages 入口）。
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


def attr(s: str) -> str:
    """用于 HTML 属性值（会转义引号）。"""
    return html.escape(s, quote=True)


def md_inline(s: str) -> str:
    """把 **粗体** 转成 <strong>，其余转义。"""
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return s


# ---------------- 生成 README.md ----------------

def render_readme() -> str:
    return f"""# {data['title']}

给想用英文玩 GTA6 的中文玩家准备的游戏英语学习资料，按游戏场景整理词汇、界面提示和专有名词，提供中英释义、美式音标及双语例句。

**在线学习：** https://makewheels.github.io/gta6-english-learning/

## 使用说明

- 按目录选择界面、操作、任务、战斗、载具等主题；建议先学 HUD、操作按键和任务目标。
- 点击音标旁的发音按钮听美式发音（需联网），点击 ☆ 将单词加入生词篮，支持定位与复制清单。
- 生词收藏保存在当前浏览器本地；支持手机、电脑阅读，以及浏览器 A4 打印。

例句为自编教学内容，不是官方游戏台词；专有名词音标为参考。

## 内容维护

词汇数据在 `vocab.json`。修改后在仓库目录运行 `python generate.py`，同步生成 `index.html` 和本 README；完整教材只放在网页中。
"""


# ---------------- 生成 index.html ----------------

CSS_TEXT = """<style>
  :root {
    --accent:#c8102e; --ink:#1a1a1a; --muted:#777; --line:#e8e2d9; --bg:#fff; --bg-soft:#faf6f0;
  }
  * { box-sizing:border-box; }
  html { -webkit-text-size-adjust:100%; scroll-behavior:smooth; }
  body {
    margin:0; color:var(--ink); background:var(--bg);
    font-family:-apple-system,"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Segoe UI",sans-serif;
    line-height:1.75; font-size:16px;
  }
  /* 目录侧栏 */
  #toc {
    position:fixed; top:0; left:0; bottom:0; width:250px; overflow-y:auto;
    background:var(--bg-soft); border-right:1px solid var(--line); padding:20px 16px;
    z-index:40; transform:translateX(-100%); transition:transform .25s ease;
  }
  #toc.open { transform:translateX(0); }
  #toc .toc-title { font-weight:700; font-size:17px; margin-bottom:10px; color:var(--accent); }
  #toc a { display:block; text-decoration:none; color:var(--ink); padding:6px 8px; border-radius:6px; font-size:14.5px; font-weight:500; line-height:1.35; }
  #toc a:hover { background:#efe7db; }
  #toc-toggle {
    position:fixed; top:12px; left:12px; z-index:50; border:1px solid var(--line);
    background:var(--bg); border-radius:8px; padding:7px 12px; cursor:pointer; font-size:14px; box-shadow:0 1px 4px rgba(0,0,0,.08);
  }
  /* 主内容 */
  main { padding:28px 22px 70px; max-width:860px; margin:0 auto; }
  .doc-header h1 { font-size:25px; margin:0 0 4px; line-height:1.35; }
  .doc-header .subtitle { color:var(--muted); margin:0 0 14px; }
  .notes-box { background:var(--bg-soft); border:1px solid var(--line); border-radius:10px; padding:12px 16px; margin:14px 0 26px; font-size:14px; }
  .notes-box ul { margin:0; padding-left:20px; }
  .notes-box li { margin:3px 0; }
  .part-title { font-size:21px; margin:38px 0 6px; padding-bottom:8px; border-bottom:3px solid var(--accent); }
  .sec h2 { font-size:17px; margin:24px 0 10px; color:var(--accent); }
  .sec h2 .en { font-weight:400; color:var(--muted); font-size:.85em; }
  /* 核心词汇表格：英文例句 | 中文翻译 | 单词 | 音标(带发音) | 词性 | 释义 | 标记 */
  .table-wrap { overflow-x:auto; -webkit-overflow-scrolling:touch; }
  table { border-collapse:collapse; width:100%; margin:10px 0; font-size:14.5px; }
  th,td { border:1px solid var(--line); padding:7px 9px; text-align:left; vertical-align:top; }
  th { background:var(--bg-soft); font-weight:600; white-space:nowrap; }
  table.vocab { table-layout:fixed; min-width:900px; font-size:16px; }
  table.vocab th, table.vocab td { padding:9px 10px; }
  table.vocab th { font-size:13.5px; color:var(--muted); white-space:normal; }
  table.vocab th.c-en   { width:28%; }
  table.vocab th.c-zh2  { width:17%; }
  table.vocab th.c-word { width:15%; }
  table.vocab th.c-ipa  { width:13%; }
  table.vocab th.c-pos  { width:5%; }
  table.vocab th.c-zh   { width:17%; }
  table.vocab th.c-mark { width:5%; text-align:center; }
  table.vocab tbody tr:nth-child(even) { background:#fdfbf7; }
  table.vocab tbody tr:hover { background:#f7efe3; }
  /* 单词列放大 */
  table.vocab .wt { font-size:20px; font-weight:700; line-height:1.35; }
  table.vocab .c-word { white-space:normal; }
  table.vocab .c-ipa { color:#666; font-size:14px; overflow-wrap:anywhere; }
  table.vocab .c-ipa .spk { margin-right:4px; }
  table.vocab .c-pos { color:var(--accent); font-size:14px; }
  table.vocab .c-zh { color:var(--ink); }
  /* 英文例句：黑色（不要灰色） */
  table.vocab .c-en { color:#000; font-size:16.5px; line-height:1.55; }
  table.vocab .c-zh2 { color:#5c5c5c; font-size:14.5px; line-height:1.55; }
  /* 发音按钮 */
  .spk { background:none; border:none; cursor:pointer; font-size:15px; padding:0 3px; vertical-align:middle; }
  .spk:hover { transform:scale(1.15); }
  /* 标记（收藏到生词篮） */
  .mark { background:none; border:none; cursor:pointer; font-size:19px; line-height:1; color:#c8b69a; padding:3px 5px; border-radius:6px; vertical-align:middle; }
  .mark:hover { color:var(--accent); background:#f4e9d8; }
  .mark.on { color:#e0a400; }
  table.vocab th.c-mark, table.vocab td.c-mark { text-align:center; }
  table.vocab tbody tr.marked td { background:#fff6df; }
  table.vocab tbody tr.marked .wt { color:var(--accent); }
  /* 生词篮：右下角按钮 + 右侧抽屉 */
  #cart-toggle {
    position:fixed; right:18px; bottom:20px; z-index:60; display:flex; align-items:center; gap:8px;
    border:none; border-radius:999px; background:var(--accent); color:#fff; padding:12px 18px;
    font-size:15px; font-family:inherit; cursor:pointer; box-shadow:0 6px 22px rgba(200,16,46,.35);
  }
  #cart-toggle:hover { filter:brightness(1.06); }
  #cart-toggle .badge { background:#fff; color:var(--accent); border-radius:999px; min-width:22px; height:22px; padding:0 6px; display:inline-flex; align-items:center; justify-content:center; font-size:12.5px; font-weight:700; }
  #cart-mask { position:fixed; inset:0; background:rgba(0,0,0,.28); z-index:65; opacity:0; pointer-events:none; transition:opacity .2s ease; }
  #cart-mask.show { opacity:1; pointer-events:auto; }
  #cart {
    position:fixed; top:0; right:0; bottom:0; width:350px; max-width:88vw; z-index:70;
    background:#fff; border-left:1px solid var(--line); box-shadow:-14px 0 34px rgba(0,0,0,.14);
    display:flex; flex-direction:column; transform:translateX(102%); transition:transform .25s ease;
  }
  #cart.open { transform:translateX(0); }
  #cart .cart-head { display:flex; align-items:flex-start; justify-content:space-between; padding:16px 16px 10px; border-bottom:1px solid var(--line); }
  #cart .cart-head strong { font-size:17px; color:var(--accent); }
  #cart #cart-sub { display:block; color:var(--muted); font-size:12.5px; }
  #cart #cart-close { border:none; background:none; font-size:22px; line-height:1; cursor:pointer; color:var(--muted); padding:0 4px; }
  #cart-empty { margin:0; padding:26px 18px; color:var(--muted); font-size:13.5px; text-align:center; line-height:1.7; }
  #cart-list { flex:1; overflow-y:auto; margin:0; padding:4px 14px; list-style:none; }
  #cart-list li { display:flex; align-items:baseline; gap:7px; padding:10px 2px; border-bottom:1px dashed var(--line); font-size:14px; }
  #cart-list .ci-word { font-size:16px; font-weight:700; background:none; border:none; padding:0; cursor:pointer; color:var(--ink); font-family:inherit; text-align:left; }
  #cart-list .ci-word:hover { color:var(--accent); }
  #cart-list .ci-ipa { color:#777; font-size:12.5px; }
  #cart-list .ci-zh { color:#555; }
  #cart-list .ci-del { margin-left:auto; border:none; background:none; color:#aaa; cursor:pointer; font-size:17px; line-height:1; padding:0 4px; }
  #cart-list .ci-del:hover { color:var(--accent); }
  #cart .cart-actions { display:flex; gap:8px; padding:12px 14px 16px; border-top:1px solid var(--line); }
  #cart .cart-actions button { flex:1; padding:9px 6px; border-radius:8px; border:1px solid var(--line); background:var(--bg-soft); font-size:14px; font-family:inherit; cursor:pointer; }
  #cart .cart-actions button:hover { background:#f0e6d7; }
  #cart #cart-clear { color:var(--accent); }
  .flash { animation:flash .9s ease; }
  @keyframes flash { 0%,100% { background:transparent; } 30% { background:#ffe9a8; } }
  .note { font-size:14px; color:#444; }
  footer { margin-top:36px; color:var(--muted); font-size:13px; border-top:1px solid var(--line); padding-top:14px; }
  /* 桌面：侧栏展开 */
  @media (min-width: 900px) {
    #toc { transform:translateX(0); }
    #toc-toggle { display:none; }
    main { margin-left:250px; max-width:1240px; padding:34px 40px 80px; }
  }
  /* 打印 */
  @page { size:A4; margin:16mm 14mm; }
  @media print {
    #toc, #toc-toggle, #cart, #cart-toggle, #cart-mask { display:none !important; }
    main { margin:0; max-width:none; padding:0; font-size:12pt; }
    .sec, tr { page-break-inside:avoid; }
    table.vocab { min-width:0; font-size:9.5pt; }
    table.vocab th, table.vocab td { padding:3px 5px; }
    table.vocab thead { display:table-header-group; }
    table.vocab .wt { font-size:11pt; }
    .part-title { page-break-after:avoid; }
    .spk, .mark { display:none; }
    table.vocab th.c-mark, table.vocab td.c-mark { display:none; }
  }
</style>"""


JS_TEXT = """<script>
(function(){
  var AUDIO_BASE = "https://dict.youdao.com/dictvoice?type=2&audio=";

  // 目录
  var toc = document.getElementById('toc');
  var tocBtn = document.getElementById('toc-toggle');
  tocBtn.addEventListener('click', function(){ toc.classList.toggle('open'); });
  toc.addEventListener('click', function(e){ if (e.target.tagName === 'A') toc.classList.remove('open'); });

  // 点击发音
  document.addEventListener('click', function(e){
    var b = e.target.closest('.spk');
    if (!b) return;
    var a = new Audio(AUDIO_BASE + encodeURIComponent(b.getAttribute('data-w')));
    a.play().catch(function(){ alert('发音加载失败，请检查网络'); });
  });

  // ---- 生词篮：点 ☆ 把单词收进来，记录只存在本机浏览器（localStorage）----
  var KEY = 'gta6-basket-v1';
  var basket = [];
  try { basket = JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (err) { basket = []; }
  if (!Array.isArray(basket)) basket = [];

  var cart = document.getElementById('cart');
  var mask = document.getElementById('cart-mask');
  var list = document.getElementById('cart-list');
  var empty = document.getElementById('cart-empty');
  var badge = document.getElementById('cart-count');
  var sub = document.getElementById('cart-sub');
  var cartBtn = document.getElementById('cart-toggle');
  var markBtns = Array.prototype.slice.call(document.querySelectorAll('button.mark'));

  function save(){ try { localStorage.setItem(KEY, JSON.stringify(basket)); } catch (err) {} }
  function find(w){ for (var i = 0; i < basket.length; i++) { if (basket[i].w === w) return i; } return -1; }
  function rowOf(w){
    for (var i = 0; i < markBtns.length; i++) {
      if (markBtns[i].getAttribute('data-w') === w) return markBtns[i].closest('tr');
    }
    return null;
  }
  function itemFrom(btn){
    var tr = btn.closest('tr');
    function txt(sel){ var el = tr.querySelector(sel); return el ? el.textContent.trim() : ''; }
    return { w: tr.getAttribute('data-w'), ipa: txt('.ipa-text'), pos: txt('.c-pos'), zh: txt('.c-zh'), en: txt('.c-en') };
  }
  function renderMarks(){
    markBtns.forEach(function(b){
      var on = find(b.getAttribute('data-w')) >= 0;
      b.classList.toggle('on', on);
      b.textContent = on ? '★' : '☆';
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      var tr = b.closest('tr');
      if (tr) tr.classList.toggle('marked', on);
    });
  }
  function renderList(){
    while (list.firstChild) list.removeChild(list.firstChild);
    basket.forEach(function(it){
      var li = document.createElement('li');
      var tw = document.createElement('button');
      tw.className = 'ci-word'; tw.textContent = it.w; tw.title = '定位到这个单词';
      tw.addEventListener('click', function(){
        var tr = rowOf(it.w);
        if (tr) {
          tr.scrollIntoView({ behavior:'smooth', block:'center' });
          tr.classList.remove('flash'); void tr.offsetWidth; tr.classList.add('flash');
        }
        closeCart();
      });
      var ipa = document.createElement('span'); ipa.className = 'ci-ipa'; ipa.textContent = it.ipa || '';
      var zh = document.createElement('span'); zh.className = 'ci-zh'; zh.textContent = it.zh || '';
      var del = document.createElement('button'); del.className = 'ci-del'; del.textContent = '×'; del.title = '移出生词篮';
      del.addEventListener('click', function(){ removeItem(it.w); });
      li.appendChild(tw); li.appendChild(ipa); li.appendChild(zh); li.appendChild(del);
      list.appendChild(li);
    });
    empty.style.display = basket.length ? 'none' : 'block';
    badge.textContent = basket.length;
    sub.textContent = basket.length ? basket.length + ' 个词 · 只存在本机浏览器' : '还没有收藏单词';
  }
  function render(){ renderMarks(); renderList(); }
  function addItem(btn){ var it = itemFrom(btn); if (find(it.w) >= 0) return; basket.push(it); save(); render(); }
  function removeItem(w){ var i = find(w); if (i >= 0) { basket.splice(i, 1); save(); render(); } }

  markBtns.forEach(function(b){
    b.addEventListener('click', function(){
      if (find(b.getAttribute('data-w')) >= 0) removeItem(b.getAttribute('data-w')); else addItem(b);
    });
  });

  function openCart(){ cart.classList.add('open'); mask.classList.add('show'); cartBtn.setAttribute('aria-expanded', 'true'); }
  function closeCart(){ cart.classList.remove('open'); mask.classList.remove('show'); cartBtn.setAttribute('aria-expanded', 'false'); }
  cartBtn.addEventListener('click', function(){ if (cart.classList.contains('open')) closeCart(); else openCart(); });
  document.getElementById('cart-close').addEventListener('click', closeCart);
  mask.addEventListener('click', closeCart);
  document.addEventListener('keydown', function(e){ if (e.key === 'Escape') closeCart(); });

  // 复制清单（方便贴到笔记 / Anki）
  document.getElementById('cart-copy').addEventListener('click', function(){
    if (!basket.length) { alert('生词篮还是空的，先点表格右侧的 ☆ 收藏几个词。'); return; }
    var lines = ['GTA6 英文速成教材 · 我的生词本（' + basket.length + ' 个）', ''];
    basket.forEach(function(it, i){
      lines.push((i + 1) + '. ' + it.w + (it.ipa ? ' ' + it.ipa : '') + (it.pos ? ' ' + it.pos : '') + (it.zh ? ' ' + it.zh : ''));
      if (it.en) lines.push('   ' + it.en);
    });
    var text = lines.join('\\n');
    function fallback(){
      var ta = document.createElement('textarea');
      ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); alert('已复制到剪贴板'); } catch (err) { alert('复制失败，请手动选择复制'); }
      document.body.removeChild(ta);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function(){ alert('已复制到剪贴板'); }, fallback);
    } else { fallback(); }
  });

  document.getElementById('cart-clear').addEventListener('click', function(){
    if (!basket.length) return;
    if (!confirm('清空生词篮里的 ' + basket.length + ' 个词？')) return;
    basket = []; save(); render();
  });

  render();
})();
</script>"""


def render_html() -> str:
    # 目录与正文
    toc_items = []   # (href, label)
    body_parts = []
    sec_counter = 0

    for pi, part in enumerate(data["parts"]):
        secs_html = []
        for sec in part["sections"]:
            sec_counter += 1
            sid = f"sec-{sec_counter}"
            head = sec["title"] + (f" <span class='en'>（{esc(sec['en'])}）</span>" if sec.get("en") else "")
            kind = sec.get("kind", "words")
            inner = ""
            if kind == "words":
                # 核心词汇表格：单词 | 音标(发音按钮+音标) | 英文例句 | 中文翻译 | 词性 | 释义 | 标记
                trs = []
                for w in sec["words"]:
                    spk = (f'<button class="spk" data-w="{attr(w["word"])}" title="点击发音" '
                           f'aria-label="点击发音 {attr(w["word"])}">🔊</button>')
                    trs.append(
                        f'<tr data-w="{attr(w["word"])}">'
                        f'<td class="c-en">{esc(w["ex_en"])}</td>'
                        f'<td class="c-zh2">{esc(w["ex_zh"])}</td>'
                        f'<td class="c-word"><span class="wt">{esc(w["word"])}</span></td>'
                        f'<td class="c-ipa">{spk}<span class="ipa-text">{esc(w["ipa"])}</span></td>'
                        f'<td class="c-pos">{esc(w["pos"])}</td>'
                        f'<td class="c-zh">{esc(w["meaning"])}</td>'
                        f'<td class="c-mark"><button class="mark" data-w="{attr(w["word"])}" '
                        f'title="标记该词（加入生词篮）" aria-label="标记 {attr(w["word"])}" aria-pressed="false">☆</button></td>'
                        f'</tr>'
                    )
                inner = (
                    '<div class="table-wrap"><table class="vocab">'
                    '<thead><tr><th class="c-en">英文例句</th><th class="c-zh2">中文翻译</th>'
                    '<th class="c-word">单词</th><th class="c-ipa">音标 / 发音</th>'
                    '<th class="c-pos">词性</th><th class="c-zh">释义</th>'
                    '<th class="c-mark">标记</th></tr></thead>'
                    f'<tbody>{"".join(trs)}</tbody></table></div>'
                )
            elif kind == "table":
                ths = "".join(f"<th>{esc(h)}</th>" for h in sec["headers"])
                trs = []
                for row in sec["rows"]:
                    tds = []
                    for ci, cell in enumerate(row):
                        # 第一列若是英文词，加发音按钮
                        if ci == 0 and re.search(r"[A-Za-z]", cell):
                            tds.append(
                                f'<td><button class="spk" data-w="{attr(cell)}" title="点击发音">🔊</button> '
                                f'{esc(cell)}</td>'
                            )
                        else:
                            tds.append(f"<td>{esc(cell)}</td>")
                    trs.append("<tr>" + "".join(tds) + "</tr>")
                inner = (f'<div class="table-wrap"><table><thead><tr>{ths}</tr></thead>'
                         f'<tbody>{"".join(trs)}</tbody></table></div>')
                if sec.get("note"):
                    inner += f'<p class="note">{md_inline(sec["note"])}</p>'
            elif kind == "bullets":
                inner = "<ul>" + "".join(f"<li>{md_inline(it)}</li>" for it in sec["items"]) + "</ul>"
            secs_html.append(f'<section class="sec" id="{sid}"><h2>{head}</h2>{inner}</section>')
            toc_items.append((sid, sec["title"]))
        body_parts.append(
            f'<section class="part" id="part-{pi}">'
            f'<h1 class="part-title">{esc(part["title"])}</h1>'
            f'{"".join(secs_html)}</section>'
        )

    # 左侧目录只保留小节标题（不再显示所属部分的小字标签）
    toc_html = "".join(
        f'<a href="#{sid}" class="toc-link">{esc(label)}</a>'
        for sid, label in toc_items
    )

    notes_html = "".join(f"<li>{md_inline(n)}</li>" for n in data["notes"])

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(data['title'])}</title>
{CSS_TEXT}
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
<button id="cart-toggle" aria-label="打开生词篮" aria-expanded="false">🛒 生词篮<span class="badge" id="cart-count">0</span></button>
<div id="cart-mask"></div>
<aside id="cart" aria-label="生词篮" aria-hidden="true">
  <div class="cart-head">
    <div><strong>生词篮</strong><span id="cart-sub">还没有收藏单词</span></div>
    <button id="cart-close" aria-label="关闭">×</button>
  </div>
  <p id="cart-empty">点词表右侧的 ☆，把要背的词收进来。<br>记录只保存在本机浏览器里。</p>
  <ul id="cart-list"></ul>
  <div class="cart-actions">
    <button id="cart-copy">复制清单</button>
    <button id="cart-clear">清空</button>
  </div>
</aside>
{JS_TEXT}
</body>
</html>
"""


(ROOT / "index.html").write_text(render_html(), encoding="utf-8")
(ROOT / "README.md").write_text(render_readme(), encoding="utf-8")
print("已生成 index.html 和 README.md")

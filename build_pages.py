"""產生 Cue Sheet 網站的首頁（index.html）與電子報列表頁（newsletter/index.html）。

資料：newsletter/issues.json（月刊與特刊同列）。
用法：python build_pages.py
"""
import json
from html import escape

SITE = "https://mesple.github.io/cuesheet/"

CSS = """
:root{
  --bg:#F2F0EA; --paper:#FBFAF6; --ink:#28251D; --muted:#7A7974; --soft:#55534C;
  --line:#D4D1CA; --teal:#01696F; --teal-bg:#EEF4F3;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#1B1A16; --paper:#24221D; --ink:#EDEBE4; --muted:#A3A19A; --soft:#C9C6BE;
    --line:#3B3932; --teal:#4FB3B8; --teal-bg:#1E3233;
  }
}
:root[data-theme="dark"]{
  --bg:#1B1A16; --paper:#24221D; --ink:#EDEBE4; --muted:#A3A19A; --soft:#C9C6BE;
  --line:#3B3932; --teal:#4FB3B8; --teal-bg:#1E3233;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:"Noto Sans TC",-apple-system,BlinkMacSystemFont,"PingFang TC","Microsoft JhengHei",sans-serif;line-height:1.6}
a{color:var(--teal)}
.wrap{max-width:820px;margin:0 auto;padding:0 16px}
header.mast{background:var(--paper);border-bottom:5px solid var(--ink)}
header.mast .wrap{padding-top:18px;padding-bottom:16px}
.topnav{display:flex;gap:16px;font-size:13px;margin:0 0 14px}
.topnav a{color:var(--soft);text-decoration:none}
.topnav a[aria-current="page"]{color:var(--ink);font-weight:700}
.topnav a:hover{color:var(--teal)}
.kicker{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}
.title{font-family:Georgia,"Noto Serif TC",serif;font-size:56px;font-weight:700;letter-spacing:-.04em;line-height:.95;margin:8px 0 0}
.title a{color:inherit;text-decoration:none}
.sub{font-size:15px;color:var(--soft);margin:12px 0 0;max-width:40em}
main .wrap{padding-top:8px;padding-bottom:40px}
.sec{font-size:13px;font-weight:700;letter-spacing:.08em;margin:30px 0 12px;padding-top:8px;border-top:1px solid var(--ink)}
.sec span{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-left:8px}
.latest{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.1fr);gap:20px;background:var(--paper);border:1px solid var(--line);padding:18px}
.latest img{width:100%;height:auto;display:block;border:1px solid var(--line)}
.label{font-size:12px;letter-spacing:.08em;color:var(--muted)}
.tag{display:inline-block;border:1px solid var(--teal);color:var(--teal);font-size:11px;padding:0 6px;margin-left:6px;line-height:1.6;vertical-align:1px}
.issue-title{font-family:Georgia,"Noto Serif TC",serif;font-size:22px;font-weight:700;line-height:1.35;margin:4px 0 8px}
.issue-title a{color:var(--ink);text-decoration:none}
.issue-title a:hover{color:var(--teal)}
.note{font-size:15px;line-height:1.75;color:var(--soft);margin:0 0 10px}
.more{font-size:14px;font-weight:700;text-decoration:none}
.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.card{display:block;background:var(--paper);border:1px solid var(--line);padding:16px;text-decoration:none;color:var(--ink)}
.card:hover{border-color:var(--teal)}
.card b{display:block;font-size:17px;margin-bottom:4px}
.card small{display:block;font-size:13px;color:var(--soft)}
.list .row{padding:16px 0;border-top:1px dotted var(--line)}
.list .row:first-child{border-top:none}
footer{border-top:3px double var(--ink);margin-top:10px;padding:12px 0 30px;font-size:12px;color:var(--muted)}
@media (max-width:600px){
  .title{font-size:40px}
  .latest{grid-template-columns:1fr;padding:14px}
  .cards{grid-template-columns:1fr}
}
"""


NAV = [("home", "首頁", ""), ("newsletter", "電子報", "newsletter/"), ("category", "分類", "category/"), ("composer", "作曲家", "composer/"), ("event", "活動", "event/")]


def page(title, desc, url, nav, body, image=None, depth=None, kicker="Monthly film music newsletter"):
    """depth：頁面在網站根目錄下第幾層（首頁 0、newsletter/ 1、item/<id>/ 2）。"""
    if depth is None:
        depth = {"home": 0}.get(nav, 1)
    prefix = "../" * depth or "./"
    navhtml = "".join(
        f'<a href="{prefix if not path else ("../" * depth) + path}"' + (' aria-current="page"' if k == nav else "") + f'>{n}</a>'
        for k, n, path in NAV)
    og_img = f'<meta property="og:image" content="{SITE}{image}">\n' if image else ""
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:url" content="{url}">
{og_img}<meta property="og:locale" content="zh_TW">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&family=Noto+Serif+TC:wght@700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<header class="mast"><div class="wrap">
  <nav class="topnav" aria-label="網站">{navhtml}</nav>
  <div class="kicker">{escape(kicker)}</div>
  <h1 class="title"><a href="{prefix}">Cue Sheet</a></h1>
  {body[0]}
</div></header>
<main><div class="wrap">
{body[1]}
</div></main>
<footer><div class="wrap">Cue Sheet 為非營利樂迷刊物，文字為編輯摘要與評論，圖片版權屬原權利人，連結皆指向原始來源。</div></footer>
</body>
</html>
"""


def issue_meta(it):
    tag = '<span class="tag">特刊</span>' if it.get("special") else ""
    return f'<div class="label">{escape(it["label"])}{tag}</div>'


def main():
    data = json.load(open("newsletter/issues.json", encoding="utf-8"))
    issues = sorted(data["issues"], key=lambda x: x["date"], reverse=True)
    latest = issues[0]

    # 首頁
    img = f'<a href="newsletter/{latest["slug"]}/"><img src="{latest["image"]}" alt="{escape(latest["label"])}封面"></a>' if latest.get("image") else ""
    home_main = f"""<div class="sec">最新一期<span>Latest Issue</span></div>
<div class="latest">
  <div>{img}</div>
  <div>
    {issue_meta(latest)}
    <div class="issue-title"><a href="newsletter/{latest['slug']}/">{escape(latest['title'])}</a></div>
    <p class="note">{escape(latest['editor_note'])}</p>
    <a class="more" href="newsletter/{latest['slug']}/">閱讀本期 →</a>
  </div>
</div>
<div class="sec">逛逛<span>Explore</span></div>
<div class="cards">
  <a class="card" href="newsletter/"><b>電子報</b><small>每月一期，加上不定期特刊，全部在這裡。</small></a>
  <a class="card" href="category/"><b>分類瀏覽</b><small>新聞、樂評、新唱片、訪談、試聽、訃聞與社群話題，依類型找。</small></a>
  <a class="card" href="composer/"><b>作曲家</b><small>點一位作曲家，看 Cue Sheet 刊過的所有相關內容。</small></a>
  <a class="card" href="event/"><b>近期國內電影音樂活動</b><small>全台電影、動畫與遊戲音樂的音樂會與講座，選地區、加入行事曆。</small></a>
</div>"""
    home_sub = '<p class="sub">給電影配樂樂迷的中文電子報。新聞、樂評、新唱片與作曲家訪談，加上全台的電影音樂活動。</p>'
    open("index.html", "w", encoding="utf-8").write(page(
        "Cue Sheet｜中文電影配樂電子報", latest["editor_note"], SITE, "home",
        (home_sub, home_main), latest.get("image")))

    # 電子報列表
    rows = []
    for it in issues:
        rows.append(f"""<div class="row">
  {issue_meta(it)}
  <div class="issue-title"><a href="{it['slug']}/">{escape(it['title'])}</a></div>
  <p class="note">{escape(it['editor_note'])}</p>
  <a class="more" href="{it['slug']}/">閱讀 →</a>
</div>""")
    list_main = f'<div class="sec">各期電子報<span>All Issues</span></div>\n<div class="list">\n' + "\n".join(rows) + "\n</div>"
    list_sub = '<p class="sub">月刊與特刊，依時間由新到舊。</p>'
    open("newsletter/index.html", "w", encoding="utf-8").write(page(
        "電子報｜Cue Sheet", "Cue Sheet 各期電子報，月刊與特刊。", SITE + "newsletter/", "newsletter",
        (list_sub, list_main), latest.get("image")))
    print(f"首頁與電子報列表已產生，共 {len(issues)} 期")
    build_latest(issues)


def redirect_page(target, label):
    return f"""<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cue Sheet｜最新一期{escape(label)}</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{SITE}newsletter/{target}/">
<meta http-equiv="refresh" content="0; url=../{target}/">
<script>location.replace("../{target}/" + location.hash);</script>
<style>body{{font-family:-apple-system,"PingFang TC","Microsoft JhengHei",sans-serif;background:#F2F0EA;color:#28251D;padding:40px 16px;text-align:center}}a{{color:#01696F}}</style>
</head><body><p>正在前往最新一期{escape(label)}……</p><p><a href="../{target}/">沒有自動跳轉請點這裡</a></p></body></html>
"""


def build_latest(issues):
    """固定網址：/newsletter/latest-collector/、/newsletter/latest-news/ 指向各版最新一期（歡迎信用）。"""
    import os
    for key, label in (("collector", "深度聆聽版"), ("news", "配樂新訊版")):
        cands = [it for it in issues if it.get("edition") in (key, "trial")]
        if not cands:
            continue
        target = max(cands, key=lambda x: x["date"])["slug"]
        os.makedirs(f"newsletter/latest-{key}", exist_ok=True)
        open(f"newsletter/latest-{key}/index.html", "w", encoding="utf-8").write(redirect_page(target, label))
        print(f"latest-{key} → {target}")


if __name__ == "__main__":
    main()

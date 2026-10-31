"""產生 Cue Sheet 網站的電子報列表頁（newsletter/index.html），並呼叫 build_items.build_home() 產生首頁。
共用的版型（刊頭、導覽、CSS）也在這裡：page()。

資料：newsletter/issues.json（月刊與特刊同列）。
用法：python build_pages.py
"""
import json
from html import escape

SITE = "https://mesple.github.io/cuesheet/"

# 訂閱表單網址（MailerLite）。留空時刊頭只顯示標語、不顯示「訂閱」連結。
SUBSCRIBE_URL = "https://preview.mailerlite.io/forms/2740876/202321965174752394/share"
TAGLINE = "一份給配樂迷的電影音樂刊物"

# MailerLite 通用程式碼（編輯 2026-11-01 提供）：首頁彈出訂閱視窗、右上角「訂閱」點擊跳出表單都靠它。
# 彈出視窗的顯示頁面、頻率在 MailerLite 後台設定，不在這裡。
ML_FORM_ID = "HeZ91R"  # 「訂閱」連結點擊後跳出的表單
ML_SNIPPET = """<!-- MailerLite Universal -->
<script>
    (function(w,d,e,u,f,l,n){w[f]=w[f]||function(){(w[f].q=w[f].q||[])
    .push(arguments);},l=d.createElement(e),l.async=1,l.src=u,
    n=d.getElementsByTagName(e)[0],n.parentNode.insertBefore(l,n);})
    (window,document,'script','https://assets.mailerlite.com/js/universal.js','ml');
    ml('account', '2740876');
</script>
<!-- End MailerLite Universal -->
<script>
// 點「訂閱」：先叫 MailerLite 跳出表單；1 秒內沒出現（同一頁關過一次後 MailerLite 不再重開、或腳本被擋）就改開訂閱頁
function cueSubscribe(a){try{ml('show','""" + ML_FORM_ID + """',true);}catch(e){}
setTimeout(function(){var ok=[].some.call(document.querySelectorAll('iframe[src*="mailerlite"]'),function(f){return f.style.display!=='none'&&f.offsetHeight>0;});
if(!ok)window.open(a.href,'_blank','noopener');},1000);return false;}
</script>"""

CSS = """
:root{
  --bg:#F4F1E8; --paper:#FBFAF6; --ink:#1F1D18; --muted:#625E55; --soft:#4B4840;
  --line:#CFC9BA; --teal:#01696F; --teal-bg:#E6EEEC;
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
.serif{font-family:"Noto Serif TC",Georgia,serif}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}
.narrow{max-width:780px;margin:0 auto}
header.mast .strip{display:flex;flex-wrap:wrap;justify-content:space-between;gap:4px 12px;font-size:12px;color:var(--muted);padding:10px 0;border-bottom:1px solid var(--ink)}
header.mast .strip a{color:var(--teal);font-weight:700;text-decoration:none}
header.mast .brand{text-align:center;padding:18px 0 10px}
.title{font-family:"Noto Serif TC",Georgia,serif;font-size:84px;line-height:1;margin:0;letter-spacing:-.03em;font-weight:900}
.title a{color:inherit;text-decoration:none}
.kicker{margin:8px 0 0;font-size:13px;letter-spacing:.2em;color:var(--muted)}
.topnav{display:flex;flex-wrap:wrap;justify-content:center;gap:8px 26px;border-top:3px double var(--ink);border-bottom:1px solid var(--ink);padding:10px 0;font-size:15px;font-weight:700}
.topnav a{color:var(--ink);text-decoration:none;display:flex;flex-direction:column;align-items:center;line-height:1.35}
.topnav a small{font-size:10px;font-weight:700;letter-spacing:.14em;color:var(--muted);margin-top:1px}
.topnav a:hover small,.topnav a[aria-current="page"] small{color:var(--teal)}
.topnav a:hover{color:var(--teal)}
.topnav a[aria-current="page"]{color:var(--teal)}
.intro{font-size:15px;color:var(--soft);margin:22px 0 0}
main .wrap{padding-top:4px;padding-bottom:40px}
.toppad{height:22px}
.sec{font-size:13px;font-weight:700;letter-spacing:.14em;margin:30px 0 12px;padding-bottom:6px;border-bottom:2px solid var(--ink)}
.sec span{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-left:8px;font-weight:700}
.sec .more-r{float:right;font-size:12px;letter-spacing:.04em;text-transform:none;color:var(--teal);text-decoration:none;margin:0}
.band{margin-top:34px;border-top:3px double var(--ink);padding-top:14px}
.band > .sec:first-child{margin-top:0}
.label{font-size:12px;letter-spacing:.08em;color:var(--muted)}
.tag{display:inline-block;border:1px solid var(--teal);color:var(--teal);font-size:11px;padding:0 6px;margin-left:6px;line-height:1.6;vertical-align:1px}
.issue-title{font-family:"Noto Serif TC",Georgia,serif;font-size:22px;font-weight:700;line-height:1.35;margin:4px 0 8px}
.issue-title a{color:var(--ink);text-decoration:none}
.issue-title a:hover{color:var(--teal)}
.note{font-size:15px;line-height:1.75;color:var(--soft);margin:0 0 10px}
.more{font-size:14px;font-weight:700;text-decoration:none}
.list .row{padding:18px 0;border-top:1px solid var(--line)}
.list .row:first-child{border-top:none}
footer{border-top:3px double var(--ink);margin-top:16px;padding:14px 0 34px;font-size:12px;color:var(--muted);text-align:center}
footer b{font-family:"Noto Serif TC",Georgia,serif;color:var(--ink);font-size:14px}
@media (max-width:760px){
  .title{font-size:52px}
  .topnav{justify-content:flex-start;gap:8px 16px;font-size:14px}
  .topnav a{align-items:flex-start}
  .topnav a small{font-size:9px;letter-spacing:.1em}
}
"""


NAV = [("home", "首頁", "HOME", ""), ("news", "新聞", "NEWS", "category/news/"), ("reviews", "樂評", "REVIEWS", "category/reviews/"),
       ("releases", "唱片架/試聽", "NEW RELEASES", "category/releases/"), ("interviews", "訪談", "INTERVIEWS", "category/interviews/"),
       ("community", "社群雷達", "COMMUNITY RADAR", "category/community/"), ("composer", "作曲家", "COMPOSERS", "composer/"),
       ("event", "國內活動", "EVENTS", "event/"), ("newsletter", "電子報", "NEWSLETTER", "newsletter/")]  # 首頁放最左（編輯 2026-10-31 指定）；電子報放最右（編輯 2026-10-30 指定）；「全部分類」已拿掉

DATE_JS = """<script>(function(){try{var d=new Date(Date.now()+8*3600e3),w="日一二三四五六";
document.getElementById("today").textContent=d.getUTCFullYear()+" 年 "+(d.getUTCMonth()+1)+" 月 "+d.getUTCDate()+" 日 星期"+w[d.getUTCDay()];}catch(e){}})();</script>"""


def masthead(prefix, nav):
    up = prefix if prefix != "./" else ""
    navhtml = "".join(
        f'<a href="{up}{path}"' + (' aria-current="page"' if k == nav else "") + f'>{n}<small>{en}</small></a>' for k, n, en, path in NAV)
    # 點擊時跳出 MailerLite 表單；腳本沒載入時照原連結開分享頁
    sub = (f' · <a href="{SUBSCRIBE_URL}" onclick="return cueSubscribe(this)">訂閱</a>'
           if SUBSCRIBE_URL else "")
    return f"""<header class="mast"><div class="wrap">
  <div class="strip"><span id="today">Cue Sheet</span><span>{TAGLINE}{sub}</span></div>
  <div class="brand"><h1 class="title"><a href="{prefix}">Cue Sheet</a></h1><p class="kicker">FILM MUSIC NEWSLETTER</p></div>
  <nav class="topnav" aria-label="網站">{navhtml}</nav>
</div></header>"""


def page(title, desc, url, nav, body, image=None, depth=None, kicker=None, wide=False):
    """depth：頁面在網站根目錄下第幾層（首頁 0、newsletter/ 1、item/<id>/ 2）。
    body：(頁首說明, 主內容)。wide=True 用整頁寬（首頁），其餘頁面主內容置中 780px。"""
    if depth is None:
        depth = {"home": 0}.get(nav, 1)
    prefix = "../" * depth or "./"
    og_img = f'<meta property="og:image" content="{SITE}{image}">\n' if image else ""
    intro = body[0].replace('class="sub"', 'class="intro"') if body[0] else ""
    inner = f"{intro}\n{body[1]}" if wide else f'<div class="narrow">{intro}\n{body[1]}</div>'
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
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&family=Noto+Serif+TC:wght@700;900&display=swap" rel="stylesheet">
<style>{CSS}</style>
{ML_SNIPPET}
</head>
<body>
{masthead(prefix, nav)}
<main><div class="wrap">
{inner}
</div></main>
<footer><div class="wrap"><b>Cue Sheet</b><br>每月 5 日深度聆聽版、20 日配樂新訊版<br>Cue Sheet 為非營利樂迷刊物，文字為編輯摘要與評論，圖片版權屬原權利人，連結皆指向原始來源。</div></footer>
{DATE_JS}
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

    # 電子報列表
    rows = []
    for it in issues:
        rows.append(f"""<div class="row">
  {issue_meta(it)}
  <div class="issue-title"><a href="{it['slug']}/">{escape(it['title'])}</a></div>
  <p class="note">{escape(it['editor_note'])}</p>
  <a class="more" href="{it['slug']}/">閱讀 →</a>
</div>""")
    list_main = f'<div class="toppad"></div>\n<div class="list">\n' + "\n".join(rows) + "\n</div>"
    list_sub = ""
    open("newsletter/index.html", "w", encoding="utf-8").write(page(
        "電子報｜Cue Sheet", "Cue Sheet 各期電子報，月刊與特刊。", SITE + "newsletter/", "newsletter",
        (list_sub, list_main), latest.get("image")))
    print(f"電子報列表已產生，共 {len(issues)} 期")
    build_latest(issues)
    from build_items import build_home
    build_home()


def redirect_page(target, label):
    return f"""<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cue Sheet｜最新一期{escape(label)}</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{SITE}newsletter/{target}/">
<meta http-equiv="refresh" content="0; url=../{target}/">
<script>location.replace("../{target}/" + location.hash);</script>
<style>body{{font-family:-apple-system,"PingFang TC","Microsoft JhengHei",sans-serif;background:#F4F1E8;color:#1F1D18;padding:40px 16px;text-align:center}}a{{color:#01696F}}</style>
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

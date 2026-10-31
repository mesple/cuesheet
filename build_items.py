"""產生網站的單則頁與分類頁。

資料：items/*.json（每期的單則）、issues/*.json（刊期組成）、composers.json（作曲家顯示名）、newsletter/issues.json（各期標籤）。
輸出：
  item/<id>/index.html        單則頁，例 /cuesheet/item/2026-10-001/
  category/index.html          分類總覽
  category/<slug>/index.html   各類型列表，例 /cuesheet/category/reviews/
只有 web 為 true 的單則會產生頁面；false（不上）與 null（待編輯決定）都不出現在網站上。
用法：python build_items.py
"""
import glob
import json
import os
import re
import shutil
import unicodedata
from html import escape

import markdown

from build_pages import CSS, SITE, page

TYPES = [  # 類型, 網址代號, 英文, 說明
    ("新聞", "news", "News", "新案、獎項、音樂活動與新片消息"),
    ("樂評", "reviews", "Reviews", "原聲帶與配樂評論摘要"),
    ("發行", "releases", "Releases", "新唱片、重發與實體版"),
    ("訪談", "interviews", "Interviews", "作曲家親口講述的創作"),
    ("試聽", "listen", "Listen", "官方釋出的配樂音軌與影片"),
    ("訃聞", "obituaries", "In memoriam", "送別作曲家與電影音樂人"),
    ("社群", "community", "Community Radar", "論壇與社論裡的熱門話題"),
]
SLUG = {t: s for t, s, _, _ in TYPES}
# 前台顯示的欄位名稱（編輯 2026-10-31 指定：社群改「社群雷達」；作曲家頁每則標欄位名）
COLUMN = {"新聞": "新聞", "樂評": "樂評", "發行": "唱片架", "訪談": "訪談", "試聽": "精選試聽", "訃聞": "訃聞", "社群": "社群雷達"}

EXTRA_CSS = """
.crumb{font-size:13px;color:var(--muted);margin:22px 0 0}
.crumb a{color:var(--soft);text-decoration:none}
.crumb a:hover{color:var(--teal)}
.pills{margin:14px 0 0;display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.pill{display:inline-block;border:1px solid var(--teal);color:var(--teal);font-size:12px;padding:1px 8px;line-height:1.6;text-decoration:none}
.pill.solid{background:var(--teal);color:var(--paper)}
.pill.plain{border-color:var(--line);color:var(--soft)}
h2.item-title{font-family:"Noto Serif TC",Georgia,serif;font-size:32px;line-height:1.3;margin:10px 0 6px;letter-spacing:-.01em}
.byline{font-size:15px;color:var(--soft);margin:0 0 4px}
.dateline{font-size:13px;color:var(--muted);margin:0 0 18px}
.deck{font-size:18px;line-height:1.6;color:var(--soft);margin:0 0 8px}
.lead{font-size:18px;line-height:1.85;margin:0 0 18px}
.body{font-size:16px;line-height:1.9}
.body h2{font-family:"Noto Serif TC",Georgia,serif;font-size:21px;margin:30px 0 8px}
.body ul{padding-left:22px}
.body li{margin:4px 0}
.media{display:grid;gap:14px;margin:6px 0 22px}
.media.multi{grid-template-columns:repeat(3,minmax(0,1fr))}
.media figure{margin:0}
.media img{display:block;width:100%;height:auto;border:1px solid var(--line);background:var(--paper)}
.media.single img{max-width:360px}
.media.single.wide img{max-width:100%}
.media.sq figure{width:fit-content;max-width:100%}
.media.sq img{height:300px;width:auto;max-width:100%;object-fit:contain}   /* 新聞單則頁圖片高 300、寬度依原圖比例（編輯 2026-10-31 指定） */
@media (max-width:600px){.media.sq img{height:auto}}   /* 手機上寬圖放不下時改依寬度縮小，避免變形 */
.byline a{color:var(--teal);text-decoration:none}.byline a:hover{text-decoration:underline}
.items .pill.col{background:var(--teal);color:var(--paper)}
.items p.sum{font-size:15px;line-height:1.85;color:var(--ink)}
.items .sum a{color:var(--teal)}
.items .sum a.cl{text-decoration:none;border-bottom:1px dotted var(--teal)}
.items .older{margin:18px 0 0;font-size:15px;font-weight:700}.items .older a{text-decoration:none}
.media figcaption{font-size:12px;color:var(--muted);margin-top:4px;line-height:1.5}
.yt{display:block;max-width:480px;text-decoration:none;color:#FBFAF6}
.yt span{display:block;background:#28251D;color:#FBFAF6;font-size:13px;padding:6px 10px}
.media .yt img{max-width:none;width:100%;aspect-ratio:16/9;object-fit:cover;border:none}  /* 影音截圖與下方黑條同寬（編輯 2026-10-31 指定） */
.items .more{font-size:14px;font-weight:700;color:var(--teal);text-decoration:none;white-space:nowrap}
.items .more:hover{text-decoration:underline}
.box{background:var(--paper);border:1px solid var(--line);padding:14px 16px;margin:22px 0 0;font-size:14px}
.box b{display:block;font-size:12px;letter-spacing:.08em;color:var(--muted);margin-bottom:6px;font-weight:700}
.box ul{margin:0;padding-left:20px}
.box li{margin:3px 0}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{border:1px solid var(--line);background:var(--bg);font-size:13px;padding:1px 8px;color:var(--ink);text-decoration:none}
a.chip:hover{border-color:var(--teal);color:var(--teal)}
.chip small{color:var(--muted);margin-left:4px}
.alias{font-size:14px;color:var(--muted);margin:4px 0 0}
.rel{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:8px}
.rel a{display:block;background:var(--paper);border:1px solid var(--line);padding:12px 14px;text-decoration:none;color:var(--ink)}
.rel a:hover{border-color:var(--teal)}
.rel small{display:block;font-size:12px;color:var(--muted)}
.rel b{display:block;font-size:15px;line-height:1.45;margin-top:2px}
.items .it{display:grid;grid-template-columns:88px minmax(0,1fr);gap:14px;padding:16px 0;border-top:1px dotted var(--line)}
.items .it:first-child{border-top:none}
.items .it.noimg{grid-template-columns:minmax(0,1fr)}
.items .it[hidden]{display:none}  /* 篩選用：display:grid 會蓋過 hidden，要明寫 */
.items .thumb img{display:block;width:88px;height:auto;border:1px solid var(--line)}
.items .it.video{grid-template-columns:150px minmax(0,1fr)}   /* 影音訪談：截圖放大 */
.items .it.video .thumb img{width:150px;aspect-ratio:16/9;object-fit:cover}
.twocol .items .it{grid-template-columns:110px minmax(0,1fr)}   /* 唱片架/試聽圖放大 25% */
.twocol .items .thumb img{width:110px}
.items .by a{color:var(--soft);text-decoration:none;border-bottom:1px dotted var(--line)}
.items .by a:hover{color:var(--teal)}
.items .src{font-size:12px;color:var(--muted);margin-top:4px}
.items .src a{color:var(--teal);text-decoration:none}
.items .meta{font-size:12px;color:var(--muted)}
.items .meta .pill{font-size:11px;padding:0 6px;margin-right:4px}
.items h3{font-size:17px;line-height:1.45;margin:4px 0 2px}
.items h3 a{color:var(--ink);text-decoration:none}
.items h3 a:hover{color:var(--teal)}
.items .by{font-size:13px;color:var(--soft)}
.items p{font-size:14px;line-height:1.7;color:var(--soft);margin:4px 0 0}
.twocol{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:0 40px}
.twocol .col + .col{border-left:1px solid var(--line);padding-left:40px}
.colhead{font-size:13px;font-weight:700;letter-spacing:.14em;padding-bottom:6px;border-bottom:2px solid var(--ink);margin-bottom:2px}
.colhead span{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-left:8px}
@media (max-width:760px){.twocol{grid-template-columns:1fr}.twocol .col + .col{border-left:none;padding-left:0;margin-top:28px}}
.filters{display:flex;flex-wrap:wrap;gap:6px;margin:4px 0 10px}
.filters button{font:inherit;font-size:13px;border:1px solid var(--line);background:var(--paper);color:var(--soft);padding:3px 10px;cursor:pointer}
.filters button[aria-pressed="true"]{border-color:var(--teal);background:var(--teal);color:var(--paper)}
.types{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.type-card{background:var(--paper);border:1px solid var(--line);padding:16px}
.type-card h3{margin:0;font-size:18px}
.type-card h3 a{color:var(--ink);text-decoration:none}
.type-card h3 a:hover{color:var(--teal)}
.type-card h3 small{font-size:12px;color:var(--muted);font-weight:400;margin-left:6px}
.type-card p{font-size:13px;color:var(--soft);margin:4px 0 8px}
.type-card ul{margin:0;padding-left:18px;font-size:14px}
.type-card li{margin:3px 0}
.type-card li a{color:var(--ink);text-decoration:none}
.type-card li a:hover{color:var(--teal)}
@media (max-width:600px){
  h2.item-title{font-size:25px}
  .lead{font-size:17px}
  .media.multi{grid-template-columns:repeat(2,minmax(0,1fr))}
  .rel,.types{grid-template-columns:1fr}
  .items .it{grid-template-columns:64px minmax(0,1fr)}
  .items .thumb img{width:64px}
  .twocol .items .it{grid-template-columns:80px minmax(0,1fr)}
  .twocol .items .thumb img{width:80px}
  .items .it.video{grid-template-columns:110px minmax(0,1fr)}
  .items .it.video .thumb img{width:110px}
}
"""


def load():
    items = []
    for f in sorted(glob.glob("items/*.json")):
        items += json.load(open(f, encoding="utf-8"))["items"]
    composers = json.load(open("composers.json", encoding="utf-8"))["composers"]
    labels = {i["slug"]: i for i in json.load(open("newsletter/issues.json", encoding="utf-8"))["issues"]}
    features = {}
    for f in glob.glob("issues/*.json"):
        d = json.load(open(f, encoding="utf-8"))
        for fid in d.get("feature", []):
            features[fid] = d["issue"]
    return items, composers, labels, features


def date_pending(it):
    return "date 待確認" in it.get("internal_note", "") and len(it["date"]) == 10


def fmt_date(it):
    d = it["date"]
    if date_pending(it):
        return ""
    y, m = d[:4], int(d[5:7])
    if len(d) == 7:
        return f"{y} 年 {m} 月"
    return f"{y} 年 {m} 月 {int(d[8:10])} 日"


def sort_key(it):
    d = it["date"]
    if date_pending(it) or len(d) == 7:
        d = (d + "-00") if len(d) == 7 else d
    return (d, it["id"])


def show_name(text, composers, codes):
    """把原刊寫法（如 Ricky Ho）換成顯示名（何國杰）。"""
    for c in codes or []:
        info = composers.get(c)
        if not info:
            continue
        for a in [info.get("name")] + info.get("aliases", []):
            if a and a not in info["display"] and a in text:
                text = text.replace(a, info["display"])
    return text


def yt_thumb(vid):
    return f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"


def media_html(it, title):
    media = it.get("media") or []
    if not media:
        return ""
    figs = []
    for m in media:
        if m["kind"] == "youtube":
            cap = escape(m.get("caption", ""))
            figs.append(f'<figure><a class="yt" href="https://www.youtube.com/watch?v={m["id"]}"><img src="{yt_thumb(m["id"])}" alt="{escape(title)} YouTube 預覽" loading="lazy"><span>▶ 到 YouTube 觀看</span></a>'
                        + (f"<figcaption>{cap}</figcaption>" if cap else "") + "</figure>")
            continue
        img = f'<img src="{m["url"]}" alt="{escape(m.get("caption") or title)}" loading="lazy">'
        if m.get("link"):
            img = f'<a href="{m["link"]}">{img}</a>'
        cap = []
        if m.get("caption") and m.get("caption") != "專輯封面":
            cap.append(escape(m["caption"]))
        if m.get("hosting") == "spotify":
            cap.append(f'封面：<a href="{m["link"]}">Spotify</a>')
        elif m.get("hosting") == "commons":
            credit = escape(m.get("credit", ""))
            if m.get("credit_url"):
                credit = f'<a href="{m["credit_url"]}">{credit}</a>'
            cap.append(credit)
        elif m.get("credit"):
            c = escape(m["credit"])
            cap.append("圖片來源：" + (f'<a href="{m["credit_url"]}">{c}</a>' if m.get("credit_url") else c))
        # media 可指定 width（px）：縮小單張圖，圖說跟著同寬（編輯 2026-10-31 指定）
        fstyle = f' style="max-width:{int(m["width"])}px"' if m.get("width") else ""
        figs.append(f"<figure{fstyle}>{img}" + (f'<figcaption>{"　".join(cap)}</figcaption>' if cap else "") + "</figure>")
    cls = "multi" if len(figs) > 1 else "single"
    if it["type"] == "新聞" and all(m["kind"] == "image" for m in media):
        cls += " sq"
    return f'<div class="media {cls}">' + "".join(figs) + "</div>"


NO_PAGE_TYPES = ("發行", "試聽")   # 唱片架、精選試聽：資訊少，不另做單則頁（編輯 2026-10-31 指定）
PAGE_MIN_CHARS = 200              # 這兩類若內文達 200 字以上，才做單則頁


NO_DATE_TYPES = ("樂評", "發行", "試聽")
NO_LIST_DATE_TYPES = NO_DATE_TYPES + ("訪談",)   # 訪談列表不放日期，單則頁才放（編輯 2026-10-31 指定）


def has_page(it):
    if it["type"] not in NO_PAGE_TYPES:
        return True
    return len(it.get("summary", "")) + len(it.get("body") or "") >= PAGE_MIN_CHARS


def ext_link(it):
    """沒有單則頁的條目，點圖或標題直接去哪：YouTube 影片 > Spotify 專輯 > 第一個來源。"""
    for m in it.get("media") or []:
        if m["kind"] == "youtube":
            return f"https://www.youtube.com/watch?v={m['id']}"
        if m.get("link"):
            return m["link"]
    src = it.get("sources") or []
    return src[0]["url"] if src else ""


def item_href(it, up):
    """回傳 (網址, 是否外部連結)。"""
    if has_page(it):
        return f'{up}item/{it["id"]}/', False
    return ext_link(it), True


def first_image(it):
    for m in it.get("media") or []:
        if m["kind"] == "youtube":
            return f"https://img.youtube.com/vi/{m['id']}/mqdefault.jpg"   # 16:9、無黑邊
        return m["url"]
    return None


def issue_label(labels, slug):
    return labels.get(slug, {}).get("label", slug)


def item_page(it, by_id, composers, labels, features):
    title = it["title"]
    codes = it.get("composers", [])
    slug = SLUG[it["type"]]
    pills = []   # 類別已顯示在選單上，不再重複（編輯 2026-10-31 指定）
    for t in it.get("tags", []):
        pills.append(f'<a class="pill" href="../../category/{slug}/?tag={escape(t)}">{escape(t)}</a>')
    if it["id"] in features:
        pills.append(f'<a class="pill plain" href="../../newsletter/{features[it["id"]]}/">{escape(issue_label(labels, features[it["id"]]))}本月專題</a>')
    byline = ""
    if it.get("byline"):
        bl = escape(show_name(it["byline"], composers, codes))
        if it["type"] == "樂評":   # 標題下的作曲家名直接連作曲家頁（編輯 2026-10-31 指定）
            for c in codes:
                if c in composers:
                    n = escape(composers[c]["display"])
                    bl = bl.replace(n, f'<a href="../../composer/{c}/">{n}</a>', 1)
        byline = f'<p class="byline">{bl}</p>'
    date = "" if it["type"] in NO_DATE_TYPES else fmt_date(it)
    dateline = f'<p class="dateline">{date}</p>' if date else ""
    summary = show_name(it["summary"], composers, codes)
    body = ""
    if it.get("body"):
        body = '<div class="body">' + markdown.markdown(show_name(it["body"], composers, codes)) + "</div>"
    lead = f'<p class="lead">{escape(summary)}</p>'
    deck = ""
    top_media, more_media = media_html(it, title), ""
    if it.get("body"):
        # 長文：摘要當副標，第一張圖放上面，其餘圖放文末
        deck, lead = ("" if it["type"] in ("樂評", "訪談") else f'<p class="deck">{escape(summary)}</p>'), ""
        if len(it.get("media") or []) > 1:
            rest = dict(it, media=it["media"][1:])
            top_media = media_html(dict(it, media=it["media"][:1]), title)
            more_media = '<div class="sec">圖片<span>Gallery</span></div>' + media_html(rest, title)
    boxes = []
    if codes and not (it["type"] == "樂評" and it.get("byline")):
        chips = "".join(f'<a class="chip" href="../../composer/{c}/">{escape(composers[c]["display"])}</a>' for c in codes if c in composers)
        boxes.append(f'<div class="box"><b>作曲家</b><div class="chips">{chips}</div></div>')
    if it.get("upcoming"):
        lis = []
        for u in sorted(it["upcoming"], key=lambda x: x["date"]):
            d = f'{int(u["date"][5:7])}/{int(u["date"][8:10])}'
            if u.get("end"):
                e = u["end"]
                d += "–" + (f"{int(e[8:10])}" if e[5:7] == u["date"][5:7] else f"{int(e[5:7])}/{int(e[8:10])}")
            lis.append(f"<li>{d}　{escape(u['label'])}</li>")
        boxes.append('<div class="box"><b>接下來</b><ul>' + "".join(lis) + "</ul></div>")
    if it.get("sources"):
        lis = "".join(f'<li><a href="{escape(s["url"])}">{escape(s["name"])}</a></li>' for s in it["sources"])
        boxes.append(f'<div class="box"><b>來源</b><ul>{lis}</ul></div>')
    rel = [by_id[r] for r in it.get("related", []) if r in by_id and has_page(by_id[r])]
    rel_html = ""
    if rel:
        cards = "".join(f'<a href="../{r["id"]}/"><small>{r["type"]}</small><b>{escape(r["title"])}</b></a>' for r in rel)
        rel_html = f'<div class="sec">相關內容<span>Related</span></div><div class="rel">{cards}</div>'
    if it["type"] in ("發行", "試聽"):
        crumb = f'<p class="crumb"><a href="../../category/releases/">唱片架/試聽</a> › {"唱片架" if it["type"] == "發行" else "精選試聽"}</p>'
    else:
        crumb = f'<p class="crumb"><a href="../../category/{slug}/">{COLUMN[it["type"]]}</a></p>'
    article = f"""<div class="toppad"></div>
<article>
{f'<div class="pills">{"".join(pills)}</div>' if pills else ""}
<h2 class="item-title">{escape(title)}</h2>
{deck}
{byline}
{dateline}
{top_media}
{lead}
{body}
{more_media}
{"".join(boxes)}
</article>
{rel_html}"""
    desc = summary if len(summary) <= 120 else summary[:118] + "…"
    html = page(f"{title}｜Cue Sheet", desc, f"{SITE}item/{it['id']}/", slug, ("", article),
                depth=2, kicker=f"Cue Sheet · {dict((t, e) for t, _, e, _ in TYPES)[it['type']]}")
    img = first_image(it)
    if img:
        html = html.replace('<meta property="og:locale"', f'<meta property="og:image" content="{img}">\n<meta property="og:locale"', 1)
    html = html.replace('<meta property="og:type" content="website">', '<meta property="og:type" content="article">')
    return html.replace("</style>", EXTRA_CSS + "</style>", 1)


def row_html(it, composers, labels, depth, show_date=True, show_by=True, show_col=False):
    """分類頁的一列。前台不顯示地區；樂評、唱片架、試聽不顯示日期（編輯 2026-10-31 指定）。
    沒有單則頁的條目（唱片架、試聽）：圖與標題直接連外，作曲家連作曲家頁，最後一行列來源。"""
    up = "../" * depth
    href, external = item_href(it, up)
    tgt = ' target="_blank" rel="noopener"' if external else ""
    img = first_image(it)
    thumb = f'<a class="thumb" href="{escape(href)}"{tgt}><img src="{img}" alt="" loading="lazy"></a>' if img else ""
    tags = "".join(f'<span class="pill">{escape(t)}</span>' for t in it.get("tags", []))
    if show_col:   # 作曲家頁：每則標上欄位名稱（編輯 2026-10-31 指定）
        tags = f'<span class="pill col">{COLUMN[it["type"]]}</span>' + tags
    date = "" if (not show_date or it["type"] in NO_LIST_DATE_TYPES) else fmt_date(it)
    meta = f'<div class="meta">{tags}{date}</div>' if (tags or date) else ""
    codes = [c for c in (it.get("composers") or []) if c in composers]
    if external and codes:
        by = '<div class="by">' + "、".join(
            f'<a href="{up}composer/{c}/">{escape(composers[c]["display"])}</a>' for c in codes) + "</div>"
    elif it.get("byline"):
        by = f'<div class="by">{escape(show_name(it["byline"], composers, it.get("composers")))}</div>'
    else:
        by = ""
    if not show_by:   # 作曲家頁：每則不再重複寫作曲家名
        by = ""
    s = show_name(it.get("teaser") or it["summary"], composers, it.get("composers"))
    more = ""
    if it["type"] in ("訪談", "樂評") and not external:
        # 訪談：約 50 字摘要，文末接「閱讀全文」（編輯 2026-10-31 指定）
        if it["type"] == "樂評":
            s = s if len(s) <= 90 else s[:88] + "…"
        more = f' <a class="more" href="{escape(href)}">閱讀全文 →</a>'
    elif not external:
        s = s if len(s) <= 90 else s[:88] + "…"
    src = ""
    if external and it.get("sources"):
        src = '<div class="src">來源：' + "・".join(
            f'<a href="{escape(x["url"])}" target="_blank" rel="noopener">{escape(x["name"])}</a>' for x in it["sources"]) + "</div>"
    data_tags = escape(" ".join(it.get("tags", [])))
    video = " video" if img and any(m["kind"] == "youtube" for m in it.get("media") or []) and it["type"] == "訪談" else ""
    return f"""<div class="it{'' if img else ' noimg'}{video}" data-tags="{data_tags}">{thumb}<div>
{meta}
<h3><a href="{escape(href)}"{tgt}>{escape(it["title"])}</a></h3>{by}
<p>{escape(s)}{more}</p>{src}</div></div>"""


def src_paren(it):
    """來源用括號接在文末，不寫「來源」兩字（編輯 2026-10-31 指定）。"""
    if not it.get("sources"):
        return ""
    return "（" + "、".join(f'<a href="{escape(x["url"])}" target="_blank" rel="noopener">{escape(x["name"])}</a>' for x in it["sources"]) + "）"


def link_composers(html_text, codes, composers, up):
    """把已跳脫的文字中出現的作曲家名（顯示名或別名，含只寫姓氏）連到作曲家頁，每位只連第一次出現（編輯 2026-10-31 指定）。"""
    cands = []
    for c in codes or []:
        info = composers.get(c)
        if not info:
            continue
        for n in dict.fromkeys([info["display"], info.get("name")] + info.get("aliases", [])):
            if n:
                cands.append((escape(n), c))
    cands.sort(key=lambda x: -len(x[0]))
    spans, done = [], set()
    for n, c in cands:
        if c in done:
            continue
        pat = (r"(?<![A-Za-zÀ-ÿ])" if n[0].isascii() and n[0].isalpha() else "") + re.escape(n) + \
              (r"(?![A-Za-zÀ-ÿ])" if n[-1].isascii() and n[-1].isalpha() else "")
        for m in re.finditer(pat, html_text):
            if any(m.start() < e and m.end() > b for b, e, _ in spans):
                continue
            spans.append((m.start(), m.end(), c))
            done.add(c)
            break
    for b, e, c in sorted(spans, reverse=True):
        html_text = html_text[:b] + f'<a class="cl" href="{up}composer/{c}/">{html_text[b:e]}</a>' + html_text[e:]
    return html_text


def full_row(it, composers, depth):
    """新聞、社群雷達列表（編輯 2026-10-31 指定）：短文全文放列表、文末括號附來源，不另列作曲家與接下來；
    有長篇內文的才連單則頁，摘要後接「閱讀全文」。單則頁照常保留，供作曲家頁、首頁與相關內容連結。"""
    up = "../" * depth
    href = f'{up}item/{it["id"]}/'
    long_ = bool(it.get("body"))
    nm = lambda t: escape(show_name(t, composers, it.get("composers")))
    img = first_image(it)
    thumb = ""
    if img:
        im = f'<img src="{img}" alt="" loading="lazy">'
        thumb = f'<a class="thumb" href="{href}">{im}</a>' if long_ else f'<span class="thumb">{im}</span>'
    tags = "".join(f'<span class="pill">{escape(t)}</span>' for t in it.get("tags", []))
    date = fmt_date(it)
    meta = f'<div class="meta">{tags}{date}</div>' if (tags or date) else ""
    title = f'<a href="{href}">{nm(it["title"])}</a>' if long_ else nm(it["title"])
    tail = f' <a class="more" href="{href}">閱讀全文 →</a>' if long_ else src_paren(it)
    summ = nm(it["summary"])
    if it["type"] == "新聞":
        summ = link_composers(summ, it.get("composers"), composers, up)
    return f"""<div class="it{'' if img else ' noimg'}" data-tags="{escape(" ".join(it.get("tags", [])))}">{thumb}<div>
{meta}
<h3>{title}</h3>
<p class="sum">{summ}{tail}</p></div></div>"""


FILTER_JS = """<script>
(function(){
  var btns=document.querySelectorAll('.filters button'), rows=document.querySelectorAll('.items .it');
  function apply(tag){
    btns.forEach(function(b){b.setAttribute('aria-pressed', b.dataset.tag===tag?'true':'false');});
    rows.forEach(function(r){r.hidden = tag && (' '+r.dataset.tags+' ').indexOf(' '+tag+' ')<0;});
  }
  btns.forEach(function(b){b.addEventListener('click',function(){
    apply(b.dataset.tag);
    try{var u=new URL(location.href); if(b.dataset.tag){u.searchParams.set('tag',b.dataset.tag);}else{u.searchParams.delete('tag');} history.replaceState(null,'',u);}catch(e){}
  });});
  var t=''; try{t=new URLSearchParams(location.search).get('tag')||'';}catch(e){}
  apply(t);
})();
</script>"""


CJK = "\u4e00-\u9fff\u3400-\u4dbf"


def lint(items, composers):
    """寫稿規則檢查（編輯 2026-10-31 指定）：每次建站列出違規的單則，上線前修正。只提醒，不擋建站。
    1. 標題不放日期（日期寫在摘要）
    2. 新聞摘要要寫出作曲家名（列表才連得到作曲家頁）
    3. 新聞、社群雷達的短文摘要不寫來源名（來源由程式接在文末括號）
    4. 兩個中文字之間不空格"""
    warns = []
    for it in items:
        if it.get("web") is not True:
            continue
        t, summ, i = it["title"], it["summary"], it["id"]
        if re.search(r"\d{1,2}/\d{1,2}|\d{1,2}\s*月(\s*\d{1,2}\s*日)?(?!號)", t) and it["type"] in ("新聞", "社群", "訪談", "樂評"):
            warns.append(f"{i} 標題含日期：{t}")
        if it["type"] == "新聞":
            names = [n for c in it.get("composers", []) if c in composers
                     for n in [composers[c]["display"], composers[c].get("name")] + composers[c].get("aliases", []) if n]
            if names and not any(n in show_name(summ, composers, it.get("composers")) for n in names):
                warns.append(f"{i} 摘要沒寫到作曲家名（列表不會有連結）：{t}")
        if it["type"] in ("新聞", "社群") and not it.get("body"):
            for src in it.get("sources", []):
                if src["name"] in summ and re.search(r"[（(][^（）()]*" + re.escape(src["name"]), summ):
                    warns.append(f"{i} 摘要括號裡已寫來源「{src['name']}」，文末會重複：{t}")
                    break
        for field in (t, summ):
            m = re.search(f"[{CJK}] +[{CJK}]", field)
            if m:
                warns.append(f"{i} 中文字之間有空格「{m.group(0)}」：{t}")
                break
    if warns:
        print(f"寫稿規則檢查：{len(warns)} 則要修正")
        for w in warns:
            print("  ・" + w)
    else:
        print("寫稿規則檢查：通過")
    return warns


def main():
    items, composers, labels, features = load()
    lint(items, composers)
    by_id = {it["id"]: it for it in items if it.get("web") is True}
    shown = sorted(by_id.values(), key=sort_key, reverse=True)

    if os.path.isdir("item"):
        shutil.rmtree("item")
    for it in shown:
        if not has_page(it):
            continue
        os.makedirs(f"item/{it['id']}", exist_ok=True)
        open(f"item/{it['id']}/index.html", "w", encoding="utf-8").write(item_page(it, by_id, composers, labels, features))

    # 各類型列表（編輯 2026-10-30：選單下方不放說明、則數與欄名；發行與試聽合併成「唱片架/試聽」兩欄）
    cards = []
    for t, slug, en, desc in TYPES:
        rows = [it for it in shown if it["type"] == t]
        if not rows:
            continue
        if t == "試聽":   # 併入唱片架/試聽頁；舊網址轉址
            os.makedirs("category/listen", exist_ok=True)
            open("category/listen/index.html", "w", encoding="utf-8").write(
                '<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex">'
                '<link rel="canonical" href="' + SITE + 'category/releases/"><meta http-equiv="refresh" content="0; url=../releases/">'
                '<script>location.replace("../releases/")</script><a href="../releases/">唱片架/試聽</a>')
        else:
            filters = ""
            if t == "新聞":
                tags = [x for x in ("獎項", "音樂活動", "新案", "新片", "其他") if any(x in it.get("tags", []) for it in rows)]
                filters = '<div class="filters"><button type="button" data-tag="" aria-pressed="true">全部</button>' + "".join(
                    f'<button type="button" data-tag="{x}" aria-pressed="false">{x}</button>' for x in tags) + "</div>"
            if t == "發行":
                listen = [it for it in shown if it["type"] == "試聽"]
                col = lambda name, rs: (f'<div class="col"><div class="colhead">{name}</div><div class="items">'
                                        + "\n".join(row_html(it, composers, labels, 2, show_date=False) for it in rs) + "</div></div>")
                body = f'<div class="toppad"></div><div class="twocol">{col("唱片架<span>Record Shelf</span>", rows)}{col("精選試聽<span>Take a Bite</span>", listen)}</div>'
                ptitle, pdesc, wide = "唱片架/試聽", "新唱片、重發、實體版，以及官方釋出的配樂音軌與影片", True
            elif t in ("新聞", "社群"):
                recent = sorted({it["issue"] for it in rows}, reverse=True)[:2]   # 只列最近兩期（編輯 2026-10-31 指定）
                older = [it for it in rows if it["issue"] not in recent]
                cur = [it for it in rows if it["issue"] in recent]
                more = '<p class="older"><a href="archive/">更早的' + COLUMN[t] + ' →</a></p>' if older else ""
                body = (f'<div class="toppad"></div>{filters}<div class="items">'
                        + "\n".join(full_row(it, composers, 2) for it in cur) + more + "</div>"
                        + (FILTER_JS if filters else ""))
                ptitle, pdesc, wide = COLUMN[t], desc, False
                arch = f"category/{slug}/archive"
                if os.path.isdir(arch):
                    shutil.rmtree(arch)
                if older:
                    os.makedirs(arch, exist_ok=True)
                    abody = (f'<div class="toppad"></div><p class="crumb"><a href="../">{COLUMN[t]}</a> › 更早的{COLUMN[t]}</p><div class="items">'
                             + "\n".join(full_row(it, composers, 3) for it in older) + "</div>")
                    ah = page(f"更早的{COLUMN[t]}｜Cue Sheet", f"Cue Sheet 較早各期的{COLUMN[t]}。", f"{SITE}{arch}/", slug, ("", abody), depth=3)
                    open(f"{arch}/index.html", "w", encoding="utf-8").write(ah.replace("</style>", EXTRA_CSS + "</style>", 1))
            else:
                body = (f'<div class="toppad"></div>{filters}<div class="items">'
                        + "\n".join(row_html(it, composers, labels, 2) for it in rows) + "</div>"
                        + (FILTER_JS if filters else ""))
                ptitle, pdesc, wide = t, desc, False
            os.makedirs(f"category/{slug}", exist_ok=True)
            html = page(f"{ptitle}｜Cue Sheet", f"Cue Sheet 的{ptitle}：{pdesc}。", f"{SITE}category/{slug}/", slug,
                        ("", body), depth=2, wide=wide)
            open(f"category/{slug}/index.html", "w", encoding="utf-8").write(html.replace("</style>", EXTRA_CSS + "</style>", 1))
        latest = "".join(f'<li><a href="../item/{it["id"]}/">{escape(it["title"])}</a></li>' for it in rows[:3])
        cards.append(f'<div class="type-card"><h3><a href="{slug}/">{t}</a><small>{len(rows)} 則</small></h3><p>{desc}</p><ul>{latest}</ul></div>')

    # 「全部分類」頁已從選單拿掉（編輯 2026-10-30），舊網址轉到首頁
    open("category/index.html", "w", encoding="utf-8").write(
        '<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex">'
        '<meta http-equiv="refresh" content="0; url=../"><script>location.replace("../")</script><a href="../">Cue Sheet</a>')

    # 作曲家頁
    if os.path.isdir("composer"):
        shutil.rmtree("composer")
    by_c = {}
    for it in shown:
        for c in it.get("composers", []):
            by_c.setdefault(c, []).append(it)
    for c, rows in by_c.items():
        info = composers[c]
        # 名字下方只列外文原名、全名與藝名；只是姓氏或只差重音符號的別名不列（編輯 2026-10-31 指定）
        bare = lambda x: "".join(ch for ch in unicodedata.normalize("NFD", x) if unicodedata.category(ch) != "Mn").lower()
        other = [n for n in [info.get("name")] + info.get("aliases", [])
                 if n and n != info["display"] and n not in info["display"] and bare(n) != bare(info["display"])]
        alias = f'<p class="alias">{escape("、".join(dict.fromkeys(other)))}</p>' if other else ""
        main_html = (f'<div class="toppad"></div><h2 class="item-title">{escape(info["display"])}</h2>{alias}'
                     f'<div class="items" style="margin-top:14px">'
                     + "\n".join(row_html(it, composers, labels, 2, show_by=False, show_col=True) for it in rows) + "</div>")
        os.makedirs(f"composer/{c}", exist_ok=True)
        html = page(f"{info['display']}｜Cue Sheet", f"Cue Sheet 刊出與 {info['display']} 相關的 {len(rows)} 則內容。",
                    f"{SITE}composer/{c}/", "composer", ("", main_html), depth=2, kicker="Cue Sheet · Composers")
        open(f"composer/{c}/index.html", "w", encoding="utf-8").write(html.replace("</style>", EXTRA_CSS + "</style>", 1))
    order = sorted(by_c, key=lambda c: (-len(by_c[c]), composers[c]["name"] or composers[c]["display"]))
    multi = [c for c in order if len(by_c[c]) >= 2]
    rest = sorted([c for c in order if len(by_c[c]) < 2], key=lambda c: (composers[c]["name"] or composers[c]["display"]).lower())
    chip = lambda c: f'<a class="chip" href="{c}/">{escape(composers[c]["display"])}<small>{len(by_c[c])}</small></a>'
    idx = (f'<div class="sec">出現兩次以上<span>{len(multi)} 位</span></div><div class="chips">' + "".join(chip(c) for c in multi) + "</div>"
           f'<div class="sec">其他作曲家<span>{len(rest)} 位</span></div><div class="chips">' + "".join(chip(c) for c in rest) + "</div>")
    html = page("作曲家｜Cue Sheet", "依作曲家瀏覽 Cue Sheet 刊出的新聞、樂評、新唱片、訪談與訃聞。", f"{SITE}composer/", "composer",
                ('<div class="toppad"></div>', idx), depth=1,
                kicker="Cue Sheet · Composers")
    open("composer/index.html", "w", encoding="utf-8").write(html.replace("</style>", EXTRA_CSS + "</style>", 1))
    print(f"作曲家頁 {len(by_c)} 位（兩則以上 {len(multi)} 位）")

    build_home()
    hidden = [it for it in items if it.get("web") is not True]
    print(f"單則頁 {len(shown)} 則；未上網站 {len(hidden)} 則：" + "、".join(f'{it["id"]}（{"待定" if it.get("web") is None else "不上"}）' for it in hidden))



HOME_CSS = """
.h-grid{display:grid;grid-template-columns:minmax(0,2.1fr) minmax(0,1fr);margin-top:22px}
.h-lead{padding-right:24px;border-right:1px solid var(--ink)}
.h-side{padding-left:24px}
.h-side .sec:first-child{margin-top:0}
.h-head{font-family:"Noto Serif TC",Georgia,serif;font-size:40px;line-height:1.2;margin:0 0 10px;font-weight:900}
.h-head a{color:var(--ink);text-decoration:none}.h-head a:hover{color:var(--teal)}
.h-deck{font-size:18px;color:var(--soft);margin:0 0 16px;line-height:1.6}
.h-pics{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr) minmax(0,1fr);gap:8px}
.h-pics img{width:100%;height:220px;object-fit:cover;display:block}
.h-pics.n1{grid-template-columns:minmax(0,1fr)}.h-pics.n1 img{height:380px}
.h-pics.n2{grid-template-columns:minmax(0,1.2fr) minmax(0,1fr)}
.h-credit{font-size:12px;color:var(--muted);margin-top:6px}
.h-credit a{color:var(--muted)}
.h-body{font-size:15px;line-height:1.85;margin-top:14px;columns:2;column-gap:24px;column-rule:1px solid var(--line)}
.h-body p{margin:0 0 .8em}
.h-read{display:inline-block;margin-top:6px;font-size:15px;font-weight:700;text-decoration:none}
.h-second{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.25fr);gap:22px;margin-top:26px;padding-top:22px;border-top:1px solid var(--ink)}
.h-second.noimg{grid-template-columns:minmax(0,1fr)}
.h-second img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block}
.h-head2{font-family:"Noto Serif TC",Georgia,serif;font-size:26px;line-height:1.3;margin:0 0 8px;font-weight:900}
.h-head2 a{color:var(--ink);text-decoration:none}.h-head2 a:hover{color:var(--teal)}
.h-deck2{font-size:16px;color:var(--soft);margin:0 0 10px;line-height:1.6}
.h-body2{font-size:15px;line-height:1.85;margin:0 0 4px}
.h-row{display:block;padding:10px 0;border-bottom:1px solid var(--line);text-decoration:none;color:var(--ink)}
.h-row b{display:block;font-family:"Noto Serif TC",Georgia,serif;font-size:17px;line-height:1.4}
.h-row:hover b{color:var(--teal)}
.h-row span{font-size:13px;color:var(--muted)}
.h-ev{display:grid;grid-template-columns:54px minmax(0,1fr);gap:8px;padding:8px 0;border-bottom:1px dotted var(--line);font-size:14px;color:var(--ink);text-decoration:none}
.h-ev:hover{color:var(--teal)}
.h-ev .d{font-family:Georgia,serif;font-weight:700;font-size:18px}
.h-ev small{display:block;color:var(--muted);font-size:12px}
.h-ev-more{display:inline-block;margin-top:10px;font-size:14px;font-weight:700;text-decoration:none}
.h-four{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:22px}
.h-cover{display:block;text-decoration:none;color:var(--ink)}
.h-cover img{width:100%;aspect-ratio:1;object-fit:cover;display:block;background:var(--paper)}
.h-cover b{display:block;font-family:"Noto Serif TC",Georgia,serif;font-size:18px;margin:8px 0 2px;line-height:1.35}
.h-cover a{text-decoration:none;color:inherit}
.h-cover a:hover b{color:var(--teal)}
.h-cover .h-more{color:var(--teal);font-size:13px;white-space:nowrap}
.h-cover .h-more:hover{text-decoration:underline}
.h-cover .by{font-size:13px;color:var(--teal)}
.h-cover p{font-size:14px;line-height:1.7;margin:6px 0 0;color:var(--soft)}
.h-three{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:28px}
.h-talk{display:block;text-decoration:none;color:var(--ink)}
.h-talk b{display:block;font-family:"Noto Serif TC",Georgia,serif;font-size:18px;line-height:1.4;margin-bottom:6px}
.h-talk:hover b{color:var(--teal)}
.h-talk span{display:block;font-size:14px;line-height:1.75;color:var(--soft)}
.h-talk small{display:block;margin-top:6px;font-size:12px;color:var(--muted)}
.h-two{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:28px}
.h-two > div > .sec:first-child{margin-top:0}
.h-rel{display:grid;grid-template-columns:70px minmax(0,1fr);gap:12px;padding:10px 0;border-bottom:1px solid var(--line);text-decoration:none;color:var(--ink)}
.h-rel img{width:70px;height:70px;object-fit:cover;display:block}
.h-rel b{font-size:16px}.h-rel:hover b{color:var(--teal)}
.h-rel span span,.h-obit span{display:block;margin-top:2px;font-size:13px;color:var(--muted)}
.h-rel span span.desc{color:var(--soft);font-size:14px;line-height:1.65;margin-top:4px}
.h-obit{display:block;padding:10px 0;border-bottom:1px solid var(--line);text-decoration:none;color:var(--ink)}
.h-obit b{font-size:16px}.h-obit:hover b{color:var(--teal)}
@media (max-width:760px){
  .h-grid,.h-two,.h-three{grid-template-columns:minmax(0,1fr)}
  .h-lead{padding-right:0;border-right:none}
  .h-side{padding-left:0;margin-top:28px}
  .h-pics{grid-template-columns:repeat(2,minmax(0,1fr))}
  .h-pics img:first-child{grid-column:span 2}
  .h-pics.n1 img{height:260px}
  .h-head{font-size:28px}
  .h-body{columns:1}
  .h-second{grid-template-columns:minmax(0,1fr);gap:12px}
  .h-head2{font-size:22px}
  .h-four{grid-template-columns:repeat(2,minmax(0,1fr))}
  .h-two > div + div > .sec:first-child{margin-top:30px}
}
"""

HOME_EVENTS_JS = """<script>
(function(){
  var REGIONS=["臺北市","新北市","基隆市","桃園市","新竹市","新竹縣","宜蘭縣","苗栗縣","臺中市","彰化縣","南投縣","雲林縣","嘉義市","嘉義縣","臺南市","高雄市","屏東縣","花蓮縣","臺東縣","澎湖縣","金門縣","連江縣"];
  function pt(s){var m=(s||"").trim().match(/^(\\d{4})\\/(\\d{1,2})\\/(\\d{1,2})(?:\\s+(\\d{1,2}):(\\d{2}))?/);return m?{y:+m[1],mo:+m[2],d:+m[3],h:m[4]!=null?+m[4]:99,mi:m[5]!=null?+m[5]:0}:null;}
  function p2(n){return String(n).padStart(2,"0");}
  function key(t){return ""+t.y+p2(t.mo)+p2(t.d)+p2(t.h)+p2(t.mi);}
  function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];});}
  var box=document.getElementById("h-events"); if(!box) return;
  var now=new Date(Date.now()+8*3600e3), today=""+now.getUTCFullYear()+p2(now.getUTCMonth()+1)+p2(now.getUTCDate());
  var bust="?t="+new Date().toISOString().slice(0,13);
  function get(u){return fetch(u+bust).then(function(r){return r.ok?r.json():null;}).catch(function(){return null;});}
  Promise.all([get("events.json"),get("manual_events.json")]).then(function(r){
    var evs=((r[0]&&r[0].events)||[]).concat((r[1]&&r[1].events)||[]), best={};
    evs.forEach(function(ev){(ev.shows||[]).forEach(function(s){
      var t=pt(s.time); if(!t||key(t).slice(0,8)<today||REGIONS.indexOf(s.city||"")<0) return;
      var k=(ev.title||"").replace(/\\s/g,"");
      if(!best[k]||key(t)<best[k].k) best[k]={k:key(t),t:t,ev:ev,s:s};
    });});
    var rows=Object.keys(best).map(function(k){return best[k];}).sort(function(a,b){return a.k<b.k?-1:1;}).slice(0,4);
    if(!rows.length){box.innerHTML='<p style="font-size:14px;color:var(--muted)">近期沒有新場次，看看活動頁的完整列表。</p>';return;}
    box.innerHTML=rows.map(function(x){
      var city=(x.s.city||"").replace(/[市縣]$/,""), url=x.ev.tickets||x.ev.web||"event/";
      return '<a class="h-ev" href="'+esc(url)+'"><span class="d">'+x.t.mo+'/'+x.t.d+'</span><span>'+esc((x.ev.title||"").replace(/^20\\d\\d/,""))+'<small>'+esc(city)+'・'+esc(x.s.venue||"")+'</small></span></a>';
    }).join("");
  });
})();
</script>"""


def _first_sentence(text, limit):
    s = text.split("。")[0]
    s = s + "。" if len(s) < len(text) else s
    return s if len(s) <= limit else s[:limit - 1] + "…"


def _plain(md):
    return re.sub(r"[*_`#>\\[\\]]", "", md).strip()


CLAMP_JS = r"""<script>
(function(){
  // 每張樂評卡的摘要裁到三行，結尾留「…（閱讀全文）」；視窗大小改變時重算
  function fit(){
    document.querySelectorAll('p.clamp3').forEach(function(p){
      var t=p.querySelector('.t'); if(!t) return;
      if(!t.dataset.full) t.dataset.full=t.textContent;
      var full=t.dataset.full, lh=parseFloat(getComputedStyle(p).lineHeight)||24, max=lh*3+2;
      t.textContent=full; if(p.offsetHeight<=max) return;
      var lo=0, hi=full.length;
      while(lo<hi){var m=(lo+hi+1)>>1; t.textContent=full.slice(0,m)+'…'; if(p.offsetHeight<=max) lo=m; else hi=m-1;}
      t.textContent=full.slice(0,lo).replace(/[，、；：\s]+$/,'')+'…';
    });
  }
  var r; window.addEventListener('resize',function(){clearTimeout(r);r=setTimeout(fit,150);});
  if(document.fonts&&document.fonts.ready){document.fonts.ready.then(fit);} fit();
})();
</script>"""


def build_home():
    """首頁（A 版報紙風，編輯 2026-10-30 定案）：頭條＋電子報／新聞／活動、樂評、社群雷達、新唱片＋In memoriam。
    內容從最新一期的單則資料自動取；活動由瀏覽器即時讀 events.json，每天自動更新。"""
    items, composers, labels, features = load()
    shown = sorted([it for it in items if it.get("web") is True], key=sort_key, reverse=True)
    by_id = {it["id"]: it for it in shown}
    issue_files = sorted((json.load(open(f, encoding="utf-8")) for f in glob.glob("issues/*.json")), key=lambda d: d["date"])
    feats = []
    for d in reversed(issue_files):
        feats = [by_id[f] for f in d.get("feature", []) if f in by_id]
        if feats:
            break
    lead = feats[0] if feats else None
    second = feats[1] if len(feats) > 1 else None
    used = {f["id"] for f in feats[:2]}
    nm = lambda it, text: escape(show_name(text, composers, it.get("composers")))

    def pick(t, n):
        rows = [it for it in shown if it["type"] == t and it["id"] not in used][:n]
        used.update(it["id"] for it in rows)
        return rows

    # 第二專題：放在頭條下方填滿左欄（左圖右文）；本期只有一個專題時，改從新聞補一則
    if not second:
        rest = [it for it in shown if it["type"] == "新聞" and it["id"] not in used and first_image(it)]
        second = rest[0] if rest else None
        if second:
            used.add(second["id"])
    second_html = ""
    if second:
        img2 = first_image(second)
        body2 = _plain((second.get("body") or second["summary"]).split("\n\n")[0])
        body2 = body2 if len(body2) <= 150 else body2[:148] + "…"
        pic2 = f'<a href="item/{second["id"]}/"><img src="{escape(img2)}" alt="{escape(second["title"])}" loading="lazy"></a>' if img2 else ""
        second_html = f"""<div class="h-second{'' if img2 else ' noimg'}">{pic2}<div>
<h3 class="h-head2"><a href="item/{second['id']}/">{nm(second, second['title'])}</a></h3>
<p class="h-deck2">{nm(second, second['summary'])}</p>
<p class="h-body2">{nm(second, body2)}</p>
<a class="h-read" href="item/{second['id']}/">閱讀全文 →</a></div></div>"""

    # 頭條
    lead_html = ""
    if lead:
        imgs = [m for m in (lead.get("media") or []) if m["kind"] == "image"][:3]
        pics = "".join(f'<img src="{escape(m["url"])}" alt="{escape(m.get("caption", ""))}" loading="lazy">' for m in imgs)
        credit = "、".join(
            escape(m.get("caption", "")) + (f'（圖：<a href="{escape(m["credit_url"])}">{escape(m["credit"])}</a>）' if m.get("credit_url") else (f'（圖：{escape(m["credit"])}）' if m.get("credit") else ""))
            for m in imgs)
        body = (lead.get("body") or lead["summary"]).split("\n\n")[0]
        lead_html = f"""<article class="h-lead">
<h2 class="h-head"><a href="item/{lead['id']}/">{nm(lead, lead['title'])}</a></h2>
<p class="h-deck">{nm(lead, lead['summary'])}</p>
{f'<div class="h-pics n{len(imgs)}">{pics}</div><div class="h-credit">{credit}</div>' if imgs else ''}
<div class="h-body"><p>{nm(lead, _plain(body))}</p></div>
<a class="h-read" href="item/{lead['id']}/">閱讀全文 →</a>
{second_html}
</article>"""

    # 側欄：電子報、新聞、活動
    nl = sorted(labels.values(), key=lambda x: x["date"], reverse=True)[:2]
    nl_html = "".join(f'<a class="h-row" href="newsletter/{i["slug"]}/"><b>{escape(i["title"])}</b><span>{escape(i["label"])}</span></a>' for i in nl)
    news = pick("新聞", 4)
    news_html = "".join(
        f'<a class="h-row" href="item/{it["id"]}/"><b>{nm(it, it["title"])}</b><span>{escape("・".join(it.get("tags", [])[:1]))}</span></a>'
        for it in news)
    side = f"""<aside class="h-side">
<div class="sec">電子報<a class="more-r" href="newsletter/">各期 →</a></div>{nl_html}
<div class="sec">新聞<a class="more-r" href="category/news/">更多 →</a></div>{news_html}
<div class="sec">近期國內活動</div>
<div id="h-events"><p style="font-size:14px;color:var(--muted)">載入中…</p></div>
<a class="h-ev-more" href="event/">全部場次 →</a>
</aside>"""

    def cover(it, with_note=True):
        img = first_image(it) or ""
        by = f'<span class="by">{nm(it, it["byline"])}</span>' if it.get("byline") else ""
        # 首頁樂評：放完整摘要，文末接「（閱讀全文）」連到單則頁（編輯 2026-10-31 指定）
        # 摘要限三行：由頁面程式依卡片寬度裁字，最後接「（閱讀全文）」（編輯 2026-10-31 指定）
        note = (f'<p class="clamp3"><span class="t">{nm(it, it["summary"])}</span><a class="h-more" href="item/{it["id"]}/">（閱讀全文）</a></p>' if with_note else "")
        return (f'<div class="h-cover"><a href="item/{it["id"]}/"><img src="{escape(img)}" alt="{escape(it["title"])} 專輯封面" loading="lazy">'
                f'<b>{nm(it, it["title"])}</b></a>{by}{note}</div>')

    def rel_lines(it):
        """首頁唱片架：第一行作曲家｜唱片公司，第二行唱片說明（編輯 2026-10-31 指定）。"""
        parts = it["summary"].split("｜")
        label, desc = (parts[0], "｜".join(parts[1:])) if len(parts) > 1 else ("", it["summary"])
        head = "｜".join(x for x in (it.get("byline") or "", label) if x)
        return (f'<span>{nm(it, head)}</span>' if head else "") + (f'<span class="desc">{nm(it, desc)}</span>' if desc else "")

    # 首頁樂評：最新一期 issues/*.json 有 home_reviews 時照編輯指定（編輯 2026-10-31 指定），沒有才取最新四則
    home_rev = next((d["home_reviews"] for d in reversed(issue_files) if d.get("home_reviews")), [])
    reviews = [by_id[r] for r in home_rev if r in by_id and r not in used][:4] or pick("樂評", 4)
    used.update(it["id"] for it in reviews)
    talk = pick("社群", 3)
    rels = pick("發行", 4)
    obits = pick("訃聞", 4)
    talk_html = "".join(
        f'<a class="h-talk" href="item/{it["id"]}/"><b>{nm(it, it["title"])}</b><span>{nm(it, _first_sentence(it["summary"], 70))}</span>'
        f'<small>{escape("、".join(s["name"] for s in it.get("sources", [])[:2]))}</small></a>' for it in talk)
    rel_html = "".join(
        f'<a class="h-rel" href="{escape(item_href(it, "")[0])}"' + (' target="_blank" rel="noopener"' if item_href(it, "")[1] else "") + f'><img src="{escape(first_image(it) or "")}" alt="{escape(it["title"])} 專輯封面" loading="lazy">'
        f'<span><b>{nm(it, it["title"])}</b>{rel_lines(it)}</span></a>' for it in rels)
    obit_html = "".join(
        f'<a class="h-obit" href="item/{it["id"]}/"><b>{nm(it, it["title"].split("：")[0])}</b><span>{nm(it, _first_sentence(it["summary"], 40))}</span></a>' for it in obits)

    main_html = f"""<div class="h-grid">
{lead_html}
{side}
</div>
{f'<section class="band"><div class="sec">樂評<a class="more-r" href="category/reviews/">全部樂評 →</a></div><div class="h-four">' + "".join(cover(it) for it in reviews) + '</div></section>' if reviews else ''}
{f'<section class="band"><div class="sec">社群雷達<a class="more-r" href="category/community/">更多 →</a></div><div class="h-three">' + talk_html + '</div></section>' if talk else ''}
<section class="band h-two">
<div><div class="sec">唱片架/試聽<a class="more-r" href="category/releases/">更多 →</a></div>{rel_html}</div>
<div><div class="sec">In memoriam<a class="more-r" href="category/obituaries/">更多 →</a></div>{obit_html}</div>
</section>
{HOME_EVENTS_JS}
{CLAMP_JS}"""
    latest = nl[0] if nl else {}
    html = page("Cue Sheet｜中文電影配樂電子報", latest.get("editor_note", "給配樂迷的電影音樂刊物"), SITE, "home",
                ("", main_html), latest.get("image"), wide=True)
    open("index.html", "w", encoding="utf-8").write(html.replace("</style>", HOME_CSS + "</style>", 1))
    print(f"首頁已產生；頭條：{lead['title'] if lead else '（無）'}")


if __name__ == "__main__":
    main()

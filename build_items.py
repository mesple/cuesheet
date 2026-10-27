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
    ("社群", "community", "Community", "論壇與社論裡的熱門話題"),
]
SLUG = {t: s for t, s, _, _ in TYPES}

EXTRA_CSS = """
.crumb{font-size:13px;color:var(--muted);margin:22px 0 0}
.crumb a{color:var(--soft);text-decoration:none}
.crumb a:hover{color:var(--teal)}
.pills{margin:14px 0 0;display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.pill{display:inline-block;border:1px solid var(--teal);color:var(--teal);font-size:12px;padding:1px 8px;line-height:1.6;text-decoration:none}
.pill.solid{background:var(--teal);color:var(--paper)}
.pill.plain{border-color:var(--line);color:var(--soft)}
h2.item-title{font-family:Georgia,"Noto Serif TC",serif;font-size:32px;line-height:1.3;margin:10px 0 6px;letter-spacing:-.01em}
.byline{font-size:15px;color:var(--soft);margin:0 0 4px}
.dateline{font-size:13px;color:var(--muted);margin:0 0 18px}
.deck{font-size:18px;line-height:1.6;color:var(--soft);margin:0 0 8px}
.lead{font-size:18px;line-height:1.85;margin:0 0 18px}
.body{font-size:16px;line-height:1.9}
.body h2{font-family:Georgia,"Noto Serif TC",serif;font-size:21px;margin:30px 0 8px}
.body ul{padding-left:22px}
.body li{margin:4px 0}
.media{display:grid;gap:14px;margin:6px 0 22px}
.media.multi{grid-template-columns:repeat(3,minmax(0,1fr))}
.media figure{margin:0}
.media img{display:block;width:100%;height:auto;border:1px solid var(--line);background:var(--paper)}
.media.single img{max-width:360px}
.media.single.wide img{max-width:100%}
.media figcaption{font-size:12px;color:var(--muted);margin-top:4px;line-height:1.5}
.yt{display:block;max-width:480px;text-decoration:none;color:#FBFAF6}
.yt span{display:block;background:#28251D;color:#FBFAF6;font-size:13px;padding:6px 10px}
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
.items .thumb img{display:block;width:88px;height:auto;border:1px solid var(--line)}
.items .meta{font-size:12px;color:var(--muted)}
.items .meta .pill{font-size:11px;padding:0 6px;margin-right:4px}
.items h3{font-size:17px;line-height:1.45;margin:4px 0 2px}
.items h3 a{color:var(--ink);text-decoration:none}
.items h3 a:hover{color:var(--teal)}
.items .by{font-size:13px;color:var(--soft)}
.items p{font-size:14px;line-height:1.7;color:var(--soft);margin:4px 0 0}
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
        figs.append(f"<figure>{img}" + (f'<figcaption>{"　".join(cap)}</figcaption>' if cap else "") + "</figure>")
    cls = "multi" if len(figs) > 1 else "single"
    if len(figs) == 1 and it["type"] in ("新聞",) and media[0]["kind"] == "image":
        cls += " wide"
    return f'<div class="media {cls}">' + "".join(figs) + "</div>"


def first_image(it):
    for m in it.get("media") or []:
        if m["kind"] == "youtube":
            return yt_thumb(m["id"])
        return m["url"]
    return None


def issue_label(labels, slug):
    return labels.get(slug, {}).get("label", slug)


def item_page(it, by_id, composers, labels, features):
    title = it["title"]
    codes = it.get("composers", [])
    slug = SLUG[it["type"]]
    pills = [f'<a class="pill solid" href="../../category/{slug}/">{it["type"]}</a>']
    for t in it.get("tags", []):
        pills.append(f'<a class="pill" href="../../category/{slug}/?tag={escape(t)}">{escape(t)}</a>')
    pills.append(f'<span class="pill plain">{escape(it["region"])}</span>')
    if it["id"] in features:
        pills.append(f'<a class="pill plain" href="../../newsletter/{features[it["id"]]}/">{escape(issue_label(labels, features[it["id"]]))}本月專題</a>')
    byline = ""
    if it.get("byline"):
        byline = f'<p class="byline">{escape(show_name(it["byline"], composers, codes))}</p>'
    date = fmt_date(it)
    dateline = f'<p class="dateline">{date + "　·　" if date else ""}首次刊出：<a href="../../newsletter/{it["issue"]}/">Cue Sheet {escape(issue_label(labels, it["issue"]))}</a></p>'
    summary = show_name(it["summary"], composers, codes)
    body = ""
    if it.get("body"):
        body = '<div class="body">' + markdown.markdown(show_name(it["body"], composers, codes)) + "</div>"
    lead = f'<p class="lead">{escape(summary)}</p>'
    deck = ""
    top_media, more_media = media_html(it, title), ""
    if it.get("body"):
        # 長文：摘要當副標，第一張圖放上面，其餘圖放文末
        deck, lead = f'<p class="deck">{escape(summary)}</p>', ""
        if len(it.get("media") or []) > 1:
            rest = dict(it, media=it["media"][1:])
            top_media = media_html(dict(it, media=it["media"][:1]), title)
            more_media = '<div class="sec">圖片<span>Gallery</span></div>' + media_html(rest, title)
    boxes = []
    if codes:
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
    rel = [by_id[r] for r in it.get("related", []) if r in by_id]
    rel_html = ""
    if rel:
        cards = "".join(f'<a href="../{r["id"]}/"><small>{r["type"]}</small><b>{escape(r["title"])}</b></a>' for r in rel)
        rel_html = f'<div class="sec">相關內容<span>Related</span></div><div class="rel">{cards}</div>'
    crumb = f'<p class="crumb"><a href="../../category/">分類</a> › <a href="../../category/{slug}/">{it["type"]}</a></p>'
    article = f"""{crumb}
<article>
<div class="pills">{"".join(pills)}</div>
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
    html = page(f"{title}｜Cue Sheet", desc, f"{SITE}item/{it['id']}/", "category", ("", article),
                depth=2, kicker=f"Cue Sheet · {dict((t, e) for t, _, e, _ in TYPES)[it['type']]}")
    img = first_image(it)
    if img:
        html = html.replace('<meta property="og:locale"', f'<meta property="og:image" content="{img}">\n<meta property="og:locale"', 1)
    html = html.replace('<meta property="og:type" content="website">', '<meta property="og:type" content="article">')
    return html.replace("</style>", EXTRA_CSS + "</style>", 1)


def row_html(it, composers, labels, depth):
    up = "../" * depth
    img = first_image(it)
    thumb = f'<a class="thumb" href="{up}item/{it["id"]}/"><img src="{img}" alt="" loading="lazy"></a>' if img else ""
    tags = "".join(f'<span class="pill">{escape(t)}</span>' for t in it.get("tags", []))
    date = fmt_date(it) or f'{escape(issue_label(labels, it["issue"]))}'
    by = f'<div class="by">{escape(show_name(it["byline"], composers, it.get("composers")))}</div>' if it.get("byline") else ""
    s = show_name(it["summary"], composers, it.get("composers"))
    s = s if len(s) <= 90 else s[:88] + "…"
    data_tags = escape(" ".join(it.get("tags", [])))
    return f"""<div class="it{'' if img else ' noimg'}" data-tags="{data_tags}">{thumb}<div>
<div class="meta">{tags}{date}　·　{escape(it["region"])}</div>
<h3><a href="{up}item/{it["id"]}/">{escape(it["title"])}</a></h3>{by}
<p>{escape(s)}</p></div></div>"""


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


def main():
    items, composers, labels, features = load()
    by_id = {it["id"]: it for it in items if it.get("web") is True}
    shown = sorted(by_id.values(), key=sort_key, reverse=True)

    if os.path.isdir("item"):
        shutil.rmtree("item")
    for it in shown:
        os.makedirs(f"item/{it['id']}", exist_ok=True)
        open(f"item/{it['id']}/index.html", "w", encoding="utf-8").write(item_page(it, by_id, composers, labels, features))

    # 各類型列表
    cards = []
    for t, slug, en, desc in TYPES:
        rows = [it for it in shown if it["type"] == t]
        if not rows:
            continue
        filters = ""
        if t == "新聞":
            tags = [x for x in ("獎項", "音樂活動", "新案", "新片", "其他") if any(x in it.get("tags", []) for it in rows)]
            filters = '<div class="filters"><button type="button" data-tag="" aria-pressed="true">全部</button>' + "".join(
                f'<button type="button" data-tag="{x}" aria-pressed="false">{x}</button>' for x in tags) + "</div>"
        main_html = (f'<p class="crumb"><a href="../">分類</a> › {t}</p>'
                     f'<div class="sec">{t}<span>{en}</span></div>{filters}<div class="items">'
                     + "\n".join(row_html(it, composers, labels, 2) for it in rows) + "</div>"
                     + (FILTER_JS if filters else ""))
        os.makedirs(f"category/{slug}", exist_ok=True)
        html = page(f"{t}｜Cue Sheet", f"Cue Sheet 的{t}：{desc}。", f"{SITE}category/{slug}/", "category",
                    (f'<p class="sub">{desc}，共 {len(rows)} 則，依日期由新到舊。</p>', main_html), depth=2,
                    kicker=f"Cue Sheet · {en}")
        open(f"category/{slug}/index.html", "w", encoding="utf-8").write(html.replace("</style>", EXTRA_CSS + "</style>", 1))
        latest = "".join(f'<li><a href="{slug}/../../item/{it["id"]}/">{escape(it["title"])}</a></li>' for it in rows[:3])
        latest = latest.replace(f'{slug}/../../', "../")
        cards.append(f'<div class="type-card"><h3><a href="{slug}/">{t}</a><small>{len(rows)} 則</small></h3><p>{desc}</p><ul>{latest}</ul></div>')

    idx = f'<div class="sec">依類型瀏覽<span>Browse</span></div><div class="types">{"".join(cards)}</div>'
    html = page("分類｜Cue Sheet", "依類型瀏覽 Cue Sheet 刊出的新聞、樂評、新唱片、訪談、試聽、訃聞與社群話題。", f"{SITE}category/", "category",
                (f'<p class="sub">電子報刊出的每一則，依類型整理。共 {len(shown)} 則。</p>', idx), depth=1)
    open("category/index.html", "w", encoding="utf-8").write(html.replace("</style>", EXTRA_CSS + "</style>", 1))

    # 作曲家頁
    if os.path.isdir("composer"):
        shutil.rmtree("composer")
    by_c = {}
    for it in shown:
        for c in it.get("composers", []):
            by_c.setdefault(c, []).append(it)
    for c, rows in by_c.items():
        info = composers[c]
        other = [n for n in [info.get("name")] + info.get("aliases", []) if n and n != info["display"]]
        alias = f'<p class="alias">{escape("、".join(dict.fromkeys(other)))}</p>' if other else ""
        main_html = (f'<p class="crumb"><a href="../">作曲家</a> › {escape(info["display"])}</p>'
                     f'<h2 class="item-title">{escape(info["display"])}</h2>{alias}'
                     f'<div class="sec">Cue Sheet 刊出的相關內容<span>{len(rows)} 則</span></div><div class="items">'
                     + "\n".join(row_html(it, composers, labels, 2) for it in rows) + "</div>")
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
                (f'<p class="sub">點作曲家，看 Cue Sheet 刊過的所有相關內容。共 {len(by_c)} 位，數字是則數。</p>', idx), depth=1,
                kicker="Cue Sheet · Composers")
    open("composer/index.html", "w", encoding="utf-8").write(html.replace("</style>", EXTRA_CSS + "</style>", 1))
    print(f"作曲家頁 {len(by_c)} 位（兩則以上 {len(multi)} 位）")

    hidden = [it for it in items if it.get("web") is not True]
    print(f"單則頁 {len(shown)} 則；未上網站 {len(hidden)} 則：" + "、".join(f'{it["id"]}（{"待定" if it.get("web") is None else "不上"}）' for it in hidden))


if __name__ == "__main__":
    main()

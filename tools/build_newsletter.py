"""Cue Sheet 電子報產生器：版型定在這支程式裡，每期只準備資料，不手排 HTML（編輯 2026-11-05 指定）。

版型以 2026 年 10 月號試刊為準，規格見 docs/版面規範.md。改版型要先改規範、經編輯同意，再改這支程式。

資料：
  issues/<slug>.json   刊頭、編者的話、各欄放哪幾則、週末cue一下、頁尾
  items/*.json         單則內容（與網站共用；欄位見 docs/版面規範.md「資料欄位」）

用法：
  python tools/build_newsletter.py 2026-11-collector
      → out/cue_sheet_2026-11-collector.html（電子報版，匯入 MailerLite）
      → newsletter/2026-11-collector/index.html（網站版，由 tools/web_version.py 轉出）
  python tools/build_newsletter.py 2026-11-collector --email-only    只產生電子報版
  python tools/build_newsletter.py --template collector|news         產生空白版型到 templates/
"""
import glob
import html
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://mesple.github.io/cuesheet/"
MAX_KB = 90   # Gmail 約 102 KB 截斷，電子報控制在 90 KB 內

# ---------------------------------------------------------------- 設計值（與 docs/版面規範.md 一致）
FONT = "'PingFang TC','Noto Sans TC','Microsoft JhengHei',Arial,sans-serif"
SERIF = "Georgia,serif"
C = dict(
    page_bg="#F2F0EA", paper="#FBFAF6", frame="#D4D1CA", ink="#28251D", body="#55534C", muted="#7A7974",
    link="#01696F", feature_bg="#F7F4EC", dark_bg="#28251D", dark_title="#FBFAF6", dark_text="#E8E6DF",
    teal_bg="#01696F", teal_title="#FFFFFF", teal_text="#E6F2F1", weblink="#8A877E",
)
W = dict(page=760, banner=678, review_cover=160, shelf_cover=160, shelf_card=172, bite_thumb=222,
         interview_media=270, interview_cover=200, eurasia_img=190, portrait=108)
L = f"color:{C['link']};"
EDITION = {"collector": "深度聆聽版", "news": "配樂新訊版", "special": "特刊"}
MONTHS = "JANUARY FEBRUARY MARCH APRIL MAY JUNE JULY AUGUST SEPTEMBER OCTOBER NOVEMBER DECEMBER".split()
# 播放鍵用 CSS 三角形，不用「▶」（Gmail 會換成 emoji，編輯 2026-11-03 指定）
TRI_W = '<span style="display:inline-block;border-left:7px solid #FBFAF6;border-top:4px solid transparent;border-bottom:4px solid transparent;margin-right:6px;vertical-align:middle"></span>'
TRI_G = '<span style="display:inline-block;border-left:6px solid #7A7974;border-top:3px solid transparent;border-bottom:3px solid transparent;margin-right:4px"></span>'

esc = lambda s: html.escape(s or "", quote=True)


def a(url, text):
    return f'<a href="{esc(url)}" style="{L}">{text}</a>'


def src_list(item, sep="、"):
    pairs = [(s["name"], s["url"]) for s in item.get("sources", [])]
    if item.get("spotify") and not any("open.spotify.com/album" in u for _, u in pairs):
        pairs.append(("Spotify", item["spotify"]))
    return sep.join(a(u, esc(n)) for n, u in pairs)


def inline(md):
    """單則文字的行內標記：**粗體**、[文字](網址)。其餘照原文跳脫。"""
    t = esc(md)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\[(.+?)\]\((https?://[^)\s]+)\)", lambda m: a(html.unescape(m.group(2)), m.group(1)), t)
    return t


def md_blocks(md, size=16, lh=1.85):
    """body（Markdown）→ 電子報 inline style：段落、## 小標、- 清單、| 表格。"""
    out = []
    for blk in re.split(r"\n\s*\n", (md or "").strip()):
        lines = blk.strip().split("\n")
        if blk.startswith("## "):
            out.append(f'<div style="font-family:{SERIF};font-size:22px;font-weight:700;line-height:1.35;margin-top:20px;">{inline(blk[3:].strip())}</div>')
        elif all(l.strip().startswith("|") for l in lines) and len(lines) >= 2:
            rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in lines if not re.match(r"^\s*\|[\s:|-]+\|\s*$", l)]
            head, body = rows[0], rows[1:]
            t = f'<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:8px;font-size:14px;line-height:1.6;table-layout:fixed;"><tr>'
            t += "".join(f'<td style="padding:7px 8px 7px 0;border-bottom:1px solid {C["ink"]};font-weight:700;vertical-align:top;">{inline(h)}</td>' for h in head) + "</tr>"
            for k, r in enumerate(body):
                bd = "" if k == len(body) - 1 else f'border-bottom:1px dotted {C["frame"]};'
                t += "<tr>" + "".join(f'<td style="padding:7px 8px 7px 0;{bd}vertical-align:top;word-break:break-word;{"font-weight:700;" if j == 0 else ""}">{inline(c)}</td>' for j, c in enumerate(r)) + "</tr>"
            out.append(t + "</table>")
        elif all(l.strip().startswith("- ") for l in lines):
            lis = "".join(f'<li style="margin:0 0 6px;">{inline(l.strip()[2:])}</li>' for l in lines)
            out.append(f'<ul style="margin:12px 0 0;padding-left:22px;font-size:{size - 1}px;line-height:1.7;">{lis}</ul>')
        else:
            out.append(f'<div style="font-size:{size}px;line-height:{lh};margin-top:12px;">{inline(blk.strip())}</div>')
    return "".join(out)


def split_title(t):
    for sep in (" — ", "—"):
        if sep in t:
            x, y = t.split(sep, 1)
            return x.strip(), y.strip()
    return t, ""


def first_media(item, kind=None):
    for m in item.get("media") or []:
        if kind is None or m["kind"] == kind:
            return m
    return None


def img_credit(m):
    if m.get("hosting") == "spotify":
        return "Spotify"
    return m.get("credit") or ""


# ---------------------------------------------------------------- 共用元件
def row(inner, pad="8px 28px 4px 28px"):
    return f'<tr><td class="pad" style="padding:{pad};">{inner}</td></tr>'


def section_head(zh, en, first=False):
    bt = "" if first else f"padding-top:8px;border-top:1px solid {C['ink']};"
    return row(f'<div style="margin:0 0 14px;{bt}font-size:13px;font-weight:700;letter-spacing:.08em;line-height:1.4;">{zh} '
               f'<span style="display:inline-block;font-size:11px;font-weight:700;letter-spacing:.14em;color:{C["muted"]};margin-left:8px;">{en}</span></div>',
               "24px 28px 4px 28px")


def yt_box(vid, alt, w):
    return (f'<a href="https://www.youtube.com/watch?v={vid}" style="display:block;text-decoration:none;color:#FBFAF6;">'
            f'<img src="https://img.youtube.com/vi/{vid}/mqdefault.jpg" alt="{esc(alt)} YouTube 預覽" width="{w}" style="display:block;width:100%;max-width:{w}px;height:auto;border:1px solid {C["frame"]};background:#28251D;">'
            f'<span style="display:block;background:#28251D;color:#FBFAF6;font-size:12px;padding:5px 8px;max-width:{w}px;box-sizing:border-box;">{TRI_W}YouTube 觀看</span></a>')


def caption(text):
    return f'<div style="font-size:11px;line-height:1.5;color:{C["muted"]};margin-top:4px;">{text}</div>'


def placeholder(w, h, text):
    """空白版型用的灰框。"""
    return (f'<div style="width:100%;max-width:{w}px;height:{h}px;box-sizing:border-box;border:1px dashed #C4C0B4;background:#F1EFE8;'
            f'display:table;text-align:center;"><div style="display:table-cell;vertical-align:middle;font-size:11px;line-height:1.5;color:#9C988C;padding:4px;">{text}</div></div>')


# ---------------------------------------------------------------- 各欄
def masthead(issue, email):
    d = issue["date"]
    kicker = issue.get("kicker") or f'FILM MUSIC NEWSLETTER · {MONTHS[int(d[5:7]) - 1]} {d[:4]} · {EDITION.get(issue["edition"], "")}'
    webl = ""
    if email:
        webl = (f'<td class="webl" valign="top" align="right" style="font-size:12px;color:{C["weblink"]};padding:0;white-space:nowrap;">'
                f'<a href="{SITE}newsletter/{issue["issue"]}/" style="color:{C["weblink"]};">沒看到完整內容？請到網頁版</a></td>')
    note = issue.get("editor_note") or "本期重點待編輯撰寫"
    return (f'<tr><td class="pad" style="padding:28px 28px 18px 28px;border-bottom:5px solid {C["ink"]};">'
            f'<table class="kick" width="100%" cellspacing="0" cellpadding="0" border="0"><tr><td valign="top" style="font-size:12px;letter-spacing:.16em;color:{C["muted"]};padding:0 12px 0 0;">{esc(kicker)}</td>{webl}</tr></table>'
            f'<div class="mast" style="margin:8px 0 0;font-family:{SERIF};font-size:56px;line-height:.95;font-weight:700;letter-spacing:-.04em;"><a href="{SITE}" style="color:{C["ink"]};text-decoration:none;">Cue Sheet</a></div>'
            f'<div style="margin:14px 0 0;font-size:15px;line-height:1.75;color:{C["body"]};">{esc(note)}</div></td></tr>')


def feature(items, tpl=False):
    if not items:
        return row(f'<div style="font-size:15px;color:{C["muted"]};">本期專題待編輯選定</div>', "0 28px 6px 28px")
    out = []
    for it in items:
        parts = []
        m = first_media(it, "image")
        if m and tpl:
            parts.append('<div style="margin:0 0 16px;">' + placeholder(W["banner"], 226, f'主圖　寬 {W["banner"]}px、高依原圖（寬幅組圖建議 1200×400）<br>放 GitHub images/YYYY-MM/') + "</div>")
            parts.append(f'<div style="font-size:11px;line-height:1.5;color:{C["muted"]};margin:-10px 0 16px;">圖說。圖片來源：○○</div>')
        elif m:
            parts.append(f'<img src="{esc(m["url"])}" alt="{esc(m.get("caption") or it["title"])}" width="{W["banner"]}" style="display:block;width:100%;max-width:{W["banner"]}px;height:auto;border:0;margin:0 0 16px;background:#3A372F;">')
            cap = esc(m.get("caption", ""))
            cr = esc(img_credit(m))
            if m.get("credit_url"):
                cr = a(m["credit_url"], cr)
            parts.append(f'<div style="font-size:11px;line-height:1.5;color:{C["muted"]};margin:-10px 0 16px;">{cap}{"。圖片來源：" + cr if cr else ""}</div>')
        parts.append(f'<div class="big" style="font-family:{SERIF};font-size:34px;font-weight:700;line-height:1.2;">{esc(it["title"])}</div>')
        if it.get("deck"):
            parts.append(f'<div style="font-size:16px;line-height:1.6;color:{C["muted"]};margin-top:6px;">{esc(it["deck"])}</div>')
        parts.append(md_blocks(it.get("body") or it["summary"]))
        if it.get("sources"):
            parts.append(f'<div style="font-size:12px;margin-top:14px;">來源：{src_list(it)}</div>')
        out.append(row(f'<div style="background:{C["feature_bg"]};border:1px solid {C["frame"]};padding:20px;">' + "".join(parts) + "</div>", "0 28px 6px 28px"))
    return "".join(out)


def prime_picks(items, tpl=False):
    out = []
    for it in items:
        m = first_media(it, "image")
        link = it.get("spotify") or (m or {}).get("link") or (it["sources"][0]["url"] if it.get("sources") else "#")
        if tpl:
            cover = placeholder(W["review_cover"], W["review_cover"], f'專輯封面<br>寬 {W["review_cover"]}px<br>高依原圖')
        elif m:
            cover = f'<a href="{esc(link)}"><img src="{esc(m["url"])}" width="{W["review_cover"]}" alt="{esc(it["title"])}" style="display:block;width:{W["review_cover"]}px;height:auto;border:1px solid {C["frame"]};"></a>'
        else:
            cover = ""
        cap = caption(f'圖片來源：{esc(img_credit(m))}') if (m and img_credit(m)) or tpl else ""
        text = it.get("body") or it["summary"]
        out.append(row(
            f'<table width="100%" cellspacing="0" cellpadding="0" border="0"><tr>'
            + (f'<td class="stk" width="{W["review_cover"]}" valign="top" style="width:{W["review_cover"]}px;padding:4px 16px 0 0;">{cover}{cap}</td>' if (cover or tpl) else "")
            + f'<td class="stk" valign="top" style="font-size:15px;line-height:1.75;"><div style="font-family:{SERIF};font-size:19px;font-weight:700;line-height:1.35;">{esc(it["title"])}</div>'
            f'<div style="font-size:13px;line-height:1.6;color:{C["muted"]};margin-top:2px;">{esc(it.get("byline", ""))}</div>'
            f'<div style="margin-top:6px;">{inline(text)}</div><div style="font-size:12px;margin-top:6px;">來源：{src_list(it)}</div></td></tr></table>',
            "14px 28px 4px 28px"))
    return "".join(out)


def record_shelf(items, tpl=False):
    cards = []
    for it in items:
        m = first_media(it, "image")
        link = it.get("spotify") or (it["sources"][0]["url"] if it.get("sources") else "#")
        if tpl:
            img = placeholder(W["shelf_cover"], W["shelf_cover"], f'封面<br>寬 {W["shelf_cover"]}px')
        elif m:
            img = f'<a href="{esc(link)}"><img src="{esc(m["url"])}" alt="{esc(it["title"])}" width="{W["shelf_cover"]}" style="display:block;width:100%;max-width:{W["shelf_cover"]}px;height:auto;border:1px solid {C["frame"]};"></a>'
        else:
            img = placeholder(W["shelf_cover"], W["shelf_cover"], "封面待補")
        cr = img_credit(m) if m else ("Spotify／廠牌" if tpl else "")
        line = "｜".join(x for x in (it.get("byline"), it["summary"]) if x)
        cards.append(f'<div style="display:inline-block;vertical-align:top;width:100%;max-width:{W["shelf_card"]}px;box-sizing:border-box;padding:0 12px 18px 0;font-size:13px;line-height:1.6;">'
                     f'{img}<div style="font-size:10px;color:{C["muted"]};margin-top:3px;">圖片來源：{esc(cr)}</div>'
                     f'<div style="font-size:16px;font-weight:700;margin-top:8px;line-height:1.4;">{esc(it["title"])}</div>'
                     f'<div style="color:{C["body"]};">{inline(line)}</div>'
                     f'<div style="font-size:11px;">{src_list(it, " · ")}</div></div>')
    return row('<div style="font-size:0;line-height:0;">' + "".join(cards) + "</div>")


def take_a_bite(items, tpl=False):
    out, cells = [], []
    for k, it in enumerate(items):
        m = first_media(it, "youtube")
        pad = "0 8px 18px 0" if k % 3 == 0 else ("0 0 18px 8px" if k % 3 == 2 else "0 8px 18px 8px")
        box = placeholder(W["bite_thumb"], 125, f'YouTube 縮圖<br>寬 {W["bite_thumb"]}px（16:9）') if tpl else (yt_box(m["id"], it["title"], W["bite_thumb"]) if m else "")
        ch = (m or {}).get("caption", "") if not tpl else "上傳頻道名"
        cells.append(f'<td class="stk" width="33.33%" valign="top" style="padding:{pad};font-size:13px;line-height:1.6;">{box}'
                     + (caption(f"圖片來源：YouTube（{esc(ch)}）") if ch else "")
                     + f'<div style="margin-top:8px;font-size:14px;line-height:1.4;font-weight:700;">{esc(it["title"])}</div>'
                     f'<div style="font-size:12px;color:{C["muted"]};">{esc(it.get("byline", ""))}</div>'
                     f'<div style="margin-top:4px;">{inline(it["summary"])}（{src_list(it)}）</div></td>')
        if len(cells) == 3 or k == len(items) - 1:
            while len(cells) < 3:
                cells.append('<td class="stk" width="33.33%"></td>')
            out.append(row('<table width="100%" cellspacing="0" cellpadding="0" border="0"><tr>' + "".join(cells) + "</tr></table>"))
            cells = []
    return "".join(out)


def interviews(items, tpl=False):
    out = []
    for it in items:
        m = first_media(it)
        if tpl:
            media = placeholder(W["interview_media"], 152, f'影片截圖 寬 {W["interview_media"]}px<br>或封面／照片 寬 {W["interview_cover"]}px')
            media += caption("圖片來源：YouTube（頻道名）／Spotify")
        elif m and m["kind"] == "youtube":
            media = yt_box(m["id"], it["title"], W["interview_media"]) + caption(f'圖片來源：YouTube（{esc(m.get("caption", ""))}）')
        elif m:
            link = m.get("link") or it.get("spotify") or "#"
            lab = "點圖到 Spotify 聽｜圖片來源：Spotify" if m.get("hosting") == "spotify" or "spotify" in link else f"圖片來源：{esc(img_credit(m) or m.get('caption', ''))}"
            media = (f'<a href="{esc(link)}"><img src="{esc(m["url"])}" alt="{esc(it["title"])}" width="{W["interview_cover"]}" style="display:block;width:100%;max-width:{W["interview_cover"]}px;height:auto;border:1px solid {C["frame"]};"></a>'
                     + caption(f"{TRI_G}{lab}" if "Spotify 聽" in lab else lab))
        else:
            media = ""
        out.append(row(
            f'<div style="font-size:0;line-height:0;border-top:1px solid {C["frame"]};padding-top:14px;">'
            f'<div class="col-img" style="display:inline-block;vertical-align:top;width:100%;max-width:286px;box-sizing:border-box;padding:0 16px 12px 0;font-size:14px;line-height:1.5;">{media}</div>'
            f'<div class="col-txt" style="display:inline-block;vertical-align:top;width:100%;max-width:390px;font-size:14px;line-height:1.75;">'
            f'<div style="font-family:{SERIF};font-size:19px;font-weight:700;line-height:1.35;">{esc(it["title"])}</div>'
            f'<div style="font-size:14px;line-height:1.85;margin-top:8px;">{inline(it.get("body") or it["summary"])}</div>'
            f'<div style="font-size:12px;margin-top:6px;margin-bottom:12px;">來源：{src_list(it)}</div></div></div>',
            "4px 28px 4px 28px"))
    return "".join(out)


def news_flash(items):
    if not items:
        return ""
    half = (len(items) + 1) // 2
    def ol(chunk, start):
        lis = "".join(f'<li style="margin-bottom:10px;"><strong>{esc(it["title"])}：</strong>{inline(it["summary"])}（{src_list(it)}）</li>' for it in chunk)
        return f'<ol start="{start}" style="margin:0;padding-left:22px;font-size:14px;line-height:1.7;">{lis}</ol>'
    return row(f'<table width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;"><tr>'
               f'<td class="stk" width="50%" valign="top" style="padding:0 10px 0 0;">{ol(items[:half], 1)}</td>'
               f'<td class="stk" width="50%" valign="top" style="padding:0 0 0 10px;border-left:1px solid {C["frame"]};">{ol(items[half:], half + 1)}</td></tr></table>')


def community(items):
    ps = "".join(f'<p style="margin:0 0 12px;font-size:15px;line-height:1.75;"><strong>{esc(it["title"])}</strong>{inline(it["summary"])}（{src_list(it)}）</p>' for it in items)
    return row(ps)


def eurasia(heads, others, tpl=False):
    out = []
    for it in heads:
        out.append(f'<div style="font-family:{SERIF};font-size:22px;font-weight:700;line-height:1.35;margin-top:20px;">{esc(it["title"])}</div>')
        m = first_media(it, "image")
        text = inline(it.get("body") or it["summary"]) + f'（{src_list(it)}）'
        if m:
            im = placeholder(W["eurasia_img"], 120, f'附圖 寬 {W["eurasia_img"]}px') if tpl else \
                f'<img src="{esc(m["url"])}" alt="{esc(m.get("caption", ""))}" width="{W["eurasia_img"]}" style="display:block;width:100%;max-width:{W["eurasia_img"]}px;height:auto;border:1px solid {C["frame"]};">'
            cr = "圖：○○（來源）" if tpl else f'圖：{esc(m.get("caption", ""))}（{a(m["credit_url"], esc(m.get("credit", ""))) if m.get("credit_url") else esc(m.get("credit", ""))}）'
            out.append(f'<div style="font-size:0;line-height:0;border-top:1px solid {C["frame"]};padding-top:14px;margin-bottom:6px;">'
                       f'<div style="display:inline-block;vertical-align:top;width:100%;max-width:206px;box-sizing:border-box;padding:0 16px 12px 0;font-size:14px;line-height:1.5;">{im}'
                       f'<div style="margin-top:4px;font-size:11px;line-height:1.4;color:{C["muted"]};">{cr}</div></div>'
                       f'<div style="display:inline-block;vertical-align:top;width:100%;max-width:466px;font-size:14px;line-height:1.75;">{text}</div></div>')
        else:
            out.append(f'<div style="font-size:15px;line-height:1.75;margin-top:6px;">{inline(it.get("body") or it["summary"])}</div>'
                       f'<div style="font-size:12px;margin-top:6px;">來源：{src_list(it)}</div>')
    if others:
        lis = "".join(f'<li style="margin:0 0 10px;"><strong>{esc(it["title"])}：</strong>{inline(it["summary"])}（{src_list(it)}）</li>' for it in others)
        out.append(f'<div style="font-family:{SERIF};font-size:22px;font-weight:700;line-height:1.35;margin-top:20px;">其他歐亞動態</div>'
                   f'<ol style="margin:8px 0 8px;padding-left:22px;font-size:14px;line-height:1.7;">{lis}</ol>')
    return row("".join(out))


def memoriam(items, briefs, tpl=False):
    if not items and not briefs:
        return row(f'<div style="font-size:15px;line-height:1.75;color:{C["body"]};">本期平安。願音樂永存，精神不朽。</div>')
    out = []
    for it in items:
        m = first_media(it, "image")
        text = f'<strong>{esc(it["title"])}。</strong>{inline(it.get("body") or it["summary"])}（{src_list(it)}）'
        if m:
            im = placeholder(W["portrait"], 140, "肖像 108px 寬<br>自由授權") if tpl else \
                f'<img src="{esc(m["url"])}" alt="{esc(it["title"])} 肖像" width="{W["portrait"]}" style="display:block;width:100%;max-width:{W["portrait"]}px;height:auto;border:1px solid {C["frame"]};filter:grayscale(100%);">'
            cr = "攝影者 · 授權 · Wikimedia Commons" if tpl else (esc(m.get("credit", "")) + (f' · {a(m["credit_url"], esc(m.get("license", "授權")))}' if m.get("credit_url") else "") + " · Wikimedia Commons")
            out.append(f'<table width="100%" cellspacing="0" cellpadding="0" border="0" style="border-top:1px solid {C["frame"]};margin-bottom:6px;"><tr>'
                       f'<td width="{W["portrait"]}" valign="top" style="width:{W["portrait"]}px;padding:14px 14px 12px 0;">{im}<div style="margin-top:4px;font-size:11px;line-height:1.4;color:{C["muted"]};">{cr}</div></td>'
                       f'<td valign="top" style="padding:14px 0 12px 0;font-size:15px;line-height:1.75;">{text}</td></tr></table>')
        else:
            out.append(f'<div style="border-top:1px solid {C["frame"]};padding:14px 0 12px;font-size:15px;line-height:1.75;">{text}</div>')
    if briefs:
        bs = "；".join(f'{inline(it["summary"])}（{src_list(it)}）' for it in briefs)
        out.append(f'<p style="margin:10px 0 0;padding-top:12px;border-top:1px solid {C["frame"]};font-size:14px;line-height:1.75;color:{C["body"]};">同期辭世者另有：{bs}。</p>')
    return row("".join(out))


def weekend(w):
    play = w.get("playlist_text") or "本週末播放清單待編輯撰寫"
    nxt = "<br>".join("· " + esc(x) for x in w.get("next", []))
    return row(f'<div style="background:{C["dark_bg"]};color:{C["dark_title"]};padding:20px;"><div style="font-size:16px;font-weight:700;margin-bottom:6px;color:{C["dark_title"]};">本週末播放清單</div>'
               f'<div style="font-size:15px;line-height:1.8;color:{C["dark_text"]};">{inline(play)}</div></div>'
               f'<div style="background:{C["teal_bg"]};color:{C["teal_title"]};padding:20px;margin-top:10px;"><div style="font-size:16px;font-weight:700;margin-bottom:6px;color:{C["teal_title"]};">下月預告</div>'
               f'<div style="font-size:15px;line-height:1.8;color:{C["teal_text"]};">{nxt}</div></div>')


def events(issue):
    """近期國內電影音樂活動（精簡版）：由 build_section.py 從 events.json、manual_events.json 產生，不手寫。"""
    sys.path.insert(0, ROOT)
    import build_section as bs
    from datetime import datetime
    evs = json.load(open(os.path.join(ROOT, "events.json"), encoding="utf-8"))["events"]
    mp = os.path.join(ROOT, "manual_events.json")
    if os.path.exists(mp):
        evs = bs.merge_manual(evs, json.load(open(mp, encoding="utf-8")).get("events", []))
    d = datetime.strptime(issue["date"], "%Y-%m-%d")
    rows, more = bs.build_slim(evs, d, 30, pick=issue.get("events_pick"), skip=issue.get("events_skip"))
    for reg, lst in more.items():
        for uid, title, md in lst:
            print(f"  未選入：{reg} {md} {title} [{uid}]")
    return bs.section_html(rows, d, 30, SITE + "event/", slim=True)


def footer(issue, email):
    unsub = '<br>不想再收到 Cue Sheet？<a href="{$unsubscribe}" style="color:#7A7974;">取消訂閱</a>' if email else ""
    return (f'<tr><td class="pad" style="padding:24px 28px 22px 28px;"><div style="border-top:3px double {C["ink"]};padding-top:10px;font-size:11px;line-height:1.7;color:{C["muted"]};">'
            f'<b>本期使用來源</b>：{esc(issue.get("sources_footer", ""))}<br>'
            f'<b>資料蒐集截止</b>：{esc(issue.get("cutoff", ""))}<br>'
            f'Cue Sheet 為非營利樂迷刊物，文字為編輯摘要與評論，圖片版權屬原權利人，連結皆指向原始來源。{unsub}</div></td></tr>')


# ---------------------------------------------------------------- 組版
SECTIONS = {  # 欄名: (英文, 產生函式)；各版欄序見 docs/版面規範.md
    "重磅點評": "PRIME PICKS", "唱片架": "RECORD SHELF", "精選試聽": "TAKE A BITE", "作曲家專訪": "COMPOSER INTERVIEW",
    "快訊": "NEWS FLASH", "社群雷達": "COMMUNITY RADAR", "歐亞觀察": "EUROPEAN &amp; ASIAN SOUNDSCAPE", "In memoriam": "",
}
ORDER = {
    "collector": ["本期專題", "重磅點評", "唱片架", "精選試聽", "作曲家專訪", "週末cue一下"],
    "news": ["本期專題", "快訊", "社群雷達", "歐亞觀察", "In memoriam", "近期國內電影音樂活動"],
}


def load_items():
    by = {}
    for f in glob.glob(os.path.join(ROOT, "items", "*.json")):
        for it in json.load(open(f, encoding="utf-8"))["items"]:
            by[it["id"]] = it
    return by


def render(issue, by, email=True, tpl=False):
    secs = {s["section"]: s for s in issue.get("sections", [])}
    pick = lambda name, key="items": [by[i] for i in secs.get(name, {}).get(key, []) if i in by]
    order = ORDER[issue["edition"] if issue["edition"] in ORDER else "collector"]
    title = f'Cue Sheet · {issue["date"][:4]} 年 {int(issue["date"][5:7])} 月 · {EDITION.get(issue["edition"], "")}'
    note = esc(issue.get("editor_note", ""))
    og_img = ""
    f0 = pick("本期專題")
    if f0 and first_media(f0[0], "image"):
        og_img = f'<meta property="og:image" content="{esc(first_media(f0[0], "image")["url"])}">'
    o = [f'''<!DOCTYPE html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{note}"><meta property="og:title" content="{title}"><meta property="og:description" content="{note}">{og_img}
<style>
@media (max-width:540px){{
 .pad{{padding-left:16px!important;padding-right:16px!important}}
 .mast{{font-size:44px!important}}
 .big{{font-size:28px!important}}
 .kick td{{display:block!important}}
 .webl{{display:block!important;text-align:left!important;padding:4px 0 0 0!important;white-space:normal!important}}
 td.stk{{display:block!important;width:auto!important;padding:0 0 10px 0!important;border-left:0!important}}
}}
</style></head><body style="margin:0;padding:0;background:{C["page_bg"]};"><table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{C["page_bg"]};"><tr><td align="center" style="padding:20px 10px;"><table width="{W["page"]}" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:{W["page"]}px;background:{C["paper"]};border:1px solid {C["frame"]};font-family:{FONT};color:{C["ink"]};">''']
    o.append(masthead(issue, email))
    for k, name in enumerate(order):
        if name == "本期專題":
            o.append(section_head("本期專題", "FEATURE STORY", first=True))
            o.append(feature(f0, tpl))
        elif name == "週末cue一下":
            o.append(section_head("週末cue一下", "WEEKEND CUE-UP"))
            o.append(weekend(issue.get("weekend", {})))
        elif name == "近期國內電影音樂活動":
            o.append(events(issue))
        else:
            o.append(section_head(name, SECTIONS[name]))
            items = pick(name)
            o.append({"重磅點評": lambda: prime_picks(items, tpl), "唱片架": lambda: record_shelf(items, tpl),
                      "精選試聽": lambda: take_a_bite(items, tpl), "作曲家專訪": lambda: interviews(items, tpl),
                      "快訊": lambda: news_flash(items), "社群雷達": lambda: community(items),
                      "歐亞觀察": lambda: eurasia(items, pick(name, "list"), tpl),
                      "In memoriam": lambda: memoriam(items, pick(name, "brief"), tpl)}[name]())
    o.append(footer(issue, email))
    o.append("</table></td></tr></table></body></html>\n")
    return "".join(o)


def check(html_text, slug):
    kb = len(html_text.encode("utf-8")) / 1024
    msg = f"{slug} 電子報版 {kb:.1f} KB"
    if kb > MAX_KB:
        msg += f"（超過 {MAX_KB} KB，Gmail 可能截斷，先告知編輯）"
    print(msg)
    if "▶" in html_text:
        print("警告：出現「▶」，Gmail 會換成 emoji，改用 CSS 三角形")


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    opts = [x for x in sys.argv[1:] if x.startswith("--")]
    if "--template" in opts:
        import template_data
        for ed in args or ["collector", "news"]:
            issue, by = template_data.sample(ed)
            out = os.path.join(ROOT, "templates", f"cue_sheet_template_{ed}.html")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            open(out, "w", encoding="utf-8").write(render(issue, by, email=True, tpl=True))
            print("空白版型 →", out)
        return
    slug = args[0]
    issue = json.load(open(os.path.join(ROOT, "issues", f"{slug}.json"), encoding="utf-8"))
    by = load_items()
    email_html = render(issue, by, email=True)
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    email_path = os.path.join(ROOT, "out", f"cue_sheet_{slug}.html")
    open(email_path, "w", encoding="utf-8").write(email_html)
    check(email_html, slug)
    print("電子報版 →", email_path)
    if "--email-only" not in opts:
        web_path = os.path.join(ROOT, "newsletter", slug, "index.html")
        os.makedirs(os.path.dirname(web_path), exist_ok=True)
        subprocess.run([sys.executable, os.path.join(ROOT, "tools", "web_version.py"), email_path, web_path], check=True)
        print("網站版 →", web_path)


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()

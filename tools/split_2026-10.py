"""一次性：把 10 月號試刊（newsletter/2026-10/index.html）拆成單則資料 items/2026-10.json。

10 月號之後各期直接以單則資料撰寫，不再從 HTML 拆。
用法：python tools/split_2026-10.py
"""
import json
import re
from bs4 import BeautifulSoup, NavigableString, Tag

SRC = "newsletter/2026-10/index.html"
html = open(SRC, encoding="utf8").read()

MARKS = [("feature", "Feature Story"), ("flash", "News Flash"), ("radar", "Community Radar"),
         ("picks", "Prime Picks"), ("shelf", "Record Shelf"), ("bite", "Take a Bite"),
         ("interview", "Composer Interview"), ("eurasia", "European &amp; Asian Soundscape"),
         ("memoriam", "In memoriam"), ("weekend", "Weekend Cue-Up")]
pos = [(k, html.index(m)) for k, m in MARKS]
SEC = {}
for i, (k, p) in enumerate(pos):
    end = pos[i + 1][1] if i + 1 < len(pos) else html.index("Upcoming in Taiwan")
    SEC[k] = BeautifulSoup(html[p:end], "lxml")


def clean(t):
    t = re.sub(r"\s+", " ", t).strip()
    return t


def links(tag):
    out = []
    for a in tag.find_all("a"):
        h = a.get("href", "")
        name = clean(a.get_text())
        if not h or "youtube.com" in h or "commons.wikimedia" in h or not name or name.startswith("▶"):
            continue
        if any(s["url"] == h and s["name"] == name for s in out):
            continue
        out.append({"name": name, "url": h})
    return out


def strip_src_paren(t):
    # 去掉句末「（來源、來源）。」這類只放來源連結的括號
    t = re.sub(r"[（(][^（）()]*[）)]([。．.]?)$", r"\1", t).strip()
    return t


def lead_blocks(soup, tags=("li", "p", "div")):
    """找出以 <strong> 開頭的段落：回傳 (tag, 標題, 內文)。"""
    out = []
    for tag in soup.find_all(tags):
        kids = [c for c in tag.children if not (isinstance(c, NavigableString) and not c.strip())]
        if not kids or not (isinstance(kids[0], Tag) and kids[0].name == "strong"):
            continue
        title = clean(kids[0].get_text()).rstrip("：:。.")
        rest = clean("".join(c.get_text() if isinstance(c, Tag) else str(c) for c in kids[1:]))
        out.append((tag, title, rest))
    return out


def date_from_url(u):
    m = re.search(r"/(20\d\d)/(\d\d)/(\d\d)/", u)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else None


def yt(tag):
    a = tag.find("a", href=re.compile("youtube.com/watch"))
    if not a:
        return None
    return re.search(r"v=([\w-]+)", a["href"]).group(1)


raw = []  # (section, dict)

# ---------- 本月專題：兩則長文 ----------
feat = SEC["feature"]
feat_text = feat.get_text("\n")


def block(start, end):
    s = feat_text.index(start)
    e = feat_text.index(end, s)
    return feat_text[s:e]


def md_from(text, heads):
    lines = [clean(x) for x in text.split("\n")]
    lines = [x for x in lines if x]
    md, para = [], []
    for ln in lines:
        if ln in heads:
            if para:
                md.append("".join(para)); para = []
            md.append("## " + ln)
        else:
            para.append(ln)
    if para:
        md.append("".join(para))
    return "\n\n".join(md)


fenton_body = md_from(block("英國作曲家 George Fenton 10 月 5 日", "五次奧斯卡提名"), ["演員出身的作曲家"])
fenton_body += ("\n\n## 五次奧斯卡提名\n\n"
                "- 1982：《甘地》（與 Ravi Shankar 合作，Richard Attenborough 執導）\n"
                "- 1987：《哭喊自由》配樂與主題曲兩項（與南非音樂家 Jonas Gwangwa 合作，Attenborough 執導）\n"
                "- 1988：《危險關係》（Stephen Frears 執導）\n"
                "- 1991：《奇幻城市》（Terry Gilliam 執導）\n\n")
fenton_body += md_from(block("好萊塢喜劇的旋律，肯洛區電影的克制", "從哪裡開始聽"),
                       ["好萊塢喜劇的旋律，肯洛區電影的克制", "David Attenborough 的聲音", "樂評界的送別"])
fenton_body += "\n\n**從哪裡開始聽：**《電子情書》〈Butterflies in the Subway〉、《奇幻城市》、《今天暫時停止》、《藍色星球》主題、《我是布萊克》。"

fenton_div = feat.find(string=re.compile("George Fenton（1949–2026）：從")).find_parent()
wsa_title_node = feat.find(string=re.compile("Daniel Pemberton 二度封王"))
feat_sources = feat.find_all(string=re.compile("^來源："))
fenton_src_tag = feat_sources[0].find_parent()
wsa_src_tag = feat_sources[1].find_parent()

fenton_media = [
    ("george-fenton-bmi.jpg", "George Fenton", "Movie Music UK", "https://moviemusicuk.us/2026/10/05/george-fenton-1949-2026/"),
    ("youve-got-mail.jpg", "《電子情書》", "Movie Wave", "https://www.movie-wave.net/youve-got-mail/"),
    ("the-blue-planet.jpg", "《藍色星球》", "Movie Wave", "https://www.movie-wave.net/the-blue-planet/"),
    ("frozen-planet.jpg", "《冰凍星球》", "Movie Wave", "https://www.movie-wave.net/frozen-planet/"),
    ("dangerous-beauty.jpg", "《Dangerous Beauty》", "Movie Wave", "https://www.movie-wave.net/dangerous-beauty/"),
    ("mary-reilly.jpg", "《Mary Reilly》", "Movie Wave", "https://www.movie-wave.net/mary-reilly/"),
    ("in-love-and-war.jpg", "《愛在戰火蔓延時》", "Movie Wave", "https://www.movie-wave.net/in-love-and-war/"),
]
IMG = "https://mesple.github.io/cuesheet/images/2026-10/"
raw.append(("feature", {
    "title": "George Fenton（1949–2026）：從《甘地》到《藍色星球》的英國聲音",
    "summary": "五度入圍奧斯卡的作曲家 10 月 5 日在倫敦驟逝，享壽 76 歲。",
    "body": fenton_body,
    "sources": links(fenton_src_tag),
    "media": [{"kind": "image", "url": IMG + f, "caption": c, "credit": cr, "credit_url": cu} for f, c, cr, cu in fenton_media],
}))

wsa_body = md_from(block("第 26 屆 World Soundtrack Awards", "完整得獎名單"), [])
awards = [("年度電影作曲家", "Daniel Pemberton"),
          ("年度電視作曲家", "Jeff Russo（《Cape Fear》《Alien: Earth》《Citadel》第二季；前兩次入圍未獲獎）"),
          ("年度新人", "Hannah Peel（《Midwinter Break》）；日本作曲家福原まり入圍未獲獎"),
          ("最佳原創歌曲", "〈Golden〉（《KPop Demon Hunters》），繼奧斯卡之後再添一座"),
          ("觀眾票選獎", "Kevin Smithers（墨西哥定格動畫《Soy Frankelda》）"),
          ("遊戲音樂獎", "Nicolas Garcia（《Cthulhu: The Cosmic Abyss》，80 人管弦樂團加罕見古樂器）"),
          ("比利時年度作曲家", "Margaret Hermant（Echo Collective 創始成員）"),
          ("青年作曲比賽", "Xabier Doural García（西班牙；題目為替《Ratched》片段重新配樂，作品由樂團現場演出）"),
          ("終身成就獎", "Trevor Jones（《大地英豪》《新娘百分百》《烈血大風暴》）")]
for a, b in awards:
    assert b.split("（")[0] in feat_text, b
wsa_body += "\n\n## 完整得獎名單\n\n" + "\n".join(f"- **{a}**：{b}" for a, b in awards)
obs = block("觀眾票與評審票分道揚鑣。", "來源：")
obs_lines = [clean(x) for x in obs.split("\n") if clean(x)]
wsa_body += "\n\n## 觀察\n\n" + "\n\n".join(f"**{obs_lines[i]}**{obs_lines[i+1]}" for i in range(0, len(obs_lines), 2))
raw.append(("feature", {
    "title": "Daniel Pemberton 二度封王：第 26 屆世界電影音樂獎揭曉",
    "summary": "10/10 根特頒獎，Jeff Russo 三度入圍終於得獎，Hannah Peel 獲新人獎。",
    "body": wsa_body,
    "sources": links(wsa_src_tag),
    "media": [{"kind": "image", "url": IMG + "wsa-2026-winners.jpg", "caption": "第 26 屆世界電影音樂獎得主", "credit": "World Soundtrack Awards", "credit_url": "https://www.worldsoundtrackawards.com/daniel-pemberton-hannah-peel-and-jeff-russo-among-the-winners-at-the-26th-world-soundtrack-awards"}],
}))

# ---------- 快訊、社群雷達 ----------
for sec in ("flash", "radar"):
    for tag, title, rest in lead_blocks(SEC[sec], ("li", "p")):
        raw.append((sec, {"title": title, "summary": strip_src_paren(rest), "sources": links(tag)}))

# ---------- 重磅點評 ----------
for t in SEC["picks"].find_all("table"):
    tdiv = t.find("div", style=re.compile("font-size:19px"))
    if not tdiv:
        continue
    divs = tdiv.find_next_siblings("div")
    img = t.find("img")
    raw.append(("picks", {
        "title": clean(tdiv.get_text()),
        "byline": clean(divs[0].get_text()),
        "summary": clean(divs[1].get_text()),
        "sources": links(divs[2]),
        "media": [{"kind": "image", "url": img["src"], "caption": "專輯封面"}] if img else [],
    }))

# ---------- 唱片架 ----------
for d in SEC["shelf"].find_all("div", style=re.compile("display:inline-block")):
    img = d.find("img")
    t = d.find("div", style=re.compile("font-size:16px"))
    if not (img and t):
        continue
    info = t.find_next_sibling("div")
    srcdiv = info.find_next_sibling("div")
    a = d.find("a")
    media = {"kind": "image", "url": img["src"], "caption": "專輯封面"}
    if "scdn.co" in img["src"]:
        media["link"] = a["href"]
        media["hosting"] = "spotify"
    raw.append(("shelf", {"title": clean(t.get_text()), "byline": clean(info.get_text()),
                          "summary": clean(info.get_text()), "sources": links(srcdiv), "media": [media]}))

# ---------- 重點試聽 ----------
for td in SEC["bite"].find_all("td"):
    v = yt(td)
    if not v or td.find("td"):
        continue
    divs = td.find_all("div", recursive=False)
    raw.append(("bite", {"title": clean(divs[0].get_text()), "summary": strip_src_paren(clean(divs[1].get_text())),
                         "sources": links(divs[1]), "media": [{"kind": "youtube", "id": v}]}))

# ---------- 作曲家專訪 ----------
iv = SEC["interview"]
v = yt(iv)
for tag, title, rest in lead_blocks(iv, ("p", "li")):
    d = {"title": title, "summary": strip_src_paren(rest), "sources": links(tag)}
    if title.startswith("Olivier"):
        d["media"] = [{"kind": "youtube", "id": v, "caption": "Resonance: A Plague Tale Legacy 原聲（Olivier Derivière 官方頻道）"}]
    raw.append(("interview", d))

# ---------- 歐亞觀察 ----------
eu = SEC["eurasia"]
for h in eu.find_all("h3"):
    name = clean(h.get_text())
    if name == "其他歐亞動態":
        continue
    row = h.find_next("table") if h.find_next("table") else None
    # 主打小節：h3 之後的第一張表（左圖右文）
    img = h.find_next("img")
    textdiv = img.find_parent("td").find_next_sibling("td") if img.find_parent("td") else None
    cap = img.find_next("div")
    body_tags = textdiv.find_all(["div", "p", "ul", "ol"], recursive=False) if textdiv else []
    raw.append(("eurasia_h3", {"title": name, "tag": textdiv, "img": img}))
for d in eu.find_all("div", style=re.compile("font-size:22px")):
    texts = d.find_next_siblings("div")
    raw.append(("eurasia", {"title": clean(d.get_text()), "summary": clean(texts[0].get_text()),
                            "sources": links(texts[1])}))
ol = eu.find("h3", string=re.compile("其他歐亞動態")).find_next("ol")
for tag, title, rest in lead_blocks(ol, ("li",)):
    raw.append(("eurasia_list", {"title": title, "summary": strip_src_paren(rest), "sources": links(tag), "tag": tag}))

# ---------- In memoriam ----------
mm = SEC["memoriam"]
for t in mm.find_all("table"):
    img = t.find("img")
    tag = t.find("strong").find_parent("div")
    title = clean(t.find("strong").get_text()).rstrip("。")
    rest = clean(tag.get_text())[len(clean(t.find("strong").get_text())):].strip()
    media = []
    if img:
        cap = img.find_next("div")
        ca = cap.find("a")
        media = [{"kind": "image", "url": img["src"], "caption": title.split("（")[0] + " 肖像",
                  "credit": clean(cap.get_text()), "credit_url": ca["href"] if ca else None, "hosting": "commons"}]
    raw.append(("memoriam", {"title": title, "summary": strip_src_paren(rest), "sources": links(tag), "media": media}))
# 無圖的訃聞（div 包 strong，不在表格內）
for tag, title, rest in lead_blocks(mm, ("div",)):
    if tag.find_parent("table"):
        continue
    raw.append(("memoriam", {"title": title, "summary": strip_src_paren(rest), "sources": links(tag), "media": []}))

exec(open("tools/assemble_2026-10.py", encoding="utf8").read())

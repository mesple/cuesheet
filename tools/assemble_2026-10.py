# 由 split_2026-10.py 以 exec 載入：把 raw（解析結果）補上類型、地區、作曲家等欄位，拆分合併條目，輸出單則資料。
# 欄位依專案檔案庫 site/cue_sheet_資料欄位草案.md（v2）。

ISSUE = "2026-10"
IMG = "https://mesple.github.io/cuesheet/images/2026-10/"

# ---------- 作曲家對照表 ----------
# 代號: (顯示名, 英文名, 別名)  顯示名規則：華人用中文，日本人有漢字用漢字，其他用原文
C = {
    "george-fenton": ("George Fenton", "George Fenton", []),
    "daniel-pemberton": ("Daniel Pemberton", "Daniel Pemberton", []),
    "jeff-russo": ("Jeff Russo", "Jeff Russo", []),
    "hannah-peel": ("Hannah Peel", "Hannah Peel", []),
    "trevor-jones": ("Trevor Jones", "Trevor Jones", []),
    "nicolas-garcia": ("Nicolas Garcia", "Nicolas Garcia", []),
    "kevin-smithers": ("Kevin Smithers", "Kevin Smithers", []),
    "margaret-hermant": ("Margaret Hermant", "Margaret Hermant", []),
    "alan-silvestri": ("Alan Silvestri", "Alan Silvestri", ["Silvestri"]),
    "james-newton-howard": ("James Newton Howard", "James Newton Howard", []),
    "michael-giacchino": ("Michael Giacchino", "Michael Giacchino", ["Giacchino"]),
    "henry-jackman": ("Henry Jackman", "Henry Jackman", ["Jackman"]),
    "michael-abels": ("Michael Abels", "Michael Abels", ["Abels"]),
    "brandon-roberts": ("Brandon Roberts", "Brandon Roberts", []),
    "nami-melumad": ("Nami Melumad", "Nami Melumad", []),
    "emily-bear": ("Emily Bear", "Emily Bear", []),
    "lukas-frank": ("Lukas Frank", "Lukas Frank", []),
    "trent-reznor": ("Trent Reznor", "Trent Reznor", ["Reznor"]),
    "atticus-ross": ("Atticus Ross", "Atticus Ross", ["Ross"]),
    "david-fleming": ("David Fleming", "David Fleming", []),
    "dave-porter": ("Dave Porter", "Dave Porter", []),
    "robert-glasper": ("Robert Glasper", "Robert Glasper", []),
    "the-newton-brothers": ("The Newton Brothers", "The Newton Brothers", []),
    "jeff-cardoni": ("Jeff Cardoni", "Jeff Cardoni", []),
    "tyler-bates": ("Tyler Bates", "Tyler Bates", []),
    "john-paesano": ("John Paesano", "John Paesano", []),
    "adam-hochstatter": ("Adam Hochstatter", "Adam Hochstatter", []),
    "olivier-arson": ("Olivier Arson", "Olivier Arson", []),
    "basil-poledouris": ("Basil Poledouris", "Basil Poledouris", ["Poledouris"]),
    "michael-kamen": ("Michael Kamen", "Michael Kamen", ["Kamen"]),
    "john-williams": ("John Williams", "John Williams", []),
    "james-horner": ("James Horner", "James Horner", []),
    "simon-rhodes": ("Simon Rhodes", "Simon Rhodes", []),
    "jerry-goldsmith": ("Jerry Goldsmith", "Jerry Goldsmith", []),
    "volker-bertelmann": ("Volker Bertelmann", "Volker Bertelmann", ["Hauschka"]),
    "will-van-de-crommert": ("Will Van de Crommert", "Will Van de Crommert", []),
    "cosmo-sheldrake": ("Cosmo Sheldrake", "Cosmo Sheldrake", []),
    "philippe-rombi": ("Philippe Rombi", "Philippe Rombi", []),
    "laura-karpman": ("Laura Karpman", "Laura Karpman", []),
    "pinar-toprak": ("Pinar Toprak", "Pinar Toprak", []),
    "olivier-deriviere": ("Olivier Derivière", "Olivier Derivière", ["Olivier Deriviere"]),
    "arturo-cardelus": ("Arturo Cardelús", "Arturo Cardelús", []),
    "hanan-townshend": ("Hanan Townshend", "Hanan Townshend", []),
    "john-barry": ("John Barry", "John Barry", []),
    "david-shire": ("David Shire", "David Shire", []),
    "alexandre-desplat": ("Alexandre Desplat", "Alexandre Desplat", ["Desplat"]),
    "harry-gregson-williams": ("Harry Gregson-Williams", "Harry Gregson-Williams", []),
    "ricky-ho": ("何國杰", "Ricky Ho", ["Ricky Ho"]),
    "isabel-latorre": ("Isabel Latorre", "Isabel Latorre", ["Isabel Latorre Sáez"]),
    "philip-glass": ("Philip Glass", "Philip Glass", []),
    "hays-holladay": ("Hays Holladay", "Hays Holladay", []),
    "ryan-holladay": ("Ryan Holladay", "Ryan Holladay", []),
    "ari-balouzian": ("Ari Balouzian", "Ari Balouzian", []),
    "marco-beltrami": ("Marco Beltrami", "Marco Beltrami", []),
    "fabio-massimo-capogrosso": ("Fabio Massimo Capogrosso", "Fabio Massimo Capogrosso", []),
    "iris-hond": ("Iris Hond", "Iris Hond", []),
    "max-aruj": ("Max Aruj", "Max Aruj", []),
    "wf-smith-leithart": ("W.F. Smith Leithart", "W.F. Smith Leithart", []),
    "christopher-benstead": ("Christopher Benstead", "Christopher Benstead", []),
    "leo-birenberg": ("Leo Birenberg", "Leo Birenberg", []),
    "zach-robinson": ("Zach Robinson", "Zach Robinson", []),
    "yoko-shimomura": ("下村陽子", "Yoko Shimomura", ["Yoko Shimomura"]),
    "max-richter": ("Max Richter", "Max Richter", ["Richter"]),
    "hans-zimmer": ("Hans Zimmer", "Hans Zimmer", ["Zimmer"]),
    "daniel-rojas": ("Daniel Rojas", "Daniel Rojas", []),
    "finneas": ("Finneas", "Finneas O'Connell", ["FINNEAS"]),
    "rupert-gregson-williams": ("Rupert Gregson-Williams", "Rupert Gregson-Williams", []),
    "terence-blanchard": ("Terence Blanchard", "Terence Blanchard", []),
    "austin-wintory": ("Austin Wintory", "Austin Wintory", []),
    "lim-giong": ("林強", "Lim Giong", ["Lim Giong", "Giong Lim"]),
    "hou-chih-chien": ("侯志堅", "", []),
    "yang-yi-hsiu": ("楊易修", "", []),
    "kao-min-lun": ("高敏倫", "", []),
    "huang-wei-che": ("黃偉哲", "", []),
    "ho-chien-liang": ("何堅良", "", []),
    "fu-duo-ma": ("福多瑪", "", []),
    "ryota-katayama": ("片山凉太", "Ryota Katayama", ["Ryota Katayama"]),
    "semin-son": ("Semin Son", "Semin Son", []),
    "gabriel-yared": ("Gabriel Yared", "Gabriel Yared", []),
    "federico-jusid": ("Federico Jusid", "Federico Jusid", ["Jusid"]),
    "john-gurtler": ("John Gürtler", "John Gürtler", []),
    "jan-miserre": ("Jan Miserre", "Jan Miserre", []),
    "katharina-nuttall": ("Katharina Nuttall", "Katharina Nuttall", []),
    "halfdan-e": ("Halfdan E.", "Halfdan E.", []),
    "patrick-doyle": ("Patrick Doyle", "Patrick Doyle", []),
    "beatriz-lopez-nogales": ("Beatriz López-Nogales", "Beatriz López-Nogales", []),
    "marcin-przybylowicz": ("Marcin Przybyłowicz", "Marcin Przybyłowicz", []),
    "koji-endo": ("遠藤浩二", "Koji Endo", ["Koji Endo"]),
    "howard-shore": ("Howard Shore", "Howard Shore", []),
    "liu-huan": ("劉歡", "Liu Huan", ["Liu Huan", "Huan Liu"]),
    "tony-gatlif": ("Tony Gatlif", "Tony Gatlif", []),
    "jean-claude-petit": ("Jean-Claude Petit", "Jean-Claude Petit", []),
    "michel-legrand": ("Michel Legrand", "Michel Legrand", []),
    "michel-berger": ("Michel Berger", "Michel Berger", []),
    "duncan-sheik": ("Duncan Sheik", "Duncan Sheik", []),
    "michel-fano": ("Michel Fano", "Michel Fano", []),
    "nick-glennie-smith": ("Nick Glennie-Smith", "Nick Glennie-Smith", []),
    "kazuo-shinoda": ("信田かずお", "Kazuo Shinoda", ["Kazuo Shinoda"]),
    "singeetam-srinivasa-rao": ("Singeetam Srinivasa Rao", "Singeetam Srinivasa Rao", []),
}

# ---------- 每則的補充欄位（依 raw 標題比對） ----------
# key: 標題開頭 → dict(type, tags, region, date, composers, ...)
N = "新聞"
META = {
    "George Fenton（1949": dict(type="訃聞", region="歐洲", date="2026-10-05", composers=["george-fenton"], feature=True,
                               internal_note="艾美獎座數 FMR 與 MMUK 不一致，內文採「兩部作品獲艾美獎」。"),
    "Daniel Pemberton 二度": dict(type=N, tags=["獎項"], region="歐洲", date="2026-10-10", feature=True,
                                composers=["daniel-pemberton", "jeff-russo", "hannah-peel", "trevor-jones", "nicolas-garcia", "kevin-smithers", "margaret-hermant"]),
    "《Behemoth!》": dict(type=N, tags=["新片"], region="北美", date="2026-10-02",
                        composers=["alan-silvestri", "james-newton-howard", "michael-giacchino", "henry-jackman", "michael-abels", "brandon-roberts", "nami-melumad", "emily-bear", "lukas-frank"],
                        upcoming=[{"date": "2026-12-04", "label": "《Behemoth!》美國上映"}]),
    "Reznor & Ross": dict(type=N, tags=["新案"], region="北美", composers=["trent-reznor", "atticus-ross"],
                          upcoming=[{"date": "2026-11-25", "label": "Reznor & Ross《Cliff Booth》IMAX 上映"}, {"date": "2026-12-23", "label": "《Cliff Booth》Netflix 上線"}]),
    "艾美獎音樂類": dict(type=N, tags=["獎項"], region="北美", composers=["david-fleming", "dave-porter"],
                      date_note="原刊未寫頒獎日期"),
    "Robert Glasper": dict(type=N, tags=["新案"], region="北美", composers=["robert-glasper"]),
    "The Newton Brothers 再接": dict(type=N, tags=["新案"], region="北美", composers=["the-newton-brothers"]),
    "Jeff Cardoni": dict(type=N, tags=["新案"], region="北美", composers=["jeff-cardoni"]),
    "哥雅獎的": dict(type="社群", region="歐洲", composers=["olivier-arson"], date_note="原刊未寫社論日期"),
    "好的評論該長": dict(type="社群", region="歐洲", date_note="原刊未寫社論日期"),
    "哪些配樂值得重錄": dict(type="社群", region="全球", composers=["basil-poledouris", "michael-kamen"], date_note="原刊未寫討論串日期"),
    "樂迷版百大配樂投票": dict(type="社群", region="全球", date_note="原刊未寫討論串日期"),
    "星戰第十部": dict(type="社群", region="全球", composers=["john-williams"], date_note="原刊未寫討論串日期"),
    "Giacchino 的萬聖節": dict(type="社群", region="北美", composers=["michael-giacchino"], date_note="原刊未寫討論串日期"),
    "Skyward Spirit": dict(type="樂評", region="全球", composers=["james-horner", "simon-rhodes"]),
    "Disclosure Day": dict(type="樂評", region="北美", composers=["john-williams"]),
    "Explorers": dict(type="樂評", region="北美", composers=["jerry-goldsmith"]),
    "Verity": dict(type="樂評", region="北美", composers=["volker-bertelmann"]),
    "Medora": dict(type="樂評", region="北美", composers=["will-van-de-crommert"]),
    "Digger": dict(type="樂評", region="北美", composers=["cosmo-sheldrake"], date_note="MundoBSO 網址沒有日期"),
    "Hope": dict(type="樂評", region="亞洲", composers=["michael-abels"], date_note="MundoBSO 網址沒有日期"),
    "Les enfants": dict(type="樂評", region="歐洲", composers=["philippe-rombi"], date_note="MundoBSO 網址沒有日期"),
    "East of Eden": dict(type="樂評", region="北美", composers=["laura-karpman"], date_note="MundoBSO 網址沒有日期"),
    "África": dict(type="樂評", region="全球", composers=["pinar-toprak"], date_note="MundoBSO 網址沒有日期"),
    "Resonance: A Plague": dict(type="樂評", region="歐洲", composers=["olivier-deriviere"], date_note="MundoBSO 網址沒有日期"),
    "Centurion": dict(type="樂評", region="歐洲", composers=["arturo-cardelus"], date_note="網址沒有日期"),
    "Clear Sky": dict(type="樂評", region="北美", composers=["hanan-townshend"], date_note="網址沒有日期"),
    "Jaws 2": dict(type="發行", region="北美", composers=["john-williams"], date_note="原刊未寫發行日"),
    "Four in the Morning": dict(type="發行", region="歐洲", composers=["john-barry"], date_note="原刊未寫發行日"),
    "Aliens": dict(type="發行", region="北美", date="2026-09-15", composers=["james-horner"]),
    "Deadfall": dict(type="發行", region="北美", composers=["david-shire"]),
    "The Social Reckoning（Desplat）": dict(type="試聽", region="北美", composers=["alexandre-desplat"]),
    "The Social Reckoning": dict(type="發行", region="北美", date="2026-10-09", composers=["alexandre-desplat"]),
    "Animals": dict(type="發行", region="北美", date="2026-10-09", composers=["harry-gregson-williams"]),
    "Carrie": dict(type="發行", region="北美", date="2026-10-07", composers=["the-newton-brothers"]),
    "The Violinist": dict(type="發行", region="亞洲", date="2026-09-25", composers=["ricky-ho", "isabel-latorre"]),
    "Philip Glass": dict(type="發行", region="歐洲", date="2026-10-09", composers=["philip-glass"]),
    "Resident Evil": dict(type="發行", region="北美", composers=["hays-holladay", "ryan-holladay"],
                          upcoming=[{"date": "2026-12-11", "label": "《Resident Evil》CD 發行"}]),
    "The Hunger Games": dict(type="發行", region="北美", composers=["james-newton-howard"],
                             upcoming=[{"date": "2026-11-13", "label": "《The Hunger Games: Sunrise on the Reaping》歌曲輯"}]),
    "Primetime": dict(type="發行", region="北美", composers=["ari-balouzian"],
                      upcoming=[{"date": "2026-11-20", "label": "《Primetime》CD／黑膠"}]),
    "Unabomber": dict(type="發行", region="北美", date="2026-09-25", composers=["marco-beltrami"]),
    "Nessun dolore": dict(type="發行", region="歐洲", date="2026-09-24", composers=["fabio-massimo-capogrosso"]),
    "Spinoza": dict(type="發行", region="歐洲", date="2026-09-28", composers=["iris-hond"]),
    "The Girl in the River": dict(type="發行", region="北美", date="2026-09-04", composers=["max-aruj", "wf-smith-leithart"]),
    "The Gentlemen": dict(type="發行", region="歐洲", date="2026-09-04", composers=["christopher-benstead"]),
    "The Uprising": dict(type="發行", region="歐洲", date="2026-09-11", composers=["volker-bertelmann"]),
    "Avian Elegy": dict(type="試聽", region="北美", composers=["cosmo-sheldrake"]),
    "Guile's Theme": dict(type="試聽", region="北美", composers=["leo-birenberg", "zach-robinson", "yoko-shimomura"]),
    "Now We Can Sing": dict(type="試聽", region="歐洲", composers=["max-richter"], date_note="DG 網址沒有日期"),
    "East of Eden（Laura": dict(type="試聽", region="北美", composers=["laura-karpman"]),
    "Draw You Out": dict(type="試聽", region="北美"),
    "Olivier Derivière 談": dict(type="訪談", region="歐洲", date="2026-09-21", composers=["olivier-deriviere"]),
    "Hans Zimmer 與 HBO": dict(type="訪談", region="全球", composers=["hans-zimmer"], date_note="原刊未寫訪談日期"),
    "Daniel Rojas": dict(type="訪談", region="北美", composers=["daniel-rojas"], date_note="原刊未寫訪談日期"),
    "Austin Wintory": dict(type="訪談", region="北美", composers=["austin-wintory"], date_note="原刊未寫訪談日期"),
    "Hans Zimmer 首度親臨": dict(type=N, tags=["音樂活動"], region="亞洲", date="2026-09-19", composers=["hans-zimmer"]),
    "Federico Jusid": dict(type=N, tags=["新案"], region="歐洲", composers=["federico-jusid"]),
    "Max Richter 10/27": dict(type=N, tags=["音樂活動"], region="亞洲", date="2026-10-27", composers=["max-richter"],
                             upcoming=[{"date": "2026-10-22", "end": "2026-10-23", "label": "蘇格蘭室內樂團演出 Richter《Recomposed: Vivaldi》（愛丁堡、格拉斯哥）"},
                                       {"date": "2026-10-27", "label": "Max Richter 塔什干首演"}]),
    "法國 Ciné-Trio": dict(type=N, tags=["音樂活動"], region="歐洲", date="2026-10-16",
                          upcoming=[{"date": "2026-10-16", "end": "2026-10-18", "label": "Ciné-Trio 三日音樂會"}]),
    "Camille 歐洲": dict(type=N, tags=["獎項"], region="歐洲", date="2026-09-22",
                       composers=["john-gurtler", "jan-miserre", "katharina-nuttall", "halfdan-e", "patrick-doyle"]),
    "聖賽巴斯提安": dict(type=N, tags=["音樂活動"], region="歐洲", date="2026-09-19", composers=["beatriz-lopez-nogales"]),
    "《巫師3》": dict(type=N, tags=["音樂活動"], region="歐洲", date="2026-10-21", composers=["marcin-przybylowicz"]),
    "Emanuel Ax": dict(type=N, tags=["音樂活動"], region="歐洲", date="2026-10-09", composers=["john-williams"]),
    "Classic FM": dict(type=N, tags=["其他"], region="歐洲", date="2026-08-31", composers=["howard-shore", "max-richter"]),
    "劉歡": dict(type="訃聞", region="亞洲", date="2026-09-25", composers=["liu-huan"]),
    "Tony Gatlif": dict(type="訃聞", region="歐洲", date="2026-09-02", composers=["tony-gatlif"]),
    "Jean-Paul Rappeneau": dict(type="訃聞", region="歐洲", date="2026-09-01",
                                composers=["jean-claude-petit", "michel-legrand", "michel-berger", "gabriel-yared"],
                                internal_note="Rappeneau 是導演不是作曲家；composers 列的是文中提到的合作作曲家。"),
    "Duncan Sheik": dict(type="訃聞", region="北美", date="2026-09-17", composers=["duncan-sheik"]),
    "Michel Fano": dict(type="訃聞", region="歐洲", date="2026-08-31", composers=["michel-fano"]),
    "Nick Glennie-Smith": dict(type="訃聞", region="北美", date="2026-08-16", composers=["nick-glennie-smith"]),
}


def meta_for(title):
    best = None
    for k in META:
        if title.startswith(k) and (best is None or len(k) > len(best)):
            best = k
    return META.get(best) if best else None


SECTION_LABEL = {"feature": "本月專題", "flash": "快訊", "radar": "社群雷達", "picks": "重磅點評", "shelf": "唱片架",
                 "bite": "重點試聽", "interview": "作曲家專訪", "eurasia": "歐亞觀察", "eurasia_h3": "歐亞觀察",
                 "eurasia_list": "歐亞觀察", "memoriam": "In memoriam"}

items = []


def add(section, d, m, **extra):
    it = {"id": None, "issue": ISSUE, "type": m["type"]}
    if m.get("tags"):
        it["tags"] = m["tags"]
    it["region"] = m["region"]
    date = m.get("date")
    if not date:
        for s in d.get("sources", []):
            date = date_from_url(s["url"])
            if date:
                break
        if not date:
            for s in d.get("sources", []):
                mm_ = re.search(r"/(20\d\d)/(\d\d)/", s["url"])
                if mm_:
                    date = f"{mm_.group(1)}-{mm_.group(2)}"
                    break
    it["date"] = date or "2026-10-12"
    it["title"] = d["title"]
    summary = d["summary"]
    if d.get("byline"):
        parts = d["byline"].split("｜")
        if section == "shelf":
            if len(parts) > 1:
                it["byline"] = parts[0]
                summary = "｜".join(parts[1:])
        else:
            it["byline"] = d["byline"]
    it["summary"] = summary
    if d.get("body"):
        it["body"] = d["body"]
    if m.get("composers"):
        it["composers"] = m["composers"]
    if m.get("upcoming"):
        it["upcoming"] = m["upcoming"]
    it["sources"] = d.get("sources", [])
    if d.get("media"):
        it["media"] = d["media"]
    it.update(extra)
    it.setdefault("web", True)
    notes = []
    if not m.get("date") and (not date or len(date) == 7):
        notes.append("date 待確認（" + m.get("date_note", "原刊未寫日期") + "），" + ("只知月份" if date else "暫用發刊日"))
    if m.get("internal_note"):
        notes.append(m["internal_note"])
    if extra.get("internal_note"):
        notes.append(extra["internal_note"])
    if notes:
        it["internal_note"] = "；".join(dict.fromkeys(notes))
    it["_section"] = SECTION_LABEL[section]
    if m.get("feature"):
        it["_feature"] = True
    items.append(it)
    return it


def src(name, url):
    return {"name": name, "url": url}


for section, d in raw:
    t = d["title"]
    if section == "flash" and t == "其他新案":
        s = d["sources"]
        add(section, {"title": "Tyler Bates 接 CBS《NCIS: New York》", "summary": "Tyler Bates 為 CBS 新影集《NCIS: New York》配樂。", "sources": [s[0]]},
            dict(type=N, tags=["新案"], region="北美", composers=["tyler-bates"]), split="A1", web=True)
        add(section, {"title": "Paesano、Hochstatter 回鍋《Diary of a Wimpy Kid Christmas: The Getaway》",
                      "summary": "John Paesano 與 Adam Hochstatter 再為 Disney+ 動畫《Diary of a Wimpy Kid Christmas: The Getaway》配樂。", "sources": [s[1]]},
            dict(type=N, tags=["新案"], region="北美", composers=["john-paesano", "adam-hochstatter"]), split="A2", web=False)
        continue
    if section == "eurasia_list" and t == "歐亞作曲家新案":
        s = d["sources"]
        add(section, {"title": "Hannah Peel 為 Netflix 真人版《Assassin's Creed》配樂", "summary": "同期拿下世界電影音樂獎新人獎的 Hannah Peel，將為 Netflix 真人影集《Assassin's Creed》配樂。", "sources": [s[0]]},
            dict(type=N, tags=["新案"], region="歐洲", composers=["hannah-peel"]), split="B1", web=True)
        add(section, {"title": "遠藤浩二再與三池崇史合作《Bad Lieutenant: Tokyo》", "summary": "遠藤浩二再度為三池崇史執導的《Bad Lieutenant: Tokyo》配樂。", "sources": [s[1]]},
            dict(type=N, tags=["新案"], region="亞洲", composers=["koji-endo"]), split="B2", web=True)
        continue
    if section == "interview" and t.startswith("Hays & Ryan"):
        src_ = d["sources"]
        add(section, {"title": "Hays & Ryan Holladay 談《Resident Evil》", "summary": "從地下室樂團到再度與 Zach Cregger 合作，談 Miles Davis 如何啟發這份脈動式的恐懼配樂。", "sources": src_},
            dict(type="訪談", region="北美", composers=["hays-holladay", "ryan-holladay"]), split="D1", web=False,
            internal_note="來源是 MPA 訪談分類頁，不是單篇")
        add(section, {"title": "Finneas 談《Beef》第二季的復古合成器", "summary": "Finneas 談《Beef》第二季的復古合成器。", "sources": src_},
            dict(type="訪談", region="北美", composers=["finneas"]), split="D2", web=False,
            internal_note="原刊只有半句，來源是分類頁")
        continue
    if section == "interview" and t.startswith("Rupert"):
        src_ = d["sources"]
        add(section, {"title": "Rupert Gregson-Williams 談《Practical Magic 2》", "summary": "OnTheScore「Film Music Live!」影音訪談。", "sources": src_},
            dict(type="訪談", region="北美", composers=["rupert-gregson-williams"]), split="D3", web=None,
            internal_note="來源是 OnTheScore 首頁，補到單篇網址後再上網站（編輯 10/25 決定）")
        add(section, {"title": "Terence Blanchard 與導演 Elegance Bratton 談《By Any Means》", "summary": "OnTheScore「Film Music Live!」同節目另一集影音訪談。", "sources": src_},
            dict(type="訪談", region="北美", composers=["terence-blanchard"]), split="D4", web=None,
            internal_note="來源是 OnTheScore 首頁，補到單篇網址後再上網站（編輯 10/25 決定）")
        continue
    if section == "eurasia_h3" and t.startswith("金馬獎"):
        add(section, {"title": t,
                      "summary": "片山凉太以《黑潮》同時入圍最佳原創電影音樂與最佳原創電影歌曲兩項；頒獎典禮 11 月 22 日晚間在臺北流行音樂中心舉行。",
                      "body": ("## 最佳原創電影音樂\n\n- 《滄海琴聲》何國杰、Isabel Latorre Sáez\n- 《女孩》林強\n- 《功夫》侯志堅、楊易修、高敏倫、黃偉哲\n"
                               "- 《我們不是陌生人》何堅良、福多瑪\n- 《黑潮》片山凉太\n\n## 最佳原創電影歌曲\n\n- 〈輕輕放下〉9m88（《雙囍》）\n"
                               "- 〈幸福在歌唱〉李方睿（《陽光女子合唱團》）\n- 〈世界好壞〉馮之行（《善男信女》）\n- 〈Stop Running〉曾國宏（《狂忘警探》）\n"
                               "- 〈一去不返〉片山凉太（《黑潮》）"),
                      "sources": [src("中央社", "https://www.cna.com.tw/news/amov/202610015003.aspx"),
                                  src("Variety", "https://variety.com/2026/film/awards/sabus-arrested-memory-golden-horse-awards-nominations-1236894708/")],
                      "media": [{"kind": "image", "url": IMG + "golden-horse-63.jpg", "caption": "金馬 63 主視覺", "credit": "遠見", "credit_url": "https://www.gvm.com.tw/article/133306"}]},
            dict(type=N, tags=["獎項"], region="臺灣", date="2026-10-01",
                 composers=["ricky-ho", "isabel-latorre", "lim-giong", "hou-chih-chien", "yang-yi-hsiu", "kao-min-lun", "huang-wei-che", "ho-chien-liang", "fu-duo-ma", "ryota-katayama"],
                 upcoming=[{"date": "2026-11-22", "label": "第 63 屆金馬獎頒獎"}],
                 internal_note="片山凉太與 IMDb 對應待確認；《功夫》《我們不是陌生人》作曲家的英文名待查"))
        continue
    if section == "eurasia_h3" and t.startswith("蘇黎世"):
        add(section, {"title": t,
                      "summary": ("10 月 1 日在蘇黎世音樂廳揭曉的「2026 最佳國際電影音樂」金眼獎（獎金一萬瑞郎）由南韓的 Semin Son 拿下。今年考題是為九分鐘短片《The Shyness of Trees》寫交響樂團配樂，"
                                  "共收到 36 國 146 件作品，另兩位決選者為 Carl Falkenau（瑞典）與 Brendan Galvin（美國／紐西蘭）。評審團主席 Gabriel Yared 當晚也獲頒蘇黎世影展終身成就獎，"
                                  "Frank Strobel 指揮蘇黎世音樂廳管弦樂團演出三位決選作品與 Yared 的作品。"),
                      "sources": [src("Filmmusikwettbewerb", "https://filmmusikwettbewerb.ch/")],
                      "media": [{"kind": "image", "url": IMG + "semin-son.jpg", "caption": "Semin Son", "credit": "Filmmusikwettbewerb", "credit_url": "https://filmmusikwettbewerb.ch/"}]},
            dict(type=N, tags=["獎項"], region="歐洲", date="2026-10-01", composers=["semin-son", "gabriel-yared"]))
        continue
    if section == "interview" and t.startswith("Olivier"):
        add(section, d, meta_for(t), web=True,
            internal_note="來源是 The Film Scorer 訪談分類頁，不是單篇；和 D3、D4 同樣的問題，編輯 10/28 決定先上，看起來單薄再拿掉")
        continue
    m = meta_for(t)
    if section == "bite" and t.startswith("The Social Reckoning"):
        m = META["The Social Reckoning（Desplat）"]
    if section == "bite" and t.startswith("East of Eden"):
        m = META["East of Eden（Laura"]
    if not m:
        raise SystemExit("沒有補充欄位：" + t)
    add(section, d, m)

# 同期辭世者兩則（原刊一句帶過）
add("memoriam", {"title": "信田かずお", "summary": "《釣魚迷日記》系列作曲家、爵士鋼琴家，9 月 20 日辭世，享年 76。",
                 "sources": [src("スポニチ", "https://www.sponichi.co.jp/entertainment/news/2026/10/04/articles/20261004s000413H4426000c.html")]},
    dict(type="訃聞", region="亞洲", date="2026-09-20", composers=["kazuo-shinoda"]), split="C1", brief=True, web=True,
    )
add("memoriam", {"title": "Singeetam Srinivasa Rao", "summary": "身兼作曲的印度導演，10 月 4 日辭世，享年 94。",
                 "sources": [src("News Today", "https://newstodaynet.com/2026/10/04/legendary-director-singeetam-srinivasa-rao-passes-away-at-94/")]},
    dict(type="訃聞", region="亞洲", date="2026-10-04", composers=["singeetam-srinivasa-rao"]), split="C2", brief=True, web=True,
    )

# ---------- 編號 ----------
for i, it in enumerate(items, 1):
    it["id"] = f"{ISSUE}-{i:03d}"

by_title = {it["title"]: it["id"] for it in items}


def rel(a, b):
    ia = next(x for x in items if x["title"].startswith(a))
    ib = next(x for x in items if x["title"].startswith(b))
    ia.setdefault("related", []).append(ib["id"])
    ib.setdefault("related", []).append(ia["id"])


for a, b in [("George Fenton（1949", "Daniel Pemberton 二度"),
             ("Daniel Pemberton 二度", "Philip Glass"),
             ("Daniel Pemberton 二度", "Hannah Peel 為 Netflix"),
             ("Digger", "Avian Elegy"),
             ("The Violinist", "金馬獎第 63 屆"),
             ("The Social Reckoning（Desplat）", "The Social Reckoning"),
             ("East of Eden（Laura", "East of Eden"),
             ("Resonance: A Plague", "Olivier Derivière 談"),
             ("The Hunger Games", "Draw You Out"),
             ("The Newton Brothers 再接", "Carrie"),
             ("Skyward Spirit", "Aliens"),
             ("Max Richter 10/27", "Now We Can Sing")]:
    ia = next(x for x in items if x["title"].startswith(a) and (a != "The Social Reckoning（Desplat）" or x["type"] == "試聽") and (a != "East of Eden（Laura" or x["type"] == "試聽"))
    ib = next(x for x in items if x["title"].startswith(b) and x is not ia and (b not in ("The Social Reckoning", "East of Eden") or x["type"] in ("發行", "樂評")))
    ia.setdefault("related", []).append(ib["id"])
    ib.setdefault("related", []).append(ia["id"])

# ---------- 刊期檔：每欄放哪幾則 ----------
order = []
for it in items:
    sec = it.pop("_section")
    feat = it.pop("_feature", False)
    if not order or order[-1]["section"] != sec:
        order.append({"section": sec, "items": []})
    order[-1]["items"].append(it["id"])

issue_doc = {
    "issue": ISSUE,
    "label": "2026 年 10 月號",
    "edition": "trial",
    "kicker": "FILM MUSIC NEWSLETTER · OCTOBER 2026 · 試刊號",
    "date": "2026-10-12",
    "editor_note": "十月，我們送走了 George Fenton。《電子情書》開場那段輕快的鋼琴，原來已經陪了我們這麼久。「世界電影音樂獎」揭曉，看看是誰接下了大師的棒子。新唱片上架、作曲家訪談...熱鬧的十月。週末有空，挑一場離你最近的電影音樂會吧。",
    "feature": [items[0]["id"], items[1]["id"]],
    "sections": order,
    "weekend": {
        "playlist": ["《You've Got Mail》〈Butterflies in the Subway〉，送別 George Fenton",
                     "《Skyward Spirit》完整版，聽到 10 分鐘處再判斷要不要備面紙",
                     "《Disclosure Day》〈Listen…〉，對照《春之祭》開頭一起聽",
                     "《Verity》〈Ending Credits – Verity〉，再接《Clayface》主題比較 Bertelmann 的兩面"],
        "next": ["10/16 起 Ciné-Trio 三日音樂會", "10/23 《Clayface》上映，Bertelmann 原聲帶本月稍晚發行", "10/27 Max Richter 塔什干首演",
                 "10/30 Lorne Balfe《The Cat in the Hat》原聲帶", "11/13 《The Hunger Games: Sunrise on the Reaping》歌曲輯",
                 "11/20 《Primetime》CD／黑膠", "11/25 Reznor & Ross《Cliff Booth》IMAX 上映", "12/4 《Behemoth!》美國上映", "12/11 《Resident Evil》CD"],
    },
    "html": "newsletter/2026-10/index.html",
    "note": "試刊號由已排版的 HTML 拆出（tools/split_2026-10.py）；電子報版面以原 HTML 為準，本檔記錄每欄的單則組成。",
}

used = sorted({c for it in items for c in it.get("composers", [])})
missing = [c for c in used if c not in C]
if missing:
    raise SystemExit("composers.json 缺：" + ", ".join(missing))
composers = {"說明": "作曲家對照表。代號用於單則的 composers 欄與日後的作曲家頁網址；display 是網站顯示名（華人用中文、日本人有漢字用漢字）；imdb 待逐位補上。",
             "composers": {k: {"display": C[k][0], "name": C[k][1], "aliases": C[k][2], "imdb": []} for k in used}}
# 草案 v2 已核對過的 IMDb ID
for k, v in {"ricky-ho": ["nm0387369"], "lim-giong": ["nm0510533", "nm15585293"], "liu-huan": ["nm3232216"],
             "isabel-latorre": ["nm4944090"], "hans-zimmer": ["nm0001877"], "george-fenton": ["nm0006070"],
             "james-horner": ["nm0000035"], "volker-bertelmann": ["nm2890617"], "cosmo-sheldrake": ["nm5117478"],
             "max-richter": ["nm2068037"], "trent-reznor": ["nm0722153"], "atticus-ross": ["nm1589604"]}.items():
    composers["composers"][k]["imdb"] = v
composers["composers"]["ryota-katayama"]["note"] = "IMDb nm14729708 待確認是否同一人"
composers["composers"]["simon-rhodes"]["note"] = "IMDb nm0722529 待確認（有兩位同名）"

import os
os.makedirs("items", exist_ok=True)
os.makedirs("issues", exist_ok=True)
json.dump({"issue": ISSUE, "items": items}, open(f"items/{ISSUE}.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
json.dump(issue_doc, open(f"issues/{ISSUE}.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
json.dump(composers, open("composers.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)

from collections import Counter
print("單則", len(items), Counter(it["type"] for it in items))
print("web", Counter(str(it["web"]) for it in items))
print("作曲家", len(used))
for it in items:
    if it.get("internal_note"):
        print(it["id"], it["title"][:30], "→", it["internal_note"])

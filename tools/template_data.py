"""空白版型的示範資料（python tools/build_newsletter.py --template）。文字即各欄的寫法說明。"""

PH_IMG = None  # 版型模式下圖片一律畫灰框


def _src():
    return [{"name": "來源名", "url": "https://example.com/"}]


def _it(i, typ, title, summary, **kw):
    d = {"id": f"tpl-{i:03d}", "type": typ, "title": title, "summary": summary, "sources": _src()}
    d.update(kw)
    return d


def sample(edition):
    items = []
    feat = _it(1, "訪談", "專題標題（一行為佳）", "",
               body=("導言段：一兩句說出這則故事為什麼值得讀，點出主角與核心問題。（內文 16px，行高 1.85）\n\n"
                     "內文段落：每段一個重點，交代人物、作品、日期、數字。段落數依內容增減。\n\n"
                     "## 小標（選用，22px 襯線字）\n\n"
                     "| 欄名 | 欄名 | 欄名 |\n|---|---|---|\n| 項目 | 比較內容 | 比較內容 |\n| 項目 | 比較內容 | 比較內容 |\n\n"
                     "收尾段：回到讀者，給一個聆聽或觀影的角度。"),
               media=[{"kind": "image", "url": "", "caption": "主圖圖說：誰／哪部作品", "credit": "○○"}])
    items.append(feat)
    if edition == "collector":
        rv = [_it(10 + k, "樂評", "中文片名 原文片名", "評論摘要：忠實轉述評者看法（含負面），寫出具體曲目、配器與比較對象；不放任何評分，不加自己的評語。約 260 字。",
                  byline="作曲家", spotify="https://open.spotify.com/", media=[{"kind": "image", "url": "", "hosting": "spotify"}]) for k in range(2)]
        sh = [_it(20 + k, "發行", "中文片名 原文片名（版本）", "廠牌｜一句片名背景、格式（數位／CD／黑膠／限量張數）、發行日、新增內容。",
                  byline="作曲家", media=[{"kind": "image", "url": "", "hosting": "spotify"}]) for k in range(4)]
        tb = [_it(30 + k, "試聽", "曲名", "這段音樂出自哪部作品、首支曲目或錄音場次、誰釋出、何時發行。",
                  byline="作曲家", media=[{"kind": "youtube", "id": "", "caption": "上傳頻道名"}]) for k in range(3)]
        iv = [_it(40 + k, "訪談", "作曲家 談《中文片名》（原文片名）",
                  "專訪摘要：作曲家親口講的創作決定（主題、配器、錄音方式、與導演的合作），具體到曲目名。網站另需約 50 字的列表摘要（teaser）。",
                  media=[{"kind": "youtube", "id": "", "caption": "頻道名"}]) for k in range(2)]
        items += rv + sh + tb + iv
        sections = [{"section": "本期專題", "items": [feat["id"]]},
                    {"section": "重磅點評", "items": [x["id"] for x in rv]},
                    {"section": "唱片架", "items": [x["id"] for x in sh]},
                    {"section": "精選試聽", "items": [x["id"] for x in tb]},
                    {"section": "作曲家專訪", "items": [x["id"] for x in iv]}]
        weekend = {"playlist_text": "一段連續文字：依序推薦 2–3 張本期專輯，各寫一句怎麼聽（從哪一軌開始、聽什麼）；最後一句把它們收束成一個主題。",
                   "next": ["M/D 事件（廠牌或場地）", "M/D–D 事件（廠牌或場地）", "依日期由早到晚，一行一件事"]}
    else:
        nf = [_it(50 + k, "新聞", "標題重點", "誰、接了什麼案子或得了什麼獎、何時上映或發行；摘要裡寫出作曲家名。") for k in range(4)]
        cr = [_it(60 + k, "社群", "議題一句話（問句或短句）。", "討論重點：誰提出、主要論點、不同意見；不寫來源名。") for k in range(2)]
        eu = [_it(70, "新聞", "主打小節標題（附圖）", "時間、地點、得主或主角、評審與作品細節。",
                  media=[{"kind": "image", "url": "", "caption": "", "credit": ""}]),
              _it(71, "新聞", "一般小節標題（不附圖）", "兩三句交代事件。")]
        el = [_it(72 + k, "新聞", "重點", "一兩句內容。") for k in range(2)]
        mm = [_it(80, "訃聞", "姓名（生年–卒年）", "辭世日期、地點、享年；代表作與在電影音樂上的意義。",
                  media=[{"kind": "image", "url": "", "credit": ""}]),
              _it(81, "訃聞", "姓名（生年–卒年）", "編輯指定不放肖像時用純文字。")]
        mb = [_it(82, "訃聞", "", "姓名、身分（日期，享年，來源）")]
        items += nf + cr + eu + el + mm + mb
        sections = [{"section": "本期專題", "items": [feat["id"]]},
                    {"section": "快訊", "items": [x["id"] for x in nf]},
                    {"section": "社群雷達", "items": [x["id"] for x in cr]},
                    {"section": "歐亞觀察", "items": [x["id"] for x in eu], "list": [x["id"] for x in el]},
                    {"section": "In memoriam", "items": [x["id"] for x in mm], "brief": [x["id"] for x in mb]}]
        weekend = {}
    issue = {"issue": f"YYYY-MM-{edition}", "edition": edition, "date": "2026-11-20" if edition == "news" else "2026-11-05",
             "kicker": f"FILM MUSIC NEWSLETTER · MONTH YYYY · {'深度聆聽版' if edition == 'collector' else '配樂新訊版'}",
             "editor_note": "編者的話：四句以內、約 100 字。第一句寫本期最打動人的一件事，其他重點一句帶過，最後一句可以是邀請。不加標題、不署名、不寫評分。",
             "sections": sections, "weekend": weekend,
             "sources_footer": "本期實際用到的網站與頻道名稱，以頓號分隔。", "cutoff": "YYYY 年 M 月 D 日（臺北時間）。"}
    return issue, {x["id"]: x for x in items}

# Cue Sheet

給電影配樂樂迷的中文電子報網站：https://mesple.github.io/cuesheet/

| 網址 | 內容 | 檔案 |
| --- | --- | --- |
| `/cuesheet/` | 首頁 | `index.html`（由 `build_pages.py` 產生） |
| `/cuesheet/newsletter/` | 電子報（深度聆聽版、配樂新訊版與特刊同列） | `newsletter/index.html`（由 `build_pages.py` 產生）、各期 `newsletter/YYYY-MM/index.html` |
| `/cuesheet/category/` | 分類瀏覽：新聞、樂評、發行、訪談、試聽、訃聞、社群 | `category/`（由 `build_items.py` 產生） |
| `/cuesheet/item/<id>/` | 單則頁，例 `/item/2026-10-001/` | `item/`（由 `build_items.py` 產生） |
| `/cuesheet/event/` | 近期國內電影音樂活動 | `event/index.html`，讀取根目錄的 `events.json`、`manual_events.json` |

## 新增一期電子報

1. 用 `python tools/web_version.py 電子報版.html newsletter/YYYY-MM-xxx/index.html` 由電子報版產生網站版（拿掉網頁版連結與退訂，活動欄加「已結束」標示），放到 `newsletter/YYYY-MM-collector/index.html`（深度聆聽版，每月 5 日）或 `newsletter/YYYY-MM-news/index.html`（配樂新訊版，每月 20 日），特刊用 `newsletter/YYYY-MM-special/`，圖片放 `images/YYYY-MM/`。
2. 在 `newsletter/issues.json` 加一筆（`editor_note` 是刊頭下方的編者的話，也是首頁與列表頁的摘要）。
3. 執行 `python build_pages.py`，更新首頁與電子報列表。

## 活動資料

- 每天臺灣時間 07:17 由 GitHub Actions 執行 `fetch_events.py`，抓文化部藝文活動開放資料（音樂、講座、電影、演唱會），依 `keywords.txt` 篩選，結果寫入 `events.json`；執行紀錄在 `last_run.json`，邊緣個案在 `candidates.json`。
- `manual_events.json`：新聞補漏與編輯補登的場次（民間主辦、未登錄開放資料者）。`note` 會顯示給讀者，只給編輯看的註記寫在 `internal_note`。
- 抓取防護：某類別筆數低於基準 50% 時沿用上次資料；失敗會自動重試。
- `build_section.py`：把活動資料排成電子報最後一欄的 HTML。例：`python build_section.py events.json 2026-11-16 60 preview.html https://mesple.github.io/cuesheet/event/`
- 長期展覽（2026-10-27 新增）：在 `manual_events.json` 用 `category: "展覽"` 加 `run`（`start`、`end`、`venue`、`city`），`shows` 留空。電子報與活動頁只列一筆、顯示展期，標「展覽」，不提供加入行事曆。只放在開展的那個月：活動頁列在開展日、該月過完就不列；電子報只放開展後的第一期配樂新訊版（不想放時用 `--skip=uid`）。展覽由編輯手動補登，不抓文化部「展覽」類。
- 文化部「電影」類一律標「影展活動」；電子報中同一部片在同一地區的放映合併成一列。
- 配樂新訊版用精簡版：`python build_section.py events.json 2026-11-20 30 preview.html --slim`。以節目計算、每區最多 2 個節目（預設日期最近），欄末連到活動頁「到線上版看更多精彩節目」；終端機會列出未選入的節目，可用 `--pick=uid1,uid2` 換上。
- `.github/workflows/keepalive.yml`：每月 1 日檢查，40 天沒有提交時留一筆紀錄，避免 GitHub 停用排程。

資料來源：文化部藝文活動開放資料，依政府資料開放授權條款使用。

## 舊網址

2026-10 以前的網址在 `mesple/cuesheet-events`（https://mesple.github.io/cuesheet-events/），已改為轉址到本站；已寄出電子報引用的圖片仍保留在那裡。

## 固定網址：最新一期（歡迎信用，2026-10-26 新增）

- `/cuesheet/newsletter/latest-collector/` → 最新一期深度聆聽版
- `/cuesheet/newsletter/latest-news/` → 最新一期配樂新訊版

由 `build_pages.py` 依 `newsletter/issues.json` 的 `edition` 自動產生（試刊 `trial` 兩版都算）。MailerLite 歡迎信連到這兩個網址，出新一期時不用改信。

## 單則資料與分類頁（2026-10-28 新增）

- `items/YYYY-MM.json`：每期的單則，一則一筆（欄位見專案檔案庫 `site/cue_sheet_資料欄位草案.md`）。`web`：`true` 上網站、`false` 不上、`null` 待編輯決定；只有 `true` 會產生頁面。`internal_note` 只給編輯看。
- `issues/YYYY-MM.json`：該期刊頭、編者的話、每欄放哪幾則、週末cue一下。
- `composers.json`：作曲家代號與顯示名（華人用中文、日本人有漢字用漢字），單則頁會把原刊寫法換成顯示名。
- 改完資料執行 `python build_items.py`，重建 `item/` 與 `category/`；首頁、列表有變動再執行 `python build_pages.py`。
- 10 月號試刊是從已排版的 HTML 拆出來的（`tools/split_2026-10.py`、`tools/assemble_2026-10.py`，一次性）；之後各期直接寫成單則資料。

## 網站版的「已結束」標示（2026-10-28 新增）

- `build_section.py` 在每列活動加上 `data-end`（該列最後一場的日期）。電子報版不受影響。
- `tools/web_version.py` 在網站版活動欄開頭加一行說明，並附一小段程式：讀者打開頁面時，依臺北時間比對 `data-end`，已結束的場次變淡、標「已結束」。
- 10 月號試刊已補上（舊刊沒有 `data-end` 時，程式會從左欄日期推算）。

## 寫稿規則檢查（2026-10-31 新增）

`python build_items.py` 開頭會先檢查單則資料，列出違規的單則（只提醒，不擋建站），上線前修正：

1. 標題不放日期（日期寫在摘要）。
2. 新聞摘要要寫出作曲家名（全名或姓氏），列表才會自動連到作曲家頁。
3. 新聞、社群雷達的短文摘要不寫來源名；來源由程式接在文末括號。
4. 兩個中文字之間不空格（中英文之間照常空一格）。

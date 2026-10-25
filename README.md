# Cue Sheet

給電影配樂樂迷的中文電子報網站：https://mesple.github.io/cuesheet/

| 網址 | 內容 | 檔案 |
| --- | --- | --- |
| `/cuesheet/` | 首頁 | `index.html`（由 `build_pages.py` 產生） |
| `/cuesheet/newsletter/` | 電子報（重度聆聽版、配樂新訊版與特刊同列） | `newsletter/index.html`（由 `build_pages.py` 產生）、各期 `newsletter/YYYY-MM/index.html` |
| `/cuesheet/event/` | 近期國內電影音樂活動 | `event/index.html`，讀取根目錄的 `events.json`、`manual_events.json` |

## 新增一期電子報

1. 把該期網頁版放到 `newsletter/YYYY-MM-collector/index.html`（重度聆聽版，每月 5 日）或 `newsletter/YYYY-MM-news/index.html`（配樂新訊版，每月 20 日），特刊用 `newsletter/YYYY-MM-special/`，圖片放 `images/YYYY-MM/`。
2. 在 `newsletter/issues.json` 加一筆（`editor_note` 是刊頭下方的編者的話，也是首頁與列表頁的摘要）。
3. 執行 `python build_pages.py`，更新首頁與電子報列表。

## 活動資料

- 每天臺灣時間 07:17 由 GitHub Actions 執行 `fetch_events.py`，抓文化部藝文活動開放資料（音樂、講座、電影、演唱會），依 `keywords.txt` 篩選，結果寫入 `events.json`；執行紀錄在 `last_run.json`，邊緣個案在 `candidates.json`。
- `manual_events.json`：新聞補漏與編輯補登的場次（民間主辦、未登錄開放資料者）。`note` 會顯示給讀者，只給編輯看的註記寫在 `internal_note`。
- 抓取防護：某類別筆數低於基準 50% 時沿用上次資料；失敗會自動重試。
- `build_section.py`：把活動資料排成電子報最後一欄的 HTML。例：`python build_section.py events.json 2026-11-16 60 preview.html https://mesple.github.io/cuesheet/event/`
- 文化部「電影」類一律標「影展活動」；電子報中同一部片在同一地區的放映合併成一列。
- 配樂新訊版用精簡版：`python build_section.py events.json 2026-11-20 30 preview.html --slim`。以節目計算、每區最多 2 個節目（預設日期最近），欄末連到活動頁「到線上版看更多精彩節目」；終端機會列出未選入的節目，可用 `--pick=uid1,uid2` 換上。
- `.github/workflows/keepalive.yml`：每月 1 日檢查，40 天沒有提交時留一筆紀錄，避免 GitHub 停用排程。

資料來源：文化部藝文活動開放資料，依政府資料開放授權條款使用。

## 舊網址

2026-10 以前的網址在 `mesple/cuesheet-events`（https://mesple.github.io/cuesheet-events/），已改為轉址到本站；已寄出電子報引用的圖片仍保留在那裡。

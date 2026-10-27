"""把電子報版 HTML 轉成網站版。

和電子報版的差別（編輯 2026-10-28 定案）：
  1. 拿掉刊頭前標右側「沒看到完整內容？請到網頁版」。
  2. 拿掉頁尾「不想再收到 Cue Sheet？取消訂閱」。
  3. 「近期國內電影音樂活動」欄：開頭說明下加一行「本欄是發刊時整理的場次……」，
     已結束的場次由瀏覽器依當天日期（臺北時間）自動變淡、標「已結束」。電子報版不做這項。

用法：
  python tools/web_version.py 電子報版.html newsletter/2026-11-news/index.html
  python tools/web_version.py newsletter/2026-10/index.html --inplace   # 已是網站版，只補第 3 項
"""
import re
import sys

EVENT_PAGE = "https://mesple.github.io/cuesheet/event/"
MARK = "data-cs-archive"

NOTE = (f'<div {MARK} style="font-size:12px;line-height:1.6;color:#7A7974;margin:0 0 6px;">'
        f'本欄是這期發刊時整理的場次，已結束的會標「已結束」；最新場次請到'
        f'<a href="{EVENT_PAGE}" style="color:#01696F;">線上活動頁</a>。</div>')

SCRIPT = f"""<script {MARK}>
(function(){{
  // 臺北時間的今天（YYYY-MM-DD）；場次最後一天早於今天就算已結束
  var today = new Date(Date.now() + 8 * 3600e3).toISOString().slice(0, 10);
  var rows = document.querySelectorAll('tr[data-end]');
  for (var i = 0; i < rows.length; i++) {{
    var tr = rows[i];
    if (tr.getAttribute('data-end') >= today) continue;
    tr.style.opacity = '.5';
    var tag = document.createElement('div');
    tag.textContent = '已結束';
    tag.style.cssText = 'display:inline-block;margin-top:4px;padding:0 5px;border:1px solid #7A7974;color:#7A7974;font-size:11px;line-height:1.5;';
    tr.cells[0].appendChild(tag);
  }}
}})();
</script>"""


def strip_email_only(html):
    # 1. 前標右側的網頁版連結（整個右側 td）
    html = re.sub(r'<td[^>]*>\s*<a [^>]*>沒看到完整內容？請到網頁版</a>\s*</td>', "", html)
    # 2. 頁尾退訂
    html = re.sub(r'\s*<br>\s*不想再收到 Cue Sheet？<a [^>]*>取消訂閱</a>', "", html)
    return html


def tag_rows(html, year, month):
    """舊刊（build_section.py 還沒輸出 data-end 時產生的）補上 data-end：取左欄最後一個 M/D。"""
    start = html.find("<!-- 11 TAIWAN EVENTS -->")
    if start < 0:
        return html
    end = html.find("<!-- FOOTER -->", start)
    end = end if end > 0 else len(html)
    sec = html[start:end]

    def fix(m):
        row = m.group(0)
        if "data-end" in row:
            return row
        left = row[:row.find("</td>")]
        left = re.sub(r"<[^>]+>", " ", left)
        dates = re.findall(r"(\d{1,2})/(\d{1,2})", left)
        if not dates:
            return row
        mm, dd = map(int, dates[-1])
        y = year + 1 if mm < month - 6 else year
        return row.replace("<tr>", f'<tr data-end="{y}-{mm:02d}-{dd:02d}">', 1)

    sec = re.sub(r'<tr>\s*<td width="86".*?</tr>', fix, sec, flags=re.S)
    return html[:start] + sec + html[end:]


def add_archive_note(html):
    if MARK in html:
        return html
    i = html.find("<!-- 11 TAIWAN EVENTS -->")
    if i < 0:
        return html
    m = re.search(r'(<div[^>]*>[^<]*依地區、日期排列。</div>)', html[i:])
    if not m:
        return html
    pos = i + m.end()
    html = html[:pos] + "\n" + NOTE + html[pos:]
    return html.replace("</body>", SCRIPT + "\n</body>", 1)


def convert(html):
    m = re.search(r"newsletter/(\d{4})-(\d{2})", html)
    year, month = (int(m.group(1)), int(m.group(2))) if m else (2026, 1)
    html = strip_email_only(html)
    html = tag_rows(html, year, month)
    return add_archive_note(html)


if __name__ == "__main__":
    src = sys.argv[1]
    dst = src if "--inplace" in sys.argv else sys.argv[2]
    out = convert(open(src, encoding="utf-8").read())
    open(dst, "w", encoding="utf-8").write(out)
    n = out.count("data-end=")
    left = [k for k in ("沒看到完整內容", "{$unsubscribe}") if k in out]
    print(f"{dst}：活動 {n} 列已標日期" + (f"；仍有電子報專用內容：{left}" if left else ""))

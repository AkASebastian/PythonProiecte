#!/usr/bin/env python3
"""
Backlink Crawler — reads from your_file.xlsx
=============================================================
Reads Source Page URLs and Anchor/Article link keywords from the
2024, 2025 and 2026 order sheets, checks each URL, and outputs
a CSV + self-contained HTML report.
 
Usage:
  1. Place this script and your_file.xlsx in the same folder
  2. Install deps:  pip install pandas openpyxl requests
  3. Run:           python backlink_checker.py
  4. Open:          backlink_report.html
"""
 
import csv
import datetime
import time
import random
import concurrent.futures
import os
import sys
 
try:
    import pandas as pd
except ImportError:
    sys.exit("Missing: run  pip install pandas openpyxl requests")
 
try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    USE_REQUESTS = True
except ImportError:
    USE_REQUESTS = False
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError
    import ssl
 
# ── CONFIGURATION ────────────────────────────────────────────────────────────
 
SPREADSHEET = "your_file.xlsx"
 
SHEETS = [
    {"name": "2026 Order List",  "url_col": "Source Page", "kw_col": "Anchor/Article link"},
    {"name": "2025 order List",  "url_col": "Source Page", "kw_col": "Anchor/Article link"},
    {"name": "2024 Order list",  "url_col": "Source Page", "kw_col": "Anchor/Article link"},
]
 
OUTPUT_CSV  = "backlink_report.csv"
OUTPUT_HTML = "backlink_report.html"
 
MAX_WORKERS   = 5
TIMEOUT       = 10
REQUEST_DELAY = 0.3
 
# ─────────────────────────────────────────────────────────────────────────────
 
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}
 
 
def load_entries():
    if not os.path.exists(SPREADSHEET):
        sys.exit(
            f"Spreadsheet not found: {SPREADSHEET}\n"
            "Place the .xlsx file in the same folder as this script."
        )
 
    entries = []
    xl = pd.ExcelFile(SPREADSHEET)
 
    for cfg in SHEETS:
        sheet_name = cfg["name"]
        if sheet_name not in xl.sheet_names:
            print(f"  [warn] Sheet '{sheet_name}' not found — skipping")
            continue
 
        df = pd.read_excel(SPREADSHEET, sheet_name=sheet_name)
        url_col = cfg["url_col"]
        kw_col  = cfg["kw_col"]
 
        if url_col not in df.columns:
            print(f"  [warn] Column '{url_col}' missing in '{sheet_name}' — skipping")
            continue
 
        for _, row in df.iterrows():
            url = str(row[url_col]).strip() if pd.notna(row[url_col]) else ""
            kw  = str(row[kw_col]).strip()  if (kw_col in df.columns and pd.notna(row.get(kw_col))) else ""
            if not url or not url.startswith("http"):
                continue
            entries.append({"url": url, "keyword": kw, "sheet": sheet_name})
 
    return entries
 
 
def check_requests(entry):
    url = entry["url"]
    time.sleep(random.uniform(0, REQUEST_DELAY))
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False, allow_redirects=True)
        code = resp.status_code
        redir = f" -> redirected to {resp.url}" if resp.url.rstrip("/") != url.rstrip("/") else ""
        if 200 <= code < 300:
            return {**entry, "status": "live",  "http_code": str(code), "note": f"Page is live{redir}"}
        elif code == 403:
            return {**entry, "status": "warn",  "http_code": "403", "note": "Forbidden — may exist but blocks crawlers"}
        elif code in (404, 410):
            labels = {404: "Page not found (404)", 410: "Page permanently gone (410)"}
            return {**entry, "status": "dead",  "http_code": str(code), "note": labels[code]}
        elif code == 429:
            return {**entry, "status": "warn",  "http_code": "429", "note": "Rate limited — try again later"}
        elif 300 <= code < 400:
            return {**entry, "status": "warn",  "http_code": str(code), "note": f"Redirect{redir}"}
        elif code >= 500:
            return {**entry, "status": "warn",  "http_code": str(code), "note": f"Server error ({code})"}
        else:
            return {**entry, "status": "dead",  "http_code": str(code), "note": f"Unexpected status {code}"}
    except requests.exceptions.ConnectionError as e:
        err = str(e)
        note = "Domain does not exist" if ("NameResolutionError" in err or "Name or service not known" in err) else f"Connection error: {err[:80]}"
        return {**entry, "status": "dead", "http_code": "-", "note": note}
    except requests.exceptions.Timeout:
        return {**entry, "status": "warn", "http_code": "-", "note": "Request timed out"}
    except Exception as e:
        return {**entry, "status": "warn", "http_code": "-", "note": f"Error: {str(e)[:80]}"}
 
 
def check_stdlib(entry):
    import urllib.parse
    url = entry["url"]
    time.sleep(random.uniform(0, REQUEST_DELAY))
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return {**entry, "status": "dead", "http_code": "-", "note": "Invalid URL"}
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=TIMEOUT, context=ctx) as resp:
            code = resp.getcode()
            redir = f" -> {resp.geturl()}" if resp.geturl().rstrip("/") != url.rstrip("/") else ""
            return {**entry, "status": "live" if 200 <= code < 300 else "warn",
                    "http_code": str(code), "note": f"HTTP {code}{redir}"}
    except HTTPError as e:
        status = "dead" if e.code in (404, 410) else "warn"
        return {**entry, "status": status, "http_code": str(e.code), "note": f"HTTP error {e.code}"}
    except URLError as e:
        note = "Domain does not exist" if "Name or service not known" in str(e.reason) else f"Unreachable: {str(e.reason)[:80]}"
        return {**entry, "status": "dead", "http_code": "-", "note": note}
    except Exception as e:
        return {**entry, "status": "warn", "http_code": "-", "note": str(e)[:80]}
 
 
check_url = check_requests if USE_REQUESTS else check_stdlib
 
 
def write_csv(results, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["sheet", "url", "keyword", "status", "http_code", "note"])
        w.writeheader()
        w.writerows(results)
 
 
def write_html(results, path):
    total = len(results)
    live  = sum(1 for r in results if r["status"] == "live")
    dead  = sum(1 for r in results if r["status"] == "dead")
    warn  = sum(1 for r in results if r["status"] == "warn")
    now   = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
 
    sheets_seen = list(dict.fromkeys(r["sheet"] for r in results))
    sheet_pills = "".join(
        f'<button class="pill" onclick="filterSheet(\'{s.replace(chr(39), chr(92)+chr(39))}\',this)">{s}</button>\n'
        for s in sheets_seen
    )
 
    def badge(s):
        labels = {"live": "Live", "dead": "Dead", "warn": "Uncertain"}
        return f'<span class="badge {s}">{labels.get(s, s)}</span>'
 
    def esc(s):
        return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
 
    rows_html = "".join(
        f'<tr class="row-{r["status"]}" data-sheet="{esc(r["sheet"])}">'
        f'<td class="sheet-cell">{esc(r["sheet"])}</td>'
        f'<td class="url-cell"><a href="{esc(r["url"])}" target="_blank" rel="noopener">{esc(r["url"])}</a></td>'
        f'<td>{esc(r.get("keyword",""))}</td>'
        f'<td>{badge(r["status"])}</td>'
        f'<td class="code">{esc(r["http_code"])}</td>'
        f'<td>{esc(r["note"])}</td>'
        f'</tr>'
        for r in results
    )
 
    safe_now = now.replace(":", "-").replace(" ", "_")
 
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Backlink Report — {now}</title>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#0e0e0f;--surface:#18181b;--surface2:#232328;
  --border:rgba(255,255,255,0.08);--text:#f0efe8;--muted:#888884;
  --accent:#c8f135;
  --live:#4ade80;--live-bg:rgba(74,222,128,0.1);
  --dead:#f87171;--dead-bg:rgba(248,113,113,0.1);
  --warn:#fbbf24;--warn-bg:rgba(251,191,36,0.1);
}}
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700&display=swap');
body{{background:var(--bg);color:var(--text);font-family:'DM Mono',monospace;padding:2.5rem 1.5rem 5rem}}
.wrap{{max-width:1100px;margin:0 auto}}
.eyebrow{{font-size:11px;letter-spacing:.12em;color:var(--accent);text-transform:uppercase;margin-bottom:8px}}
h1{{font-family:'Syne',sans-serif;font-size:2.2rem;font-weight:700;margin-bottom:6px}}
h1 span{{color:var(--accent)}}
.meta{{font-size:12px;color:var(--muted);margin-bottom:2rem}}
.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:2rem}}
@media(max-width:520px){{.stats{{grid-template-columns:repeat(2,1fr)}}}}
.stat{{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px}}
.stat-num{{font-family:'Syne',sans-serif;font-size:2rem;font-weight:700;line-height:1}}
.stat-num.all{{color:var(--text)}}.stat-num.live{{color:var(--live)}}
.stat-num.dead{{color:var(--dead)}}.stat-num.warn{{color:var(--warn)}}
.stat-label{{font-size:11px;color:var(--muted);margin-top:6px;text-transform:uppercase;letter-spacing:.08em}}
.section-label{{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px}}
.filter-bar{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:.75rem;align-items:center}}
.pill{{font-size:12px;padding:5px 14px;border-radius:99px;border:1px solid var(--border);
  background:transparent;color:var(--muted);cursor:pointer;font-family:'DM Mono',monospace;transition:all .12s}}
.pill:hover{{border-color:rgba(255,255,255,.2);color:var(--text)}}
.pill.active{{background:rgba(200,241,53,.12);border-color:var(--accent);color:var(--accent)}}
.export{{font-size:12px;padding:5px 14px;border-radius:99px;border:1px solid var(--border);
  background:transparent;color:var(--muted);cursor:pointer;font-family:'DM Mono',monospace;
  transition:all .12s;margin-left:auto}}
.export:hover{{border-color:rgba(255,255,255,.2);color:var(--text)}}
.divider{{border:none;border-top:1px solid var(--border);margin:.75rem 0 1rem}}
.table-wrap{{overflow-x:auto}}
table{{width:100%;border-collapse:collapse;font-size:12px}}
thead th{{text-align:left;padding:10px 12px;color:var(--muted);border-bottom:1px solid var(--border);
  font-size:11px;text-transform:uppercase;letter-spacing:.08em;white-space:nowrap}}
tbody tr{{border-bottom:1px solid var(--border);transition:background .1s}}
tbody tr:hover{{background:var(--surface)}}
td{{padding:10px 12px;vertical-align:top}}
.sheet-cell{{color:var(--muted);white-space:nowrap;font-size:11px}}
.url-cell a{{color:var(--accent);text-decoration:none;word-break:break-all}}
.url-cell a:hover{{text-decoration:underline}}
.code{{color:var(--muted);white-space:nowrap}}
.badge{{font-size:10px;letter-spacing:.08em;text-transform:uppercase;padding:3px 10px;
  border-radius:99px;border:1px solid;white-space:nowrap}}
.badge.live{{background:var(--live-bg);color:var(--live);border-color:rgba(74,222,128,.25)}}
.badge.dead{{background:var(--dead-bg);color:var(--dead);border-color:rgba(248,113,113,.25)}}
.badge.warn{{background:var(--warn-bg);color:var(--warn);border-color:rgba(251,191,36,.25)}}
.hidden{{display:none!important}}
</style>
</head>
<body>
<div class="wrap">
  <div class="eyebrow">// backlink report</div>
  <h1>Backlink <span>Crawler</span></h1>
  <p class="meta">Generated {now} &nbsp;&middot;&nbsp; {total} URLs checked across {len(sheets_seen)} sheets</p>
 
  <div class="stats">
    <div class="stat"><div class="stat-num all">{total}</div><div class="stat-label">Total</div></div>
    <div class="stat"><div class="stat-num live">{live}</div><div class="stat-label">Live</div></div>
    <div class="stat"><div class="stat-num dead">{dead}</div><div class="stat-label">Dead</div></div>
    <div class="stat"><div class="stat-num warn">{warn}</div><div class="stat-label">Uncertain</div></div>
  </div>
 
  <div class="section-label">Filter by status</div>
  <div class="filter-bar" id="status-bar">
    <button class="pill active" onclick="filterStatus('all',this)">All</button>
    <button class="pill" onclick="filterStatus('live',this)">Live</button>
    <button class="pill" onclick="filterStatus('dead',this)">Dead</button>
    <button class="pill" onclick="filterStatus('warn',this)">Uncertain</button>
    <button class="export" onclick="exportCSV()">Export CSV ↓</button>
  </div>
 
  <div class="section-label">Filter by sheet</div>
  <div class="filter-bar" id="sheet-bar">
    <button class="pill active" onclick="filterSheet('all',this)">All sheets</button>
    {sheet_pills}
  </div>
 
  <div class="divider"></div>
  <div class="table-wrap">
    <table id="tbl">
      <thead>
        <tr>
          <th>Sheet</th>
          <th style="min-width:260px">Source URL</th>
          <th style="min-width:120px">Keyword</th>
          <th>Status</th>
          <th>Code</th>
          <th>Note</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
  </div>
</div>
<script>
let activeStatus='all', activeSheet='all';
function applyFilters(){{
  document.querySelectorAll('#tbl tbody tr').forEach(tr=>{{
    const ok=(activeStatus==='all'||tr.classList.contains('row-'+activeStatus))
           &&(activeSheet==='all'||tr.dataset.sheet===activeSheet);
    tr.classList.toggle('hidden',!ok);
  }});
}}
function filterStatus(f,btn){{
  activeStatus=f;
  document.querySelectorAll('#status-bar .pill').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active'); applyFilters();
}}
function filterSheet(s,btn){{
  activeSheet=s;
  document.querySelectorAll('#sheet-bar .pill').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active'); applyFilters();
}}
function exportCSV(){{
  const rows=[['Sheet','URL','Keyword','Status','Code','Note']];
  document.querySelectorAll('#tbl tbody tr:not(.hidden)').forEach(tr=>{{
    const c=tr.querySelectorAll('td');
    rows.push([c[0].textContent,c[1].querySelector('a').href,c[2].textContent,
               c[3].textContent.trim(),c[4].textContent,c[5].textContent]);
  }});
  const csv=rows.map(r=>r.map(c=>'"'+String(c).replace(/"/g,'""')+'"').join(',')).join('\\n');
  const a=document.createElement('a');
  a.href='data:text/csv;charset=utf-8,'+encodeURIComponent(csv);
  a.download='backlinks_{safe_now}.csv'; a.click();
}}
</script>
</body>
</html>"""
 
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
 
 
def main():
    print("Loading URLs from spreadsheet...")
    entries = load_entries()
 
    if not entries:
        print("No valid URLs found. Check the spreadsheet path and column names.")
        return
 
    seen, unique = set(), []
    for e in entries:
        if e["url"] not in seen:
            seen.add(e["url"])
            unique.append(e)
 
    dupes = len(entries) - len(unique)
    print(f"Found {len(entries)} URLs ({dupes} duplicates removed -> {len(unique)} to check)\n")
 
    results = []
    completed = 0
 
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        future_map = {ex.submit(check_url, e): e for e in unique}
        for future in concurrent.futures.as_completed(future_map):
            result = future.result()
            results.append(result)
            completed += 1
            icon = {"live": "v", "dead": "x", "warn": "?"}.get(result["status"], "?")
            print(f"  [{completed:>3}/{len(unique)}] {icon} {result['status'].upper():<9}  {result['url']}")
 
    order = {"dead": 0, "warn": 1, "live": 2}
    results.sort(key=lambda r: (order.get(r["status"], 3), r.get("sheet", "")))
 
    write_csv(results, OUTPUT_CSV)
    write_html(results, OUTPUT_HTML)
 
    live = sum(1 for r in results if r["status"] == "live")
    dead = sum(1 for r in results if r["status"] == "dead")
    warn = sum(1 for r in results if r["status"] == "warn")
 
    print(f"\n{'─'*55}")
    print(f"  Done!  {len(results)} unique URLs checked")
    print(f"  Live:       {live}")
    print(f"  Dead:       {dead}")
    print(f"  Uncertain:  {warn}")
    print(f"{'─'*55}")
    print(f"  Report  ->  {OUTPUT_HTML}")
    print(f"  CSV     ->  {OUTPUT_CSV}")
 
 
if __name__ == "__main__":
    main()
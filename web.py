#!/usr/bin/env python3
"""
OSINT Username Checker — Web Interface

Jalankan:  .venv/bin/python web.py
Lalu buka: http://127.0.0.1:8000
"""

import json

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, StreamingResponse

from osint.checker import UsernameChecker

app = FastAPI(title="OSINT Username Checker")


@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_PAGE


@app.get("/scan")
async def scan(
    username: str = Query(..., min_length=1, max_length=100),
    timeout: int = Query(10, ge=1, le=60),
    concurrency: int = Query(50, ge=1, le=200),
):
    """Stream hasil scan satu per satu via Server-Sent Events."""
    checker = UsernameChecker(timeout=timeout, concurrency=concurrency)

    async def event_stream():
        yield _sse({"type": "start", "total": len(checker.platforms), "username": username})
        async for result in checker.check_all(username):
            yield _sse({"type": "result", **result})
        yield _sse({"type": "done"})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


HTML_PAGE = r"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OSINT Username Checker</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🔍</text></svg>">
<style>
  :root {
    --bg:#0b0f17; --bg2:#0d1320; --panel:#141b2b; --panel2:#1a2335;
    --border:#26314a; --border2:#33415f;
    --text:#e8eef7; --muted:#8b98b0; --faint:#5e6b85;
    --green:#3fb950; --green-bg:rgba(63,185,80,.14);
    --blue:#58a6ff; --amber:#e3b341; --amber-bg:rgba(227,179,65,.14);
    --red:#f85149; --red-bg:rgba(248,81,73,.14);
    --grey-bg:rgba(139,152,176,.12);
    --shadow:0 8px 30px rgba(0,0,0,.35);
    --r:14px;
  }
  * { box-sizing:border-box; }
  html,body { margin:0; }
  body {
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Inter,sans-serif;
    background:
      radial-gradient(1200px 600px at 80% -10%, rgba(88,166,255,.10), transparent 60%),
      radial-gradient(900px 500px at -10% 10%, rgba(63,185,80,.08), transparent 55%),
      var(--bg);
    color:var(--text); line-height:1.55; min-height:100vh;
    -webkit-font-smoothing:antialiased;
  }
  .wrap { max-width:1040px; margin:0 auto; padding:40px 20px 100px; }

  header.top { display:flex; align-items:center; gap:14px; margin-bottom:6px; }
  header.top .logo { font-size:30px; line-height:1; filter:drop-shadow(0 2px 6px rgba(88,166,255,.4)); }
  h1 { font-size:26px; margin:0; letter-spacing:-.3px; }
  .sub { color:var(--muted); margin:0 0 28px; font-size:14.5px; }

  .card {
    background:linear-gradient(180deg,var(--panel),var(--bg2));
    border:1px solid var(--border); border-radius:var(--r);
    box-shadow:var(--shadow);
  }
  .search-card { padding:22px; }

  form { display:flex; gap:12px; align-items:center; }
  .input-wrap { position:relative; flex:1; }
  .input-wrap .at { position:absolute; left:14px; top:50%; transform:translateY(-50%); color:var(--faint); font-size:17px; pointer-events:none; }
  input, select {
    background:var(--bg); border:1px solid var(--border2); color:var(--text);
    border-radius:10px; font-size:15px; outline:none; transition:border-color .15s, box-shadow .15s;
  }
  input:focus, select:focus { border-color:var(--blue); box-shadow:0 0 0 3px rgba(88,166,255,.18); }
  #username { width:100%; padding:13px 14px 13px 34px; font-size:16px; }
  .small { width:84px; padding:13px 10px; }

  button.primary {
    background:linear-gradient(180deg,#3fb950,#2ea043); color:#04210b;
    border:0; padding:13px 26px; border-radius:10px; font-size:15px; font-weight:700;
    cursor:pointer; white-space:nowrap; transition:filter .15s, transform .05s;
  }
  button.primary:hover { filter:brightness(1.06); }
  button.primary:active { transform:translateY(1px); }
  button.primary:disabled { opacity:.55; cursor:not-allowed; filter:none; }

  .adv-toggle { margin-top:14px; font-size:13px; color:var(--blue); cursor:pointer; user-select:none; display:inline-flex; align-items:center; gap:5px; }
  .adv-toggle:hover { text-decoration:underline; }
  .adv { display:none; gap:18px; margin-top:14px; padding-top:16px; border-top:1px solid var(--border); }
  .adv.open { display:flex; flex-wrap:wrap; }
  .field { display:flex; flex-direction:column; gap:6px; }
  .field label { font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:.6px; font-weight:600; }

  /* progress */
  .progress { margin-top:18px; display:none; }
  .progress.active { display:block; }
  .bar-bg { background:var(--bg); border:1px solid var(--border); border-radius:999px; height:10px; overflow:hidden; }
  .bar-fill { background:linear-gradient(90deg,#2ea043,#3fb950,#58a6ff); height:100%; width:0; border-radius:999px; transition:width .2s ease; }
  .progress-text { font-size:13px; color:var(--muted); margin-top:9px; display:flex; justify-content:space-between; gap:10px; }

  /* stats */
  .stats { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:26px 0 18px; }
  .stat { padding:14px 16px; border-radius:12px; border:1px solid var(--border); background:var(--panel); }
  .stat .n { font-size:24px; font-weight:800; line-height:1; }
  .stat .l { font-size:12px; color:var(--muted); margin-top:6px; }
  .stat.ok .n { color:var(--green); } .stat.no .n { color:var(--muted); }
  .stat.bl .n { color:var(--amber); } .stat.er .n { color:var(--red); }

  /* toolbar */
  .toolbar { display:none; gap:10px; align-items:center; margin:6px 0 16px; flex-wrap:wrap; }
  .toolbar.active { display:flex; }
  .toolbar .filter { flex:1; min-width:200px; position:relative; }
  .toolbar .filter input { width:100%; padding:10px 12px 10px 34px; font-size:14px; }
  .toolbar .filter .ico { position:absolute; left:11px; top:50%; transform:translateY(-50%); color:var(--faint); }
  .btn {
    background:var(--panel2); border:1px solid var(--border2); color:var(--text);
    padding:10px 14px; border-radius:10px; font-size:13.5px; font-weight:600; cursor:pointer;
    display:inline-flex; align-items:center; gap:7px; transition:background .15s, border-color .15s;
  }
  .btn:hover { background:var(--border); border-color:var(--blue); }

  /* results */
  .group-title {
    display:flex; align-items:center; gap:10px;
    font-size:13px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:.7px;
    margin:22px 0 12px;
  }
  .group-title .count { color:var(--faint); font-weight:600; }
  .group-title::after { content:""; flex:1; height:1px; background:var(--border); }

  .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:12px; }
  .tile {
    background:var(--panel); border:1px solid var(--border); border-radius:12px;
    padding:14px 15px; display:flex; flex-direction:column; gap:8px;
    transition:border-color .15s, transform .15s, box-shadow .15s;
    animation:pop .25s ease both;
  }
  .tile:hover { border-color:var(--green); transform:translateY(-2px); box-shadow:0 6px 18px rgba(0,0,0,.3); }
  @keyframes pop { from{opacity:0; transform:translateY(6px) scale(.98);} to{opacity:1; transform:none;} }
  .tile .row1 { display:flex; align-items:center; justify-content:space-between; gap:8px; }
  .tile .pname { font-weight:700; font-size:15.5px; display:flex; align-items:center; gap:8px; }
  .tile .pname .dot { width:8px; height:8px; border-radius:50%; background:var(--green); box-shadow:0 0 8px var(--green); }
  .tile a.link { color:var(--blue); font-size:13px; text-decoration:none; word-break:break-all; }
  .tile a.link:hover { text-decoration:underline; }
  .tile .actions { display:flex; gap:6px; }
  .icon-btn {
    background:transparent; border:1px solid var(--border2); color:var(--muted);
    width:30px; height:30px; border-radius:8px; cursor:pointer; font-size:13px;
    display:inline-flex; align-items:center; justify-content:center; transition:all .15s;
  }
  .icon-btn:hover { color:var(--text); border-color:var(--blue); background:var(--panel2); }

  .badge { font-size:11px; padding:3px 9px; border-radius:999px; font-weight:700; letter-spacing:.3px; }
  .b-dev{background:rgba(88,166,255,.16);color:#79c0ff}
  .b-social{background:rgba(210,168,255,.16);color:#d2a8ff}
  .b-professional{background:rgba(165,214,255,.16);color:#a5d6ff}
  .b-gaming{background:rgba(63,185,80,.16);color:#3fb950}
  .b-creative{background:rgba(227,179,65,.16);color:#e3b341}
  .b-forum{background:rgba(248,81,73,.16);color:#ff7b72}
  .b-tech{background:rgba(121,192,255,.16);color:#79c0ff}
  .b-indonesia{background:rgba(255,166,87,.16);color:#ffa657}
  .b-other{background:var(--grey-bg);color:var(--muted)}

  /* collapsible other sections */
  details.sec { margin-top:14px; }
  details.sec summary {
    cursor:pointer; list-style:none; padding:13px 16px; border:1px solid var(--border);
    border-radius:12px; background:var(--panel); font-size:14px; font-weight:600;
    display:flex; align-items:center; gap:10px; user-select:none;
  }
  details.sec summary:hover { border-color:var(--border2); }
  details.sec summary::-webkit-details-marker { display:none; }
  details.sec summary .chev { transition:transform .2s; color:var(--faint); }
  details.sec[open] summary .chev { transform:rotate(90deg); }
  details.sec .sec-body { padding:8px 4px 0; }
  .minirow { display:flex; align-items:center; gap:10px; padding:8px 12px; font-size:13.5px; border-bottom:1px solid var(--border); }
  .minirow:last-child { border-bottom:0; }
  .minirow .pn { font-weight:600; min-width:140px; }
  .minirow .mu { color:var(--muted); }
  .minirow a { color:var(--blue); text-decoration:none; word-break:break-all; }

  .empty { text-align:center; color:var(--muted); padding:48px 20px; }
  .empty .big { font-size:40px; margin-bottom:10px; }

  .hint { font-size:12.5px; color:var(--faint); margin-top:24px; text-align:center; }
  footer.credit {
    margin-top:18px; padding-top:18px; border-top:1px solid var(--border);
    text-align:center; font-size:13px; color:var(--muted); line-height:1.8;
  }
  footer.credit a { color:var(--blue); text-decoration:none; }
  footer.credit a:hover { text-decoration:underline; }
  footer.credit .name { color:var(--text); font-weight:700; }
  footer.credit .sep { color:var(--faint); margin:0 8px; }
  .toast {
    position:fixed; bottom:24px; left:50%; transform:translateX(-50%) translateY(20px);
    background:var(--panel2); border:1px solid var(--border2); color:var(--text);
    padding:11px 18px; border-radius:10px; font-size:14px; box-shadow:var(--shadow);
    opacity:0; pointer-events:none; transition:all .25s; z-index:50;
  }
  .toast.show { opacity:1; transform:translateX(-50%) translateY(0); }

  @media (max-width:640px){
    .stats{grid-template-columns:repeat(2,1fr);}
    form{flex-direction:column; align-items:stretch;}
    button.primary{width:100%;}
  }
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <span class="logo">🔍</span>
    <h1>OSINT Username Checker</h1>
  </header>
  <p class="sub">Cek jejak sebuah username di puluhan platform sosial media &amp; developer sekaligus.</p>

  <div class="card search-card">
    <form id="scanForm" autocomplete="off">
      <div class="input-wrap">
        <span class="at">@</span>
        <input id="username" name="username" placeholder="masukkan username, mis. johndoe" required>
      </div>
      <button id="scanBtn" class="primary" type="submit">Scan</button>
    </form>

    <div class="adv-toggle" id="advToggle">⚙ Opsi lanjutan</div>
    <div class="adv" id="adv">
      <div class="field">
        <label for="timeout">Timeout (detik)</label>
        <input id="timeout" class="small" type="number" value="10" min="1" max="60">
      </div>
      <div class="field">
        <label for="concurrency">Request paralel</label>
        <input id="concurrency" class="small" type="number" value="50" min="1" max="200">
      </div>
    </div>

    <div class="progress" id="progress">
      <div class="bar-bg"><div class="bar-fill" id="barFill"></div></div>
      <div class="progress-text">
        <span id="progressLabel">Menyiapkan…</span>
        <span id="progressPct">0%</span>
      </div>
    </div>
  </div>

  <div id="statsWrap"></div>
  <div class="toolbar" id="toolbar">
    <div class="filter">
      <span class="ico">⌕</span>
      <input id="filterInput" placeholder="Filter platform…">
    </div>
    <button class="btn" id="copyBtn">📋 Copy semua URL</button>
    <button class="btn" id="jsonBtn">⬇ Download JSON</button>
  </div>

  <div id="results"></div>

  <p class="hint">Hanya untuk edukasi &amp; riset OSINT. Hasil "ditemukan" bisa saja false-positive — verifikasi manual lewat link.</p>

  <footer class="credit">
    Created by <a class="name" href="https://muhamadakbarfadilah.my.id/" target="_blank" rel="noopener">Akbar Fadilah</a>
    <span class="sep">·</span>
    Founder &amp; Co-Founder at <a href="https://afdatech.com/" target="_blank" rel="noopener">Afda Technology Solutions</a>
  </footer>
</div>

<div class="toast" id="toast"></div>

<script>
const $ = (id) => document.getElementById(id);
const form = $('scanForm'), btn = $('scanBtn');
const progress = $('progress'), barFill = $('barFill');
const progressLabel = $('progressLabel'), progressPct = $('progressPct');
const statsWrap = $('statsWrap'), toolbar = $('toolbar'), resultsEl = $('results');
const CAT_CLASS = { Developer:'dev', Social:'social', Professional:'professional', Gaming:'gaming', Creative:'creative', Forum:'forum', Tech:'tech', Indonesia:'indonesia' };

let es = null, all = [], lastUsername = '';

$('advToggle').onclick = () => $('adv').classList.toggle('open');

form.addEventListener('submit', (e) => {
  e.preventDefault();
  const username = $('username').value.trim();
  if (!username) return;
  startScan(username, $('timeout').value || 10, $('concurrency').value || 50);
});

function startScan(username, timeout, concurrency) {
  if (es) es.close();
  lastUsername = username;
  all = [];
  btn.disabled = true; btn.textContent = 'Scanning…';
  progress.classList.add('active');
  barFill.style.width = '0'; progressPct.textContent = '0%';
  statsWrap.innerHTML = ''; toolbar.classList.remove('active');
  resultsEl.innerHTML = `<div class="group-title">Ditemukan <span class="count" id="liveCount">0</span></div><div class="grid" id="liveGrid"></div>`;

  let total = 0, done = 0;
  const url = `/scan?username=${encodeURIComponent(username)}&timeout=${timeout}&concurrency=${concurrency}`;
  es = new EventSource(url);

  es.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.type === 'start') {
      total = m.total;
      progressLabel.textContent = `0 / ${total} platform`;
    } else if (m.type === 'result') {
      done++; all.push(m);
      const pct = Math.round(done / total * 100);
      barFill.style.width = pct + '%'; progressPct.textContent = pct + '%';
      const found = all.filter(r => r.found).length;
      progressLabel.textContent = `${done} / ${total} platform — ${found} ditemukan`;
      if (m.found) appendLiveTile(m);
    } else if (m.type === 'done') {
      es.close(); finishScan();
    }
  };
  es.onerror = () => { es.close(); if (all.length) finishScan(); else fail(); };
}

function appendLiveTile(r) {
  const grid = $('liveGrid'); if (!grid) return;
  grid.insertAdjacentHTML('beforeend', tileHTML(r));
  const lc = $('liveCount'); if (lc) lc.textContent = all.filter(x => x.found).length;
}

function fail() {
  btn.disabled = false; btn.textContent = 'Scan';
  progress.classList.remove('active');
  resultsEl.innerHTML = `<div class="card empty"><div class="big">⚠️</div>Gagal terhubung ke server.</div>`;
}

function finishScan() {
  btn.disabled = false; btn.textContent = 'Scan';
  progress.classList.remove('active');
  render();
}

function render(filter = '') {
  const f = filter.toLowerCase();
  const match = (r) => !f || r.platform.toLowerCase().includes(f) || (r.category||'').toLowerCase().includes(f);

  const found   = all.filter(r => r.found).sort(byCat);
  const blocked = all.filter(r => r.status === 'blocked');
  const errors  = all.filter(r => r.status === 'error');
  const notFound= all.filter(r => r.status === 'not_found');

  // stats
  statsWrap.innerHTML = `<div class="stats">
    <div class="stat ok"><div class="n">${found.length}</div><div class="l">Ditemukan</div></div>
    <div class="stat no"><div class="n">${notFound.length}</div><div class="l">Tidak ada</div></div>
    <div class="stat bl"><div class="n">${blocked.length}</div><div class="l">Diblokir / ragu</div></div>
    <div class="stat er"><div class="n">${errors.length}</div><div class="l">Error</div></div>
  </div>`;
  toolbar.classList.add('active');

  let html = '';
  const visFound = found.filter(match);
  if (found.length === 0) {
    html += `<div class="card empty"><div class="big">🤔</div>Username <b>@${esc(lastUsername)}</b> tidak terdeteksi di platform manapun.</div>`;
  } else {
    // group by category
    const groups = {};
    visFound.forEach(r => (groups[r.category||'Other'] ??= []).push(r));
    html += `<div class="group-title">Ditemukan <span class="count">${visFound.length}${f?` dari ${found.length}`:''}</span></div>`;
    for (const cat of Object.keys(groups).sort()) {
      html += `<div class="grid">` + groups[cat].map(tileHTML).join('') + `</div>`;
    }
    if (visFound.length === 0) html += `<div class="empty">Tidak ada yang cocok dengan filter.</div>`;
  }

  if (blocked.length) html += sectionHTML('🛡️ Diblokir / tidak bisa dipastikan', blocked, '#e3b341');
  if (errors.length)  html += sectionHTML('⚠️ Error (timeout / koneksi)', errors, '#f85149');
  if (notFound.length)html += sectionHTML('✕ Tidak ditemukan', notFound, '#8b98b0');

  resultsEl.innerHTML = html;
}

function byCat(a, b){ return (a.category||'').localeCompare(b.category||'') || a.platform.localeCompare(b.platform); }
function catClass(c){ return 'b-' + (CAT_CLASS[c] || 'other'); }

function tileHTML(r){
  return `<div class="tile">
    <div class="row1">
      <span class="pname"><span class="dot"></span>${esc(r.platform)}</span>
      <span class="badge ${catClass(r.category)}">${esc(r.category||'Other')}</span>
    </div>
    <a class="link" href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.url)}</a>
    <div class="actions">
      <button class="icon-btn" title="Buka" onclick="window.open('${esc(r.url)}','_blank')">↗</button>
      <button class="icon-btn" title="Copy URL" onclick="copyText('${esc(r.url)}')">📋</button>
    </div>
  </div>`;
}

function sectionHTML(title, items, color){
  const rows = items.sort((a,b)=>a.platform.localeCompare(b.platform)).map(r => `
    <div class="minirow">
      <span class="pn">${esc(r.platform)}</span>
      <span class="mu">${r.error ? esc(r.error) : ('HTTP ' + (r.status_code ?? '—'))}</span>
      <a href="${esc(r.url)}" target="_blank" rel="noopener" style="margin-left:auto">${esc(r.url)}</a>
    </div>`).join('');
  return `<details class="sec"><summary><span class="chev">▸</span><span style="border-left:3px solid ${color};padding-left:10px">${title}</span><span class="count" style="margin-left:auto;color:var(--faint)">${items.length}</span></summary><div class="sec-body card" style="padding:6px 10px">${rows}</div></details>`;
}

// toolbar actions
$('filterInput').addEventListener('input', (e) => render(e.target.value));
$('copyBtn').onclick = () => {
  const urls = all.filter(r => r.found).map(r => r.url).join('\n');
  if (!urls) return toast('Belum ada hasil');
  copyText(urls, `${all.filter(r=>r.found).length} URL tersalin`);
};
$('jsonBtn').onclick = () => {
  const data = { username:lastUsername, scanned_at:new Date().toISOString(),
    stats:{ total:all.length, found:all.filter(r=>r.found).length }, results:all };
  const blob = new Blob([JSON.stringify(data,null,2)], {type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `osint_${lastUsername}_${Date.now()}.json`;
  a.click(); URL.revokeObjectURL(a.href);
};

function copyText(t, msg){ navigator.clipboard.writeText(t).then(()=>toast(msg||'Tersalin ✓')).catch(()=>toast('Gagal menyalin')); }
let toastTimer;
function toast(msg){
  const el = $('toast'); el.textContent = msg; el.classList.add('show');
  clearTimeout(toastTimer); toastTimer = setTimeout(()=>el.classList.remove('show'), 1800);
}
function esc(s){ return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
</script>
</body>
</html>
"""


if __name__ == "__main__":
    import os

    import uvicorn

    # Host pakai 0.0.0.0 + PORT dari environment saat di-deploy (Render/Railway/HF).
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host=host, port=port)

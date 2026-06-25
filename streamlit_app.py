#!/usr/bin/env python3
"""
OSINT Username Checker — Streamlit App
Versi ini yang dideploy ke https://streamlit.app

Jalankan lokal:  streamlit run streamlit_app.py
"""

import asyncio
import json
from datetime import datetime

import streamlit as st

from osint.checker import UsernameChecker
from osint.platforms import PLATFORMS

st.set_page_config(
    page_title="OSINT Username Checker",
    page_icon="🔍",
    layout="wide",
)

CAT_COLORS = {
    "Developer": "#79c0ff", "Social": "#d2a8ff", "Professional": "#a5d6ff",
    "Gaming": "#3fb950", "Creative": "#e3b341", "Forum": "#ff7b72",
    "Tech": "#79c0ff", "Indonesia": "#ffa657",
}

st.markdown(
    """
    <style>
      .stApp {
        background:
          radial-gradient(1200px 600px at 80% -10%, rgba(88,166,255,.10), transparent 60%),
          radial-gradient(900px 500px at -10% 10%, rgba(63,185,80,.08), transparent 55%),
          #0b0f17;
      }
      .block-container { max-width: 1040px; padding-top: 2.5rem; }

      /* Search card wrapper around the form */
      div[data-testid="stForm"] {
        background:linear-gradient(180deg,#141b2b,#0d1320);
        border:1px solid #26314a; border-radius:14px;
        box-shadow:0 8px 30px rgba(0,0,0,.35); padding:22px;
      }
      /* Username input */
      div[data-testid="stForm"] input {
        background:#0b0f17 !important; border:1px solid #33415f !important;
        color:#e8eef7 !important; border-radius:10px !important; font-size:16px !important;
        padding:12px 14px !important;
      }
      div[data-testid="stForm"] input:focus {
        border-color:#58a6ff !important; box-shadow:0 0 0 3px rgba(88,166,255,.18) !important;
      }
      /* Advanced options expander — flatten it inside the card */
      div[data-testid="stForm"] details {
        background:transparent !important; border:0 !important; box-shadow:none !important;
      }
      div[data-testid="stForm"] summary { color:#58a6ff !important; font-size:13px; }

      /* Scan button */
      div[data-testid="stForm"] button[kind="primaryFormSubmit"] {
        background:linear-gradient(180deg,#3fb950,#2ea043) !important; color:#04210b !important;
        border:0 !important; font-weight:700 !important; border-radius:10px !important;
      }
      div[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover { filter:brightness(1.06); }

      .tile {
        background:#141b2b; border:1px solid #26314a; border-radius:12px;
        padding:14px 15px; margin-bottom:10px; transition:border-color .15s, transform .15s;
      }
      .tile:hover { border-color:#3fb950; transform:translateY(-2px); }
      .tile .pname { font-weight:700; font-size:15px; display:flex; align-items:center; gap:8px; }
      .tile .dot { width:8px; height:8px; border-radius:50%; background:#3fb950; box-shadow:0 0 8px #3fb950; display:inline-block; }
      .tile a { color:#58a6ff; text-decoration:none; font-size:13px; word-break:break-all; }
      .tile a:hover { text-decoration:underline; }
      .badge { font-size:11px; padding:3px 9px; border-radius:999px; font-weight:700; }
      .group-title {
        display:flex; align-items:center; gap:10px;
        font-size:13px; font-weight:700; color:#8b98b0;
        text-transform:uppercase; letter-spacing:.7px; margin:22px 0 12px;
      }
      .group-title::after { content:""; flex:1; height:1px; background:#26314a; }
      .credit { text-align:center; color:#8b98b0; font-size:13px; line-height:1.9; }
      .credit a { color:#58a6ff; text-decoration:none; }
      .credit .name { color:#e8eef7; font-weight:700; }
    </style>
    """,
    unsafe_allow_html=True,
)


def run_scan(username: str, timeout: int, concurrency: int):
    """Drive async generator secara sinkron sambil update progress bar Streamlit."""
    checker = UsernameChecker(timeout=timeout, concurrency=concurrency)
    total = len(checker.platforms)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    agen = checker.check_all(username)

    results = []
    bar = st.progress(0.0, text=f"0 / {total} platform…")
    try:
        while True:
            try:
                r = loop.run_until_complete(agen.__anext__())
            except StopAsyncIteration:
                break
            results.append(r)
            found = sum(1 for x in results if x["found"])
            bar.progress(
                len(results) / total,
                text=f"{len(results)} / {total} platform — {found} ditemukan",
            )
    finally:
        loop.run_until_complete(agen.aclose())
        loop.close()
    bar.empty()
    return results


def badge(category: str) -> str:
    color = CAT_COLORS.get(category, "#8b98b0")
    return (
        f"<span class='badge' style='background:{color}22;color:{color}'>"
        f"{category}</span>"
    )


# ─── Header ──────────────────────────────────────────────────────────────────
st.title("🔍 OSINT Username Checker")
st.caption(
    f"Cek jejak sebuah username di {len(PLATFORMS)} platform sosial media & "
    "developer sekaligus."
)

with st.form("scan_form"):
    username = st.text_input(
        "Username",
        placeholder="@ masukkan username, mis. johndoe",
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button("🔎 Scan", type="primary", use_container_width=True)
    with st.expander("⚙ Opsi lanjutan"):
        c1, c2 = st.columns(2)
        timeout = c1.number_input("Timeout (detik)", 1, 60, 10)
        concurrency = c2.number_input("Request paralel", 1, 200, 50)

if submitted and username.strip():
    username = username.strip()
    with st.spinner("Scanning…"):
        results = run_scan(username, int(timeout), int(concurrency))

    found = sorted(
        [r for r in results if r["found"]],
        key=lambda x: (x["category"], x["platform"]),
    )
    blocked = [r for r in results if r["status"] == "blocked"]
    errors = [r for r in results if r["status"] == "error"]
    not_found = [r for r in results if r["status"] == "not_found"]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("✓ Ditemukan", len(found))
    m2.metric("✕ Tidak ada", len(not_found))
    m3.metric("🛡️ Diblokir / ragu", len(blocked))
    m4.metric("⚠️ Error", len(errors))

    # Download JSON
    payload = {
        "username": username,
        "scanned_at": datetime.now().isoformat(),
        "stats": {
            "total": len(results), "found": len(found),
            "blocked": len(blocked), "errors": len(errors),
        },
        "results": results,
    }
    st.download_button(
        "⬇ Download JSON",
        data=json.dumps(payload, indent=2),
        file_name=f"osint_{username}.json",
        mime="application/json",
    )

    st.divider()

    if not found:
        st.info(f"Username **@{username}** tidak terdeteksi di platform manapun.")
    else:
        st.subheader(f"Ditemukan di {len(found)} platform")
        from itertools import groupby

        for category, group in groupby(found, key=lambda x: x["category"]):
            items = list(group)
            st.markdown(
                f"<div class='group-title'>{category} ({len(items)})</div>",
                unsafe_allow_html=True,
            )
            cols = st.columns(2)
            for i, r in enumerate(items):
                with cols[i % 2]:
                    st.markdown(
                        f"<div class='tile'>"
                        f"<div class='pname'><span class='dot'></span>{r['platform']} {badge(r['category'])}</div>"
                        f"<a href='{r['url']}' target='_blank'>{r['url']}</a>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

    def detail_table(title, items, cols=("Platform", "Info", "URL")):
        if not items:
            return
        with st.expander(f"{title} ({len(items)})"):
            rows = [
                {
                    "Platform": r["platform"],
                    "Info": r["error"] or f"HTTP {r.get('status_code', '—')}",
                    "URL": r["url"],
                }
                for r in sorted(items, key=lambda x: x["platform"])
            ]
            st.dataframe(rows, use_container_width=True, hide_index=True)

    detail_table("🛡️ Diblokir / tidak bisa dipastikan", blocked)
    detail_table("⚠️ Error (timeout / koneksi)", errors)
    detail_table("✕ Tidak ditemukan", not_found)

# ─── Footer ──────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<div class='credit'>Hanya untuk edukasi &amp; riset OSINT. "
    "Hasil \"ditemukan\" bisa saja false-positive — verifikasi manual lewat link.<br>"
    "Created by <a class='name' href='https://muhamadakbarfadilah.my.id/' target='_blank'>Akbar Fadilah</a> · "
    "Founder &amp; Co-Founder at "
    "<a href='https://afdatech.com/' target='_blank'>Afda Technology Solutions</a></div>",
    unsafe_allow_html=True,
)

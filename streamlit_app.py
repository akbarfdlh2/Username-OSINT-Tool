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
      .block-container { max-width: 1100px; padding-top: 2rem; }
      .tile {
        background:#141b2b; border:1px solid #26314a; border-radius:12px;
        padding:14px 15px; margin-bottom:10px;
      }
      .tile .pname { font-weight:700; font-size:15px; }
      .tile a { color:#58a6ff; text-decoration:none; font-size:13px; word-break:break-all; }
      .tile a:hover { text-decoration:underline; }
      .badge { font-size:11px; padding:3px 9px; border-radius:999px; font-weight:700; }
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
    c1, c2, c3 = st.columns([3, 1, 1])
    username = c1.text_input("Username", placeholder="mis. johndoe", label_visibility="collapsed")
    timeout = c2.number_input("Timeout (s)", 1, 60, 10)
    concurrency = c3.number_input("Paralel", 1, 200, 50)
    submitted = st.form_submit_button("🔎 Scan", type="primary", use_container_width=True)

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
        cols = st.columns(2)
        for i, r in enumerate(found):
            with cols[i % 2]:
                st.markdown(
                    f"<div class='tile'>"
                    f"<div class='pname'>🟢 {r['platform']} {badge(r['category'])}</div>"
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

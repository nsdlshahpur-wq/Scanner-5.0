"""Scanner 5.0 Streamlit dashboard for US, NSE and BSE research outputs."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Scanner 5.0 | Market Dashboard", page_icon="📈", layout="wide")
st.markdown("""<style>.block-container{padding-top:1.5rem;padding-bottom:2.5rem}[data-testid="stMetric"]{background:#f4f7fb;padding:14px 16px;border-radius:12px;border:1px solid #e4eaf3}</style>""", unsafe_allow_html=True)
st.title("📈 Scanner 5.0 - Market Dashboard")
st.caption("US · NSE · BSE | Daily scans, intraday signals and research outputs")

def records_from_json(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, list): rows = raw
    elif isinstance(raw, dict):
        rows = raw.get("results", raw.get("signals", raw.get("rows", [])))
        if isinstance(rows, dict): rows = list(rows.values())
        if not isinstance(rows, list): rows = [raw] if raw else []
    else: rows = []
    return [row for row in rows if isinstance(row, dict)]

def infer_market(filename: str) -> str:
    name = filename.lower()
    if "nse" in name or "india" in name: return "NSE"
    if "bse" in name: return "BSE"
    if any(token in name for token in ("us", "nasdaq", "nyse", "sp500", "s&p")): return "US"
    return "Other"

def load_uploaded_file(upload):
    try:
        payload = json.loads(upload.getvalue().decode("utf-8-sig"))
        return {"name": upload.name, "market": infer_market(upload.name), "rows": records_from_json(payload)}, None
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {}, f"{upload.name}: invalid JSON ({exc})"

with st.sidebar:
    st.header("Dashboard controls")
    market_filter = st.multiselect("Markets", ["US", "NSE", "BSE", "Other"], default=["US", "NSE", "BSE", "Other"])
    search_text = st.text_input("Search symbol, setup or value")
    st.divider()
    uploads = st.file_uploader("Upload scanner JSON files", type=["json"], accept_multiple_files=True,
        help="Select multiple US, NSE and BSE scanner output files together.")

if not uploads:
    st.info("Upload scanner JSON output files to populate the dashboard. You can select daily and intraday files for multiple markets.")
    st.markdown("""Generate India outputs from the scanner-core directory:
- python trader-india/india.py --universe trader-india/universe.csv --output trader/india-daily.json
- python trader-india/intraday.py --universe trader-india/universe.csv --output trader/india-intraday.json
- python trader-india/bse.py --universe trader-india/bse-universe.csv --output trader/bse-daily.json
- python trader-india/bse_intraday.py --universe trader-india/bse-universe.csv --output trader/bse-intraday.json
""")
    st.stop()

sections, errors = [], []
for upload in uploads:
    section, error = load_uploaded_file(upload)
    if error: errors.append(error)
    else: sections.append(section)
for error in errors: st.error(error)

visible = [s for s in sections if s["market"] in market_filter]
if search_text.strip():
    needle = search_text.strip().lower()
    visible = [s for s in visible if needle in s["name"].lower() or needle in json.dumps(s["rows"], ensure_ascii=False, default=str).lower()]
total_records = sum(len(s["rows"]) for s in visible)
a, b, c = st.columns(3)
a.metric("Data sections", len(visible))
b.metric("Total records", total_records)
c.metric("Markets represented", len({s["market"] for s in visible}))
if not visible: st.warning("No matching records. Check selected markets or search text.")

for section in visible:
    with st.container(border=True):
        left, right = st.columns([4, 1])
        left.subheader(f'{section["market"]} · {Path(section["name"]).stem}')
        right.metric("Records", len(section["rows"]))
        st.caption(f'Source file: {section["name"]}')
        if section["rows"]:
            st.dataframe(pd.json_normalize(section["rows"], sep="."), use_container_width=True, hide_index=True)
        else: st.info("Valid JSON file, but no tabular records were found.")

st.divider()
st.caption("Data notice: displays uploaded JSON files only and does not independently fetch or verify live exchange data. Upstream feeds may be delayed or incomplete. Signals are research outputs, not guaranteed trade recommendations. Paper mode only - no orders are placed or transmitted.")

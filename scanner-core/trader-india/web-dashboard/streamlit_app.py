"""Scanner 5.0 dashboard with optional DhanHQ broker panel."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
import pandas as pd
import streamlit as st
from dhan_broker import DhanAPIError, DhanClient, live_orders_enabled

st.set_page_config(page_title="Scanner 5.0 | Market Dashboard", page_icon="📈", layout="wide")
st.markdown("""<style>.block-container{padding-top:1.5rem;padding-bottom:2.5rem}[data-testid="stMetric"]{background:#f4f7fb;padding:14px 16px;border-radius:12px;border:1px solid #e4eaf3}</style>""", unsafe_allow_html=True)
st.title("📈 Scanner 5.0")
st.caption("US · NSE · BSE · DhanHQ | Market research, broker data and user-confirmed order tickets")

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

scanner_tab, broker_tab = st.tabs(["📊 Scanner Dashboard", "🔗 Dhan Broker Connect"])

with scanner_tab:
    with st.sidebar:
        st.header("Dashboard controls")
        market_filter = st.multiselect("Markets", ["US", "NSE", "BSE", "Other"], default=["US", "NSE", "BSE", "Other"])
        search_text = st.text_input("Search symbol, setup or value")
        st.divider()
        uploads = st.file_uploader("Upload scanner JSON files", type=["json"], accept_multiple_files=True,
            help="Select multiple US, NSE and BSE scanner output files together.")
    if not uploads:
        st.info("Upload scanner JSON output files to populate the dashboard. Dhan Broker Connect is available in the second tab.")
        st.markdown("""Generate India outputs from the scanner-core directory:
- python trader-india/india.py --universe trader-india/universe.csv --output trader/india-daily.json
- python trader-india/intraday.py --universe trader-india/universe.csv --output trader/india-intraday.json
- python trader-india/bse.py --universe trader-india/bse-universe.csv --output trader/bse-daily.json
- python trader-india/bse_intraday.py --universe trader-india/bse-universe.csv --output trader/bse-intraday.json
""")
    else:
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
    st.caption("Scanner signals are research outputs, not guaranteed recommendations. Verify symbol, Security ID, price, quantity and risk before any trade.")

with broker_tab:
    st.subheader("DhanHQ Broker Connect")
    st.warning("यह सुविधा वास्तविक ट्रेडिंग अकाउंट से जुड़ती है। Token कोड/फाइल में सेव नहीं होता; यह केवल वर्तमान browser session में रहता है। किसी को भी अपना Token, PIN या API Secret न दें।")
    if "dhan_client_id" not in st.session_state: st.session_state.dhan_client_id = ""
    if "dhan_access_token" not in st.session_state: st.session_state.dhan_access_token = ""
    with st.form("dhan_connect_form"):
        client_id_input = st.text_input("Dhan Client ID", value=st.session_state.dhan_client_id)
        token_input = st.text_input("Dhan Access Token (24-hour token)", value=st.session_state.dhan_access_token, type="password")
        connect = st.form_submit_button("Connect / Verify Dhan Account", type="primary")
    if connect:
        try:
            client = DhanClient(client_id_input, token_input)
            profile = client.profile()
            st.session_state.dhan_client_id = client_id_input.strip()
            st.session_state.dhan_access_token = token_input.strip()
            st.session_state.dhan_profile = profile
            st.success("Dhan account connected and token verified.")
        except DhanAPIError as exc:
            st.error(f"Connection failed: {exc}")
    if st.session_state.dhan_access_token and st.session_state.get("dhan_profile"):
        client = DhanClient(st.session_state.dhan_client_id, st.session_state.dhan_access_token)
        profile = st.session_state.dhan_profile
        st.success(f"Connected · Client ID: {profile.get('dhanClientId', st.session_state.dhan_client_id)}")
        p1, p2, p3 = st.columns(3)
        p1.metric("Token validity", profile.get("tokenValidity", "Not provided"))
        p2.metric("Active segments", profile.get("activeSegment", "Not provided"))
        p3.metric("Data API plan", profile.get("dataPlan", "Unknown"))
        if profile.get("dataPlan") != "Active":
            st.info("Live Market Quote के लिए Dhan Data API subscription आवश्यक हो सकती है। Trading API और account endpoints अलग हैं।")
        st.markdown("#### Live Market Quote")
        q1, q2, q3 = st.columns([1.2, 1.2, 1])
        with q1:
            quote_segment = st.selectbox("Exchange Segment", ["NSE_EQ", "BSE_EQ", "NSE_FNO", "BSE_FNO", "MCX_COMM"])
        with q2:
            quote_security_id = st.text_input("Security ID", placeholder="उदाहरण: 11536")
        with q3:
            st.write("")
            st.write("")
            refresh_quote = st.button("Refresh LTP")
        if refresh_quote:
            try:
                quote = client.ltp(quote_segment, quote_security_id)
                quote_data = quote.get("data", {}).get(quote_segment, {}).get(str(quote_security_id), {})
                if quote_data:
                    st.metric("Last Traded Price", f"₹ {quote_data.get('last_price', 'N/A')}")
                    st.caption("यह Dhan API का request-time real-time quote snapshot है।")
                else: st.json(quote)
            except DhanAPIError as exc: st.error(str(exc))
        st.markdown("#### Account Overview")
        c1, c2, c3, c4 = st.columns(4)
        for col, label, fn in [
            (c1, "Funds & Margin", client.funds), (c2, "Holdings", client.holdings),
            (c3, "Positions", client.positions), (c4, "Today's Orders", client.orders),
        ]:
            if col.button(f"Load {label}"):
                try: st.session_state[f"dhan_{label}"] = fn()
                except DhanAPIError as exc: col.error(str(exc))
            if f"dhan_{label}" in st.session_state:
                with col: st.json(st.session_state[f"dhan_{label}"])
        st.divider()
        st.markdown("#### Manual Order Ticket")
        if not live_orders_enabled():
            st.error("Live order transmission अभी बंद है। Render सर्वर पर DHAN_ENABLE_LIVE_ORDERS=true और DHAN_STATIC_IP=<Dhan में whitelisted वही स्थिर outbound IP> सेट होने तक order button सक्रिय नहीं होगा। Streamlit Community Cloud को static outbound IP मानकर उपयोग न करें।")
        with st.form("dhan_order_form"):
            o1, o2, o3 = st.columns(3)
            with o1:
                side = st.selectbox("Transaction", ["BUY", "SELL"])
                order_segment = st.selectbox("Order Segment", ["NSE_EQ", "BSE_EQ", "NSE_FNO", "BSE_FNO", "MCX_COMM"])
                security_id = st.text_input("Security ID", placeholder="Exchange instrument ID")
            with o2:
                product = st.selectbox("Product", ["CNC", "INTRADAY", "MARGIN", "MTF"])
                order_type = st.selectbox("Order Type", ["LIMIT", "MARKET", "STOP_LOSS", "STOP_LOSS_MARKET"])
                validity = st.selectbox("Validity", ["DAY", "IOC"])
            with o3:
                quantity = st.number_input("Quantity", min_value=1, max_value=100000, value=1, step=1)
                price = st.number_input("Limit / SL Price", min_value=0.0, value=0.0, step=0.05)
                trigger = st.number_input("Trigger Price (SL)", min_value=0.0, value=0.0, step=0.05)
            ack = st.checkbox("मैंने Symbol, Security ID, BUY/SELL, Quantity और अनुमानित जोखिम जाँच लिया है।")
            confirm_text = st.text_input('Live order भेजने के लिए "PLACE LIVE ORDER" लिखें')
            submit_order = st.form_submit_button("Review & Place Live Order", type="primary", disabled=not live_orders_enabled())
        if submit_order:
            if not ack or confirm_text.strip() != "PLACE LIVE ORDER":
                st.error("Order भेजने से पहले checkbox और exact confirmation आवश्यक है।")
            else:
                try:
                    response = client.place_order(transaction_type=side, exchange_segment=order_segment,
                        product_type=product, order_type=order_type, validity=validity,
                        security_id=security_id, quantity=int(quantity), price=float(price),
                        trigger_price=float(trigger))
                    st.success("Order request Dhan को भेजी गई। यह fill होने की गारंटी नहीं है।")
                    st.json(response)
                except DhanAPIError as exc: st.error(str(exc))
        if st.button("Disconnect Dhan"):
            for key in list(st.session_state.keys()):
                if key.startswith("dhan_"): del st.session_state[key]
            st.rerun()
    else:
        st.info("Connect करने के लिए Dhan Client ID और 24-hour Access Token भरें। Token Dhan Web → Profile → Access DhanHQ APIs से बनता है।")
        st.markdown("[Open Dhan Web](https://web.dhan.co/) · [DhanHQ API Documentation](https://dhanhq.co/docs/v2/)")

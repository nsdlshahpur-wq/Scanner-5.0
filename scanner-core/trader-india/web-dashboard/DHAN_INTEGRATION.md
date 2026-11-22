# DhanHQ Broker Integration

Scanner 5.0 includes an optional DhanHQ v2 panel in the Streamlit dashboard.

## Connect
1. Open Dhan Web → My Profile → Access DhanHQ APIs.
2. Generate an Access Token (valid for 24 hours).
3. In Scanner 5.0 → Dhan Broker Connect, enter Client ID and Access Token.
4. The app verifies the token through the Dhan profile endpoint. Credentials remain in the active Streamlit session and are not written to repository files.

## Live market data
- The panel requests Dhan's real-time-at-request Market Quote LTP endpoint.
- Dhan Data API subscription is required for live market-data endpoints; check current pricing in Dhan Web.
- Enter the exchange segment and Dhan Security ID, then press Refresh LTP.

## Orders and static IP requirement
Dhan requires a whitelisted static IP for order placement, modification and cancellation. Live order transmission is disabled by default.

Only on a Render deployment with a dedicated, fixed outbound IP that is already whitelisted in Dhan:
- Set `DHAN_ENABLE_LIVE_ORDERS=true`.
- Set `DHAN_STATIC_IP` to the exact whitelisted outbound IP (used as a deployment guard; it does not allocate an IP).
- Ensure Render's actual outbound traffic uses that fixed IP. Do not enable orders on Streamlit Community Cloud or any host without a verified fixed outbound IP.
- Dhan may restrict changing the registered IP for seven days after an update.

Do not enable order transmission until the hosting provider confirms the fixed egress IP and Dhan shows that exact IP as registered. Trading API access is free, but data APIs may require a paid subscription.

## Order safety
- Orders are manual only. Scanner signals never place orders automatically.
- The user must review the exchange segment, security ID, side, product, order type, validity and quantity.
- Live order submission requires an explicit checkbox and the exact phrase `PLACE LIVE ORDER`.
- Market orders can execute at a different price than expected. Orders can be rejected or partially filled.
- Do not paste tokens, PINs, TOTP seeds or API secrets into source code, issues, chat or logs.
- The 24-hour access token must be regenerated when expired.

## Supported in this initial integration
- Profile/token verification
- LTP quote snapshot
- Funds, holdings, positions and order-book retrieval
- Manual BUY/SELL order placement with server-side static-IP gate

WebSocket tick streaming, automatic signal execution, order modification/cancellation UI, multi-user OAuth and persistent credential vault are not included.

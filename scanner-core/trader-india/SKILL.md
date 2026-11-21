---
name: trader-india
description: >-
  Scans NSE cash equities using Yahoo Finance chart data for daily technical
  rule matches and supports conservative paper position sizing. Research only;
  no broker orders. Use for NSE / Indian stocks, daily breakout, RSI, MA20,
  bull flag, opening range breakout, and paper-trading risk calculations.
argument-hint: "--symbols RELIANCE,TCS,INFY | --universe trader-india/universe.csv"
---

# NSE India Scanner

Run from scanner-core:

\`\`\`bash
python trader-india/india.py --universe trader-india/universe.csv --output trader/india-watchlist.json
python trader-india/india.py --symbols RELIANCE,TCS,INFY
python trader-india/paper.py --symbol RELIANCE --capital 100000 --entry 1500 --stop 1485 --record trader/paper-ledger.json
python -m unittest discover -s tests -v
\`\`\`

Daily rules: 20-session closing breakout, bull-flag consolidation, MA20 reclaim,
RSI-14 oversold and oversold bounce. Today's unfinished daily candle is excluded
before 15:45 IST. A daily setup is a candidate, not an entry. Intraday ORB uses
completed 5-minute candles and the first 15 minutes of NSE regular trading.

The default universe is a curated liquid watchlist, not the full NSE listing.
Use an updated symbols CSV for broader coverage. Yahoo Finance is an unofficial
data source; verify all prices, corporate actions, liquidity and timestamps.

Paper sizing defaults to 0.5% capital risk per trade and 20% maximum position
notional. The ledger is local JSON only. No broker API is called and no orders
are transmitted.

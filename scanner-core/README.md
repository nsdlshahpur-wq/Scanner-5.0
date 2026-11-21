# Scanner 5.0 - Market Analysis Toolkit

A modular research and decision-support toolkit for US and Indian equities. Existing US modules are retained. The NSE engine is a separate module with its own symbol universe, market timezone, data adapter, indicators and paper-trading controls.

## Markets and modules

| Module | Purpose |
| --- | --- |
| \`trader-scanner\` | Existing US-listed stock scanner (NYSE / NASDAQ) |
| \`trader-india\` | NSE daily technical scanner and conservative paper sizing |
| \`trader-news\` | US market headlines and company filings |
| \`trader-entry\` / \`trader-exit\` | Setup timing and exit planning |
| \`trader-risk\` / \`trader-budget\` | Risk checks and position sizing |
| \`trader-timemachine\` | Historical scenario simulation |
| \`trader-broker\` | Existing broker ticket preparation; do not enable live orders during development |

## NSE quick start

From this directory:

\`\`\`bash
python trader-india/india.py --universe trader-india/universe.csv --output trader/india-watchlist.json
python trader-india/india.py --symbols RELIANCE,TCS,INFY
python trader-india/paper.py --symbol RELIANCE --capital 100000 --entry 1500 --stop 1485 --record trader/paper-ledger.json
\`\`\`

The included CSV is a curated starter watchlist, not the complete NSE universe. Supply an updated CSV with a \`symbol\` column to scan more securities. Daily setups include 20-session closing breakout, bull flag, MA20 reclaim, RSI-14 oversold and oversold bounce. The unfinished current-day daily candle is excluded before 15:45 IST. Intraday opening-range analysis uses completed 5-minute bars and the first 15 minutes of the NSE session.

## Conservative paper mode

- Default risk budget: 0.5% of capital per trade.
- Maximum position notional: 20% of capital.
- Paper ledger is local JSON; it does not connect to a broker.
- No order is transmitted, and a signal is not a buy recommendation.
- Backtest results and paper fills must include fees, slippage, gaps and corporate actions before any live consideration.

## Data limitations

The NSE module currently uses Yahoo Finance's unofficial chart endpoint for public price history. It may lag, rate-limit, omit symbols or contain adjusted/split-related data. NSE F&O open interest, official bhavcopy ingestion, full-market universe refresh, sector breadth and live alerts are planned subsequent phases and are not claimed as implemented yet. Never treat incomplete scans as full-market coverage.

## Tests

\`\`\`bash
python -m unittest discover -s tests -v
\`\`\`

The tests are offline and deterministic. Live data quality and paper-trading validation are separate acceptance gates.

## Safety

For research and education only, not financial advice. All trading remains paper-only during development. Do not place real orders or store broker credentials in this project.

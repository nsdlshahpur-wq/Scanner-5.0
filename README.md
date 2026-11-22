# Scanner 5.0

A modular market research toolkit for US and Indian equities. The existing US Scanner is preserved. Independent NSE and BSE engines add daily and intraday screening, derivatives analysis from supplied exchange files, sector snapshots, paper portfolio tracking, backtesting, local alerts and an offline dashboard.

## Project structure

- `scanner-core/` - Python tools, skills, plugin metadata, documentation and offline tests.
- `.github/workflows/scanner-tests.yml` - automated Python test workflow.
- `scanner-core/day-trading/` - end-to-end Day Trading workflow orchestrating the US, NSE/BSE, risk, sizing, alerts and DhanHQ modules.
- `scanner-core/trader-india/` - independent NSE/BSE research and exchange-aware paper-trading engine.
- `render.yaml` and `scanner-core/trader-india/web-dashboard/streamlit_app.py` - shared web dashboard deployment for Render and Streamlit Community Cloud. See [deployment guide](DEPLOYMENT.md).

## Modules

- `trader-scanner` - existing US market scanner
- `trader-news` - market news and company filings
- `trader-entry` - setup and entry timing
- `trader-exit` - stop-loss and exit planning
- `trader-timemachine` - historical scenario simulation
- `trader-risk` - risk controls
- `trader-budget` - position sizing
- `trader-broker` - broker ticket preparation in the original US workflow
- `trader-alerts` - alert monitoring
- `trader-analyst` - company and earnings analysis
- `trader-pelosi` - public congressional-trade disclosures
- `trader-india` - independent NSE/BSE scanners, paper portfolio and optional DhanHQ broker panel

## Day Trading workflow

The `day-trading` skill coordinates the existing scanner, news, entry, exit, replay, sizing, risk and alert skills. It includes separate US and NSE/BSE workflows, a mandatory risk checklist and a DhanHQ manual-order handoff. See [Day Trading Skill](scanner-core/day-trading/SKILL.md) and [Day Trading Playbook](scanner-core/day-trading/PLAYBOOK.md).

## NSE and BSE capabilities

- Daily technical setups and completed-candle handling for NSE and BSE.
- 5-minute intraday scanners with 15-minute opening-range breakout and volume confirmation for NSE and BSE.
- Curated sector relative-strength snapshot and user-supplied NSE universe import.
- F&O futures open-interest buildup classification from normalized bhavcopy CSV.
- Conservative position sizing, exchange-aware local paper portfolio, mark-to-market and stop alerts.
- Daily OHLCV baseline backtesting.
- Local JSON alerts and offline HTML dashboard.

## Important

NSE `.NS` and BSE `.BO` price feeds currently use an unofficial Yahoo Finance chart endpoint and may be delayed or incomplete. F&O and full-universe imports require user-supplied exchange files. Unit tests do not validate live data or profitability. This is research software, not financial advice or a guarantee of results. DhanHQ integration supports live quote snapshots and user-confirmed orders, but live order transmission remains disabled until a verified fixed outbound IP is whitelisted with Dhan.

## Safety and limitations

- Do not treat scanner signals as buy or sell recommendations.
- Scanner signals only prefill an order ticket; they never auto-submit live orders. Manual order placement is gated by Dhan static-IP whitelisting and explicit user confirmation.
- Verify exchange data, corporate actions, fees, slippage, gaps and liquidity.
- The default NSE and BSE universes and sector map are curated samples, not complete market coverage.
- F&O analysis is currently normalized-CSV based for NSE; BSE derivatives and full option-chain PCR/max-pain are not implemented. BSE cash universe import uses a user-downloaded BSE scrip master and requires code validation.
- Existing US Scanner modules are preserved and are not used as NSE data sources.

## License and attribution

The original imported source license and attribution are retained in `scanner-core/LICENSE`.

See [scanner-core/README.md](scanner-core/README.md) for commands, CSV formats, tests and implementation limitations.


Dhan integration setup: [DHAN_INTEGRATION.md](scanner-core/trader-india/web-dashboard/DHAN_INTEGRATION.md).
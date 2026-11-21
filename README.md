# Scanner 5.0

A modular market research toolkit for US and Indian equities. The existing US Scanner is preserved. Independent NSE and BSE engines add daily and intraday screening, derivatives analysis from supplied exchange files, sector snapshots, paper portfolio tracking, backtesting, local alerts and an offline dashboard.

## Project structure

- `scanner-core/` - Python tools, skills, plugin metadata, documentation and offline tests.
- `.github/workflows/scanner-tests.yml` - automated Python test workflow.
- `scanner-core/trader-india/` - independent NSE/BSE research and exchange-aware paper-trading engine.

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
- `trader-india` - independent NSE/BSE scanners and exchange-aware paper-only modules

## NSE and BSE capabilities

- Daily technical setups and completed-candle handling for NSE and BSE.
- 5-minute intraday scanners with 15-minute opening-range breakout and volume confirmation for NSE and BSE.
- Curated sector relative-strength snapshot and user-supplied NSE universe import.
- F&O futures open-interest buildup classification from normalized bhavcopy CSV.
- Conservative position sizing, exchange-aware local paper portfolio, mark-to-market and stop alerts.
- Daily OHLCV baseline backtesting.
- Local JSON alerts and offline HTML dashboard.

## Important

NSE `.NS` and BSE `.BO` price feeds currently use an unofficial Yahoo Finance chart endpoint and may be delayed or incomplete. F&O and full-universe imports require user-supplied exchange files. Unit tests do not validate live data or profitability. This is research software, not financial advice or a guarantee of results. No NSE or BSE broker orders are sent; paper mode only.

## Safety and limitations

- Do not treat scanner signals as buy or sell recommendations.
- Do not use the NSE or BSE modules for live trading.
- Verify exchange data, corporate actions, fees, slippage, gaps and liquidity.
- The default NSE and BSE universes and sector map are curated samples, not complete market coverage.
- F&O analysis is currently normalized-CSV based for NSE; BSE derivatives and full option-chain PCR/max-pain are not implemented. BSE cash universe import uses a user-downloaded BSE scrip master and requires code validation.
- Existing US Scanner modules are preserved and are not used as NSE data sources.

## License and attribution

The original imported source license and attribution are retained in `scanner-core/LICENSE`.

See [scanner-core/README.md](scanner-core/README.md) for commands, CSV formats, tests and implementation limitations.

# Scanner 5.0

A modular market research toolkit for US and Indian equities. The existing US Scanner is preserved. The independent NSE engine adds daily and intraday screening, derivatives analysis from supplied exchange files, sector snapshots, paper portfolio tracking, backtesting, local alerts and an offline dashboard.

## Project structure

- `scanner-core/` - Python tools, skills, plugin metadata, documentation and offline tests.
- `.github/workflows/scanner-tests.yml` - automated Python test workflow.
- `scanner-core/trader-india/` - independent NSE research and paper-trading engine.

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
- `trader-india` - independent NSE scanner and paper-only modules

## NSE capabilities

- Daily technical setups and completed-candle handling.
- 5-minute intraday scanner with 15-minute opening-range breakout and volume confirmation.
- Curated sector relative-strength snapshot and user-supplied NSE universe import.
- F&O futures open-interest buildup classification from normalized bhavcopy CSV.
- Conservative position sizing, local paper portfolio, mark-to-market and stop alerts.
- Daily OHLCV baseline backtesting.
- Local JSON alerts and offline HTML dashboard.

## Important

The NSE price feed currently uses an unofficial Yahoo Finance chart endpoint and may be delayed or incomplete. F&O and full-universe imports require user-supplied exchange files. Unit tests do not validate live data or profitability. This is research software, not financial advice or a guarantee of results. No NSE broker orders are sent; paper mode only.

## Safety and limitations

- Do not treat scanner signals as buy or sell recommendations.
- Do not use the NSE modules for live trading.
- Verify exchange data, corporate actions, fees, slippage, gaps and liquidity.
- The default NSE universe and sector map are curated samples, not complete market coverage.
- F&O analysis does not yet provide full option-chain PCR, max pain or automated exchange downloads.
- Existing US Scanner modules are preserved and are not used as NSE data sources.

## License and attribution

The original imported source license and attribution are retained in `scanner-core/LICENSE`.

See [scanner-core/README.md](scanner-core/README.md) for commands, CSV formats, tests and implementation limitations.

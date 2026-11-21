# Scanner 5.0

A modular market research toolkit for US and Indian equities. The existing US Scanner is preserved. NSE features live in an independent `scanner-core/trader-india/` engine and remain paper-only.

## NSE capabilities

- Daily technical setups and completed-candle handling.
- 5-minute intraday scanner with 15-minute opening-range breakout and volume confirmation.
- Curated sector relative-strength snapshot and user-supplied NSE universe import.
- F&O futures open-interest buildup classification from a normalized bhavcopy CSV.
- Conservative position sizing, local paper portfolio, mark-to-market and stop alerts.
- Daily OHLCV baseline backtesting.
- Local JSON alerts and an offline HTML dashboard.

## Start here

See [scanner-core/README.md](scanner-core/README.md) for installation, commands, input CSV formats, test instructions and data limitations.

## Important

NSE market data currently uses an unofficial Yahoo Finance chart feed for prices. F&O and full-universe imports require user-supplied exchange files. Unit tests do not validate live data or profitability. This is research software, not financial advice. No broker orders are sent; do not use it for live trading.

The original US Scanner modules and attribution remain preserved.

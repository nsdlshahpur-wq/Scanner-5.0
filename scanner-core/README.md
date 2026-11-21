# Scanner 5.0 - Market Analysis Toolkit

A modular research and decision-support toolkit for US and Indian equities. Existing US modules remain separate and preserved. NSE and BSE use separate exchange adapters and starter universes, with an exchange-aware paper-only portfolio.

## Modules

| Module | Purpose |
| --- | --- |
| `trader-scanner` | Existing US-listed stock scanner |
| `trader-india/india.py` | NSE daily setups: 20-day breakout, bull flag, MA20 reclaim, RSI-14 and oversold bounce |
| `trader-india/intraday.py` | NSE completed 5-minute candles, 15-minute ORB and volume confirmation |
| `trader-india/bse.py` | Independent BSE daily scanner using `.BO` tickers |
| `trader-india/bse_intraday.py` | BSE 5-minute ORB and volume confirmation |
| `trader-india/bse-universe.csv` | Curated BSE scrip-code starter universe |
| `trader-india/sectors.py` | Relative-strength snapshot for the curated sector map |
| `trader-india/derivatives.py` | Offline F&O futures OI buildup classification from normalized CSV |
| `trader-india/universe.py` | Validate/import a user-downloaded NSE equity master CSV |
| `trader-india/paper.py` | Conservative position sizing and sizing-plan ledger |
| `trader-india/portfolio.py` | Paper open/close events, mark-to-market P&L and stop alerts |
| `trader-india/backtest.py` | Daily breakout baseline backtest with next-open entry |
| `trader-india/alerts.py` | Local JSON alerts; no push service or orders |
| `trader-india/dashboard.py` | Offline HTML dashboard from scanner JSON outputs |

## Quick start

Run commands from `scanner-core`:

```bash
python trader-india/india.py --universe trader-india/universe.csv --output trader/india-daily.json
python trader-india/bse.py --universe trader-india/bse-universe.csv --output trader/bse-daily.json
python trader-india/bse_intraday.py --universe trader-india/bse-universe.csv --output trader/bse-intraday.json
python trader-india/bse.py --universe trader-india/bse-universe.csv --output trader/bse-daily.json
python trader-india/bse_intraday.py --universe trader-india/bse-universe.csv --output trader/bse-intraday.json
python trader-india/intraday.py --universe trader-india/universe.csv --output trader/india-intraday.json
python trader-india/sectors.py --universe trader-india/universe.csv --output trader/sector-strength.json
python trader-india/sectors.py --exchange BSE --universe trader-india/bse-universe.csv --output trader/bse-sector-strength.json
python trader-india/sectors.py --exchange BSE --universe trader-india/bse-universe.csv --output trader/bse-sector-strength.json
python trader-india/alerts.py --input trader/india-intraday.json --output trader/india-alerts.json
python trader-india/dashboard.py --input Daily=trader/india-daily.json --input Intraday=trader/india-intraday.json --output trader/india-dashboard.html
```

### Universe refresh

Download the latest official NSE equity master CSV yourself, then import it:

```bash
python trader-india/universe.py --input /path/to/nse-equity-master.csv --output trader-india/universe.csv --series EQ
```

Both NSE and BSE CSVs are curated starter lists, not complete exchange listings. BSE uses numeric scrip codes mapped to Yahoo Finance `.BO` tickers. Verify the official exchange scrip-code mapping and feed availability. The default NSE CSV is only a curated starter list, not the full NSE listing. Verify the date, format and series of the source file before replacing the universe.

### F&O / OI analysis

Download an official NSE derivatives bhavcopy and map its columns to this normalized CSV schema:

`symbol,instrument,expiry,open_interest,change_in_oi,volume,close,underlying_close,previous_underlying_close`

```bash
python trader-india/derivatives.py --csv /path/to/normalized-fo-bhavcopy.csv --output trader/fo-analysis.json
```

It classifies futures long buildup, short buildup, short covering and long unwinding only when price and OI changes are available. This module does not currently calculate a full option-chain PCR, max pain or automated expiry analytics.

### Paper portfolio

```bash
python trader-india/paper.py --exchange NSE --symbol RELIANCE --capital 100000 --entry 1500 --stop 1485 --record trader/paper-sizing.json
python trader-india/paper.py --exchange BSE --symbol 500325 --capital 100000 --entry 1500 --stop 1485 --record trader/bse-paper-sizing.json
python trader-india/portfolio.py --ledger trader/paper-portfolio.json open --exchange NSE --symbol RELIANCE --qty 5 --entry 1500 --stop 1480
python trader-india/portfolio.py --ledger trader/paper-portfolio.json open --exchange BSE --symbol 500325 --qty 5 --entry 1500 --stop 1480
python trader-india/portfolio.py --ledger trader/paper-portfolio.json mark --prices /path/to/prices.json  # keys: NSE:RELIANCE, BSE:500325
python trader-india/portfolio.py --ledger trader/paper-portfolio.json close --symbol RELIANCE --price 1520 --fee 5
```

Portfolio marks and fills are supplied by the user; stop alerts are informational and never execute trades.

### Backtesting

Provide a chronological OHLCV CSV with `open,high,low,close,volume` columns:

```bash
python trader-india/backtest.py --csv /path/to/daily-ohlcv.csv --capital 100000 --output trader/backtest.json
```

The baseline strategy signals on a completed close and enters at the next bar's open. Daily-bar backtests cannot fully model intraday path, gaps, liquidity, taxes or survivorship bias.

## Risk controls and safety

- Default sizing risk budget: 0.5% of stated capital per trade.
- Maximum position notional: 20% of stated capital.
- Long-only paper sizing requires stop below entry.
- No broker credentials, broker API calls, order transmission or live execution are included.
- Signals are rule matches, not buy/sell recommendations.
- Paper results require independent validation for fees, slippage, gaps, corporate actions and data quality.

## Data quality limitations

NSE and BSE daily/intraday price history currently uses Yahoo Finance's unofficial chart endpoint; it may be delayed, rate-limited, incomplete or adjusted. Sector tags cover selected liquid names, not every NSE stock or official index constituents. F&O analysis requires a user-supplied normalized exchange file. Universe refresh is an import utility, not an automatic claim that every current NSE listing has been downloaded. Alerts are local JSON only; no external push delivery is configured.

## Tests

```bash
python -m unittest discover -s tests -v
```

All test fixtures are offline and deterministic. A green unit-test run does not validate live market-data quality, trading profitability or execution behavior.

## Preserved US scanner

The India exchange engines are isolated under `trader-india`; existing US scanner modules and workflows are not repurposed as NSE data sources.

## License and attribution

The original imported source license and attribution are retained in LICENSE.

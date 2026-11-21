# Scanner 5.0 - Market Analysis Toolkit

A modular research and decision-support toolkit for US and Indian equities. Existing US modules are preserved. NSE and BSE use separate exchange adapters and starter universes, with an exchange-aware paper-only portfolio.

## Modules

| Module | Purpose |
| --- | --- |
| `trader-scanner` | Existing US-listed stock scanner |
| `trader-india/india.py` | NSE daily setups: 20-day breakout, bull flag, MA20 reclaim, RSI-14 and oversold bounce |
| `trader-india/intraday.py` | NSE completed 5-minute candles, 15-minute ORB and volume confirmation |
| `trader-india/bse.py` | Independent BSE daily scanner using `.BO` tickers |
| `trader-india/bse_intraday.py` | BSE 5-minute ORB and volume confirmation |
| `trader-india/bse-universe.csv` | Curated BSE scrip-code starter universe |
| `trader-india/bse_universe.py` | Import a user-downloaded BSE scrip master CSV |
| `trader-india/sectors.py` | Relative-strength snapshot for curated NSE/BSE sector maps |
| `trader-india/derivatives.py` | Offline NSE F&O futures OI buildup classification from normalized CSV |
| `trader-india/universe.py` | Validate/import a user-downloaded NSE equity master CSV |
| `trader-india/paper.py` | Exchange-labelled conservative position sizing |
| `trader-india/portfolio.py` | Exchange-aware paper open/close, mark-to-market P&L and stop alerts |
| `trader-india/backtest.py` | Daily breakout baseline backtest with next-open entry |
| `trader-india/alerts.py` | Local JSON alerts; no push service or orders |
| `trader-india/dashboard.py` | Offline HTML dashboard from scanner JSON outputs |

## Quick start

Run commands from `scanner-core`:

```bash
# NSE daily and intraday
python trader-india/india.py --universe trader-india/universe.csv --output trader/india-daily.json
python trader-india/intraday.py --universe trader-india/universe.csv --output trader/india-intraday.json

# BSE daily and intraday
python trader-india/bse.py --universe trader-india/bse-universe.csv --output trader/bse-daily.json
python trader-india/bse_intraday.py --universe trader-india/bse-universe.csv --output trader/bse-intraday.json

# Sector relative strength
python trader-india/sectors.py --universe trader-india/universe.csv --output trader/nse-sectors.json
python trader-india/sectors.py --exchange BSE --universe trader-india/bse-universe.csv --output trader/bse-sectors.json

# Alerts and dashboard
python trader-india/alerts.py --input trader/india-intraday.json --output trader/india-alerts.json
python trader-india/dashboard.py --input NSE-Daily=trader/india-daily.json --input BSE-Daily=trader/bse-daily.json --output trader/combined-dashboard.html
```

## Universe refresh

For NSE, import a current user-downloaded equity master:

```bash
python trader-india/universe.py --input /path/to/nse-equity-master.csv --output trader-india/universe.csv --series EQ
```

For BSE, import a current user-downloaded equity scrip master:

```bash
python trader-india/bse_universe.py --input /path/to/bse-scrip-master.csv --output trader-india/bse-universe.csv
```

Both repository universes are curated starter lists, not complete exchange listings. BSE uses numeric scrip codes mapped to Yahoo Finance `.BO` tickers. Verify each code against the current BSE scrip master and confirm feed availability before relying on scan results.

## F&O / OI analysis

The current derivatives CSV parser is documented for NSE F&O data. Map the downloaded exchange file to:

`symbol,instrument,expiry,open_interest,change_in_oi,volume,close,underlying_close,previous_underlying_close`

```bash
python trader-india/derivatives.py --csv /path/to/normalized-nse-fo-bhavcopy.csv --output trader/nse-fo-analysis.json
```

It classifies futures long buildup, short buildup, short covering and long unwinding only when price and OI changes are available. BSE derivatives, full option-chain PCR, max pain and automated exchange downloads are not included.

## Exchange-aware paper portfolio

```bash
python trader-india/paper.py --exchange NSE --symbol RELIANCE --capital 100000 --entry 1500 --stop 1485 --record trader/nse-paper-sizing.json
python trader-india/paper.py --exchange BSE --symbol 500325 --capital 100000 --entry 1500 --stop 1485 --record trader/bse-paper-sizing.json

python trader-india/portfolio.py --ledger trader/paper-portfolio.json open --exchange NSE --symbol RELIANCE --qty 5 --entry 1500 --stop 1480
python trader-india/portfolio.py --ledger trader/paper-portfolio.json open --exchange BSE --symbol 500325 --qty 5 --entry 1500 --stop 1480
python trader-india/portfolio.py --ledger trader/paper-portfolio.json mark --prices /path/to/prices.json
python trader-india/portfolio.py --ledger trader/paper-portfolio.json close --exchange BSE --symbol 500325 --price 1520 --fee 5
```

Price JSON should use exchange-qualified keys such as `NSE:RELIANCE` and `BSE:500325`. Legacy plain NSE symbol keys remain supported. Position sizing defaults to 0.5% risk per trade and 20% maximum notional. Marks and fills are user-supplied; stop alerts never execute orders.

## Backtesting

Provide a chronological OHLCV CSV with `open,high,low,close,volume` columns:

```bash
python trader-india/backtest.py --csv /path/to/daily-ohlcv.csv --capital 100000 --output trader/backtest.json
```

The baseline strategy signals on a completed close and enters at the next bar's open. Daily-bar backtests cannot fully model intraday path, gaps, liquidity, taxes or survivorship bias.

## Safety and limitations

- No broker credentials, broker API calls, order transmission or live execution are included.
- Signals are rule matches, not buy/sell recommendations.
- NSE and BSE prices currently use Yahoo Finance's unofficial chart endpoint; it may be delayed, rate-limited, incomplete or adjusted.
- BSE intraday coverage may be missing for some scrips. Failed or missing bars are reported as errors, not fabricated.
- Sector maps cover selected symbols only, not official full-market breadth.
- F&O analysis currently accepts normalized user-supplied NSE derivatives CSV only.
- Paper results require independent validation for fees, slippage, gaps, corporate actions and data quality.

## Tests

```bash
python -m unittest discover -s tests -v
```

Tests are offline and deterministic. A green unit-test run does not validate live market-data quality, trading profitability or execution behavior.

## Preserved US scanner

The NSE and BSE engines are isolated under `trader-india`; existing US scanner modules and workflows are not repurposed as India data sources.

## License and attribution

The original imported source license and attribution are retained in LICENSE.

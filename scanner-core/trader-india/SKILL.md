---
name: trader-india
description: >-
  Independent NSE cash-equity research scanner with daily and 5-minute
  technical rules, sector snapshots, offline F&O futures OI classification,
  conservative paper sizing, local paper portfolio, backtesting and offline
  dashboard/alerts. Does not connect to brokers or transmit orders.
argument-hint: "--symbols RELIANCE,TCS,INFY | --universe trader-india/universe.csv"
---

# NSE India Scanner 5.0

The India engine is isolated from the existing US scanner. Do not reuse US
symbol universes, calendars or market assumptions.

## Daily and intraday scans

Run from `scanner-core`:

    python trader-india/india.py --universe trader-india/universe.csv --output trader/india-daily.json
    python trader-india/intraday.py --universe trader-india/universe.csv --output trader/india-intraday.json
    python trader-india/sectors.py --universe trader-india/universe.csv --output trader/sector-strength.json

Daily rules include 20-session breakout, bull flag, MA20 reclaim, RSI-14
oversold and oversold bounce. Intraday requires completed 5-minute bars,
a 15-minute opening range and a close above its high with relative volume
confirmation. Sector snapshots are limited to the curated sector map.

## Universe and derivatives data

    python trader-india/universe.py --input /path/to/nse-equity-master.csv --output trader-india/universe.csv --series EQ
    python trader-india/derivatives.py --csv /path/to/normalized-fo-bhavcopy.csv --output trader/fo-analysis.json

The equity master and F&O files are user-supplied. Check source date, columns,
series, expiry and symbol mappings. Derivatives input schema:

    symbol,instrument,expiry,open_interest,change_in_oi,volume,close,underlying_close,previous_underlying_close

Futures OI classification covers long buildup, short buildup, short covering
and long unwinding when both price and OI changes exist. Full option-chain PCR,
max pain and automated official-file downloads are not implemented.

## Paper-only risk and portfolio

    python trader-india/paper.py --symbol RELIANCE --capital 100000 --entry 1500 --stop 1485 --record trader/paper-sizing.json
    python trader-india/portfolio.py --ledger trader/paper-portfolio.json open --symbol RELIANCE --qty 5 --entry 1500 --stop 1480
    python trader-india/portfolio.py --ledger trader/paper-portfolio.json mark --prices /path/to/prices.json
    python trader-india/portfolio.py --ledger trader/paper-portfolio.json close --symbol RELIANCE --price 1520 --fee 5

Sizing caps are 0.5% risk per trade and 20% notional by default. Portfolio
marks and fills are user-supplied. Stop alerts are informational and do not
place exit orders. The local ledger is not a broker statement or tax record.

## Backtest, alerts and dashboard

    python trader-india/backtest.py --csv /path/to/daily-ohlcv.csv --capital 100000 --output trader/backtest.json
    python trader-india/alerts.py --input trader/india-intraday.json --output trader/india-alerts.json
    python trader-india/dashboard.py --input Daily=trader/india-daily.json --input Intraday=trader/india-intraday.json --output trader/india-dashboard.html

Backtest CSV must be chronological OHLCV. Entries are next-open after a prior
completed-close signal. Daily-bar simulation cannot model all intraday paths,
gaps, liquidity, taxes or survivorship bias.

## Data quality and safety

Daily/intraday prices use Yahoo Finance's unofficial chart endpoint and may
be delayed, incomplete, adjusted or rate-limited. The default universe is a
starter list, not the entire NSE market. No broker API, credential, order
transmission or live execution is present. All outputs are research rules,
not recommendations. Do not use for live trading without independent data,
risk, legal and execution validation.

Run offline tests:

    python -m unittest discover -s tests -v

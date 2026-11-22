---
name: trader-india
description: >-
  Independent NSE and BSE cash-equity research scanners with daily and 5-minute
  technical rules, sector snapshots, offline NSE F&O futures OI classification,
  conservative exchange-aware paper portfolio, backtesting and local dashboard.
  No broker connection or live order transmission.
argument-hint: "--exchange NSE|BSE --symbols SYMBOL1,SYMBOL2"
---

# India Equity Scanner 5.0 (NSE + BSE)

The India engines are isolated from the existing US scanner. NSE and BSE use
separate exchange adapters and symbol universes. Do not reuse US market assumptions.

## NSE daily and intraday

    python trader-india/india.py --universe trader-india/universe.csv --output trader/india-daily.json
    python trader-india/intraday.py --universe trader-india/universe.csv --output trader/india-intraday.json

Daily setups include 20-session breakout, bull flag, MA20 reclaim, RSI-14
oversold and oversold bounce. Intraday uses completed 5-minute candles, a
15-minute opening range and volume confirmation.

## BSE daily and intraday

BSE uses numeric scrip codes mapped to Yahoo Finance `.BO` tickers:

    python trader-india/bse.py --universe trader-india/bse-universe.csv --output trader/bse-daily.json
    python trader-india/bse.py --symbols 500325,532540
    python trader-india/bse_intraday.py --universe trader-india/bse-universe.csv --output trader/bse-intraday.json

The included BSE list is a small starter sample, not the full exchange listing.
Validate each scrip code against the latest BSE scrip master and verify whether
Yahoo Finance supplies reliable daily and intraday bars for that code.

## Sector snapshots

    python trader-india/sectors.py --universe trader-india/universe.csv --output trader/nse-sectors.json
    python trader-india/sectors.py --exchange BSE --universe trader-india/bse-universe.csv --output trader/bse-sectors.json

Sector classification covers selected symbols only and is not official index breadth.

## NSE universe and derivatives

    python trader-india/universe.py --input /path/to/nse-equity-master.csv --output trader-india/universe.csv --series EQ
    python trader-india/derivatives.py --csv /path/to/normalized-fo-bhavcopy.csv --output trader/fo-analysis.json

F&O CSV must be mapped to:
`symbol,instrument,expiry,open_interest,change_in_oi,volume,close,underlying_close,previous_underlying_close`

Futures OI buildup is classified only when prior underlying close and OI changes
are present. Full option-chain PCR, max pain and automated official downloads
are not included. This F&O parser is currently documented for NSE files.

## Exchange-aware paper portfolio

    python trader-india/portfolio.py --ledger trader/paper-portfolio.json open --exchange NSE --symbol RELIANCE --qty 5 --entry 1500 --stop 1480
    python trader-india/portfolio.py --ledger trader/paper-portfolio.json open --exchange BSE --symbol 500325 --qty 5 --entry 1500 --stop 1480
    python trader-india/portfolio.py --ledger trader/paper-portfolio.json mark --prices /path/to/prices.json
    python trader-india/portfolio.py --ledger trader/paper-portfolio.json close --exchange BSE --symbol 500325 --price 1520 --fee 5

Price JSON keys should be exchange-qualified, for example `NSE:RELIANCE` and
`BSE:500325`. Plain NSE symbol keys remain accepted for older ledgers.

Sizing module defaults to 0.5% capital risk per trade and 20% maximum notional.
Marks and fills are user-supplied. Stop alerts never execute orders.

## Backtest, alerts and dashboard

    python trader-india/backtest.py --csv /path/to/daily-ohlcv.csv --capital 100000 --output trader/backtest.json
    python trader-india/alerts.py --input trader/india-intraday.json --output trader/india-alerts.json
    python trader-india/dashboard.py --input Daily=trader/india-daily.json --input Intraday=trader/india-intraday.json --output trader/india-dashboard.html

Backtest input is chronological OHLCV. It is a baseline daily-bar simulation,
not a prediction or a full market microstructure replay.

## Data quality and safety

NSE `.NS` and BSE `.BO` prices use an unofficial Yahoo Finance chart feed;
it may be delayed, rate-limited, incomplete or lack BSE intraday coverage.
The BSE starter universe and sector map are not complete exchange coverage.
F&O analysis currently accepts normalized user-supplied NSE derivatives CSV.
No broker credentials, broker API, order transmission or live execution is
included. Research only; not financial advice.

Run offline tests:

    python -m unittest discover -s tests -v


## DhanHQ Broker Connect
The web dashboard includes an optional DhanHQ v2 panel for profile verification,
LTP quote snapshots, funds, holdings, positions, order book and manually
confirmed BUY/SELL orders. See `web-dashboard/DHAN_INTEGRATION.md`.

Live order transmission is disabled by default. Dhan requires a fixed,
whitelisted static IP for order placement. Never enable live orders on a host
without verifying that its outbound IP is fixed and registered with Dhan.
Scanner signals may prefill the order ticket but never auto-submit orders.

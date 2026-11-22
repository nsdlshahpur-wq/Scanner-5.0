---
name: trader-india
description: >-
  Independent NSE and BSE cash-equity research scanners with daily and 5-minute
  technical rules, sector snapshots, offline NSE F&O futures OI classification,
  conservative exchange-aware paper portfolio, backtesting and DhanHQ broker
  connection with manually confirmed orders behind a static-IP safety gate.
argument-hint: "--exchange NSE|BSE --symbols SYMBOL1,SYMBOL2"
---

# India Equity Scanner 5.0 (NSE + BSE)

The India engines are isolated from the existing US scanner. NSE and BSE use
separate exchange adapters and symbol universes. Do not reuse US market assumptions.

## NSE daily and intraday
    python trader-india/india.py --universe trader-india/universe.csv --output trader/india-daily.json
    python trader-india/intraday.py --universe trader-india/universe.csv --output trader/india-intraday.json

## BSE daily and intraday
    python trader-india/bse.py --universe trader-india/bse-universe.csv --output trader/bse-daily.json
    python trader-india/bse_intraday.py --universe trader-india/bse-universe.csv --output trader/bse-intraday.json

## DhanHQ Broker Connect
The web dashboard includes an optional DhanHQ v2 panel for profile verification,
LTP quote snapshots, funds, holdings, positions, order book and manually
confirmed BUY/SELL orders. See `web-dashboard/DHAN_INTEGRATION.md`.

Live order transmission is disabled by default. Dhan requires a fixed,
whitelisted static IP for order placement. Never enable live orders on a host
without verifying that its outbound IP is fixed and registered with Dhan.
Scanner signals never auto-submit orders.

## Research and safety
Scanner outputs are research signals, not recommendations. Validate instrument
IDs, price, liquidity, fees, slippage, gaps and position risk. No profitability
is guaranteed. The original NSE/BSE research and paper portfolio modules remain
available independently of Dhan integration.

Run offline tests:
    python -m unittest discover -s tests -v

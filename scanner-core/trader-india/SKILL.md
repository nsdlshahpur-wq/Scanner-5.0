---
name: trader-india
description: >-
  Scans Indian NSE cash equities using public price history for technical
  setup candidates, computes conservative risk-based paper position sizing,
  and stores local paper-trade records. Supports daily breakout, bull flag,
  moving-average reclaim, RSI oversold and opening-range confirmation. Does
  not transmit orders or connect to a broker. Use for NSE stocks, Indian
  market scanning, technical analysis and paper-trading preparation.
argument-hint: "--symbols RELIANCE,TCS,INFY | --universe trader-india/universe.csv"
---

# NSE India Scanner

## Purpose

The NSE scanner is an independent market engine. It does not reuse the US
Nasdaq symbol universe, US trading calendar or US market timezone. The existing
US scanner remains unchanged.

## Run

Run commands from the scanner-core directory:

    python trader-india/india.py --universe trader-india/universe.csv --output trader/india-watchlist.json
    python trader-india/india.py --symbols RELIANCE,TCS,INFY
    python trader-india/paper.py --symbol RELIANCE --capital 100000 --entry 1500 --stop 1485 --record trader/paper-ledger.json
    python -m unittest discover -s tests -v

## Daily setups

- breakout_20d: last completed close above the previous 20 completed closes.
- bull_flag: prior advance greater than 10 percent, followed by a tight five-bar range.
- reclaim_ma20: previous close below its 20-session average and latest close above it.
- oversold: Wilder RSI-14 below 30.
- oversold_bounce: RSI-14 was below 30 on the prior completed close and price has advanced.

The current session's unfinished daily candle is excluded before 15:45 IST.
The daily scanner reports candidates only. It does not create an entry order.
A conservative watch flag rejects candidates extended more than 5 percent
above the 20-session average.

## Intraday opening range

The opening-range helper requires three completed five-minute bars for the
first 15 minutes of the regular NSE session (09:15 to 09:30 IST). A signal is
reported only when a later completed five-minute bar closes above the opening
range high. The range low is returned as a structural reference, not a
guaranteed stop price.

## Conservative paper sizing

- Maximum risk budget is 0.5 percent of stated capital per trade.
- Maximum position notional is 20 percent of stated capital.
- Quantity is rounded down to whole shares.
- Stop must be below entry for a long position.
- Paper ledger records are local JSON records only.

The sizing function does not account automatically for taxes, brokerage,
slippage, gaps, circuit limits, liquidity or corporate actions. A gap can cause
losses larger than the planned stop risk. Do not widen a stop after entry.

## Data and universe

The default CSV is a curated starter list of liquid NSE names, not the full
NSE listing. Supply a maintained CSV with a symbol column to scan a wider
universe. Yahoo Finance chart endpoints are unofficial, may be delayed,
rate-limited or incomplete, and must be independently verified.

## Planned later phases

Official NSE bhavcopy ingestion, F&O open-interest buildup, full-universe
refresh, sector breadth, live alerting, multi-timeframe filters and systematic
backtesting are not yet implemented. Do not describe them as active features.

## Safety

This is research software, not financial advice. No broker integration is
called by this module. Paper mode only during development. Never paste broker
credentials into source files or chat. Verify data quality and all risk
assumptions before relying on a setup.

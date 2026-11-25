---
name: trader-smc
description: >-
  Explainable Smart Money Concepts research for NSE equities. Detects
  confirmed swing structure, BOS/CHOCH, liquidity sweeps, fair-value gaps,
  heuristic order-block candidates and premium/discount location from Yahoo
  Finance OHLCV bars. Use when the user requests SMC, market structure,
  liquidity, imbalance or institutional-style technical screening. This is
  an analytical approximation, not access to institutional order flow.
argument-hint: "--symbols RELIANCE,TCS [--interval 5m|15m|60m|1d]"
---

# Trader SMC

Run from scanner-core:

    python trader-india/smc.py --symbols RELIANCE,TCS --interval 5m --range 5d
    python trader-india/smc.py --universe trader-india/universe.csv --interval 15m --output trader/smc-watchlist.json

## Included concepts

- Confirmed swing highs and lows (right-side bars required to avoid look-ahead).
- Break of Structure (BOS) and Change of Character (CHOCH) approximations.
- Buy-side and sell-side liquidity sweep candidates.
- Three-candle Fair Value Gap (FVG) candidates.
- Heuristic last-opposite-candle order-block candidates before a structure break.
- Premium, discount and equilibrium location in a recent dealing range.
- Transparent observations and a small confluence score; no probability or win-rate claim.

## Workflow

1. Start with the higher timeframe (for example 1d or 60m) to establish context.
2. Use 15m or 5m for structure and setup review; do not treat a developing candle as confirmed.
3. Check whether a sweep is followed by a structure shift and whether an FVG or order-block candidate is nearby.
4. Review the dealing-range location. A discount/premium label alone is not an entry.
5. Require a separate entry trigger, invalidation, stop, target, position sizing and risk approval through the existing day-trading workflow.
6. Refresh the quote and verify liquidity, spread, news and feed timestamp before any decision.

## Important limitations

The linked SMC Intelligence Elite web app is a visual reference only; this repository does not import its private source code, signals or backend. The implementation here is an independent, explainable approximation based on OHLCV bars. It does not know actual resting orders, dealer inventory, footprint, DOM, exchange order book or institutional intent. Yahoo Finance data is unofficial and may be delayed, incomplete or rate-limited. NSE only in this first integration; BSE support and broker streaming are not implied.

No automatic orders are placed. This is research tooling, not financial advice.

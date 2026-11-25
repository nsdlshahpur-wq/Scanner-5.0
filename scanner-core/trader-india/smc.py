#!/usr/bin/env python3
"""Explainable Smart Money Concepts (SMC) research scanner for NSE OHLCV bars.

Detects confirmed swing structure, BOS/CHOCH, liquidity sweeps, fair-value
gaps, simple order-block candidates and premium/discount location. It emits
research observations only; it does not place orders or predict outcomes.
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from india import IST, fetch_chart


def _number(bar, key):
    value = bar.get(key)
    return float(value) if value is not None else None


def confirmed_swings(bars, window=2):
    """Return pivot highs/lows only after window bars form on each side."""
    if window < 1:
        raise ValueError("window must be >= 1")
    highs, lows = [], []
    for i in range(window, len(bars) - window):
        high, low = _number(bars[i], "high"), _number(bars[i], "low")
        if high is None or low is None:
            continue
        left = bars[i-window:i]
        right = bars[i+1:i+window+1]
        if all(high > float(x["high"]) for x in left + right if x.get("high") is not None):
            highs.append({"index": i, "price": high, "time": bars[i].get("time")})
        if all(low < float(x["low"]) for x in left + right if x.get("low") is not None):
            lows.append({"index": i, "price": low, "time": bars[i].get("time")})
    return highs, lows


def detect_fvg(bars):
    """Three-candle imbalance candidates; middle candle is displacement."""
    gaps = []
    for i in range(2, len(bars)):
        first, third = bars[i-2], bars[i]
        first_high, first_low = _number(first, "high"), _number(first, "low")
        third_high, third_low = _number(third, "high"), _number(third, "low")
        if None in (first_high, first_low, third_high, third_low):
            continue
        if third_low > first_high:
            gaps.append({"type": "bullish_fvg", "lower": first_high,
                         "upper": third_low, "index": i, "time": third.get("time")})
        elif third_high < first_low:
            gaps.append({"type": "bearish_fvg", "lower": third_high,
                         "upper": first_low, "index": i, "time": third.get("time")})
    return gaps


def detect_order_block(bars, swings):
    """Find last opposite candle before a close breaks a confirmed swing."""
    candidates = []
    for side, pivots in (("bullish", swings[0]), ("bearish", swings[1])):
        for pivot in pivots:
            level, pivot_i = pivot["price"], pivot["index"]
            for i in range(pivot_i + 1, len(bars)):
                close = _number(bars[i], "close")
                if close is None:
                    continue
                broken = close > level if side == "bullish" else close < level
                if not broken:
                    continue
                for j in range(i - 1, pivot_i, -1):
                    op, cl = _number(bars[j], "open"), _number(bars[j], "close")
                    hi, lo = _number(bars[j], "high"), _number(bars[j], "low")
                    if None in (op, cl, hi, lo):
                        continue
                    opposite = cl < op if side == "bullish" else cl > op
                    if opposite:
                        candidates.append({"type": side + "_order_block",
                                           "lower": lo, "upper": hi,
                                           "index": j, "break_index": i,
                                           "time": bars[j].get("time")})
                        break
                break
    return candidates


def analyze_smc(symbol, bars, window=2, lookback=100):
    bars = list(bars)[-lookback:]
    if len(bars) < max(2 * window + 5, 15):
        return {"symbol": symbol, "status": "insufficient_data", "bars": len(bars),
                "observations": [], "score": 0, "bias": "neutral"}
    highs, lows = confirmed_swings(bars, window)
    close = _number(bars[-1], "close")
    if close is None or not highs or not lows:
        return {"symbol": symbol, "status": "insufficient_structure", "bars": len(bars),
                "observations": [], "score": 0, "bias": "neutral"}

    last_high, last_low = highs[-1], lows[-1]
    prev_high = highs[-2] if len(highs) > 1 else None
    prev_low = lows[-2] if len(lows) > 1 else None
    previous_close = _number(bars[-2], "close")
    observations = []
    bias = "neutral"

    if previous_close is not None and previous_close <= last_high["price"] < close:
        kind = "bullish_bos" if prev_high and last_high["price"] > prev_high["price"] else "bullish_choch"
        observations.append(kind)
        bias = "bullish"
    elif previous_close is not None and previous_close >= last_low["price"] > close:
        kind = "bearish_bos" if prev_low and last_low["price"] < prev_low["price"] else "bearish_choch"
        observations.append(kind)
        bias = "bearish"

    bar_high, bar_low = _number(bars[-1], "high"), _number(bars[-1], "low")
    if bar_high is not None and bar_low is not None:
        if bar_high > last_high["price"] and close < last_high["price"]:
            observations.append("buy_side_liquidity_sweep")
        if bar_low < last_low["price"] and close > last_low["price"]:
            observations.append("sell_side_liquidity_sweep")

    gaps = detect_fvg(bars)
    active_gaps = [g for g in gaps if g["index"] >= max(0, len(bars) - 12)]
    for gap in active_gaps:
        if gap["type"] not in observations:
            observations.append(gap["type"])

    blocks = detect_order_block(bars, (highs, lows))
    active_blocks = [b for b in blocks if b["break_index"] >= len(bars) - 12]
    for block in active_blocks:
        if block["type"] not in observations:
            observations.append(block["type"])

    range_high = max(x["price"] for x in highs[-5:])
    range_low = min(x["price"] for x in lows[-5:])
    midpoint = (range_high + range_low) / 2
    location = "discount" if close < midpoint else "premium" if close > midpoint else "equilibrium"
    observations.append(location)

    directional = "bullish" if any(x.startswith(("bullish_", "sell_side_")) for x in observations) else (
        "bearish" if any(x.startswith(("bearish_", "buy_side_")) for x in observations) else bias)
    aligned = [x for x in observations if
               (directional == "bullish" and x.startswith(("bullish_", "sell_side_"))) or
               (directional == "bearish" and x.startswith(("bearish_", "buy_side_")))]
    score = min(5, len(set(aligned)) + int(
        (directional == "bullish" and location == "discount") or
        (directional == "bearish" and location == "premium")))
    return {
        "symbol": symbol, "status": "ok", "as_of": bars[-1].get("time"),
        "bars": len(bars), "last_close": close, "bias": directional,
        "structure": {"last_swing_high": last_high, "last_swing_low": last_low},
        "dealing_range": {"high": range_high, "low": range_low,
                          "equilibrium": midpoint, "location": location},
        "observations": observations, "recent_fvgs": active_gaps[-5:],
        "recent_order_blocks": active_blocks[-5:], "confluence_score": score,
        "watch_only": score >= 2,
        "method_note": "Rule-based SMC approximations from OHLCV; pivots require right-side confirmation. "
                       "Order blocks are heuristic candidates, not institutional order-flow data.",
        "data_warning": "Yahoo Finance chart feed is unofficial and may be delayed or incomplete."
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="NSE SMC structure scanner (research/paper only)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--symbols", help="Comma-separated NSE symbols")
    group.add_argument("--universe", help="CSV file with a symbol column")
    parser.add_argument("--interval", choices=("5m", "15m", "30m", "60m", "1d"), default="5m")
    parser.add_argument("--range", dest="range_", default="5d")
    parser.add_argument("--lookback", type=int, default=100)
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    if args.lookback < 15:
        parser.error("--lookback must be at least 15")
    if args.symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    else:
        with open(args.universe, newline="", encoding="utf-8-sig") as handle:
            symbols = [r["symbol"].strip().upper() for r in csv.DictReader(handle) if r.get("symbol")]
    now = dt.datetime.now(IST)
    results, errors = [], []
    for symbol in dict.fromkeys(symbols):
        try:
            bars = fetch_chart(symbol, interval=args.interval, range_=args.range_)
            results.append(analyze_smc(symbol, bars, lookback=args.lookback))
        except Exception as exc:
            errors.append({"symbol": symbol, "error": str(exc)})
    payload = {"market": "NSE", "mode": "research_only", "strategy": "SMC",
               "interval": args.interval, "as_of": now.isoformat(), "results": results,
               "watchlist": [r for r in results if r.get("watch_only")], "errors": errors,
               "safety": "No broker orders are sent. SMC observations are not trade recommendations."}
    rendered = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered + "\n")
    print("SMC scanned:", len(results), "watchlist:", len(payload["watchlist"]), "errors:", len(errors))
    print(rendered if not args.output else "Saved: " + args.output)
    return 0 if results else 1


if __name__ == "__main__":
    raise SystemExit(main())

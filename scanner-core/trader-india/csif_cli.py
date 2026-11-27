#!/usr/bin/env python3
"""CSIF CLI for timestamped 5-minute OHLCV CSV files; paper mode only."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path

from csif.engine import parse_bars, scan
from csif.backtest import run_backtest
from csif.paper import open_paper_position


def main(argv=None):
    parser = argparse.ArgumentParser(description="CSIF CRT-SMC-ICT Fusion Scanner")
    parser.add_argument("--csv", required=True, help="5-minute OHLCV CSV with timestamp,open,high,low,close,volume")
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--exchange", choices=("NSE", "BSE"), required=True)
    parser.add_argument("--mode", choices=("intraday", "swing", "both"), default="both")
    parser.add_argument("--action", choices=("scan", "backtest"), default="scan")
    parser.add_argument("--capital", type=float, default=100000.0)
    parser.add_argument("--risk-pct", type=float, default=0.5)
    parser.add_argument("--fee-bps", type=float, default=5.0)
    parser.add_argument("--slippage-bps", type=float, default=5.0)
    parser.add_argument("--output", help="Optional JSON output path")
    parser.add_argument("--paper-open-first-signal", action="store_true",
                        help="Explicitly open the first qualified signal in the local paper ledger")
    parser.add_argument("--paper-ledger", default="trader/csif-paper-ledger.json")
    args = parser.parse_args(argv)

    with open(args.csv, newline="", encoding="utf-8-sig") as handle:
        bars = parse_bars(csv.DictReader(handle))
    modes = ("intraday", "swing") if args.mode == "both" else (args.mode,)

    if args.action == "backtest":
        result = run_backtest(bars, args.symbol, args.exchange,
            initial_capital=args.capital, risk_pct=args.risk_pct,
            fee_bps=args.fee_bps, slippage_bps=args.slippage_bps, modes=modes)
    else:
        result = {"strategy": "CSIF CRT-SMC-ICT Fusion", "mode": list(modes),
                  "symbol": args.symbol, "exchange": args.exchange,
                  "bar_count": len(bars), "signals": scan(bars, args.symbol, args.exchange, modes)}

    if args.paper_open_first_signal:
        if args.action != "scan":
            parser.error("--paper-open-first-signal can only be used with --action scan")
        if not result["signals"]:
            parser.error("No qualified signal is available to open in the paper ledger")
        result["paper_position"] = open_paper_position(
            args.paper_ledger, result["signals"][0], args.capital, args.risk_pct)

    rendered = json.dumps(result, indent=2, default=str)
    if args.output:
        destination = Path(args.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

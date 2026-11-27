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


def load_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return parse_bars(csv.DictReader(handle))


def main(argv=None):
    parser = argparse.ArgumentParser(description="CSIF CRT-SMC-ICT Fusion Scanner")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--csv", help="One symbol's 5-minute OHLCV CSV")
    source.add_argument("--data-dir", help="Directory containing one 5-minute OHLCV CSV per symbol")
    parser.add_argument("--symbol", help="Required with --csv; otherwise derived from CSV filename")
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

    if args.csv and not args.symbol:
        parser.error("--symbol is required when --csv is used")
    if args.data_dir and args.paper_open_first_signal:
        parser.error("Paper-open is supported only for one explicit --csv signal")
    modes = ("intraday", "swing") if args.mode == "both" else (args.mode,)
    paths = [Path(args.csv)] if args.csv else sorted(Path(args.data_dir).glob("*.csv"))
    if not paths:
        parser.error("No CSV files found")
    results = []
    for path in paths:
        symbol = args.symbol if args.csv else path.stem.replace("-5m", "").replace("_5m", "")
        bars = load_csv(path)
        if args.action == "backtest":
            result = run_backtest(bars, symbol, args.exchange,
                initial_capital=args.capital, risk_pct=args.risk_pct,
                fee_bps=args.fee_bps, slippage_bps=args.slippage_bps, modes=modes)
        else:
            result = {"strategy": "CSIF CRT-SMC-ICT Fusion", "mode": list(modes),
                      "symbol": symbol, "exchange": args.exchange,
                      "source_file": str(path), "bar_count": len(bars),
                      "signals": scan(bars, symbol, args.exchange, modes)}
        if args.paper_open_first_signal:
            if args.action != "scan":
                parser.error("--paper-open-first-signal can only be used with --action scan")
            if not result["signals"]:
                parser.error("No qualified signal is available to open in the paper ledger")
            result["paper_position"] = open_paper_position(
                args.paper_ledger, result["signals"][0], args.capital, args.risk_pct)
        results.append(result)

    payload = results[0] if args.csv else {"exchange": args.exchange, "action": args.action,
                                           "symbols_processed": len(results), "results": results}
    rendered = json.dumps(payload, indent=2, default=str)
    if args.output:
        destination = Path(args.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

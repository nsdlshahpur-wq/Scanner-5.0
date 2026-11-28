"""Local CSIF paper ledger. No broker calls and no live-order capability."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import math


def _load(path: str, initial_capital: float = 100000.0) -> dict[str, Any]:
    file = Path(path)
    if not file.exists():
        return {"mode": "PAPER_ONLY", "cash": float(initial_capital), "initial_capital": float(initial_capital), "positions": [], "closed_trades": []}
    data = json.loads(file.read_text(encoding="utf-8"))
    if data.get("mode") != "PAPER_ONLY":
        raise ValueError("CSIF ledger must remain PAPER_ONLY")
    return data


def _save(path: str, data: dict[str, Any]) -> None:
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    temp = file.with_suffix(file.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    temp.replace(file)


def open_paper_position(path: str, signal: dict[str, Any], capital: float,
                        risk_pct: float = 0.5, max_notional_pct: float = 20.0,
                        max_total_risk_pct: float = 1.0, max_open_positions: int = 2) -> dict[str, Any]:
    if capital <= 0 or not 0 < risk_pct <= 1 or not 0 < max_notional_pct <= 100 or not 0 < max_total_risk_pct <= 5 or max_open_positions < 1:
        raise ValueError("Invalid paper capital or risk parameters")
    if signal.get("direction") not in {"BULLISH", "BEARISH"}:
        raise ValueError("Signal direction must be BULLISH or BEARISH")
    entry, stop, target = (float(signal[k]) for k in ("entry_reference", "stop", "target"))
    risk = entry - stop if signal["direction"] == "BULLISH" else stop - entry
    if risk <= 0 or abs(target - entry) / risk < 2:
        raise ValueError("Invalid stop or reward-to-risk below 1:2")
    ledger = _load(path, capital)
    if len(ledger["positions"]) >= max_open_positions:
        raise ValueError("Maximum concurrent paper positions reached")
    if any(x["symbol"] == signal["symbol"] and x["exchange"] == signal["exchange"]
           for x in ledger["positions"]):
        raise ValueError("An open paper position already exists for this exchange/symbol")
    risk_cash = capital * risk_pct / 100
    qty = min(math.floor(risk_cash / risk),
              math.floor(capital * max_notional_pct / 100 / entry))
    if signal["direction"] == "BULLISH":
        qty = min(qty, math.floor(max(0.0, float(ledger["cash"])) / entry))
    if qty < 1:
        raise ValueError("Position size is zero under configured risk/notional/cash caps")
    existing_risk = sum(float(x.get("max_loss_estimate", 0)) for x in ledger["positions"])
    if existing_risk + qty * risk > capital * max_total_risk_pct / 100:
        raise ValueError("Aggregate open risk would exceed the configured portfolio risk cap")
    position = {
        "id": f"CSIF-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}",
        "status": "OPEN_PAPER", "opened_at": datetime.now(timezone.utc).isoformat(),
        "symbol": signal["symbol"], "exchange": signal["exchange"],
        "mode": signal["mode"], "direction": signal["direction"],
        "entry": entry, "stop": stop, "target": target, "quantity": qty,
        "score": int(signal["score"]), "signal_time": signal["timestamp"],
        "max_loss_estimate": round(qty * risk, 2)
    }
    ledger["positions"].append(position)
    ledger["cash"] = (float(ledger["cash"]) - qty * entry) if signal["direction"] == "BULLISH" else (float(ledger["cash"]) + qty * entry)
    _save(path, ledger)
    return position


def mark_paper_positions(path: str, prices: dict[str, float]) -> dict[str, Any]:
    ledger = _load(path)
    marks = []
    for position in ledger["positions"]:
        key = f'{position["exchange"]}:{position["symbol"]}'
        if key not in prices:
            continue
        price = float(prices[key])
        direction = 1 if position["direction"] == "BULLISH" else -1
        pnl = (price - position["entry"]) * position["quantity"] * direction
        marks.append({"id": position["id"], "symbol": key, "ltp": price,
                      "unrealized_pnl": round(pnl, 2)})
    return {"mode": "PAPER_ONLY", "marks": marks}


def close_paper_position(path: str, position_id: str, exit_price: float,
                         fee_bps: float = 5.0, slippage_bps: float = 5.0) -> dict[str, Any]:
    if exit_price <= 0 or fee_bps < 0 or slippage_bps < 0:
        raise ValueError("Invalid exit price or costs")
    ledger = _load(path)
    position = next((x for x in ledger["positions"] if x["id"] == position_id), None)
    if position is None:
        raise ValueError("Open paper position not found")
    direction = 1 if position["direction"] == "BULLISH" else -1
    gross = (exit_price - position["entry"]) * position["quantity"] * direction
    costs = (position["entry"] + exit_price) * position["quantity"] * (fee_bps + slippage_bps) / 10000
    net = gross - costs
    ledger["cash"] = (ledger["cash"] + position["quantity"] * exit_price - costs) if position["direction"] == "BULLISH" else (ledger["cash"] - position["quantity"] * exit_price - costs)
    ledger["positions"].remove(position)
    closed = {**position, "status": "CLOSED_PAPER",
              "closed_at": datetime.now(timezone.utc).isoformat(),
              "exit": exit_price, "gross_pnl": round(gross, 2),
              "costs": round(costs, 2), "net_pnl": round(net, 2)}
    ledger["closed_trades"].append(closed)
    _save(path, ledger)
    return closed

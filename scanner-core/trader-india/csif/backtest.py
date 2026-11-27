"""CSIF historical simulation: close-confirmed signal, next-bar FVG fill."""
from __future__ import annotations
from typing import Any
import math
from datetime import timedelta
from .engine import Bar, scan


def run_backtest(
    bars: list[Bar], symbol: str, exchange: str = "NSE",
    initial_capital: float = 100000.0, risk_pct: float = 0.5,
    daily_loss_pct: float = 1.0, fee_bps: float = 5.0,
    slippage_bps: float = 5.0, min_rr: float = 2.0,
    modes: tuple[str, ...] = ("intraday", "swing"),
    rolling_window: int = 2400
) -> dict[str, Any]:
    if initial_capital <= 0 or not 0 < risk_pct <= 1 or not 0 < daily_loss_pct <= 5:
        raise ValueError("Invalid capital or risk configuration")
    if fee_bps < 0 or slippage_bps < 0 or rolling_window < 700:
        raise ValueError("Invalid costs or rolling window; use at least 700 bars")
    if len(bars) < 700:
        raise ValueError("At least 700 five-minute bars are required for HTF warm-up")
    cash = float(initial_capital)
    equity_curve = [cash]
    trades: list[dict[str, Any]] = []
    position = None
    daily_realized: dict[str, float] = {}
    signal_map: dict[str, dict[str, Any]] = {}
    max_trades_per_day = 2
    daily_count: dict[str, int] = {}

    for i in range(600, len(bars) - 1):
        history = bars[max(0, i - rolling_window + 1):i + 1]
        # Scan only on the current completed 5m close. Hourly swing signals
        # are emitted only when a complete 1h bucket becomes available.
        for signal in scan(history, symbol, exchange, modes, 80, min_rr):
            signal_map[signal["timestamp"]] = signal

        bar = bars[i]
        day = bar.timestamp.date().isoformat()
        daily_pnl = daily_realized.get(day, 0.0)
        if position:
            exit_price = reason = None
            if position["direction"] == "BULLISH":
                if bar.low <= position["stop"]:
                    exit_price, reason = position["stop"], "stop"
                elif bar.high >= position["target"]:
                    exit_price, reason = position["target"], "target"
            else:
                if bar.high >= position["stop"]:
                    exit_price, reason = position["stop"], "stop"
                elif bar.low <= position["target"]:
                    exit_price, reason = position["target"], "target"
            if exit_price is not None:
                gross = (exit_price - position["entry"]) * position["qty"]
                if position["direction"] == "BEARISH":
                    gross = -gross
                costs = (position["entry"] + exit_price) * position["qty"] * (
                    fee_bps + slippage_bps) / 10000
                pnl = gross - costs
                if position["direction"] == "BULLISH":
                    cash += position["qty"] * exit_price - costs
                else:
                    cash -= position["qty"] * exit_price + costs
                daily_realized[day] = daily_realized.get(day, 0.0) + pnl
                trades.append({**position, "exit_time": bar.timestamp.isoformat(),
                    "exit": exit_price, "exit_reason": reason,
                    "gross_pnl": round(gross, 2), "costs": round(costs, 2),
                    "net_pnl": round(pnl, 2)})
                position = None

        if position is None:
            daily_pnl = daily_realized.get(day, 0.0)
            if daily_pnl > -initial_capital * daily_loss_pct / 100 and daily_count.get(day, 0) < max_trades_per_day:
                signal_time_5m = (bar.timestamp.replace(second=0, microsecond=0) +
                                  timedelta(minutes=5)).isoformat()
                signal = signal_map.get(signal_time_5m)
                if signal:
                    next_bar = bars[i + 1]
                    fill = next_bar.open
                    zone_low, zone_high = signal["fvg_low"], signal["fvg_high"]
                    if zone_low <= fill <= zone_high:
                        stop = float(signal["stop"])
                        direction = signal["direction"]
                        risk_per_share = fill - stop if direction == "BULLISH" else stop - fill
                        if risk_per_share > 0 and abs(float(signal["target"]) - fill) / risk_per_share >= min_rr:
                            risk_cash = cash * risk_pct / 100
                            qty = min(math.floor(risk_cash / risk_per_share),
                                      math.floor(cash * 0.20 / fill))
                            if qty > 0:
                                position = {"symbol": symbol, "exchange": exchange,
                                    "mode": signal["mode"], "direction": direction,
                                    "signal_time": signal["timestamp"],
                                    "entry_time": next_bar.timestamp.isoformat(),
                                    "entry": fill, "stop": stop, "target": float(signal["target"]),
                                    "qty": qty, "score": int(signal["score"]),
                                    "risk_per_share": risk_per_share}
                                cash = cash - qty * fill if direction == "BULLISH" else cash + qty * fill
                                daily_count[day] = daily_count.get(day, 0) + 1

        mark = cash + ((position["qty"] * bar.close) if position and position["direction"] == "BULLISH" else (-position["qty"] * bar.close if position else 0.0))
        equity_curve.append(mark)

    if position:
        last = bars[-1]
        exit_price = last.close
        gross = (exit_price - position["entry"]) * position["qty"]
        if position["direction"] == "BEARISH":
            gross = -gross
        costs = (position["entry"] + exit_price) * position["qty"] * (
            fee_bps + slippage_bps) / 10000
        pnl = gross - costs
        cash = (cash + position["qty"] * exit_price - costs) if position["direction"] == "BULLISH" else (cash - position["qty"] * exit_price - costs)
        trades.append({**position, "exit_time": last.timestamp.isoformat(),
            "exit": exit_price, "exit_reason": "end_of_data",
            "gross_pnl": round(gross, 2), "costs": round(costs, 2),
            "net_pnl": round(pnl, 2)})

    wins = [x for x in trades if x["net_pnl"] > 0]
    losses = [x for x in trades if x["net_pnl"] <= 0]
    peak, max_dd = equity_curve[0], 0.0
    for value in equity_curve:
        peak = max(peak, value)
        if peak:
            max_dd = max(max_dd, (peak - value) / peak)
    profit = sum(x["net_pnl"] for x in wins)
    loss = abs(sum(x["net_pnl"] for x in losses))
    return {
        "strategy": "CSIF CRT-SMC-ICT Fusion",
        "symbol": symbol, "exchange": exchange, "modes": list(modes),
        "initial_capital": initial_capital, "ending_equity": round(cash, 2),
        "net_pnl": round(cash - initial_capital, 2),
        "trade_count": len(trades),
        "win_rate_pct": round(100 * len(wins) / len(trades), 2) if trades else 0.0,
        "profit_factor": round(profit / loss, 2) if loss else None,
        "max_drawdown_pct": round(max_dd * 100, 2),
        "average_net_trade": round(sum(x["net_pnl"] for x in trades) / len(trades), 2) if trades else 0.0,
        "trades": trades,
        "assumptions": [
            "Input is timestamped 5-minute OHLCV; all signals use completed bars.",
            "Signal is confirmed at candle close; entry is attempted at next 5m open.",
            "Entry is skipped unless next open remains inside the FVG zone.",
            "If stop and target are touched in one OHLC bar, stop is assumed first.",
            "Costs are fixed basis-point estimates, not a broker fee schedule.",
            "The 1% daily loss and two-trades/day limits are conservative research defaults.",
            "Corporate actions, taxes, impact, queue position and survivorship bias need separate modelling.",
            "A backtest is not a forecast or evidence of future profitability."
        ]
    }

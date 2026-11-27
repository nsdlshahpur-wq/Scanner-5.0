"""CSIF: CRT + SMC + ICT Fusion signal engine.

Deterministic research logic. It consumes completed OHLCV bars only; feed and
broker execution adapters are deliberately kept outside this module.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Iterable, Optional


@dataclass(frozen=True)
class Bar:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


@dataclass(frozen=True)
class Zone:
    low: float
    high: float
    created_at: datetime
    direction: str


@dataclass
class Setup:
    symbol: str
    exchange: str
    mode: str
    direction: str
    timestamp: str
    entry_reference: float
    stop: float
    target: float
    risk_reward: float
    score: int
    crt_source: str
    crt_high: float
    crt_low: float
    sweep_extreme: float
    fvg_low: float
    fvg_high: float
    confirmations: list[str]
    invalidation: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def parse_bars(rows: Iterable[dict[str, Any]]) -> list[Bar]:
    bars = []
    for row in rows:
        ts = row.get("timestamp") or row.get("datetime") or row.get("date")
        if not ts:
            raise ValueError("Each OHLCV row requires timestamp/datetime/date")
        stamp = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        values = {key: float(row[key]) for key in ("open", "high", "low", "close")}
        volume = float(row.get("volume", 0) or 0)
        if values["high"] < max(values["open"], values["close"], values["low"]):
            raise ValueError(f"Invalid OHLC high at {ts}")
        if values["low"] > min(values["open"], values["close"], values["high"]):
            raise ValueError(f"Invalid OHLC low at {ts}")
        if min(values.values()) <= 0 or volume < 0:
            raise ValueError(f"Non-positive price or negative volume at {ts}")
        bars.append(Bar(stamp, **values, volume=volume))
    bars.sort(key=lambda item: item.timestamp)
    if len({bar.timestamp for bar in bars}) != len(bars):
        raise ValueError("Duplicate timestamps in OHLCV input")
    return bars


def resample(bars: list[Bar], minutes: int) -> list[Bar]:
    """Aggregate 5m bars into NSE/BSE session-aligned buckets from 09:15."""
    if not bars:
        return []
    buckets: dict[datetime, list[Bar]] = {}
    for bar in bars:
        ts = bar.timestamp
        minute_of_day = ts.hour * 60 + ts.minute
        anchor = 9 * 60 + 15
        offset = minute_of_day - anchor
        if offset < 0:
            continue
        bucket_index = offset // minutes
        start_minute = anchor + bucket_index * minutes
        key = ts.replace(hour=start_minute // 60, minute=start_minute % 60,
                         second=0, microsecond=0)
        buckets.setdefault(key, []).append(bar)
    out = []
    for key, group in sorted(buckets.items()):
        expected = max(1, minutes // 5)
        if minutes > 5 and len(group) < expected:
            continue
        out.append(Bar(key, group[0].open, max(x.high for x in group),
                       min(x.low for x in group), group[-1].close,
                       sum(x.volume for x in group)))
    return out


def sma(values: list[float], period: int) -> Optional[float]:
    return sum(values[-period:]) / period if len(values) >= period else None


def atr(bars: list[Bar], period: int = 14) -> Optional[float]:
    if len(bars) < period + 1:
        return None
    tr = []
    for i in range(1, len(bars)):
        cur, prev = bars[i], bars[i - 1]
        tr.append(max(cur.high - cur.low, abs(cur.high - prev.close),
                      abs(cur.low - prev.close)))
    return sum(tr[-period:]) / period if len(tr) >= period else None


def confirmed_swings(bars: list[Bar], left: int = 2, right: int = 2):
    """Return (confirmation_index, pivot_price); no unconfirmed pivots."""
    highs, lows = [], []
    for pivot in range(left, len(bars) - right):
        window = bars[pivot-left:pivot+right+1]
        if bars[pivot].high == max(x.high for x in window):
            highs.append((pivot + right, bars[pivot].high))
        if bars[pivot].low == min(x.low for x in window):
            lows.append((pivot + right, bars[pivot].low))
    return highs, lows


def htf_bias(hourly: list[Bar]) -> str:
    closes = [bar.close for bar in hourly]
    fast, slow = sma(closes, 20), sma(closes, 50)
    prior_fast = sma(closes[:-1], 20) if len(closes) > 20 else None
    if fast is None or slow is None or prior_fast is None:
        return "NEUTRAL"
    if fast > slow and fast > prior_fast and closes[-1] > fast:
        return "BULLISH"
    if fast < slow and fast < prior_fast and closes[-1] < fast:
        return "BEARISH"
    return "NEUTRAL"


def _latest_completed(series: list[Bar], asof: datetime, width: int):
    eligible = [bar for bar in series if bar.timestamp + timedelta(minutes=width) <= asof]
    return eligible[-1] if eligible else None


def _crt_sweep(raw: list[Bar], direction: str, lookback: int = 18):
    q15, q60 = resample(raw, 15), resample(raw, 60)
    start = max(0, len(raw) - lookback)
    found = []
    for index in range(start, len(raw)):
        execution = raw[index]
        asof = execution.timestamp + timedelta(minutes=5)
        for label, series, width in (("15M", q15, 15), ("1H", q60, 60)):
            current = _latest_completed(series, asof, width)
            if current is None:
                continue
            prior = [x for x in series if x.timestamp < current.timestamp]
            if not prior:
                continue
            reference = prior[-1]
            if direction == "BULLISH" and execution.low < reference.low and execution.close > reference.low:
                found.append((index, {"label": label, "high": reference.high,
                    "low": reference.low, "extreme": execution.low, "timestamp": execution.timestamp}))
            elif direction == "BEARISH" and execution.high > reference.high and execution.close < reference.high:
                found.append((index, {"label": label, "high": reference.high,
                    "low": reference.low, "extreme": execution.high, "timestamp": execution.timestamp}))
    if not found:
        return None
    return max(found, key=lambda item: item[0])[1]


def _mss(bars: list[Bar], direction: str) -> bool:
    if len(bars) < 8:
        return False
    highs, lows = confirmed_swings(bars[:-1])
    current = bars[-1]
    if direction == "BULLISH":
        levels = [price for index, price in highs if index < len(bars) - 1]
        return bool(levels and current.close > levels[-1])
    levels = [price for index, price in lows if index < len(bars) - 1]
    return bool(levels and current.close < levels[-1])


def _displacement(bars: list[Bar], direction: str) -> bool:
    current_atr = atr(bars[:-1], 14)
    if current_atr is None:
        return False
    bar = bars[-1]
    if abs(bar.close - bar.open) < current_atr * 0.8:
        return False
    return bar.close > bar.open if direction == "BULLISH" else bar.close < bar.open


def _recent_fvg(bars: list[Bar], direction: str, max_age: int = 12):
    """Find the newest FVG formed before the current (retest) candle."""
    if len(bars) < 4:
        return None
    current_index = len(bars) - 1
    first = max(2, current_index - max_age)
    for i in range(current_index - 1, first - 1, -1):
        a, c = bars[i - 2], bars[i]
        if direction == "BULLISH" and c.low > a.high:
            zone = Zone(a.high, c.low, c.timestamp, direction)
            if bars[-1].low <= zone.high and bars[-1].high >= zone.low and bars[-1].close > zone.low:
                return zone
        if direction == "BEARISH" and c.high < a.low:
            zone = Zone(c.high, a.low, c.timestamp, direction)
            if bars[-1].high >= zone.low and bars[-1].low <= zone.high and bars[-1].close < zone.high:
                return zone
    return None


def _entry_signal(bars: list[Bar], raw: list[Bar], symbol: str, exchange: str,
                  mode: str, minimum_score: int = 80, min_rr: float = 2.0):
    if len(bars) < 60 or len(raw) < 600:
        return None
    bias = htf_bias(resample(raw, 60))
    direction = bias if bias in {"BULLISH", "BEARISH"} else ""
    if not direction:
        return None
    crt = _crt_sweep(raw, direction)
    if not crt:
        return None
    # Structure shift and displacement must be complete before the retest bar.
    confirmation_bars = bars[:-1]
    if not _mss(confirmation_bars, direction):
        return None
    if not _displacement(confirmation_bars, direction):
        return None
    if crt["timestamp"] >= confirmation_bars[-1].timestamp:
        return None
    zone = _recent_fvg(bars, direction)
    if zone is None:
        return None
    retest = bars[-1]
    entry = (zone.low + zone.high) / 2
    stop = crt["extreme"]
    risk = entry - stop if direction == "BULLISH" else stop - entry
    if risk <= 0:
        return None
    minimum_target = entry + min_rr * risk if direction == "BULLISH" else entry - min_rr * risk
    liquidity = crt["high"] if direction == "BULLISH" else crt["low"]
    target = (liquidity if direction == "BULLISH" and liquidity >= minimum_target
              else liquidity if direction == "BEARISH" and liquidity <= minimum_target
              else minimum_target)
    rr = abs(target - entry) / risk
    if rr < min_rr:
        return None
    confirmations = ["1H bias aligned", f"{crt['label']} CRT sweep + close back inside",
                     "SMC MSS", "ICT displacement", "FVG retest"]
    # Weights: HTF 15, sweep 20, MSS 15, displacement 15, FVG 10,
    # retest 10, premium/discount 10, dual-CRT confluence 5.
    score = 85
    equilibrium = (crt["high"] + crt["low"]) / 2
    if (direction == "BULLISH" and entry <= equilibrium) or (direction == "BEARISH" and entry >= equilibrium):
        score += 10
        confirmations.append("Discount/premium alignment")
    # Both windows must have a matching sweep for the final +5.
    last_raw = raw[-1]
    swept_windows = set()
    for label, series, width in (("15M", resample(raw, 15), 15), ("1H", resample(raw, 60), 60)):
        completed = _latest_completed(series, last_raw.timestamp + timedelta(minutes=5), width)
        if completed:
            prior = [x for x in series if x.timestamp < completed.timestamp]
            if prior:
                ref = prior[-1]
                if direction == "BULLISH" and last_raw.low < ref.low and last_raw.close > ref.low:
                    swept_windows.add(label)
                if direction == "BEARISH" and last_raw.high > ref.high and last_raw.close < ref.high:
                    swept_windows.add(label)
    if {"15M", "1H"}.issubset(swept_windows):
        score += 5
        confirmations.append("15M + 1H CRT confluence")
    score = min(100, score)
    if score < minimum_score:
        return None
    return Setup(symbol, exchange, mode, direction, (retest.timestamp + timedelta(minutes=5 if mode == "intraday" else 60)).isoformat(),
        round(entry, 4), round(stop, 4), round(target, 4), round(rr, 2), score,
        crt["label"], round(crt["high"], 4), round(crt["low"], 4),
        round(crt["extreme"], 4), round(zone.low, 4), round(zone.high, 4),
        confirmations, "A completed close beyond the sweep extreme invalidates the setup")


def scan(raw_bars: list[Bar], symbol: str, exchange: str = "NSE",
         modes: tuple[str, ...] = ("intraday", "swing"),
         minimum_score: int = 80, min_rr: float = 2.0) -> list[dict[str, Any]]:
    """Scan completed 5m bars; swing signals are evaluated on completed 1h bars."""
    if exchange not in {"NSE", "BSE"}:
        raise ValueError("exchange must be NSE or BSE")
    raw = sorted(raw_bars, key=lambda item: item.timestamp)
    results = []
    for mode in modes:
        if mode not in {"intraday", "swing"}:
            raise ValueError("mode must be intraday or swing")
        working = raw if mode == "intraday" else resample(raw, 60)
        setup = _entry_signal(working, raw, symbol, exchange, mode, minimum_score, min_rr)
        if setup:
            results.append(setup.to_dict())
    return results

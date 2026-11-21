import datetime as dt
import importlib.util
import json
import os
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(path, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

india = load("trader-india/india.py", "scanner_india")
paper = load("trader-india/paper.py", "scanner_india_paper")
IST = india.IST

def daily_bars(closes, volumes=None, day="2026-11-20"):
    volumes = volumes or [100000] * len(closes)
    start = dt.date.fromisoformat(day) - dt.timedelta(days=len(closes)-1)
    rows = []
    for i, close in enumerate(closes):
        date = start + dt.timedelta(days=i)
        rows.append({"time": dt.datetime.combine(date, dt.time(15, 30), IST).isoformat(),
                     "open": close-0.5, "high": close+1, "low": close-1,
                     "close": close, "volume": volumes[i]})
    return rows

class Indicators(unittest.TestCase):
    def test_sma(self):
        self.assertEqual(india.sma([1,2,3,4], 3), 3)
        self.assertIsNone(india.sma([1,2], 3))

    def test_rsi_flat(self):
        self.assertEqual(india.rsi_wilder([100]*16), 50)

    def test_rsi_rising(self):
        self.assertEqual(india.rsi_wilder(list(range(100,116))), 100)

    def test_yahoo_symbol_validation(self):
        self.assertEqual(india.yahoo_ticker("reliance"), "RELIANCE.NS")
        with self.assertRaises(ValueError):
            india.yahoo_ticker("RELIANCE;DROP")

    def test_insufficient_history(self):
        result = india.analyze_daily("TEST", daily_bars(list(range(100,120))))
        self.assertEqual(result["status"], "insufficient_data")

    def test_breakout_rule(self):
        closes = [100 + i*0.1 for i in range(25)]
        closes[-1] = max(closes[-21:-1]) + 2
        result = india.analyze_daily("TEST", daily_bars(closes))
        self.assertIn("breakout_20d", result["setups"])

    def test_universe_deduplicates(self):
        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", newline="") as f:
            f.write("symbol,name\nRELIANCE,Reliance\nTCS,TCS\nRELIANCE,Reliance duplicate\n")
            path = f.name
        try:
            self.assertEqual(india.load_universe(path), ["RELIANCE", "TCS"])
        finally:
            os.unlink(path)

    def test_today_incomplete_bar_is_dropped(self):
        now = dt.datetime(2026,11,20,12,0,tzinfo=IST)
        rows = daily_bars(list(range(100,125)), day="2026-10-27")
        rows.append({"time":"2026-11-20T15:30:00+05:30","close":999,"high":1000,"low":998,"open":999,"volume":1})
        clean = india.normalize_daily_bars(rows, now)
        self.assertNotEqual(clean[-1]["close"], 999)

class PaperSizing(unittest.TestCase):
    def test_conservative_size(self):
        plan = paper.size_position(100000, 100, 98)
        self.assertEqual(plan["quantity"], 200)
        self.assertEqual(plan["estimated_max_loss"], 400)
        self.assertEqual(plan["mode"], "paper_only")

    def test_position_cap(self):
        plan = paper.size_position(100000, 100, 99, risk_pct=0.5, max_position_pct=2)
        self.assertEqual(plan["quantity"], 20)

    def test_invalid_stop(self):
        with self.assertRaises(ValueError):
            paper.size_position(100000, 100, 101)

    def test_risk_cap_rejects_aggressive_setting(self):
        with self.assertRaises(ValueError):
            paper.size_position(100000, 100, 95, risk_pct=1)


    def test_opening_range_breakout_requires_completed_close(self):
        day = dt.date(2026, 11, 23)
        bars = []
        for minute, high, low, close in [(15,101,99,100),(20,102,99,101),(25,103,100,102),
                                          (30,105,102,104)]:
            stamp = dt.datetime.combine(day, dt.time(9, minute), IST)
            bars.append({"time":stamp.isoformat(),"open":close-0.5,"high":high,
                         "low":low,"close":close,"volume":1000})
        result = india.analyze_opening_range(bars, now=dt.datetime(2026,11,23,9,40,tzinfo=IST))
        self.assertTrue(result["signal"])
        self.assertEqual(result["range_high"], 103)
        self.assertEqual(result["breakout_close"], 104)

    def test_paper_ledger_append(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "ledger.json")
            paper.append_paper_record(path, {"symbol":"TEST","quantity":1})
            rows = json.load(open(path, encoding="utf-8"))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["mode"], "paper_only")

if __name__ == "__main__":
    unittest.main()

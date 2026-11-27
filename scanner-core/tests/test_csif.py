import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "trader-india"))
from csif.engine import Bar, parse_bars, resample, confirmed_swings
from csif.paper import open_paper_position, close_paper_position


class CSIFCoreTests(unittest.TestCase):
    def test_parse_and_sort(self):
        rows = [
            {"timestamp": "2026-01-01T09:20:00+05:30", "open": 101, "high": 103, "low": 100, "close": 102, "volume": 10},
            {"timestamp": "2026-01-01T09:15:00+05:30", "open": 100, "high": 102, "low": 99, "close": 101, "volume": 9},
        ]
        bars = parse_bars(rows)
        self.assertEqual(len(bars), 2)
        self.assertLess(bars[0].timestamp, bars[1].timestamp)

    def test_invalid_ohlc_rejected(self):
        with self.assertRaises(ValueError):
            parse_bars([{"timestamp": "2026-01-01T09:15:00+05:30",
                         "open": 100, "high": 99, "low": 98, "close": 100}])

    def test_resample_session_aligned_15m(self):
        start = datetime(2026, 1, 1, 9, 15)
        bars = [Bar(start + timedelta(minutes=5*i), 100+i, 102+i, 99+i, 101+i, 10) for i in range(3)]
        result = resample(bars, 15)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].volume, 30)
        self.assertEqual(result[0].high, 104)

    def test_confirmed_swings_returns_confirmation_index(self):
        start = datetime(2026, 1, 1, 9, 15)
        bars = [Bar(start+timedelta(minutes=5*i), 10, h, 8, 9, 1)
                for i, h in enumerate([10, 11, 15, 12, 11, 10])]
        highs, _ = confirmed_swings(bars, 1, 1)
        self.assertIn((3, 15), highs)

    def test_paper_ledger_is_paper_only_and_closes(self):
        signal = {"symbol": "RELIANCE", "exchange": "NSE", "mode": "intraday",
                  "direction": "BULLISH", "entry_reference": 100, "stop": 98,
                  "target": 104, "score": 85,
                  "timestamp": "2026-01-01T09:30:00+05:30"}
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / "paper.json")
            position = open_paper_position(path, signal, 100000)
            self.assertEqual(position["status"], "OPEN_PAPER")
            closed = close_paper_position(path, position["id"], 104)
            self.assertEqual(closed["status"], "CLOSED_PAPER")
            self.assertGreater(closed["net_pnl"], 0)


if __name__ == "__main__":
    unittest.main()

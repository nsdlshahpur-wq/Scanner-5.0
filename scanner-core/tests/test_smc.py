import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "trader-india"))
from smc import confirmed_swings, detect_fvg, analyze_smc


def bar(o, h, l, c, t):
    return {"open": o, "high": h, "low": l, "close": c, "volume": 1000, "time": t}


class SMCTests(unittest.TestCase):
    def test_confirmed_swing_high_and_low(self):
        bars = [bar(10, 11, 9, 10, str(i)) for i in range(9)]
        bars[4] = bar(10, 15, 7, 11, "4")
        highs, lows = confirmed_swings(bars, window=2)
        self.assertEqual([x["index"] for x in highs], [4])
        self.assertEqual([x["index"] for x in lows], [4])

    def test_bullish_fvg(self):
        bars = [bar(10, 11, 9, 10, "0"), bar(10, 13, 10, 12, "1"),
                bar(12, 14, 12, 13, "2")]
        gaps = detect_fvg(bars)
        self.assertEqual(gaps[0]["type"], "bullish_fvg")
        self.assertEqual(gaps[0]["lower"], 11)
        self.assertEqual(gaps[0]["upper"], 12)

    def test_insufficient_data_is_safe(self):
        result = analyze_smc("TEST", [bar(10, 11, 9, 10, str(i)) for i in range(8)])
        self.assertEqual(result["status"], "insufficient_data")
        self.assertFalse(result.get("watch_only", False))


if __name__ == "__main__":
    unittest.main()

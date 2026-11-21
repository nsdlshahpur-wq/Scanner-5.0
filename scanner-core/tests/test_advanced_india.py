import datetime as dt
import importlib.util
import json
import os
import tempfile
import unittest

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,os.path.join(ROOT,path))
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

deriv=load("trader-india/derivatives.py","advanced_derivatives")
portfolio=load("trader-india/portfolio.py","advanced_portfolio")
backtest=load("trader-india/backtest.py","advanced_backtest")
intraday=load("trader-india/intraday.py","advanced_intraday")
dashboard=load("trader-india/dashboard.py","advanced_dashboard")

class AdvancedModules(unittest.TestCase):
    def test_oi_buildup_classifications(self):
        self.assertEqual(deriv.classify_buildup(2,100),"long_buildup")
        self.assertEqual(deriv.classify_buildup(-2,100),"short_buildup")
        self.assertEqual(deriv.classify_buildup(2,-100),"short_covering")
        self.assertEqual(deriv.classify_buildup(-2,-100),"long_unwinding")

    def test_futures_row_uses_prior_underlying_close(self):
        row={"SYMBOL":"ABC","INSTRUMENT":"FUTSTK","EXPIRY_DT":"2026-12-31",
             "OPEN_INT":"1100","CHG_IN_OI":"100","CONTRACTS":"500",
             "CLOSE":"120","UNDERLYING_VALUE":"121","PREV_CLOSE":"119"}
        result=deriv.analyze_rows([row])
        self.assertEqual(result["symbols"]["ABC"][0]["buildup"],"long_buildup")

    def test_invalid_fo_rows_reported(self):
        result=deriv.analyze_rows([{"symbol":"X"}])
        self.assertEqual(len(result["errors"]),1)

    def test_paper_portfolio_lifecycle_and_stop_alert(self):
        with tempfile.TemporaryDirectory() as folder:
            path=os.path.join(folder,"portfolio.json")
            portfolio.open_position(path,"ABC",10,100,95)
            marked=portfolio.mark_portfolio(path,{"ABC":94})
            self.assertEqual(marked["stop_alerts"],["ABC"])
            self.assertEqual(marked["unrealized_pnl"],-60)
            closed=portfolio.close_position(path,"ABC",94,1)
            self.assertEqual(closed["net_pnl"],-61)
            self.assertEqual(portfolio.mark_portfolio(path,{} )["realized_pnl"],-61)

    def test_duplicate_paper_position_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path=os.path.join(folder,"portfolio.json")
            portfolio.open_position(path,"ABC",1,100,95)
            with self.assertRaises(ValueError):portfolio.open_position(path,"ABC",1,100,95)

    def test_intraday_requires_volume_confirmation(self):
        day=dt.date(2026,11,23);bars=[]
        for minute,hi,lo,cl,vol in [(15,101,99,100,100),(20,102,99,101,100),(25,103,100,102,100),(30,105,102,104,200)]:
            stamp=dt.datetime.combine(day,dt.time(9,minute),intraday.IST)
            bars.append({"time":stamp.isoformat(),"open":cl-1,"high":hi,"low":lo,"close":cl,"volume":vol})
        r=intraday.analyze_intraday("RELIANCE",bars,dt.datetime(2026,11,23,9,40,tzinfo=intraday.IST),1.5)
        self.assertTrue(r["paper_watch"])

    def test_backtest_returns_metrics(self):
        bars=[]
        for i in range(80):
            close=100+i*0.2
            bars.append({"open":close-0.1,"high":close+0.5,"low":close-0.5,"close":close,"volume":1000})
        result=backtest.run_backtest(bars)
        self.assertIn("max_drawdown_pct",result)
        self.assertGreaterEqual(result["trade_count"],0)

    def test_dashboard_escapes_untrusted_data(self):
        with tempfile.TemporaryDirectory() as folder:
            src=os.path.join(folder,"in.json");out=os.path.join(folder,"out.html")
            with open(src,"w",encoding="utf-8") as f:json.dump({"results":[{"symbol":"<script>alert(1)</script>"}]},f)
            dashboard.build_dashboard([("Test",src)],out)
            with open(out,encoding="utf-8") as f:body=f.read()
            self.assertNotIn("<script>alert(1)</script>",body)

if __name__=="__main__":unittest.main()

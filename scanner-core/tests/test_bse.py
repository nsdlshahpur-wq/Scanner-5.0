import datetime as dt
import importlib.util
import json
import os
import tempfile
import unittest

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,os.path.join(ROOT,path))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

bse=load("trader-india/bse.py","bse_module")
bse_intraday=load("trader-india/bse_intraday.py","bse_intraday_module")
bse_universe=load("trader-india/bse_universe.py","bse_universe_module")
portfolio=load("trader-india/portfolio.py","exchange_portfolio")
IST=bse.IST

def bars():
    start=dt.date(2026,10,1);rows=[]
    for i in range(30):
        day=start+dt.timedelta(days=i);close=100+i*.5
        rows.append({"time":dt.datetime.combine(day,dt.time(15,30),IST).isoformat(),
          "open":close-.2,"high":close+.5,"low":close-.5,"close":close,"volume":10000})
    return rows

class BSESupport(unittest.TestCase):
    def test_bse_ticker_suffix_and_validation(self):
        self.assertEqual(bse.bse_ticker("500325"),"500325.BO")
        with self.assertRaises(ValueError):bse.bse_ticker("bad;symbol")

    def test_bse_daily_scanner_uses_bse_adapter(self):
        result=bse.scan_bse(["500325"],fetcher=lambda symbol:bars(),
          now=dt.datetime(2026,11,22,16,0,tzinfo=IST))
        self.assertEqual(result["market"],"BSE")
        self.assertEqual(result["results"][0]["ticker"],"500325.BO")
        self.assertEqual(result["results"][0]["exchange"],"BSE")

    def test_bse_intraday_exchange_label(self):
        day=dt.date(2026,11,23);rows=[]
        for minute,hi,lo,close,vol in [(15,101,99,100,100),(20,102,99,101,100),(25,103,100,102,100),(30,105,102,104,200)]:
            stamp=dt.datetime.combine(day,dt.time(9,minute),IST)
            rows.append({"time":stamp.isoformat(),"open":close-1,"high":hi,"low":lo,"close":close,"volume":vol})
        result=bse_intraday.analyze_bse_intraday("500325",rows,dt.datetime(2026,11,23,9,40,tzinfo=IST))
        self.assertEqual(result["exchange"],"BSE")
        self.assertTrue(result["paper_watch"])


    def test_bse_scrip_master_import(self):
        with tempfile.TemporaryDirectory() as folder:
            source=os.path.join(folder,"master.csv");dest=os.path.join(folder,"universe.csv")
            with open(source,"w",newline="",encoding="utf-8") as handle:
                handle.write("SCRIP_CD,Scrip_Name\\n500325,Reliance\\nBAD,Invalid\\n500325,Duplicate\\n")
            result=bse_universe.import_bse_master(source,dest)
            self.assertEqual(result["accepted"],1)
            self.assertEqual(result["rejected"],1)
            with open(dest,encoding="utf-8") as handle:self.assertIn("500325",handle.read())

    def test_portfolio_keeps_same_symbol_separate_by_exchange(self):
        with tempfile.TemporaryDirectory() as folder:
            path=os.path.join(folder,"portfolio.json")
            portfolio.open_position(path,"ABC",10,100,95,exchange="NSE")
            portfolio.open_position(path,"ABC",5,200,190,exchange="BSE")
            result=portfolio.mark_portfolio(path,{"NSE:ABC":101,"BSE:ABC":202})
            self.assertEqual(len(result["open_positions"]),2)
            self.assertEqual({row["exchange"] for row in result["open_positions"]},{"NSE","BSE"})
            portfolio.close_position(path,"ABC",210,exchange="BSE")
            result=portfolio.mark_portfolio(path,{"NSE:ABC":101})
            self.assertEqual(len(result["open_positions"]),1)
            self.assertEqual(result["open_positions"][0]["exchange"],"NSE")

if __name__=="__main__":unittest.main()

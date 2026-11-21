import importlib.util,os,tempfile,unittest,csv
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(path,name):
 s=importlib.util.spec_from_file_location(name,os.path.join(ROOT,path));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
sectors=load("trader-india/sectors.py","nse_sectors")
alerts=load("trader-india/alerts.py","nse_alerts")
universe=load("trader-india/universe.py","nse_universe")
class NSEOperations(unittest.TestCase):
 def test_sector_snapshot_groups_members(self):
  data={"RELIANCE":[{"close":100},{"close":110}],"TCS":[{"close":100},{"close":105}]}
  result=sectors.sector_snapshot(list(data),fetcher=lambda s:data[s])
  self.assertGreaterEqual(len(result["sectors"]),1)
  self.assertEqual(result["errors"],[])
 def test_alert_rules(self):
  result=alerts.build_alerts({"results":[{"symbol":"ABC","paper_watch":True,"conservative_watch":True,"setups":["breakout_20d"]}]})
  self.assertEqual(len(result["alerts"]),2)
  self.assertEqual(result["mode"],"paper_only")
 def test_universe_import_filters_and_deduplicates(self):
  with tempfile.TemporaryDirectory() as folder:
   src=os.path.join(folder,"source.csv");dst=os.path.join(folder,"universe.csv")
   with open(src,"w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=["SYMBOL","SERIES","NAME"]);w.writeheader()
    w.writerow({"SYMBOL":"RELIANCE","SERIES":"EQ","NAME":"Reliance"})
    w.writerow({"SYMBOL":"RELIANCE","SERIES":"EQ","NAME":"Duplicate"})
    w.writerow({"SYMBOL":"ABC","SERIES":"BE","NAME":"Other"})
   result=universe.import_universe(src,dst)
   self.assertEqual(result["accepted"],1);self.assertEqual(result["rejected"],1)
   with open(dst,encoding="utf-8") as f:self.assertIn("RELIANCE",f.read())
if __name__=="__main__":unittest.main()

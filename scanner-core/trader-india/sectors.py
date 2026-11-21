#!/usr/bin/env python3
"""Sector relative-strength snapshot from daily OHLCV data."""
import argparse,csv,json,os,sys
sys.path.insert(0,os.path.dirname(__file__))
from india import fetch_chart,IST
from intraday import SECTORS

def sector_snapshot(symbols,fetcher=fetch_chart):
    groups={};errors=[]
    for symbol in dict.fromkeys(s.strip().upper() for s in symbols if s.strip()):
        try:
            bars=fetcher(symbol)
            if len(bars)<2:raise ValueError("Need at least two daily bars")
            prev=float(bars[-2]["close"]);last=float(bars[-1]["close"])
            if prev<=0:raise ValueError("Invalid previous close")
            change=(last/prev-1)*100;sector=SECTORS.get(symbol,"Other")
            groups.setdefault(sector,[]).append({"symbol":symbol,"change_pct":round(change,2)})
        except Exception as e:errors.append({"symbol":symbol,"error":str(e)})
    rows=[]
    for name,members in groups.items():
        rows.append({"sector":name,"members":len(members),
          "average_change_pct":round(sum(x["change_pct"] for x in members)/len(members),2),
          "constituents":sorted(members,key=lambda x:x["change_pct"],reverse=True)})
    rows.sort(key=lambda x:x["average_change_pct"],reverse=True)
    return {"market":"NSE","as_of":IST.tzname(None),"sectors":rows,"errors":errors,
      "note":"Starter sector map covers selected liquid names only; this is not official index breadth or a complete sector index return."}

def main(argv=None):
    p=argparse.ArgumentParser(description="NSE/BSE sector relative strength")
    g=p.add_mutually_exclusive_group(required=True);g.add_argument("--symbols");g.add_argument("--universe")
    p.add_argument("--output");p.add_argument("--exchange",choices=("NSE","BSE"),default="NSE");a=p.parse_args(argv)
    if a.symbols:symbols=a.symbols.split(",")
    else:
        with open(a.universe,encoding="utf-8-sig",newline="") as f:symbols=[r["symbol"] for r in csv.DictReader(f) if r.get("symbol")]
    if a.exchange=="BSE":
        import bse
        result=sector_snapshot(symbols,fetcher=bse.fetch_bse_chart)
        result["market"]="BSE"
    else:
        result=sector_snapshot(symbols)
    data=json.dumps(result,indent=2)
    if a.output:
        os.makedirs(os.path.dirname(os.path.abspath(a.output)),exist_ok=True)
        with open(a.output,"w",encoding="utf-8") as f:f.write(data+"\n")
    print(data);return 0
if __name__=="__main__":raise SystemExit(main())

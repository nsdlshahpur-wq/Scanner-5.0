#!/usr/bin/env python3
"""Event-based paper portfolio: open/close positions, marks, stops and P&L."""
import argparse,datetime as dt,json,math,os

def _load(path):
    if not os.path.exists(path): return {"cash":0.0,"events":[]}
    with open(path,encoding="utf-8") as f: data=json.load(f)
    if not isinstance(data,dict) or not isinstance(data.get("events"),list): raise ValueError("Invalid paper portfolio")
    return data

def _save(path,data):
    os.makedirs(os.path.dirname(os.path.abspath(path)),exist_ok=True);tmp=path+".tmp"
    with open(tmp,"w",encoding="utf-8") as f:json.dump(data,f,indent=2);f.write("\n")
    os.replace(tmp,path)

def positions(data):
    live={}
    for e in data["events"]:
        sym=e["symbol"]
        if e["event"]=="OPEN":live[sym]=dict(e)
        elif e["event"]=="CLOSE":live.pop(sym,None)
    return live

def open_position(path,symbol,qty,entry,stop,fee=0):
    symbol=symbol.strip().upper()
    if not symbol or qty<=0 or entry<=0 or stop<=0 or stop>=entry or fee<0:raise ValueError("Invalid long paper position")
    d=_load(path);live=positions(d)
    if symbol in live:raise ValueError("Position already open for "+symbol)
    if qty*entry+fee>d["cash"] and d["cash"]>0:raise ValueError("Insufficient paper cash")
    e={"event":"OPEN","symbol":symbol,"qty":int(qty),"entry":float(entry),"stop":float(stop),"fee":float(fee),"time":dt.datetime.now(dt.timezone.utc).isoformat()}
    d["events"].append(e);_save(path,d);return e

def close_position(path,symbol,exit_price,fee=0):
    symbol=symbol.strip().upper();d=_load(path);live=positions(d)
    if symbol not in live:raise ValueError("No open position for "+symbol)
    if exit_price<=0 or fee<0:raise ValueError("Invalid exit price/fee")
    pos=live[symbol];gross=(exit_price-pos["entry"])*pos["qty"];net=gross-pos.get("fee",0)-fee
    e={"event":"CLOSE","symbol":symbol,"qty":pos["qty"],"entry":pos["entry"],"exit":float(exit_price),
       "gross_pnl":round(gross,2),"net_pnl":round(net,2),"fee":float(fee),"time":dt.datetime.now(dt.timezone.utc).isoformat()}
    d["events"].append(e);_save(path,d);return e

def mark_portfolio(path,prices):
    d=_load(path);live=positions(d);rows=[];unreal=0
    for sym,p in live.items():
        if sym not in prices:continue
        mark=float(prices[sym]);pnl=(mark-p["entry"])*p["qty"]-p.get("fee",0);unreal+=pnl
        rows.append({"symbol":sym,"qty":p["qty"],"entry":p["entry"],"mark":mark,"stop":p["stop"],
          "unrealized_pnl":round(pnl,2),"stop_breached":mark<=p["stop"]})
    closed=[e for e in d["events"] if e["event"]=="CLOSE"]
    realized=sum(e["net_pnl"] for e in closed)
    return {"mode":"paper_only","open_positions":rows,"realized_pnl":round(realized,2),
      "unrealized_pnl":round(unreal,2),"total_pnl":round(realized+unreal,2),
      "stop_alerts":[r["symbol"] for r in rows if r["stop_breached"]],"note":"Marks are user-supplied; this function does not execute stop orders."}

def main(argv=None):
    p=argparse.ArgumentParser(description="Paper portfolio ledger")
    p.add_argument("--ledger",default="trader/paper-portfolio.json")
    sub=p.add_subparsers(dest="cmd",required=True)
    o=sub.add_parser("open");o.add_argument("--symbol",required=True);o.add_argument("--qty",type=int,required=True);o.add_argument("--entry",type=float,required=True);o.add_argument("--stop",type=float,required=True);o.add_argument("--fee",type=float,default=0)
    c=sub.add_parser("close");c.add_argument("--symbol",required=True);c.add_argument("--price",type=float,required=True);c.add_argument("--fee",type=float,default=0)
    m=sub.add_parser("mark");m.add_argument("--prices",required=True,help="JSON file mapping symbols to latest prices")
    a=p.parse_args(argv)
    if a.cmd=="open":r=open_position(a.ledger,a.symbol,a.qty,a.entry,a.stop,a.fee)
    elif a.cmd=="close":r=close_position(a.ledger,a.symbol,a.price,a.fee)
    else:
        with open(a.prices,encoding="utf-8") as f:prices=json.load(f)
        r=mark_portfolio(a.ledger,prices)
    print(json.dumps(r,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())

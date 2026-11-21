#!/usr/bin/env python3
"""Offline F&O bhavcopy/derivatives CSV normalizer and OI buildup classifier.

Accepts a user-downloaded exchange bhavcopy after mapping headers to the documented
normalized schema. No credentials, broker API or order endpoint is used.
"""
import argparse,csv,json,os

REQUIRED=("symbol","instrument","expiry","open_interest","change_in_oi","volume","close","underlying_close")\nOPTIONAL=("previous_underlying_close",)
ALIASES={"symbol":["symbol","underlying","ticker"],"instrument":["instrument","instrument_type"],
 "expiry":["expiry","expiry_dt","expiry_date"],"open_interest":["open_interest","oi","openint"],
 "change_in_oi":["change_in_oi","chg_in_oi","change_oi"],"volume":["volume","contracts"],
 "close":["close","settle_pr","close_price"],"underlying_close":["underlying_close","underlying_price","underlying_value"]}

def normalize_row(row):
    low={str(k).strip().lower():v for k,v in row.items()}
    out={}
    for key in REQUIRED:
        value=next((low[a] for a in ALIASES[key] if a in low and low[a] not in (None,"")),None)
        if value is None: raise ValueError("Missing required field: "+key)
        out[key]=value
    for key in ("open_interest","change_in_oi","volume","close","underlying_close"):
        out[key]=float(str(out[key]).replace(",",""))
    previous=next((low[a] for a in ("previous_underlying_close","prev_underlying_close","prev_close") if a in low and low[a] not in (None,"")),None)\n    out["previous_underlying_close"]=float(str(previous).replace(",","")) if previous is not None else None\n    out["symbol"]=str(out["symbol"]).strip().upper()
    out["instrument"]=str(out["instrument"]).strip().upper()
    return out

def classify_buildup(price_change,oi_change):
    if price_change>0 and oi_change>0:return "long_buildup"
    if price_change<0 and oi_change>0:return "short_buildup"
    if price_change>0 and oi_change<0:return "short_covering"
    if price_change<0 and oi_change<0:return "long_unwinding"
    return "neutral_or_flat"

def analyze_rows(rows):
    parsed=[]; errors=[]
    for n,row in enumerate(rows,2):
        try: parsed.append(normalize_row(row))
        except (ValueError,TypeError) as e: errors.append({"row":n,"error":str(e)})
    by_symbol={}
    for r in parsed:
        if r["instrument"] not in ("FUTSTK","FUTIDX","FUTURE","FUT"):
            continue
        prev=r.get("previous_underlying_close")
        price_change=((r["underlying_close"]/float(prev))-1)*100 if prev else None
        r["price_change_pct"]=round(price_change,2) if price_change is not None else None
        r["oi_change_pct"]=round((r["change_in_oi"]/(r["open_interest"]-r["change_in_oi"]))*100,2) if r["open_interest"]!=r["change_in_oi"] else None
        r["buildup"]=classify_buildup(price_change,r["change_in_oi"]) if price_change is not None else "oi_only_no_price_baseline"
        by_symbol.setdefault(r["symbol"],[]).append(r)
    return {"records_parsed":len(parsed),"futures_symbols":len(by_symbol),"symbols":by_symbol,"errors":errors,
      "note":"Price/OI buildup requires a previous underlying close. Option-chain PCR, max pain and expiry effects are not inferred from incomplete files."}

def main(argv=None):
    p=argparse.ArgumentParser(description="Analyze normalized NSE F&O bhavcopy CSV")
    p.add_argument("--csv",required=True);p.add_argument("--output")
    a=p.parse_args(argv)
    with open(a.csv,encoding="utf-8-sig",newline="") as f: result=analyze_rows(list(csv.DictReader(f)))
    data=json.dumps(result,indent=2)
    if a.output:
        os.makedirs(os.path.dirname(os.path.abspath(a.output)),exist_ok=True)
        with open(a.output,"w",encoding="utf-8") as f:f.write(data+"\n")
    print(data)
    return 0
if __name__=="__main__":raise SystemExit(main())

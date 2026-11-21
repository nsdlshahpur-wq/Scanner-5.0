#!/usr/bin/env python3
"""Build a portable offline HTML dashboard from scanner JSON outputs."""
import argparse,html,json,os,datetime

def build_dashboard(inputs,output):
    sections=[]
    for label,path in inputs:
        with open(path,encoding="utf-8") as f:data=json.load(f)
        rows=data.get("results",data.get("signals",[]))
        if isinstance(rows,dict):rows=list(rows.values())
        if not isinstance(rows,list):rows=[]
        cols=sorted({k for r in rows if isinstance(r,dict) for k,v in r.items() if isinstance(v,(str,int,float,bool))})
        body="".join("<tr>"+"".join("<td>"+html.escape(str(r.get(c,"")))+"</td>" for c in cols)+"</tr>" for r in rows if isinstance(r,dict))
        sections.append("<section><h2>"+html.escape(label)+"</h2><p>Records: "+str(len(rows))+"</p><div class='scroll'><table><thead><tr>"+"".join("<th>"+html.escape(c)+"</th>" for c in cols)+"</tr></thead><tbody>"+body+"</tbody></table></div></section>")
    doc="""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Scanner 5.0 NSE Dashboard</title><style>
body{font:15px system-ui;margin:24px;background:#f5f7fa;color:#172033}header,section{background:white;padding:18px;margin:14px 0;border-radius:12px;box-shadow:0 1px 5px #ccd}
h1{margin:0}h2{margin-top:0}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:13px}th,td{padding:8px;border-bottom:1px solid #e3e7ee;text-align:left;white-space:nowrap}th{background:#eef2f7}small{color:#526078}
</style></head><body><header><h1>Scanner 5.0 · NSE</h1><p>Offline research dashboard · Generated """+html.escape(datetime.datetime.now().astimezone().isoformat())+"""</p><small>Paper mode only. Verify source data; this dashboard does not execute orders.</small></header>"""+ "".join(sections)+"</body></html>"
    os.makedirs(os.path.dirname(os.path.abspath(output)),exist_ok=True)
    with open(output,"w",encoding="utf-8") as f:f.write(doc)
    return output

def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument("--input",action="append",required=True,help="Label=path.json (repeatable)");p.add_argument("--output",default="trader/india-dashboard.html")
    a=p.parse_args(argv);pairs=[]
    for item in a.input:
        if "=" not in item: p.error("--input must be Label=path.json")
        pairs.append(item.split("=",1))
    print(build_dashboard(pairs,a.output));return 0
if __name__=="__main__":raise SystemExit(main())

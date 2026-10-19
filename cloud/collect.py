"""Only collect from explicitly permitted public sources, or operator-reviewed CSV."""
from __future__ import annotations
import csv,json,sys,html,re,time
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin,urlsplit
from urllib.request import Request,urlopen
from urllib.robotparser import RobotFileParser
from xml.etree import ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core import URL,CODES,parse,normalize,now
ROOT=Path(__file__).resolve().parents[1]
class Parser(HTMLParser):
 def __init__(self):
  super().__init__();self.links=[];self._href=None;self._text=[]
 def handle_starttag(self,t,attrs):
  if t=="a":self._href=dict(attrs).get("href");self._text=[]
 def handle_data(self,s):
  if self._href is not None:self._text.append(s)
 def handle_endtag(self,t):
  if t=="a" and self._href is not None:self.links.append((self._href," ".join(self._text)));self._href=None
def fetch(url):
 if urlsplit(url).scheme!="https":raise ValueError("HTTPS only")
 host=urlsplit(url).hostname or ""
 if host in ("localhost","127.0.0.1") or host.endswith((".local",".internal")):raise ValueError("internal host blocked")
 robots=f"https://{host}/robots.txt"
 rp=RobotFileParser();rp.set_url(robots)
 try:rp.read()
 except Exception as e:raise PermissionError("cannot verify robots.txt") from e
 if not rp.can_fetch("FABResourceFinder/1.0",url):raise PermissionError("robots disallow")
 delay=rp.crawl_delay("FABResourceFinder/1.0") or 1.5
 if delay>30:raise PermissionError("crawl delay too long")
 time.sleep(max(1.5,delay))
 with urlopen(Request(url,headers={"User-Agent":"FABResourceFinder/1.0"}),timeout=12) as r:
  if not any(t in r.headers.get("Content-Type","") for t in ("html","xml","text")):raise ValueError("unsupported type")
  buf=r.read(1000001)
 if len(buf)>1000000:raise ValueError("oversize")
 return buf.decode("utf-8-sig","replace")
def extract(data,origin,title):
 p=Parser();p.feed(data);out=[]
 for link,label in p.links:
  info=parse(link)
  if info:
   m=CODES.search(label)
   out.append({**info,"title":label.strip() or title,"origin":origin,"extraction_code":m.group(1) if m else "","source_url":origin})
 for match in URL.finditer(html.unescape(data)):
  info=parse(match.group())
  if info:
   tail=html.unescape(data)[match.end():match.end()+80].split("<",1)[0]
   m=CODES.search(tail)
   out.append({**info,"title":title,"extraction_code":m.group(1) if m else "","source_url":origin,"origin":origin})
 return out
def main():
 index_path=ROOT/"docs/index.json";source_path=ROOT/"config/sources.json";csv_path=ROOT/"config/manual_links.csv"
 try:old=json.loads(index_path.read_text(encoding="utf-8")).get("records",[])
 except (OSError,ValueError):old=[]
 records={x["id"]:x for r in old if (x:=normalize(r))}
 if csv_path.exists():
  for row in csv.DictReader(csv_path.open(encoding="utf-8-sig",newline="")):
   if row.get("permission_confirmed","").lower() in ("yes","true","1"):
    if item:=normalize({**row,"origin":"人工授权清单"}):records[item["id"]]=item
 sources=json.loads(source_path.read_text(encoding="utf-8"))
 for s in sources:
  if not(s.get("enabled") and s.get("permission_confirmed")):continue
  url=s.get("url","")
  try:
   if s.get("type") not in ("page","rss"):raise ValueError("only page and rss sources supported")
   data=fetch(url)
   if s["type"]=="rss":
    root=ET.fromstring(data)
    entries=[]
    for el in root.iter():
     if el.tag.split("}")[-1] not in ("item","entry"):continue
     title=next((x.text or "" for x in el if x.tag.split("}")[-1]=="title"),"RSS公开分享")
     payload=" ".join("".join(x.itertext()) for x in el)
     entries.extend(extract(payload,url,title))
   else:entries=extract(data,url,s.get("name") or url)
   for r in entries:
    if item:=normalize(r):records[item["id"]]=item
  except Exception as e:print("Source skipped",url,str(e),file=sys.stderr)
 output={"schema_version":1,"generated_at":now(),"collector":"FAB Resource Finder V1.0","count":len(records),"records":list(records.values())}
 index_path.parent.mkdir(parents=True,exist_ok=True)
 index_path.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("Indexed",len(records),"records")
if __name__=="__main__":main()

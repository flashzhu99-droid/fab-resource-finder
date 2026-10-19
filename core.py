"""FAB Resource Finder: metadata-only normalizer (public shares)."""
from __future__ import annotations
import re, hashlib, html
from datetime import datetime,timezone
from urllib.parse import urlsplit,urlunsplit,parse_qs
PROVIDERS={"百度网盘":("pan.baidu.com",),"夸克网盘":("pan.quark.cn",),"阿里云盘":("www.alipan.com","www.aliyundrive.com"),"115网盘":("115.com",),"迅雷云盘":("pan.xunlei.com",),"腾讯微云":("share.weiyun.com",)}
URL=re.compile(r'https?://[^\s<>"\']+',re.I)
CODES=re.compile(r'(?:提取码|访问码|密码|口令)\s*[：:= ]\s*([a-zA-Z0-9]{4,8})')
CATEGORIES={"GDS特气":["特气","气瓶柜","gas cabinet","vmb","gds","气体输送"],"UPW超纯水":["超纯水","upw","edi","反渗透","ro膜"],"PCW工艺冷却水":["pcw","工艺冷却水"],"CDA压缩空气":["cda","压缩空气","空压机"],"洁净空调":["洁净室","ffu","mau","洁净厂房"],"EHS环保安全":["废水","废气","scrubber","消防","ehs"],"电气与自控":["ups","变压器","配电","plc","fmcs"],"半导体厂务综合":["厂务","晶圆厂","fab","半导体"]}
def now():return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def parse(url):
    try:
        u=urlsplit(html.unescape(url).strip().rstrip('.,;，。；）)'))
        host=(u.hostname or '').lower().rstrip('.')
        if u.scheme not in ("https","http") or u.username or u.password:return None
        provider=next((k for k,v in PROVIDERS.items() if any(host==d or host.endswith("."+d) for d in v)),None)
        if not provider:return None
        if not u.path or u.path=="/":return None
        normalized=urlunsplit(("https",host,u.path.rstrip("/"),u.query,""))
        return {"id":hashlib.sha256(normalized.encode()).hexdigest()[:24],"share_url":normalized,"provider":provider}
    except ValueError:return None
def normalize(record):
    if not isinstance(record,dict):return None
    base=parse(record.get("share_url",""))
    if not base:return None
    title=str(record.get("title","公开分享资源"))[:200]
    blob=(title+" "+str(record.get("description",""))).lower()
    category=next((k for k,v in CATEGORIES.items() if any(w in blob for w in v)),"未分类")
    if not any(w in blob for w in sum(CATEGORIES.values(),[])):return None
    doc=next((name for name,terms in {"工程图纸":["p&id","图纸","施工图"],"设备手册":["手册","manual"],"培训教材":["培训","课件","ppt"],"运维SOP":["sop","维护","运维"]}.items() if any(w in blob for w in terms)),"其他资料")
    return {**base,"title":title,"description":str(record.get("description",""))[:400],"source_url":str(record.get("source_url",""))[:500],"extraction_code":str(record.get("extraction_code",""))[:12],"category":category,"doc_type":doc,"origin":str(record.get("origin","授权来源"))[:100],"first_seen":str(record.get("first_seen") or now()),"last_seen":now(),"status":"待验证"}

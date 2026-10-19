"""PanSou operator-owned search connector. Indexes PUBLIC share-link metadata only."""
import argparse,json,re,sys,time
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request,urlopen
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
try:
 from core import normalize_record as normalize
except ImportError:
 from core import normalize
ROOT=Path(__file__).resolve().parents[1]
TECH=('半导体厂务','晶圆厂','洁净厂房','洁净室','特气','特种气体','超纯水','纯水系统',
      '工艺冷却水','无油空压机','压缩空气','气瓶柜','气体输送','尾气处理','废气处理',
      '半导体废水','厂务系统','调压阀','气体侦测','氯气','氮气纯化','洁净空调',
      '厂务工程','供配电','设备二次配','厂务设计','冷冻站','反渗透','洗涤塔')
ENGLISH=('upw','pcw','cda','gds','vmb','vmp','hvac','fmcs','scrubber','chiller','ionpure','mau','ffu','edi','acs510','gas cabinet','ultrapure water')
PLATFORMS=('baidu','aliyun','quark','tianyi','uc','mobile','115','xunlei','123')
def matches(title):
 s=str(title or '').lower().strip()
 if not s or any(t in s for t in ('fab four','fabfour','半导体股票','影视资源')):return False
 return any(x in s for x in TECH) or any(re.search(r'(?<![a-z0-9])'+re.escape(x)+r'(?![a-z0-9])',s) for x in ENGLISH)
def api_json(url,payload=None):
 headers={'Content-Type':'application/json','User-Agent':'FABResourceFinder/1.2'}
 request=Request(url,data=json.dumps(payload,ensure_ascii=False).encode() if payload else None,headers=headers,method='POST' if payload else 'GET')
 with urlopen(request,timeout=55) as f:
  b=f.read(5000001)
  if len(b)>5000000:raise ValueError('response too large')
  return json.loads(b)
def unpack_response(payload):
 """PanSou res=merge may return raw provider groups, or nested merged_by_type."""
 if not isinstance(payload,dict):raise ValueError('PanSou response is not a JSON object')
 if 'error' in payload or ('code' in payload and payload['code'] not in (None,0,200)):
  raise RuntimeError('PanSou upstream error: '+str(payload.get('message') or payload.get('error'))[:150])
 obj=payload.get('data',payload)
 if not isinstance(obj,dict):raise ValueError('PanSou response data is not an object')
 if isinstance(obj.get('merged_by_type'),dict):return {'merged_by_type':obj['merged_by_type']}
 if isinstance(obj.get('data'),dict) and isinstance(obj['data'].get('merged_by_type'),dict):
  return {'merged_by_type':obj['data']['merged_by_type']}
 providers=set(PLATFORMS)|{'others','guangya','pikpak'}
 if obj and any(k in providers for k in obj):
  return {'merged_by_type':{k:v for k,v in obj.items() if k in providers and isinstance(v,list)}}
 if obj=={}:return {'merged_by_type':{}}
 raise ValueError('Unexpected PanSou schema; top-level keys='+','.join(list(obj)[:12]))
def count_upstream_links(payload):
 return sum(len(v) for v in unpack_response(payload)['merged_by_type'].values() if isinstance(v,list))
def convert(data,keyword):
 result=[]
 for kind,links in unpack_response(data)['merged_by_type'].items():
  if kind not in PLATFORMS or not isinstance(links,list):continue
  for x in links:
   if not isinstance(x,dict):continue
   title=str(x.get('work_title') or x.get('note') or x.get('title') or '')
   if not matches(title):continue
   source=str(x.get('source') or 'PanSou公开频道')
   raw={'title':title,'share_url':x.get('url',''),'extraction_code':x.get('password',''),
        'description':f'公开来源：{source}；搜索词：{keyword}。结果未经有效性或版权复核。',
        'origin':'PanSou公开资源候选'}
   normalized=normalize(raw)
   if normalized:
    normalized['status']='待验证'
    normalized['search_keyword']=keyword
    normalized['search_source']=source[:100]
    result.append(normalized)
 return result
def main():
 p=argparse.ArgumentParser()
 p.add_argument('--query',default='')
 p.add_argument('--index',default=str(ROOT/'docs/index.json'))
 p.add_argument('--keywords',default=str(ROOT/'config/fab_search_keywords.json'))
 p.add_argument('--source',choices=('tg','plugin','all'),default='tg')
 p.add_argument('--limit',type=int,default=20)
 a=p.parse_args()
 base='http://127.0.0.1:8888'
 health=api_json(base+'/api/health')
 if health.get('status')!='ok':raise RuntimeError('PanSou backend unhealthy')
 cfg=json.loads(Path(a.keywords).read_text(encoding='utf-8'))
 queries=[a.query] if a.query else cfg.get('queries',[])
 queries=[q.strip()[:70] for q in queries[:max(1,min(a.limit,30))] if q.strip()]
 original=json.loads(Path(a.index).read_text(encoding='utf-8')) if Path(a.index).exists() else {'records':[]}
 index={}
 for r in original.get('records',[]):
  normalized=normalize(r)
  if normalized:index[normalized['id']]={**normalized,**r}
 added=0;errors=[];answered=0;upstream_links=0;matching_links=0
 for q in queries:
  try:
   data=api_json(base+'/api/search',{'kw':q,'res':'merge','src':a.source,'cloud_types':list(PLATFORMS)})
   raw_count=count_upstream_links(data)
   candidates=convert(data,q);answered+=1
   upstream_links+=raw_count;matching_links+=len(candidates)
   for candidate in candidates:
    if candidate['id'] not in index:
     index[candidate['id']]=candidate;added+=1
   print(f'{q}: upstream={raw_count}, qualified={len(candidates)}, new={added}',flush=True)
  except Exception as e:
   errors.append(f'{q}: {type(e).__name__}: {e}')
   print('ERROR',errors[-1],file=sys.stderr,flush=True)
  time.sleep(1)
 if not answered:raise RuntimeError('All searches failed: '+str(errors[:2]))
 from datetime import datetime,timezone
 now=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
 doc={**original,'schema_version':1,'generated_at':now,
      'collector':'FAB Resource Finder V1.2 / PanSou bridge',
      'count':len(index),'records':list(index.values()),
      'discovery':{'searched':len(queries),'answered':answered,'upstream_links':upstream_links,
                   'qualified_candidates':matching_links,'new_candidates':added,
                   'errors':errors[:10],'link_status':'unverified','source':a.source}}
 Path(a.index).write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('New candidates:',added,'total:',len(index))
if __name__=='__main__':main()

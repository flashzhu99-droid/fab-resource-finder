"""Read-only diagnostic. Prints aggregated search counts, never links or titles."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cloud.pansou_bridge import api_json,unpack_response,count_upstream_links

PROBES=[
 ("三体","all"),
 ("三体","plugin"),
 ("三体","tg"),
 ("Python","all"),
 ("半导体","all"),
 ("超纯水","all"),
]

def main():
 print("DIAGNOSTIC: read-only counts, not storing found links.",flush=True)
 for keyword,source in PROBES:
  try:
   raw=api_json('http://127.0.0.1:8888/api/search',
      {'kw':keyword,'src':source,'res':'all','cloud_types':['baidu','quark','aliyun','115','xunlei']})
   data=unpack_response(raw)
   total=data.get('total','unknown')
   links=count_upstream_links(raw)
   # Result groups may be omitted in an empty response.
   groups={k:len(v) for k,v in data['merged_by_type'].items() if isinstance(v,list) and v}
   print(f"PROBE keyword={keyword!r} source={source} upstream_total={total} grouped_links={links} group_counts={groups}",flush=True)
  except Exception as e:
   print(f"PROBE ERROR keyword={keyword!r} source={source} error={type(e).__name__}: {str(e)[:160]}",flush=True)
 print("DIAGNOSTIC COMPLETE",flush=True)
if __name__=="__main__":main()

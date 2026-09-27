"""Crossref title/year/citation navigation; no primary reaction verification."""
import argparse,sys,json,re,time,hashlib,concurrent.futures
from pathlib import Path
from difflib import SequenceMatcher
import requests
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.operate import write,event

def norm(s):return re.sub(r'[^a-z0-9]','',s.lower().replace('\\n',' '))
def resolve(pair):
 title,citation=pair;url='https://api.crossref.org/works'
 if not title:return {'title':title,'citation':citation,'status':'manual_needed','reason':'missing title'}
 try:
  r=requests.get(url,params={'query.title':title.replace('\\n',' '),'rows':3},headers={'User-Agent':'FlavoRetro-source-navigation/1.0'},timeout=30);r.raise_for_status();items=r.json()['message']['items']
  candidates=[];year=re.search(r'\((19|20)\d{2}\)',citation);expected=int(year.group()[1:-1]) if year else None
  for it in items:
   t=' '.join(it.get('title',[]));sim=SequenceMatcher(None,norm(title),norm(t)).ratio();years=set()
   for field in ['published','published-print','published-online','issued']:
    points=it.get(field,{}).get('date-parts',[])
    if points and points[0]:years.add(points[0][0])
   candidates.append({'doi':it.get('DOI'),'title':t,'title_similarity':sim,'years':sorted(years),'journal':it.get('container-title',[]),'volume':it.get('volume'),'page':it.get('page'),'authors':[x.get('family','') for x in it.get('author',[])],'year_matches':expected in years if expected else None,'links':it.get('link',[])})
  candidates.sort(key=lambda x:-x['title_similarity']);best=candidates[0] if candidates else None
  # Keep ambiguous/changed-year references unresolved. A DOI match only identifies a paper.
  matched=best and best['title_similarity']>=0.96 and best['year_matches'] is True
  return {'title':title,'citation':citation,'status':'metadata_matched' if matched else 'manual_needed','primary_reaction_verified':False,'doi':best['doi'] if matched else None,'candidates':candidates,'lookup':'Crossref public API','accessed_date':'2026-09-27'}
 except Exception as e:return {'title':title,'citation':citation,'status':'lookup_failed','reason':str(e),'primary_reaction_verified':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',default='outputs/review/task015/references.json');a=p.parse_args()
 if Path(a.output).exists():raise ValueError('preserve existing references; choose --output')
 rows=[json.loads(x) for x in Path('outputs/triage/task014-final/review.jsonl').read_text().splitlines()];pairs={}
 for row in rows:
  f=row['input_record']['raw']['fields'];title=f.get('RXN:VAR(1):REFERENCE(1):TITLE','');citation=f.get('RXN:VAR(1):REFERENCE(1):CITATION','');pairs[title]=citation
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(resolve,pairs.items()))
 output={x['title']:x for x in results}
 write('TASK-015',a.output,json.dumps(output,ensure_ascii=False,indent=2)+'\n')
 from collections import Counter
 print(json.dumps(dict(Counter(x['status'] for x in results))))
if __name__=='__main__':main()

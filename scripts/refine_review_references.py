"""One paced retry of failed journal lookups; patent locators remain unverified."""
import argparse,json,re,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.review_references import resolve
from scripts.operate import write
p=argparse.ArgumentParser();p.add_argument('--input',default='outputs/review/task015/references.json');p.add_argument('--output',default='outputs/review/task015/references-v2.json');a=p.parse_args()
if Path(a.output).exists():raise ValueError('preserve existing reference refinement; choose --output')
path=Path(a.input);refs=json.loads(path.read_text())
for title,item in refs.items():
 m=re.search(r'\b(CN|US|WO|EP|JP|KR)\s*(\d{6,})\s*([A-Z]\d?)\b',item['citation'])
 if m:
  item['patent_number']=''.join(m.groups());item['patent_number_status']='as_reported_in_source_not_verified';item['status']='patent_locator_as_reported';item['doi']=None
 elif item['status']=='lookup_failed':
  retry=resolve((title,item['citation']));retry['prior_attempt']=item;retry['attempts']=2;refs[title]=retry;time.sleep(2)
for item in refs.values():
 item['metadata_comparison_scope']='title and publication year only; author/journal/volume/pages not independently compared'
write('TASK-015',a.output,json.dumps(refs,ensure_ascii=False,indent=2)+'\n')
from collections import Counter
print(dict(Counter(x['status'] for x in refs.values())))

import sys,argparse,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from flavoretro.review_cards import build
p=argparse.ArgumentParser();p.add_argument('--review',default='outputs/triage/task014-final/review.jsonl');p.add_argument('--references',default='outputs/review/task015/references.json');p.add_argument('--output',default='outputs/review/task015');a=p.parse_args()
print(json.dumps(build(a.review,a.references,a.output),ensure_ascii=False,indent=2))

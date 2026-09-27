"""Reconstruct only pinned generated protobuf modules; never modify foundation deps."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import requests
from scripts.operate import write,digest
m=json.loads(Path('environment/task015-ord-schema.json').read_text())
for name,item in m['schema_files'].items():
 path='outputs/validation/task015-dependencies/ord_schema/proto/'+name
 if Path(path).exists():
  if digest(path)!=item['sha256']:raise ValueError('preserve unexpected local schema; stop')
  continue
 r=requests.get(item['frozen_url'],timeout=30);r.raise_for_status()
 if hashlib.sha256(r.content).hexdigest()!=item['sha256']:raise ValueError('schema content mismatch')
 write('TASK-015',path,r.text)
for path in ['outputs/validation/task015-dependencies/ord_schema/__init__.py','outputs/validation/task015-dependencies/ord_schema/proto/__init__.py']:
 if not Path(path).exists():write('TASK-015',path,'')
print('Frozen generated schema modules available; foundation packages unchanged')

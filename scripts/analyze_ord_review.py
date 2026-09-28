"""Recompute ORD source, identity and topology diagnostics from frozen TASK-015 outputs."""
import json
from collections import Counter, defaultdict
from pathlib import Path
from scripts.operate import write, digest
TASK='TASK-015-P1'
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--output',default='outputs/coverage/task015-p1');args=parser.parse_args()
OUT=args.output
if Path(OUT).exists():raise ValueError('Preserve prior analysis; choose a new --output directory')
def readjl(p): return [json.loads(x) for x in Path(p).read_text().splitlines()]
def save(name,data): write(TASK,OUT+'/'+name,json.dumps(data,ensure_ascii=False,indent=2)+'\n')
ds=json.loads(Path('outputs/coverage/task015-summary/datasets.json').read_text())
rows=[]
for d in ds:
 for r in readjl(Path(d['folder'])/'candidates.jsonl'):
  r['dataset_name']=d['name'];r['dataset_id']=d['dataset_id'];rows.append(r)
gly=[r for r in rows if r['features']['domain_glycoside_candidate']]
local=readjl('outputs/triage/task014-final/pilot.jsonl')
def exact(r): return r['features'].get('exact_group') if r['features'].get('normalized_reaction') else None
def products(r):
 n=r['features'].get('normalized_reaction')
 return n.split('>>')[-1] if n and '>>' in n else None
classes=defaultdict(list)
for d in ds:
 cls='USPTO grants' if d['name']=='uspto-grants' else ('C8SC04228D ML splits' if 'C8SC04228D' in d['name'] else 'Other datasets')
 classes[cls].append(d)
source_summary={k:{'datasets':len(v),**{f:sum(d[f] for d in v) for f in ('rows','candidates','glycosides','unknown')}} for k,v in classes.items()}
def identities(rs): return {exact(r) for r in rs if exact(r)}
groups=defaultdict(list)
for r in rows:
 if exact(r):groups[exact(r)].append(r)
cross=[{'exact_group':k,'datasets':sorted({r['dataset_name'] for r in v}),'ids':[r['id'] for r in v]} for k,v in groups.items() if len({r['dataset_id'] for r in v})>1]
localp={products(r) for r in local if products(r)}
localg={products(r) for r in local if products(r) and r['features']['domain_glycoside_candidate']}
proc=defaultdict(list)
for r in gly:
 p=' '.join(r['raw_ord'].get('notes',{}).get('procedure_details','').split())
 if p:proc[p].append(r)
procdups=[{'procedure_sha256':__import__('hashlib').sha256(p.encode()).hexdigest(),'ids':[r['id'] for r in v],'patents':sorted({r.get('patent') or '' for r in v})} for p,v in proc.items() if len(v)>1]
diag=[]
for r in gly:
 f=r['features'];n=f.get('normalized_reaction',''); left,right=n.split('>>') if '>>' in n else ('','')
 dom_new=f.get('product_domain_sites',{}).get('aryl_O_candidate',0)>0 and not f.get('reactant_domain_sites',{}).get('aryl_O_candidate',0)
 all_pre=f.get('reactant_sites',{}).get('aryl_O_candidate',0)>0
 diag.append({'id':r['id'],'patent':r.get('patent'),'dataset_name':r['dataset_name'],'exact_group':exact(r),'identical_complete_sides':bool(left) and left==right,'aryl_O_domain_appearance':dom_new,'aryl_O_already_present_any_reactant':all_pre,'reactant_domain_sites':f.get('reactant_domain_sites',{}),'product_domain_sites':f.get('product_domain_sites',{}),'local_exact_product_set_match':products(r) in localp,'procedure_present':bool(r['raw_ord'].get('notes',{}).get('procedure_details'))})
summary={'input_summary_sha256':digest('outputs/coverage/task015-summary/summary.json'),'source_summary':source_summary,'candidate_rows':len(rows),'strict_groups':len(groups),'incomplete_candidates':sum(not exact(r) for r in rows),'cross_dataset_strict_groups':len(cross),'cross_dataset_strict_source_rows':sum(len(g['ids']) for g in cross),'glycoside_rows':len(gly),'glycoside_strict_groups':len(identities(gly)),'glycoside_patent_strings':len({r['patent'] for r in gly if r.get('patent')}),'glycoside_identical_complete_sides':sum(d['identical_complete_sides'] for d in diag),'glycoside_domain_aryl_O_appearance':sum(d['aryl_O_domain_appearance'] for d in diag),'appearance_with_preexisting_aryl_O_anywhere':sum(d['aryl_O_domain_appearance'] and d['aryl_O_already_present_any_reactant'] for d in diag),'appearance_without_preexisting_aryl_O_anywhere':sum(d['aryl_O_domain_appearance'] and not d['aryl_O_already_present_any_reactant'] for d in diag),'glycoside_duplicate_procedure_groups':len(procdups),'glycoside_duplicate_procedure_rows':sum(len(g['ids']) for g in procdups),'ord_exact_product_set_overlap_local':len({products(r) for r in rows if products(r) in localp}),'ord_glyco_exact_product_set_overlap_local':len({products(r) for r in gly if products(r) in localg}),'ord_glyco_rows_with_product_set_overlap_local':sum(products(r) in localg for r in gly),'limitations':['Product-only overlap is not the same reaction or an independent experiment.','No removal of stereochemistry, salts or tautomers; strict false negatives remain possible.','Topology appearance does not identify a newly formed bond.','Only source examples specifically described in companion report were manually source-audited; this is not precision/recall evaluation.']}
assert len(rows)==8509 and len(groups)==6013 and len(gly)==78 and len(identities(gly))==65
assert sum(d['rows'] for d in ds)==2428291
save('analysis.json',summary);save('cross-dataset-strict-groups.json',cross);save('duplicate-glycoside-procedures.json',procdups)
write(TASK,OUT+'/glycoside-diagnostics.jsonl',''.join(json.dumps(d,ensure_ascii=False)+'\n' for d in diag))
print(json.dumps(summary,ensure_ascii=False,indent=2))

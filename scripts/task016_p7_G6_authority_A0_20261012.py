"""Freeze chemical source input universe for genuinely independent A4/A5 graph extraction."""
from pathlib import Path
import json,datetime,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
T='TASK-016-P7';B=Path('outputs/task016-p7/v1');O=B/'G6_three_decisions_20261012_v1'
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
 out=O/'C_PMC13564134_A0_PubChem_three_complete_graph_inputs.json'
 if (ROOT/out).exists():raise RuntimeError('immutable')
 r=json.loads((ROOT/O/'C_PubChem_raw_HTTP_receipts.json').read_text())
 assert len(r['records'])==6 and all(x['status']==200 and x['error'] is None for x in r['records'])
 src=Path('data/raw/task016-p7/prospective_G6_round_20261011_v1/PMC13564134.original_JATS_XML')
 expected={'luteolin':5280445,'isoorientin':114776,'UDP-glucose':8629}
 for x in r['records']:
  assert (x.get('CID_property') or x.get('CID_record'))==expected[x['name']]
  assert sha(Path(x['path']))==x['sha256']
 obj={'task':T,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
   'A0_role':'graph_input_frozen','source_article_DOI':'10.1016/j.abiote.2026.100085',
   'source_original_JATS':str(src),'source_original_SHA':sha(src),
   'A3_original_front_sha':sha(B/'prospective_G6_round_20261011_v1/C_PMC13564134_A3_original_front_and_exposure.json'),
   'C_E02_G4_sha':sha(B/'C/E02/stages/G4_SCOPE_FREEZE.json'),
   'authoritative_cids':expected,'structure_requests':r['records'],
   'A4':'fresh process PubChem property JSON stereochemical name to SMILES; no A5 output',
   'A5':'fresh process PubChem PC_Compounds record ABS SMILES + atom-bond graph; no A4 output',
   'A6':'only after both; independent canonical stereochemistry/full graph + C6/C1 site + full donor and complete reference and source closure',
   'never_guess_from_name':True,'no_model_outcomes_read':True,'G6_full_reaction_fresh_qualified':False}
 write(T,str(out),json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 event(T,'C_PMC13564134_authoritative_three_graph_input_frozen',sha256=sha(out),CIDs=expected)
 print(json.dumps({'input_SHA':sha(out),'sources':6,'CIDs':expected}))
if __name__=='__main__':main()

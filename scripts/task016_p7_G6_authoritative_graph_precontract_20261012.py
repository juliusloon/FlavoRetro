"""Pre-register authoritative PubChem atom/stereo records for PMC13564134's three named molecules.
Each request logged as G6 structure evidence, not as fresh acceptance, no name-derived guesses.
"""
import hashlib,json,datetime,urllib.parse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
T='TASK-016-P7';B=Path('outputs/task016-p7/v1')
O=B/'G6_three_decisions_20261012_v1'
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
 names=['luteolin','isoorientin','UDP-glucose']
 q=[]
 for n in names:
  enc=urllib.parse.quote(n,safe='')
  q.append({'name':n,'route':'PubChem_PUG_name_to_properties',
    'url':f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{enc}/property/CanonicalSMILES,IsomericSMILES,MolecularFormula,ExactMass,IUPACName,InChI,InChIKey/JSON',
    'max_HTTP':1,'max_bytes':1000000,'status':'preregistered'})
  q.append({'name':n,'route':'PubChem_PUG_name_to_molecule_record',
    'url':f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{enc}/record/JSON',
    'max_HTTP':1,'max_bytes':2000000,'status':'preregistered'})
 pre={'task':T,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'source':'PMC13564134','DOI':'10.1016/j.abiote.2026.100085',
 'primary_article_JATS':str(Path('data/raw/task016-p7/prospective_G6_round_20261011_v1/PMC13564134.original_JATS_XML')),
 'primary_article_sha':'7dc62ce308ada55a410f72db97140979e23d1de964a6f7da05c61dda28a3a283',
 'G5_stage_sha':'fd2e41de8228c7b0772c86c0c9ef89fc3e9b75777ed72edf3f4da8dd10b2ae7d',
 'three_workstreams_precontract_sha256':sha(O/'three_workstreams_precontract.json'),
 'why':'official PubChem structural identity for source-named acceptor/product/donor with author JATS chain; verify stereochemistry and complete graph',
 'max_total_HTTP':6,'max_total_new_bytes':9000000,
 'A4_in_one_process':'extract name to authoritative stereochemical isomeric SMILES properties',
 'A5_independent_process':'parse original PubChem graph JSON into bond/atom stereo and compare source graph not read A4',
 'A6_requires':'independent canonical molecular graph agreement, named compound source identity chain, C6 connectivity, UDP-Glu complete precursor, historic assay closure, static frozen scope',
 'no_manually_guessed_SMILES':True,'do_not_auto_promote_if_pubchem_ambiguous':True,
 'original_source_chemical_read_already_exposed_in_current_epoch':True,
 'read_model_outcome':False,'G6_fresh_admitted':0,'queries':q}
 path=O/'C_PMC13564134_authoritative_graph_query_precontract.json'
 if (ROOT/path).exists():raise RuntimeError('immutable')
 write(T,str(path),json.dumps(pre,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 event(T,'C_PMC13564134_PubChem_atom_graph_precontract',queries=6,sha256=sha(path))
 print(json.dumps({'query_count':len(q),'plan':str(path),'sha':sha(path)}))
if __name__=='__main__':main()

"""A0 precontract for source-bound dual textual/structural attempts, no guessed molecular SMILES."""
import hashlib,json,datetime
from pathlib import Path
from scripts.operate import write,event
ROOT=Path(__file__).resolve().parents[1];T='TASK-016-P7'
B=Path('outputs/task016-p7/v1');O=B/'prospective_G6_round_20261011_v1'
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
 g5=O/'C-PMC13564134/stages/G5_FRESH_HOLDOUT_ACQUIRE.json'
 a3=O/'C_PMC13564134_A3_original_front_and_exposure.json'
 src=Path('data/raw/task016-p7/prospective_G6_round_20261011_v1/PMC13564134.original_JATS_XML')
 data={'task':T,'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'agent_role':'A0','epoch':'C-E02','source':'PMC13564134','DOI':'10.1016/j.abiote.2026.100085',
 'G5_SHA':sha(g5),'A3_SHA':sha(a3),'source_SHA':sha(src),
 'A4':{'method':'lxml_original_results_and_discussion_xpath','read_A5_output':False},
 'A5':{'method':'independent_xml_etree_stream_reverse_topic_extract','read_A4_output':False},
 'A4_A5_input_same_immutable_original':True,
 'no_name_based_SMILES':'source machine-readable atom graphs or authenticated database chain only',
 'frozen_C6_gate':'requires source-bound one-step direct flavone C6 UDP beta-D-Glc',
 'mandatory_output_fields':['acceptor','donor','product','bond_atoms','site','sugar_identity','anomer_stereo','direction','step_count','structure_origin','reference_precursors','original_evidence_location'],
 'unknown_fields_must_be_null_not_guessed':True,
 'A6_must_compare_claims_and_graphs_and_full historical name/assay closure':True,
 'read_model_outcomes':False,'fresh_admission_at_start':False,'human_reviewed':False,
 'original_scientific_body_already_A3_reviewed':True}
 p=O/'C_PMC13564134_A0_dual_science_read_precontract.json'
 if (ROOT/p).exists():raise RuntimeError('immutable')
 write(T,str(p),json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 event(T,'C_PMC13564134_A4_A5_preregistered',precontract_sha=sha(p))
 print(json.dumps({'dual_precontract_path':str(p),'sha':sha(p)}))
if __name__=='__main__':main()

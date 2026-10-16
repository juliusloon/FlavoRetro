"""R64 independent P7 named-gap verification: raw status vs actual body, frozen original.
No new HTTP and no chemistry admission.
"""
import gzip,json,hashlib
from collections import Counter
from pathlib import Path
from scripts.operate import ROOT,write
from scripts.task016_p7_c_e02_http import physical_attempts

T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R61=B/"C/E02/fresh/C-E02-R61-two-legacy-official-original-recovery-v1/raw_custody_summary.json"
R62=B/"verification-v32-pending-original-source-inventory/named_pending_original_inventory.json"
O=B/"verification-v32-pending-original-source-inventory/independent_A11_named_source_access_reconciliation.json"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def load(p):return json.loads((ROOT/p).read_text())
def main():
 if (ROOT/O).exists():raise RuntimeError("IMMUTABLE")
 a=load(R62);r61=load(R61)
 checks=[]
 def ck(label,condition):
  checks.append(dict(check=label,passed=bool(condition)))
  if not condition:raise AssertionError(label)
 ck("sixteen_named_targets",a["denominator"]==16 and len(a["items"])==16)
 ck("C8_SS8",Counter(x["family"] for x in a["items"])==Counter(C=8,SS=8))
 ck("all_input_evidence_exact_Sha",all(sha(Path(p))==digest for p,digest in a["source_evidence_sha"].items()))
 for x in a["items"]:
  ck("each_unavailable_source_proof_"+x["source_identifier"],Path(x["source_evidence"]).exists() and (ROOT/x["source_evidence"]).is_file())
  ck("no_wrong_claim_fresh_"+x["source_identifier"],x["not_fresh_until_proven"])
 physical=physical_attempts()
 ck("physical_HTTP_1208",len(physical)==1208)
 ck("physical_bytes_1242654272",sum(x["bytes"] for x in physical)==1242654272)
 ck("latest_two_500_after_prereg",r61["HTTP"]==2 and [x["status_code"] for x in r61["sources"]]==[500,500])
 for r in r61["sources"]:
  p=Path(r["raw_pointer"]["path"])
  ck("R61_exact_stored_sha_"+r["pmcid"],sha(p)==r["raw_pointer"]["sha256"])
 for pid in ("PMC2709393","PMC7720146"):
  url="https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/"+pid+"/unicode"
  existing=[x for x in physical if x["url"]==url]
  ck("BioC_no_retry_previous_"+pid,len(existing)==1 and existing[0]["status_code"]==200)
  response=(ROOT/existing[0]["path"]).read_bytes()
  ck("BioC_raw_SHA_"+pid,hashlib.sha256(response).hexdigest()==existing[0]["sha256"])
  ck("BioC_gzipped_not_original_"+pid,response.startswith(b"\x1f\x8b") and gzip.decompress(response).startswith(b"[Error] : No result can be found."))
  url2="https://www.ebi.ac.uk/europepmc/webservices/rest/"+pid+"/fullTextXML"
  tried=[x for x in physical if x["url"]==url2]
  ck("EPMC_two_attempts_exact_"+pid,len(tried)==2 and all(z["status_code"]==500 for z in tried))
 for x in a["items"]:
  ck("source_labels_not_already_full_admitted_"+x["source_identifier"],x["chemical_qualification"]!="qualified")
 result=dict(task=T,approval_type="agent_delegated",role="A11_source_access_not_science",human_reviewed=False,checks=checks,passed=len(checks),failed=0,source_inventory_SHA=sha(R62),R61_SHA=sha(R61),registered_named_cases=16,real_valid_new_primary_originals=0,source_500_explicit_2=2,old_BioC_200_errors_2=2,new_HTTP=2,new_bytes=300,current_HTTP=1208,current_bytes=1242654272,source_saturation=False,independent_chemical_validation=False,fresh_C=0,fresh_SS=0,scientific_ABE=0,metrics=None)
 write(T,str(O),json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
 print(json.dumps(dict(passed=len(checks),fresh_C=0,fresh_SS=0,registered_named=16,old_BioC_errors=2)))
if __name__=="__main__":main()

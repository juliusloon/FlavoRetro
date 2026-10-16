"""P7 R62: named outstanding original-file/source-qualification inventory from immutable records.

This is a finite known-backlog reconciliation, not source saturation or proof of full coverage.
Never reads new scientific bodies; no HTTP, no prospective fresh admission.
"""
import json,hashlib
from pathlib import Path
from collections import Counter
from scripts.operate import ROOT,write
from scripts.task016_p7_c_e02_http import physical_attempts

TASK="TASK-016-P7";BASE=Path("outputs/task016-p7/v1")
O=BASE/"verification-v32-pending-original-source-inventory"
R12=BASE/"C/E02/fresh/C-E02-R12/6_source_lawful_access_dispositions_v1.json"
R61=BASE/"C/E02/fresh/C-E02-R61-two-legacy-official-original-recovery-v1/raw_custody_summary.json"
R9=BASE/"SS/E02/fresh/SS-E02-R9-access-completion-v1/source_custody_universe.json"
R9G=BASE/"SS/E02/fresh/SS-E02-R9-access-completion-v1/R5_access_gap_clarification.json"
R16=BASE/"SS/E02/fresh/SS-E02-R16-verified-publisher-PDF-access-v1/bounded_raw_access_dispositions.json"
R32=BASE/"SS/E02/fresh/SS-E02-R32-ACS-SI-expiry-recovery-v1/raw_custody_summary.json"
R55=BASE/"SS/E02/fresh/SS-E02-R55-Laportea-tabular-SI-custody-v1/raw_custody_summary.json"
R56=BASE/"SS/E02/fresh/SS-E02-R56-Laportea-tabular-science-v1/A6/source_scientific_assessment.json"
R58=BASE/"SS/E02/fresh/SS-E02-R58-declared-primary-PDF-custody-v1/raw_custody_summary.json"
R52=BASE/"C/E02/fresh/C-E02-R52-mungbean-declared-VoR-v1/raw_custody_summary.json"
R46=BASE/"C/E02/fresh/C-E02-R46-Iris-advertised-assets-v1/raw_custody_summary.json"

def read(path):return json.loads((ROOT/path).read_text())
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def main():
 if (ROOT/O).exists():raise RuntimeError("IMMUTABLE INVENTORY")
 evidence=[R12,R61,R9,R9G,R16,R32,R55,R56,R58,R52,R46]
 for p in evidence:assert (ROOT/p).exists(),p
 x12=read(R12); x61=read(R61);x9=read(R9);x9g=read(R9G)
 x16=read(R16);x32=read(R32);x55=read(R55);x56=read(R56);x58=read(R58);x52=read(R52);x46=read(R46)
 assert len(x12["sources"])==6
 assert x61["HTTP"]==2 and x61["valid_JATS"]==0 and set(r["status_code"] for r in x61["sources"])=={500}
 assert x9["denominator"]==4 and x9g["counts"]["actual_source_access_gaps"]==4
 assert x58["valid_PDF"]==0 and x58["HTTP_statuses"]==[403,403]
 assert x55["valid_XLSX"] and x56["fresh_admitted"]==0 and x56["chemical_qualification"]=="deferred"
 assert x32["files_available"]==3 and x32["pdf_magic_and_official_size_MD5_SHA_verified"]==3
 assert x52["valid_PDF_count"]==0 and x52["original_custody_available"]==0
 assert any(z["query_id"]=="R46-SI" and z["status"]=="access_pending" for z in x46["records"])
 rows=[]
 def add(family,identity,pending,sourcepath,latest_route,known_raw,qualification,priority,notes,scope):
  rows.append(dict(family=family,source_identifier=identity,outstanding_file_or_evidence=pending,source_evidence=str(sourcepath),latest_access_state=latest_route,valid_original_already_available=known_raw,chemical_qualification=qualification,priority=priority,notes=notes,not_fresh_until_proven=True,scientific_scope_claim=scope,do_not_retry_prior_denied_or_max_attempts=True))
 for item in x12["sources"]:
  id=item.get("doi") or item["source_id"]
  legacy=item["source_id"].startswith("PMC")
  if legacy:
   recovery=next(t for t in x61["sources"] if t["pmcid"]==id)
   latest="EPMC_fullTextXML_second_attempt_HTTP500; no valid JATS" 
   assert recovery["status_code"]==500
  else:
   latest="original identity/body pending; R12 lawful access attempt recorded"
  add("C",id,"primary-original/article+reaction qualification",R12,latest,False,"pending", "medium", "Legacy source historical exposure; no source independent fresh eligibility" if legacy else "metadata hints only, no A3 original identity.", "no claims from metadata")
 # Reconcile latest separately named C cases not R12 six.
 add("C","10.1111/tpj.70932","primary scientific article full-text original",R52,"Crossref VoR PDF and XML 403; publisher landing 403; no valid bytes",False,"pending","high","Publisher/index metadata may show OA but original not accessed; no access control bypass", "isovitexin title does not establish direct flavone C6")
 add("C","10.1002/cbic.70486","originally advertised supplemental PDF",R46,"R46 HTTP200 CAPTCHA HTML, not PDF; main public HTML and figures retained",True,"main body A6 deferred, SI access pending","medium","Original main HTML present; no verification of missing SI", "frozen C direct C6 unproven")
 for item in x9["fixed_pending_sources"]:
  add("SS",item["DOI"],"primary scientific article original",R9,"R5/R9 raw retrieval ended without valid PDF/XML; no legal challenge bypass",False,"pending","low","1975/1979/1984/1997 older studies, historical source suitability unresolved","3-O/7-O/triglucoside names do not establish sugar-residue O2")
 for item in x32["sources"]:
  doi=item["DOI"]
  assert item["original_path"] and sha(Path(item["original_path"]))==item["original_SHA"]
  notes="Official supplementary PDF obtained and science-screened at R34; original main article still required."
  if doi=="10.1021/acs.jafc.4c00488": notes+=" Additional official XLSX fully screened at R56, A6 deferred."
  add("SS",doi,"main scientific article original; source-bound complete reaction evidence",R32,"ACS subscription/403 main-original paths retained; official SI PDF available",False,"supplements screened, full source deferred","high" if doi!="10.1021/acs.jafc.4c00488" else "medium",notes,"SS frozen sugar-residue O2 unproven")
 rs=x16["raw_dispositions"]
 assert any(r["DOI"]=="10.1111/tpj.16898" and r["HTTP_status"]==403 for r in rs)
 add("SS","10.1111/tpj.16898","publisher primary-original PDF",R16,"actual PDF 403; no valid original",False,"pending","medium","R16 source is separate from three ACS items, bibliography-only pending", "scope undecided")
 assert len(rows)==16, len(rows)
 assert len({(x["family"],x["source_identifier"]) for x in rows})==16
 assert Counter(x["family"] for x in rows)==Counter(C=8,SS=8)
 physical=physical_attempts()
 assert len(physical)==1208 and sum(r["bytes"] for r in physical)>=1242653972
 result=dict(task=TASK,approval_type="agent_delegated",human_reviewed=False,kind="known_explicit_pending_original_and_source_qualification_inventory",items=rows,denominator=16,axis_counts=dict(C=8,SS=8),not_aggregate_all_possible_literature=True,not_all_95_title_hints_as_missing_files=True,not_scientific_saturation=True,do_not_claim_fresh_from_web_snippets=True,accepted_original_SI_not_same_as_main_article=True,source_identity_and_full_chemistry_separate=True,legal_stop_for_same_exact_failed_endpoint=True,zero_benchmark_cells=True,source_evidence_sha={str(p):sha(p) for p in evidence},physical_HTTP=len(physical),physical_bytes=sum(r["bytes"] for r in physical),scientific_C_fresh=0,scientific_SS_fresh=0,scientific_transfer_metrics=None,priority_order="One verified original/license route at a time; G5 before any new scientific read; A3+A4/A5+A6 before full graph; do not retry 403/captcha/URL caps",status="In Progress")
 out=O/"named_pending_original_inventory.json"
 write(T,str(out),json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
 summary=["# P7 可核的具名待获取原件与来源资格清单","","> 截面：progress-v32；仅覆盖既有成果中明确具名并有记录的16项访问/资格缺口，不代表全部文献穷尽。","",f"已登记 {len(rows)} 项（C 8、SS 8）；新的科学 fresh C=0 / SS=0。已获取的SI/PDF/XLSX与未获取主文严格分离。","", "| 轴 | DOI/PMCID | 仍缺 | 最新证据状态 |", "| --- | --- | --- | --- |"]
 for a in rows:summary.append(f"| {a['family']} | {a['source_identifier']} | {a['outstanding_file_or_evidence']} | {a['latest_access_state']} |")
 summary+=["","**不可擅自升级：** metadata、摘要、已暴露反应、原始补充材料、HTTP200非PDF、官方OA标签均不能替代原主文、完整反应结构或fresh holdout。","",
 "**后续执行规则：** 不重新请求先前403、验证码、单URL尝试上限；只有新的明确、合法、真实来源路径才可在新预登记预算内继续获取；无原件则维持pending，不声明来源饱和。",""]
 write(T,str(O/"README.md"),"\n".join(summary))
 print(json.dumps(dict(named_pending=len(rows),C=8,SS=8,physical_HTTP=len(physical),physical_bytes=result["physical_bytes"],fresh=0)))
if __name__=="__main__":main()

"""P7 v18 A11 independent evidence-boundary audit of R6 bibliography and alias screening."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from scripts.operate import ROOT,write
TASK="TASK-016-P7";B=Path("outputs/task016-p7/v1")
A3=B/"SS/E02/fresh/SS-E02-R6-A3-original-identity-v1"
A61=B/"SS/E02/fresh/SS-E02-R6-A6-documentary-exposure-screen-v1"
A62=B/"SS/E02/fresh/SS-E02-R6-A6-documentary-exposure-screen-v2"
R4=B/"SS/E02/fresh/SS-E02-R4-bibliographic-resolution-v1/authoritative_bibliographic_records.jsonl"
R3=B/"SS/E02/fresh/SS-E02-R3-metadata-closure-v1/source_exposure_projection.jsonl"
V17=B/"report_snapshots/progress-v17.json"
OUT=B/"verification-v18-ss-r6"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def rows(p):return [json.loads(s) for s in (ROOT/p).read_text().splitlines() if s.strip()]
def load(p):return json.loads((ROOT/p).read_text())
def save(p,x):write(TASK,str(OUT/p),json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def main():
    if (ROOT/OUT).exists():raise RuntimeError("IMMUTABLE_OUTPUT_EXISTS")
    frozen=[A3/"preflight.json",A3/"A3_original_identity_results.json",A3/"role_A3_manifest.json",
      A61/"A6_source_exposure_dispositions.json",A62/"preflight.json",
      A62/"A6_full_alias_union_dispositions.json",A62/"role_A6_manifest.json",R4,R3,V17]
    inp={str(p):sha(p) for p in frozen}
    checks={};failures=[]
    def test(name,v):
        checks[name]=bool(v)
        if not v:failures.append(name)
    v17=load(V17)
    test("v17_current_REPORT_SHA",sha(Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md"))==v17["current_REPORT_sha"])
    test("v17_current_STATE_SHA",sha(Path("STATE.md"))==v17["current_STATE_sha"])
    test("v17_previous_evidence_SHA",all(sha(Path(p))==s for p,s in v17["evidence_SHA"].items()))
    a=load(A3/"A3_original_identity_results.json")
    x=load(A62/"A6_full_alias_union_dispositions.json")
    official=rows(R4);history=rows(R3)
    test("A3_6_conserve",len(a["results"])==6 and a["counts"]["processed"]==a["counts"]["passed"]+a["counts"]["pending"]+a["counts"]["rejected"])
    verify=[s for s in a["results"] if s["publication_identity_verified"]]
    test("A3_two_origins_all_ten_checks",len(verify)==2 and all(len(s["checks"])==10 and all(s["checks"].values()) for s in verify))
    test("A3_original_bytes_sha",len(verify)==2 and all(sha(Path(s["source_raw_path"]))==s["source_raw_sha"] for s in verify))
    test("A3_not_read_chemical",a["scientific_body_figures_read"] is False and all(not s["abstract_or_chemical_body_read"] for s in a["results"]))
    test("A6_six_and_28_names",len(x["sources"])==6 and x["unverified_literal_hypothesis_counts"]=={"SS_pre_G4":9,"C_pre_G4":16,"C_post_G4":3})
    expected={}
    for src in a["results"]:
        doi="doi:"+src["DOI"]
        matched=[r for r in official if doi in [z.lower() for z in r["normalized_identifier_tokens"]]]
        expected[src["source_id"]]=sorted(set(t.lower() for r in matched for t in r["normalized_identifier_tokens"]
             if t.startswith(("doi:","pmid:","article:"))))
    actual={r["source_id"]:r["official_alias_union"] for r in x["sources"]}
    test("A6_union_equals_all_R4_official_aliases",actual==expected)
    positive={t.lower() for r in history if r.get("known_exposed") is True for t in r["identifier_tokens"]}
    should_positive={k for k,v in expected.items() if positive.intersection(v)}
    claimed_positive={r["source_id"] for r in x["sources"] if r["positive_match_count"]>0}
    test("A6_independent_exposure_projection_recompute",should_positive==claimed_positive)
    test("A6_NO_certified_negative",x["source_exposure_nonmatch_does_not_establish_freshness"] is True and
        all(r["source_historical_exposure"]!="proven_unexposed" for r in x["sources"]))
    test("A6_v1_preserved_as_superseded",sha(A61/"A6_source_exposure_dispositions.json")==load(A62/"preflight.json")["input_SHA256"][str(A61/"A6_source_exposure_dispositions.json")])
    test("G6_scientific_and_MCTS_not_claimed",a["fresh_admitted"]==0 and x["counts"]["fresh_admitted"]==0 and x["counts"]["new_chemically_qualified"]==0 and x["new_MCTS"]==0)
    test("no_A3_A6_HTTP",a["new_HTTP"]==0 and x["new_HTTP"]==0)
    status={"task":TASK,"agent_role":"A11","timestamp":datetime.now(timezone.utc).isoformat(),
       "inputs_SHA":inp,"checks":checks,"passed":sum(checks.values()),"failed":len(failures),
       "failures":failures,"identity_verified_original_count":len(verify),
       "identity_remaining_pending":4,
       "official_positive_matches":len(should_positive),
       "unverified_names":28,"fresh_C":0,"fresh_SS":0,"scientific_ABE_cells":0,
       "new_HTTP":0,"new_MCTS":0,"scientific_metrics":None,
       "not_a_scientific_identity_or_transitive_closure_certificate":True,
       "full_P7_task_completed":False,"human_reviewed":False}
    save("independent_R6_verification.json",status)
    print(json.dumps({"status":"pass" if not failures else "fail","checks":len(checks),"passed":status["passed"],
           "failed":status["failed"],"A3_verified":len(verify),"fresh":0},ensure_ascii=False))
    if failures:raise RuntimeError("A11_VERIFICATION_FAILURE "+",".join(failures))
if __name__=="__main__":main()

"""P7 SS R6 A6 v2: independent complete official-ID union exposure screen."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from scripts.operate import ROOT,write
from scripts.task016_p7_ss_r6_a6_alias_screen import direct_matches
TASK="TASK-016-P7";B=Path("outputs/task016-p7/v1")
A3=B/"SS/E02/fresh/SS-E02-R6-A3-original-identity-v1/A3_original_identity_results.json"
A6V1=B/"SS/E02/fresh/SS-E02-R6-A6-documentary-exposure-screen-v1/A6_source_exposure_dispositions.json"
R4=B/"SS/E02/fresh/SS-E02-R4-bibliographic-resolution-v1/authoritative_bibliographic_records.jsonl"
R3=B/"SS/E02/fresh/SS-E02-R3-metadata-closure-v1/source_exposure_projection.jsonl"
NAMEFILES=[B/"SS/E02_design/root_prefreeze_name_hypotheses_registered_late_v1/permanent_unverified_name_exposures.jsonl",
 B/"C/E02/pre_freeze_hypothesis_exposure/v1/permanent_name_hypothesis_exposure.jsonl",
 B/"C/E02/post_scope_internal_hypotheses/v1/permanent_name_hypothesis_exposure.jsonl"]
OUT=B/"SS/E02/fresh/SS-E02-R6-A6-documentary-exposure-screen-v2"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def rows(p):return [json.loads(s) for s in (ROOT/p).read_text().splitlines() if s.strip()]
def load(p):return json.loads((ROOT/p).read_text())
def save(p,a):write(TASK,str(OUT/p),json.dumps(a,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def collect_aliases(source,official):
    d="doi:"+source["DOI"].lower()
    matched=[r for r in official if d in (str(t).lower() for t in r["normalized_identifier_tokens"])]
    if not matched:raise RuntimeError("NO_R4_OFFICIAL_DOI "+d)
    aliases=sorted(set(t.strip().lower() for r in matched for t in r["normalized_identifier_tokens"]
                if t.startswith(("doi:","pmid:","article:"))))
    if d not in aliases:raise RuntimeError("DOI_LOST")
    if source["publication_identity_verified"]:
        front=source["front"]["ids"]
        for k,prefix in (("doi","doi:"),("pmid","pmid:"),("pmcid","article:")):
            for name in front.get(k,[]):
                if prefix+name.lower() not in aliases:
                    raise RuntimeError("INDEPENDENT_ORIGINAL_ALIAS_MISMATCH "+name)
    return aliases,[{"record_id":r["record_id"],"route":r["route"]} for r in matched]
def main():
    if (ROOT/OUT).exists():raise RuntimeError("IMMUTABLE_OUTPUT_EXISTS")
    inp=[A3,A6V1,R4,R3]+NAMEFILES
    fixed={str(p):sha(p) for p in inp}
    a=load(A3)["results"];history=rows(R3);off=rows(R4);old=load(A6V1)
    assert len(a)==6 and len(old["source_dispositions"])==6
    ss,pre,post=[rows(p) for p in NAMEFILES]
    assert (len(ss),len(pre),len(post))==(9,16,3)
    save("preflight.json",{"task":TASK,"role":"A6","timestamp":datetime.now(timezone.utc).isoformat(),
        "input_SHA256":fixed,
        "supersedes_A6_v1_due_to_missing_non_original_PMID_aliases":True,
        "no_original_science_read":True,
        "registered_official_metadata_only":True,
        "fresh_admitted":0})
    results=[]
    for source in a:
        alias,pointers=collect_aliases(source,off)
        found=direct_matches(alias,history)
        results.append({"source_id":source["source_id"],"DOI":source["DOI"],"official_alias_union":alias,
            "official_bibliographic_pointers":pointers,
            "positive_exposure_matches":[{"pointer":x.get("pointer"),"identifier_tokens":x.get("identifier_tokens"),
                  "positive_exposure_flags":x.get("positive_exposure_flags")} for x in found],
            "positive_match_count":len(found),
            "source_historical_exposure":"known_exposed" if found else "unresolved_not_certified_negative",
            "source_original_bibliography_verified":source["publication_identity_verified"],
            "title_narrative_not_used_as_alias_evidence":True,
            "SS_unresolved_name_hypotheses":len(ss),"C_unresolved_name_hypotheses":len(pre)+len(post),
            "full_source_and_reaction_closure_performed":False,
            "source_original_science_read":False,"reaction_qualified":False,
            "fresh_admitted":False})
    assert len(results)==6
    known=sum(bool(r["positive_match_count"]) for r in results)
    result={"task":TASK,"epoch_id":"SS-E02","agent_role":"A6",
       "timestamp":datetime.now(timezone.utc).isoformat(),
       "input_preflight_sha":sha(OUT/"preflight.json"),
       "counts":{"processed":6,"known_exposed_positive":known,"pending_without_positive":6-known,
          "original_bibliography_verified":2,"new_chemically_qualified":0,"fresh_admitted":0},
       "historic_projection_rows":len(history),"sources":results,
       "unverified_literal_hypothesis_counts":{"SS_pre_G4":len(ss),"C_pre_G4":len(pre),"C_post_G4":len(post)},
       "name_synthetic_graph_matches_performed":False,
       "source_exposure_nonmatch_does_not_establish_freshness":True,
       "no_chemical_source_or_reaction_eligibility_claim":True,
       "not_final_transitive_closure":True,
       "A6_v1_preserved_and_superseded":True,
       "new_HTTP":0,"new_MCTS":0,"human_reviewed":False}
    save("A6_full_alias_union_dispositions.json",result)
    save("role_A6_manifest.json",{"task":TASK,"agent_role":"A6","input_sha":sha(OUT/"preflight.json"),
       "output_sha":sha(OUT/"A6_full_alias_union_dispositions.json"),
       "counts":{"processed":6,"passed_fresh":0,"positive_exposure":known,"pending":6-known},
       "source_evidence_pointers":[str(p) for p in inp],
       "unprocessed":["all official name/synonym-to-graph closure for 28 preserved hypotheses",
           "original chemical assay/structure evidence and source assay transitive closure"],
       "read_holdout_chemical_content":False,"read_model_outcome":False,
       "fresh_admitted":0,"human_reviewed":False})
    print(json.dumps({"union_identifiers":[len(x["official_alias_union"]) for x in results],
      "historical_positive_hits_sources":known,"pending_not_fresh":6-known,
      "new_HTTP":0,"fresh_admitted":0},ensure_ascii=False))
if __name__=="__main__":main()

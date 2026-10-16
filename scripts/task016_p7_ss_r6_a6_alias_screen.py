"""TASK-016-P7 SS-E02 R6 A6 conservative documentary alias screen.

Exact registered source identifiers are checked against frozen historical
exposure projections. A negative hit is never a freshness certificate.
Unverified named-acceptor hypotheses are permanently blocking until independent
name/structure alias closure.
"""
import hashlib,json,re
from pathlib import Path
from datetime import datetime,timezone
from scripts.operate import ROOT,write

TASK="TASK-016-P7"; B=Path("outputs/task016-p7/v1")
A3=B/"SS/E02/fresh/SS-E02-R6-A3-original-identity-v1"
R3=B/"SS/E02/fresh/SS-E02-R3-metadata-closure-v1"
R5=B/"SS/E02/fresh/SS-E02-R5-original-acquisition-v1"
ROOTN=B/"SS/E02_design/root_prefreeze_name_hypotheses_registered_late_v1/permanent_unverified_name_exposures.jsonl"
C1=B/"C/E02/pre_freeze_hypothesis_exposure/v1/permanent_name_hypothesis_exposure.jsonl"
C2=B/"C/E02/post_scope_internal_hypotheses/v1/permanent_name_hypothesis_exposure.jsonl"
OUT=B/"SS/E02/fresh/SS-E02-R6-A6-documentary-exposure-screen-v1"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def load(p):return json.loads((ROOT/p).read_text())
def rows(p):return [json.loads(s) for s in (ROOT/p).read_text().splitlines() if s.strip()]
def save(name,obj):write(TASK,str(OUT/name),json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
def ntoken(s):return str(s).casefold().strip()
def direct_matches(tokens,exposures):
    """Positive source-level only; negatives never mean no exposure elsewhere."""
    uniq=set(ntoken(x) for x in tokens if x)
    return [r for r in exposures if r.get("known_exposed") is True and
            uniq.intersection(ntoken(t) for t in r.get("identifier_tokens",[]) if t)]
def main():
    if (ROOT/OUT).exists():raise RuntimeError("IMMUTABLE_OUTPUT_ALREADY_EXISTS")
    inputs=[A3/"A3_original_identity_results.json",A3/"role_A3_manifest.json",
       R3/"source_exposure_projection.jsonl", R5/"selection_dispositions.json",ROOTN,C1,C2]
    fixed={str(p):sha(p) for p in inputs}
    a=load(A3/"A3_original_identity_results.json")
    assert a["fresh_admitted"]==0 and a["counts"]["passed"]==2 and a["counts"]["pending"]==4
    nss=rows(ROOTN);nc1=rows(C1);nc2=rows(C2)
    assert len(nss)==9 and len(nc1)==16 and len(nc2)==3
    exposure=rows(R3/"source_exposure_projection.jsonl")
    assert len(exposure)>=2200
    save("A6_preflight.json",{"task":TASK,"agent_role":"A6","timestamp":datetime.now(timezone.utc).isoformat(),
       "input_SHA256":fixed,"documentary_only":True,
       "no_source_body_or_figure_read":True,"no_new_HTTP":True,
       "documentary_positive_match_not_full_transitive_closure":True,
       "name_hypotheses":len(nss)+len(nc1)+len(nc2)})
    sources=[]
    for src in a["results"]:
        tokens=[]
        for rs in src["R4_records"]:
            # Primary identity pointers are frozen R4 authoritative results;
            # A3 triple-confirmed identifiers for the two original-front cases.
            pass
        sid=src["source_id"];tokens.append("article:"+sid if sid.startswith("PMC") else "")
        tokens.append("doi:"+src["DOI"])
        # No fabricated PMID: original-front IDs only when A3 verified.
        front=src.get("front",{})
        if src["publication_identity_verified"]:
            for ident in front.get("ids",{}).get("pmid",[]):
                tokens.append("pmid:"+ident)
        tokens=[x for x in tokens if x]
        known=direct_matches(tokens,exposure)
        sources.append({"source_id":sid,"DOI":src["DOI"],
           "identifier_tokens_checked":tokens,
           "matched_positive_exposures":[{"pointer":r.get("pointer"),"tokens":r.get("identifier_tokens"),"flags":r.get("positive_exposure_flags")} for r in known],
           "known_positive_match_in_R3_index":bool(known),
           "R3_index_rows_scanned":len(exposure),
           "A3_original_bibliography_verified":src["publication_identity_verified"],
           "unresolved_internal_name_aliases_SS":len(nss),
           "unresolved_internal_name_aliases_C":len(nc1)+len(nc2),
           "source_exposure_final":"positively_development_exposed" if known else "unknown_not_cleared",
           "evidence_reaction_qualified":False,
           "fresh_eligible":False,
           "scope_applicability":None,
           "not_scientific_chemistry_read":True,
           "reason":"known exposure blocks fresh" if known else
              "no positive match from the frozen documentary index is insufficient; names/assay/reaction closure remain unresolved"})
    assert len(sources)==6
    exposed=sum(x["known_positive_match_in_R3_index"] for x in sources)
    save("A6_source_exposure_dispositions.json",{"task":TASK,"role":"A6",
      "timestamp":datetime.now(timezone.utc).isoformat(),"input_preflight_sha":sha(OUT/"A6_preflight.json"),
      "source_dispositions":sources,
      "counts":{"processed":6,"identity_verified":sum(x["A3_original_bibliography_verified"] for x in sources),
        "known_positive_exposed":exposed,"unknown_unresolved":6-exposed,
        "fresh_admitted":0,"reaction_admitted":0,"closure_groups_admitted":0},
      "unresolved_literal_hypotheses":{"SS_pre_G4":len(nss),"C_pre_G4":len(nc1),"C_post_G4":len(nc2)},
      "no_verified_name_to_graph_or_source_link":True,
      "not_a_full_reaction_assay_closure_or_final_G6":True,
      "source_exposure_is_not_certified_negative":True,
      "new_HTTP":0,"new_MCTS":0,"human_reviewed":False})
    save("role_A6_manifest.json",{"task":TASK,"role":"A6","timestamp":datetime.now(timezone.utc).isoformat(),
       "input_preflight_sha":sha(OUT/"A6_preflight.json"),
       "output_sha":sha(OUT/"A6_source_exposure_dispositions.json"),
       "source_evidence_pointers":[str(p) for p in inputs],"counts":{"processed":6,
          "passed_fresh":0,"rejected_positive_exposure":exposed,"pending":6-exposed},
       "unprocessed":["official name/structure synonym equivalence for 28 permanent hypotheses",
                     "unread source original chemistry, assay/reaction identities and downstream transitive closure"],
       "read_holdout":False,"read_model_outcome":False,"read_chemical_body":False,
       "fresh_eligible":False,"human_reviewed":False})
    print(json.dumps({"source_records":len(sources),"A3_original_verified":2,
      "positive_historical_matches_in_bounded_R3_index":exposed,
      "unresolved_names":28,"fresh_admitted":0,"new_HTTP":0},ensure_ascii=False))
if __name__=="__main__":main()

"""Append-only correction of the A3 Springer citation-author literal parser."""
from __future__ import annotations
import json
from pathlib import Path
from scripts.task016_p7_c_e02_source_qualification import Meta,normalize,ptr,load,rows,js,save,OUT,ROOT,EXPECTED
from scripts.task016_p7_orchestrate import now,sha_file
def main():
 original=OUT/"A3_source_publication_identity.jsonl"
 original_role=OUT/"role_A3_manifest.json"
 rs=rows(original)
 html="data/raw/task016-p7/C/8f5e15f10c169f0258aeabfc065eea54d3eb10f8045d00840646f591a3aca4e6.attempt-1.metadata"
 epmc="data/raw/task016-p7/C/b179044c5b5b846769c6570d8e5f329bab85280f4a222c193fd710ef68a7b7f3.attempt-1.discovery"
 parser=Meta();parser.feed((ROOT/html).read_text())
 raw_authors=parser.fields["citation_author"]
 if not all("," in s for s in raw_authors):raise ValueError("Source author delimiter missing; cannot infer surnames")
 actual_surnames=[s.partition(",")[0].strip() for s in raw_authors]
 core=load(epmc)["resultList"]["result"]
 index=next(i for i,e in enumerate(core) if e.get("id")=="29308528")
 secondary=[a.get("lastName") for a in core[index]["authorList"]["author"]]
 passed=[normalize(x) for x in actual_surnames]==[normalize(x) for x in secondary]
 if not passed:raise ValueError("Literal Springer surname field still disagrees with official CORE")
 r=next(r for r in rs if r["doi"]=="10.1007/s00253-017-8694-6")
 previous=r["field_checks"]["author_surnames"]
 r["field_checks"]["author_surnames"]=dict(primary_literal=raw_authors,primary=actual_surnames,secondary=secondary,
  primary_surname_field_parse="literal comma-separated citation_author field: substring before comma",
  raw_equal=actual_surnames==secondary,normalized_equal=passed)
 r["source_identity_verified"]=all(v.get("normalized_equal",v.get("passed",False)) for v in r["field_checks"].values())
 r["source_publication_identity_matches"]=r["source_identity_verified"]
 r["schema_parser_correction"]=dict(previous_failed_author_check=previous,source_fields_unchanged=True,
  original_record_preserved=True,reason="previous parser incorrectly took final space-delimited token from publisher Surname, Given names citation_author")
 js(OUT/"A3_source_publication_identity.v2.jsonl",rs)
 correction=dict(task="TASK-016-P7",candidate_epoch_id="C-E02",agent_role="A3 Source Identity Verifier",timestamp=now(),
  correction_type="own_metadata_parser_bug_append_only",original_outputs=[ptr(original),ptr(original_role)],
  changed_source="10.1007/s00253-017-8694-6",previous_failed_author_check=previous,
  source_raw_author_values=raw_authors,actual_source_surname_values=actual_surnames,official_CORE_surname_values=secondary,
  raw_pointers=[ptr(html),dict(**ptr(epmc),json_pointer=f"/resultList/result/{index}")],
  literal_source_field_format="Surname, Given names",parser_rule="take literal substring preceding first comma",
  corrected_match=passed,other_identity_fields_unchanged=True,raw_files_unchanged=True,
  chemical_qualification_not_granted=True,evidence_eligible_granted=False,
  read_A5_finalgraphs=False,scope_built_or_modified=False,human_reviewed=False,approval_type="agent_delegated")
 save(OUT/"A3_author_parser_correction.json",correction)
 role=load(original_role)
 role.update(timestamp=now(),schema_version="v2_append_only_parser_correction",
  supersedes_original_role_pointer=ptr(original_role),correction_pointer=ptr(OUT/"A3_author_parser_correction.json"),
  counts=dict(processed=len(rs),bibliographic_identity_passed=sum(x["source_identity_verified"] for x in rs),
   publisher_second_source_available=0,publisher_missing_secondary=len(rs)),
  output_file_sha={str((OUT/"A3_source_publication_identity.v2.jsonl").relative_to(ROOT)):sha_file(OUT/"A3_source_publication_identity.v2.jsonl")})
 save(OUT/"role_A3_manifest.v2.json",role)
 print(json.dumps(dict(bibliographic_identity_matches=sum(x["source_identity_verified"] for x in rs),
  role_pointer=ptr(OUT/"role_A3_manifest.v2.json"),correction_pointer=ptr(OUT/"A3_author_parser_correction.json"),
  output_pointer=ptr(OUT/"A3_source_publication_identity.v2.jsonl"))))
if __name__=="__main__":main()

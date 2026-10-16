"""Additional metadata scout round while frozen-scope semantic adjudication is pending."""
import sys,urllib.parse
from scripts import task016_p7_c_sources as s
queries=[
 '("C-glycosyltransferase" OR "C-glucosyltransferase") AND (flavone OR flavonol) AND (chrysin OR acacetin OR diosmetin OR baicalein OR scutellarein)',
 '("GtUF6CGT" OR "UGT708D1" OR "WjGT1" OR "GcCGT")',
 '("C-glycosyltransferase") AND ("8-C" OR "6-C" OR "direct") AND flavonoid',
 '("gallic acid" OR "methylgallic acid") AND ("C-glucoside" OR "C-glycosylation" OR "C-glucosyltransferase")',
 '(flavonol OR quercetin OR kaempferol OR myricetin) AND ("C-glucosyltransferase" OR "C-glycosyltransferase")',
 '("C-glycosyltransferase") AND (flavone OR flavonol) AND ("substrate promiscuity" OR "substrate scope" OR "protein engineering")'
]
base="https://www.ebi.ac.uk/europepmc/webservices/rest/"
qq=[dict(query=q,route="EuropePMC_keyword_search",database="EuropePMC",url=base+"search?"+urllib.parse.urlencode(dict(query=q,format="json",resultType="core",pageSize=100))) for q in queries]
q="flavone C glycosyltransferase GtUF6CGT1 UGT708D1 chrysin acacetin substrate specificity";qq.append(dict(query=q,route="Crossref_bibliographic_search",database="Crossref",url="https://api.crossref.org/works?"+urllib.parse.urlencode({"query.bibliographic":q,"rows":80})))
qq.append(dict(query="forward citations of original WjGT1 bioconversion MED/34302563",route="EuropePMC_citation_chase",database="EuropePMC",url=base+"MED/34302563/citations?"+urllib.parse.urlencode(dict(format="json",pageSize=100))))
for i,q in enumerate(qq):q.update(query_id=f"C-E01-R3-Q{i+1:02d}",family="C",scope_id="C-E01-scope-bank-v1",reason="additional distinct source closure scouting after lawful attachment transport failures; source evidence review allowed, fresh admission remains paused",max_pages=1,max_objects=100)
def plan(n):
 if n!=3:raise ValueError("this namespace is R3 only")
 return dict(task="TASK-016-P7",epoch_id="C-E01",round_id="C-R3",queries=qq,preregistered_at=s.now(),scope_semantic_review_pending=True,fresh_admission_paused=True,scope_build_or_change=False,donor_context_cannot_be_inferred_from_enzyme_name=True)
if __name__=="__main__":
 s.query_plan=plan
 if sys.argv[1]=="round":s.discovery_round(3)
 elif sys.argv[1]=="resolve":s.resolve_hints(3)
 elif sys.argv[1]=="acquire":s.acquire_selected(3)

"""A3 PMC13564134 official original publication front identity and text evidence index.
No chemistry structure qualification; previous web snippet scientific exposure is recorded.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys
from lxml import etree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain
T='TASK-016-P7';B=Path('outputs/task016-p7/v1');OUT=B/'prospective_G6_round_20261011_v1'
RAW=Path('data/raw/task016-p7/prospective_G6_round_20261011_v1/PMC13564134.original_JATS_XML')
G5=OUT/'C-PMC13564134/stages/G5_FRESH_HOLDOUT_ACQUIRE.json'
def main():
 assert verify_stage_chain(ROOT/G5,sha_file(ROOT/G5))['stage']=='G5_FRESH_HOLDOUT_ACQUIRE'
 b=(ROOT/RAW).read_bytes()
 root=etree.fromstring(b,etree.XMLParser(resolve_entities=False,no_network=True))
 ids={i.get('pub-id-type'):''.join(i.itertext()).strip() for i in root.xpath('.//front//article-id')}
 title=' '.join(''.join(root.xpath('.//front//article-title')[0].itertext()).split())
 journal=' '.join(''.join(root.xpath('.//front//journal-title')[0].itertext()).split())
 publisher=' '.join(''.join(root.xpath('.//front//publisher-name')[0].itertext()).split())
 assert ids['doi']=='10.1016/j.abiote.2026.100085' and ids['pmcid']=='PMC13564134'
 assert 'isoorientin' in title.lower() and journal.lower()=='abiotech'
 text=' '.join(''.join(root.xpath('.//front//abstract')[0].itertext()).split())
 evidence=[]
 for sec in root.xpath('.//body//sec'):
  titles=sec.xpath('./title');section=' '.join(''.join(titles[0].itertext()).split()) if titles else 'untitled'
  for p in sec.xpath('./p|./fig/caption'):
   s=' '.join(''.join(p.itertext()).split())
   if any(k in s.lower() for k in ('6-c-glycosyltransferase','gycgt1','isoorientin biosynthesis')):
    evidence.append({'section':section,'paragraph':s[:900],
      'paragraph_sha256':hashlib.sha256(s.encode()).hexdigest(),'topic_only_not_graph':True})
 rec={'task':T,'timestamp':datetime.now(timezone.utc).isoformat(),
 'agent_role':'A3','epoch_id':'C-E02','original_sha256':sha_file(ROOT/RAW),
 'G5_manifest_sha256':sha_file(ROOT/G5),
 'official_PMCID':ids['pmcid'],'official_PMID':ids.get('pmid'),'official_DOI':ids['doi'],
 'title':title,'journal':journal,'publisher':publisher,
 'identity_verified':True,'publication_year':2026,
 'original_science_read_after_immutable_G5':True,
 'web_search_external_snippet_read_after_G5_metadata_but_prior_to_this_A3':True,
 'scientific_source_content_now_exposed_to_current_epoch':True,
 'prior_target_name_exposure_unknown_requires_closure':True,
 'original_article_DOI_vs_original_XML_and_PMCIDs_consistent':True,
 'candidate_source_only_not_reaction_identity':True,
 'source_claim_location_index':evidence[:12],'claim_count':len(evidence),
 'full_structure_evidence_verified':False,'fresh_admitted':False}
 out=OUT/'C_PMC13564134_A3_original_front_and_exposure.json'
 if (ROOT/out).exists():raise RuntimeError('immutable already exists')
 write(T,str(out),json.dumps(rec,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 event(T,'C_PMC13564134_A3_verified_original',source_sha256=rec['original_sha256'],
       DOI=ids['doi'],PMCID=ids['pmcid'],fresh_admitted=False)
 print(json.dumps({'A3_identity_pass':True,'DOI':ids['doi'],'PMCID':ids['pmcid'],
   'cited_body_claim_locations':len(evidence),'output':str(out)},ensure_ascii=False))
if __name__=='__main__':main()

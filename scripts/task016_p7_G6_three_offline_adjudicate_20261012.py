"""Offline formal A6 NAME-only exposure ruling + source10 SI binding + source14 linkage adjudication.
Historical evidence is classified at its actual granularity, never rewritten as a fresh pass.
"""
from __future__ import annotations
import hashlib,json,subprocess,re,datetime,sys
from pathlib import Path
from lxml import html
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
T='TASK-016-P7';B=Path('outputs/task016-p7/v1');O=B/'G6_three_decisions_20261012_v1'
PRE=O/'three_workstreams_precontract.json'
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def dsha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(name,x):
 p=O/name
 if (ROOT/p).exists():raise RuntimeError('immutable already exists '+str(p))
 write(T,str(p),json.dumps(x,sort_keys=True,ensure_ascii=False,indent=2)+'\n')
 return str(p)
def main():
 plan=json.loads((ROOT/PRE).read_text())
 for r in plan['inputs'].values():assert sha(Path(r['path']))==r['sha256'],r['path']
 namefiles=[Path(plan['inputs'][k]['path']) for k in ('A6_prior_exposure','A6_prior_exposure_v2','A6_prior_exposure_effective')]
 exposures=[];distinct={}
 for p in namefiles:
  batch=[]
  for i,line in enumerate((ROOT/p).read_text().splitlines(),1):
   x=json.loads(line)
   tokens=x.get('closure_tokens',[])
   if 'partial-target-name:isoorientin' not in tokens:continue
   digest=dsha(x)
   entry={'file':str(p),'line':i,'file_sha256':sha(p),'record_sha256':digest,
     'exposure_id':x.get('exposure_id'),'entity_kind':x.get('entity_kind'),
     'source_DOI':x.get('doi'),'reported_exposure_type':x.get('exposure_type'),
     'source_family':x.get('family'),'source_name':x.get('partial_target_source_name'),
     'source_assay':x.get('assay_id'),'source_assay_level':'biological endpoint grouped analyte, not isolated target',
     'graph':x.get('target_graph'),'site':x.get('site'),'site_claim':x.get('site_claim'),
     'reaction_signature':x.get('reaction_signature'),'reaction_id':x.get('reaction_id'),
     'acceptor_graph':x.get('acceptor_smiles'),'product_graph':x.get('product_smiles'),
     'donor_graph':x.get('donor_smiles'),'actual_first_review_at':x.get('first_actual_chemical_review_at'),
     'chemical_exposure_claimed_but_without_target_graph':bool(x.get('development_exposed'))}
   assert all(entry[k] is None for k in ['graph','site','site_claim','reaction_signature',
    'reaction_id','acceptor_graph','product_graph','donor_graph'])
   assert x.get('entity_kind')=='biological_endpoint'
   batch.append(entry);distinct.setdefault(digest,entry)
  assert len(batch)==12,(str(p),len(batch))
  exposures+=batch
 assert len(exposures)==36 and len(distinct)==12
 # Actual source (Buckwheat Table3) is a composite analyte list, not product-isoorientin-specific structure/site.
 original_path=Path('outputs/task016-p7/v1/SS/fresh_buckwheat2018_A4_Table3_all_cells.jsonl')
 orig=[];origbytes=(ROOT/original_path).read_text()
 for l in origbytes.splitlines():
  try:x=json.loads(l)
  except:continue
  if 'isoorientin' in l.lower():orig.append(x)
 assert orig
 ruling={'task':T,'at':now(),'role':'A6','decision_id':'A6-ISOORIENTIN-NAME-EXPOSURE-20261012',
  'decision_scope':'ONLY pre-G4 name token exposure recorded in SS-E01 Buckwheat2018 grouped analyte',
  'decision':'NAME_ONLY_IS_NOT_STRUCTURE_SITE_REACTION_LEAKAGE',
  'name_token_automatic_fresh_rejection':False,
  'name_token_automatic_fresh_admission':False,
  'historical_source_group_itself_remains_exposed':True,
  'source_claim':'C-glucosylflavones total analyte group, including alternative analyte names',
  'distinct_exposure_records':12,'original_line_instances':36,
  'original_physical_line_bindings':exposures,
  'origin_review_file':str(original_path),'origin_review_sha256':hashlib.sha256(origbytes.encode()).hexdigest(),
  'origin_review_records_with_name':len(orig),
  'full_graph_site_reaction_fields_non_null':0,
  'A6_scope_exposure_from_this_name_token_proven':False,
  'same_exact_target_graph_closure_proven':False,
  'full_A6_reaction_source_assay_cohort_closure_proven':False,
  'PMC13564134_fresh_status':'DEFERRED_FOR_COMPLETE_FULL_GRAPH_AND_REACTION_COHORT_CLOSURE',
  'permanent_prior_name_record_preserved':True,'this_epoch_original_science_read_exposed':True,
  'human_reviewed':False,'no_prior_file_mutated':True,
  'corrects_old_A6_36_distinct_overcount_to_12':True,
  'corrects_old_A6_invalid_line_pointers':True}
 a6=save('A6_isoorientin_name_only_formal_ruling.json',ruling)
 print('A6',len(distinct),'distinct',len(exposures),'instances','ruling',ruling['decision'])
 # Item10: check original already-preserved NCBI PMC page bibliographic DOI/title and official SI anchor.
 pmc=Path(plan['inputs']['Iris_official_PMC_HTML']['path']);h=(ROOT/pmc).read_text()
 dom=html.fromstring(h)
 doi=dom.xpath('//meta[@name="citation_doi"]/@content')
 title=dom.xpath('//meta[@name="citation_title"]/@content')
 links=dom.xpath('//a[contains(@href,"CBIC-27-e70486-s001.pdf")]/@href')
 assert doi==['10.1002/cbic.70486'] and len(title)==1 and len(links)>=1
 assert 'UGT707B2' in title[0] and 'Iris' in title[0]
 assets=Path(plan['inputs']['Iris_official_SI_advertised_plan']['path'])
 assetplan=json.loads((ROOT/assets).read_text())
 official='https://pmc.ncbi.nlm.nih.gov/articles/instance/13422134/bin/CBIC-27-e70486-s001.pdf'
 assert official in assetplan['advertised_SI_links']
 assert any('CBIC-27-e70486-s001.pdf' in x for x in links)
 owner=Path(plan['inputs']['Iris_owner_SI']['path'])
 pdftxt=subprocess.run(['pdftotext','-layout',str(ROOT/owner),'-'],capture_output=True,text=True,check=True).stdout
 assert 'UGT707B2' in pdftxt and 'Iris tectorum' in pdftxt
 assert 'Fig. S1' in pdftxt and 'Fig. S6' in pdftxt and 'Table S3' in pdftxt
 report10={'task':T,'role':'A3_A6','at':now(),'number':'10','family':'C',
  'DOI':'10.1002/cbic.70486','official_PMCID':'PMC13422134',
  'official_citation_DOI_confirmed':True,'official_main_article_title':title[0],
  'original_official_PMC_page_path':str(pmc),'main_article_archive_sha256':sha(pmc),
  'official_exposed_supplementary_relative_hrefs':sorted(set(links)),
  'official_full_SI_URL':official,'official_asset_preplan_path':str(assets),
  'official_asset_preplan_sha256':sha(assets),
  'owner_SI_path':str(owner),'owner_SI_SHA256':sha(owner),
  'owner_SI_title':'Cloning and functional analysis of a new glycosyltransferase UGT707B2 from Iris tectorum Maxim.',
  'owner_SI_FigS1_to_FigS6_and_TableS3_confirmed':True,
  'publication_family_SI_attachment_mapping':'HIGH_CONFIDENCE_CONFIRMED',
  'publication_linkage_supported_by':['official_citation_DOI_title',
    'official_PMC_main_article_explicit_SI_href',
    'cached_advertised_original_SI_url','SI_internal_UGT707B2_Iris_title_figures'],
  'owner_SI_exact_binary_equality_to_official_download':'NOT_PROVEN_official_SI_download_cache_is_recaptcha_HTML',
  'official_SI_original_pdf_source_SHA_verifiable':False,
  'site_C6_graph_qualified':False,'fresh_reaction_admitted':False,
  'remaining_gap':'no official SI bytes to perform byte-exact attachment identity; structural C6 proof not established',
  'source_family':'paper_group_bound_but_binary_authenticity_not_proven',
  'current_immutable_custody_not_modified':True}
 p10=save('source10_Iris_SI_to_main_original_linkage_ruling.json',report10)
 print('10 SI association:',report10['publication_family_SI_attachment_mapping'],'official DOI=',doi[0])
 # Item14: DOI PDF all page text and absence of atom-level linkage claim
 pea=Path(plan['inputs']['Pea_original_PDF']['path'])
 pdftext=subprocess.run(['pdftotext','-layout',str(ROOT/pea),'-'],capture_output=True,text=True,check=True).stdout
 pages=[x for x in pdftext.split('\f') if x.strip()]
 assert len(pages)==4
 signals=['kaempferol-3-monoglucoside','kaempferol-3-diglucoside','3-triglucoside','UDP']
 loci=[]
 for si,pg in enumerate(pages,1):
  for term in signals:
   pattern=re.escape(term).replace('\\-','[-\\s]*')
   mo=re.search(pattern,pg,re.I)
   if mo:
    loci.append({'page':si,'text_SHA256':hashlib.sha256(pg.encode()).hexdigest(),
     'needle':term,'snippet':' '.join(pg[max(0,mo.start()-115):mo.end()+210].split())[:390]})
 assert len(loci)>=3
 has_specific=bool(re.search(r'(?:1\s*[→=>-]\s*2|2\s*[-’′]*O[- ]glucosyl|sugar.{0,65}O.?2|O.?2.{0,65}sugar)',pdftext,re.I))
 # 1->2 raw may be text mention in paper citations, manually inspect if present.
 report14={'task':T,'at':now(),'role':'A6','number':'14','family':'SS',
   'DOI':'10.1515/znc-1979-9-1014',
   'original_source':str(pea),'original_sha256':sha(pea),
   'original_pages':4,'real_text_anchors':loci[:12],
   'experiment_supported':'UDP-glucose-dependent kaempferol/quercetin 3-O mono/diglucoside to triglucoside pathways using crude plant extracts',
   'site_inner_sugar_O2_source_confirmed':False,
   'sugar_stereo_and_glycosidic_linkage_1_to_2_confirmed':False,
   'complete_atom_mapped_acceptor_product_UDP_glucose_reference':False,
   'observed_text_potential_O2_regex':has_specific,
   'decision':'DEFERRED_NOT_ESTABLISHED_IN_ORIGINAL_1979_PDF',
   'scope_SS_O2_pass':False,
   'chemical_rejection_of_all_article_reactions':False,
   'reason':'compound class and substitution degree do not uniquely define which glucose hydroxyl receives the new glucosyl group',
   'further_old_reference_figures_may_be_needed':'paper references structural isolation studies; would require independent source provenance and new evidence',
   'historical_exposure':True,'fresh_reaction_admitted':False}
 p14=save('source14_Pisum_inner_sugar_O2_original_ruling.json',report14)
 print('14 O2 proven:',report14['site_inner_sugar_O2_source_confirmed'],'possible regex',has_specific)
 event(T,'three_G6_A6_and_historical_source_decisions_recorded',A6_sha=sha(Path(a6)),SI_sha=sha(Path(p10)),
   Pea_sha=sha(Path(p14)),fresh=0)
if __name__=='__main__':main()

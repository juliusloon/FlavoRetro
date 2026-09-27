"""Browser verification with synthetic annotations in an isolated context only."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from playwright.sync_api import sync_playwright
from scripts.operate import write,event
p=argparse.ArgumentParser();p.add_argument('--cards',default='outputs/review/task015-v2/index.html');p.add_argument('--output',default='outputs/validation/task015-cards');a=p.parse_args()
out=Path(a.output);out.mkdir(parents=True,exist_ok=False);errors=[];checks={}
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True);context=browser.new_context(accept_downloads=True);page=context.new_page();page.set_viewport_size({'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(Path(a.cards).resolve().as_uri());page.wait_for_selector('article',timeout=10000)
 assert page.locator('article').count()==1
 checks['initial_blank']=page.locator('#progress').inner_text()=='0 / 60 已填写';assert checks['initial_blank']
 checks['all_cards_and_input']=page.evaluate('records.length===60&&records.every(r=>Object.values(r.annotation).every(x=>x===null)&&r.production_eligible===false)');assert checks['all_cards_and_input']
 assert page.evaluate('document.querySelectorAll(".molecule svg").length>0')
 page.locator('#filter').select_option('glycoside');assert page.locator('#position').inner_text()=='当前 1 / 30';checks['glycoside_filter']=True
 page.locator('#next').click();assert page.locator('#position').inner_text()=='当前 2 / 30';page.locator('#prev').click()
 # Partial annotation is a draft, not a primary review. No artificial reviewer or date.
 page.locator('#domain_relevance').select_option('uncertain');page.locator('#decision').select_option('retain_candidate');page.locator('#disagreement').fill('BROWSER TEST FIXTURE — not a human chemistry review');page.locator('button[type=submit]').click()
 assert page.locator('#progress').inner_text()=='1 / 60 已填写'
 page.reload();page.wait_for_selector('article');page.locator('#filter').select_option('glycoside');assert page.locator('#disagreement').input_value().startswith('BROWSER TEST FIXTURE');checks['draft_persisted']=True
 with page.expect_download() as d:page.locator('#export').click()
 d.value.save_as(str(out/'fixture-export.json'));export=json.loads((out/'fixture-export.json').read_text());annotated=[r for r in export['records'] if r['annotation']['decision']];assert len(annotated)==1;assert annotated[0]['annotation']['reviewer_id'] is None;assert annotated[0]['annotation']['reviewed_at'] is None;assert export['production_eligible'] is False;checks['export_unvalidated']=True
 # Validate complete identity binding and atomic rejection of invalid input.
 bad=json.loads(json.dumps(export));bad['input_sha256']='bad';write('TASK-015',str(out/'fixture-wrong-input.json'),json.dumps(bad));page.locator('#import').set_input_files(str(out/'fixture-wrong-input.json'));page.wait_for_function('document.querySelector("#status").textContent.includes("导入失败")');assert page.locator('#progress').inner_text()=='1 / 60 已填写';checks['wrong_input_rejected']=True
 bad=json.loads(json.dumps(export));bad['records'][0]['source_sha256']='bad';write('TASK-015',str(out/'fixture-wrong-source.json'),json.dumps(bad));page.locator('#import').set_input_files(str(out/'fixture-wrong-source.json'));page.wait_for_function('document.querySelector("#status").textContent.includes("来源不一致")');checks['wrong_source_rejected']=True
 bad=json.loads(json.dumps(export));bad['records'][0]['annotation']['decision']='primary_checked';write('TASK-015',str(out/'fixture-incomplete-primary.json'),json.dumps(bad));page.locator('#import').set_input_files(str(out/'fixture-incomplete-primary.json'));page.wait_for_function('document.querySelector("#status").textContent.includes("原文已核对需")');checks['incomplete_primary_rejected']=True
 context2=browser.new_context(accept_downloads=True);other=context2.new_page();other.goto(Path(a.cards).resolve().as_uri());other.wait_for_selector('article');assert other.locator('#progress').inner_text()=='0 / 60 已填写';other.locator('#import').set_input_files(str(out/'fixture-export.json'));other.wait_for_function('document.querySelector("#status").textContent.includes("已导入")');assert other.locator('#progress').inner_text()=='1 / 60 已填写';checks['valid_import']=True
 # Browser storage denial must preserve editable state and a working JSON backup.
 denied_context=browser.new_context(accept_downloads=True);denied=denied_context.new_page();denied.goto(Path(a.cards).resolve().as_uri());denied.wait_for_selector('article')
 denied.evaluate("() => { Storage.prototype.setItem=()=>{throw new Error('fixture storage denied')}; }")
 denied.locator('#domain_relevance').select_option('uncertain');denied.locator('#decision').select_option('retain_candidate');denied.locator('button[type=submit]').click()
 assert denied.locator('#progress').inner_text()=='1 / 60 已填写';assert '仍在本页内存' in denied.locator('#status').inner_text()
 with denied.expect_download() as d:denied.locator('#export').click()
 d.value.save_as(str(out/'fixture-storage-denied-export.json'));backup=json.loads((out/'fixture-storage-denied-export.json').read_text());assert backup['records'][0]['annotation']['domain_relevance']=='uncertain';checks['storage_denied_backup_preserved']=True
 # Exporting HTML/source strings cannot inject script elements; structures only generated SVG.
 assert page.evaluate('document.querySelectorAll("script").length===2');checks['script_delimiters_safe']=True
 pristine=browser.new_context().new_page();pristine.goto(Path(a.cards).resolve().as_uri());pristine.wait_for_selector('article');page=pristine;page.set_viewport_size({'width':1440,'height':1000});page.screenshot(path=str(out/'desktop.png'),full_page=True)
 checks['overflow']={}
 for width,height in [(1440,1000),(390,844),(320,740)]:
  page.set_viewport_size({'width':width,'height':height});overflow=page.evaluate('document.documentElement.scrollWidth>innerWidth');checks['overflow'][str(width)]=overflow;assert not overflow
 page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(out/'mobile.png'),full_page=True)
 # Loop all 60 cards including incomplete/generic cases; drawing and form remain usable.
 for index in range(60):
  assert page.locator('article').count()==1
  if index<59:page.locator('#next').click()
 checks['all_60_rendered']=True
 assert not errors,errors;browser.close()
checks['javascript_errors']=errors;checks['fixture_only']='isolated browser contexts; artificial drafts are not project annotations'
write('TASK-015',str(out/'checks.json'),json.dumps(checks,ensure_ascii=False,indent=2)+'\n');event('TASK-015','review_cards_browser_verified',output=str(out),checks=checks);print(json.dumps(checks,ensure_ascii=False))

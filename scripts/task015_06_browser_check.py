"""Actual Chromium desktop/mobile checks; search payloads are browser-only fixtures."""
import copy,json,sys,threading
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
from flavoretro.web import Handler
from flavoretro.workspace import root
from flavoretro.reviewed_resources import load_review,row_signature
from flavoretro.worker import annotate
from flavoretro.resources import dumps,sha

out=root()/'outputs/validation/task015-06-browser-v4';out.mkdir(exist_ok=True)
runtime=json.loads((root()/'outputs/validation/task015-06-runtime.json').read_text())
cell=next(c for c in runtime['cells'] if c['view']=='adjudicated' and c['status']=='ok')
fixture=json.loads((root()/'outputs/runs'/cell['run_id']/'result.json').read_text())
view=load_review(); rows=json.loads((root()/'data/derived/v3/records.json').read_text())
source=next(r for r in rows if view.record(r['id']).get('positive_source_support') and len(row_signature(r).split('>>')[1].split('.'))==1)
left,right=row_signature(source).split('>>');precursors=left.split('.')
tree={'type':'mol','smiles':right,'children':[{'type':'reaction','metadata':{'classification':'0.0 Unrecognized','policy_name':'browser_fixture_only'},'children':[{'type':'mol','smiles':s,'in_stock':False,'children':[]} for s in precursors]}]}
annotate(tree,False,view)
fixture['run_id']='20261005T000000-'+'a'*32;fixture['execution_source']='BROWSER TEST ONLY';fixture['limitations']=['BROWSER TEST ONLY; not a live prediction or user review']
fixture['candidate_count']=1;fixture['routes']=[{'route_id':'a'*64,'tree':tree,'steps':1,'closure':'partial','evidence_closed':False,'actionable':False,'score':1+2*len(precursors),'score_status':'provisional_cost_lower_is_better','cost':{'steps':1,'unresolved_materials':len(precursors),'known_hazards':0,'unspecified_leaf_stereo':0}}]
old=copy.deepcopy(fixture);old['run_id']='20261005T000000-'+'b'*32;old.pop('review_binding',None)
def remove_review(node):
    node.pop('review',None);node.get('metadata',{}).pop('review',None)
    for child in node.get('children',[]):remove_review(child)
remove_review(old['routes'][0]['tree'])
(out/'fixture.json').write_text(dumps(fixture))
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
base='http://127.0.0.1:'+str(server.server_address[1]);checks=[];errors=[]
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        for width,height in [(1440,1000),(390,844)]:
            context=browser.new_context(viewport={'width':width,'height':height},accept_downloads=True)
            page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            state={'fail':False}
            def search_route(route):
                if state['fail']:route.fulfill(status=503,content_type='application/json',body=dumps({'message':'review_manifest_integrity_failed (browser fixture)'}))
                else:route.fulfill(status=200,content_type='application/json',body=dumps(fixture))
            def saved_route(route):
                data=old if route.request.url.endswith(old['run_id']) else fixture
                route.fulfill(status=200,content_type='application/json',body=dumps({'execution_source':'explicit_saved_run','integrity':'verified','manifest':{'run_id':data['run_id'],'scope':'BROWSER TEST ONLY','files':{'result.json':__import__('hashlib').sha256(dumps(data).encode()).hexdigest()}},'result':data}))
            page.route('**/api/search',search_route);page.route('**/api/runs/*',saved_route)
            page.goto(base,wait_until='networkidle')
            page.locator('#smiles').fill(right);page.locator('#submit').click()
            page.locator('#routes').get_by_text('该结构变换有指定原文实例支持；本次预测条件与可行性未确认。').wait_for()
            checks.append({'viewport':width,'positive_instance_display':True})
            page.locator('.step-card details').first.locator('summary').click()
            page.locator('.step-card').first.screenshot(path=str(out/f'step-{width}.png'))
            checks.append({'viewport':width,'expanded_step_no_overflow':page.evaluate('document.documentElement.scrollWidth <= innerWidth')})
            with page.expect_download() as download:page.locator('#download').click()
            file=download.value;file.save_as(str(out/f'export-{width}.json'))
            exported=json.loads((out/f'export-{width}.json').read_text())
            assert exported['result']['review_binding']==fixture['review_binding']
            checks.append({'viewport':width,'export_review_matches':True})
            for tab in ['resources','literature','governance','search']:
                page.locator(f'[data-tab="{tab}"]').click();page.wait_for_timeout(150)
                checks.append({'viewport':width,'tab':tab,'no_overflow':page.evaluate('document.documentElement.scrollWidth <= innerWidth')})
            page.locator('[data-tab="resources"]').click();page.locator('#kind').select_option('stock');page.locator('#query').fill('TBSCl');page.locator('#find').click()
            page.wait_for_function("document.getElementById('count').textContent.includes('共 1 条')")
            page.locator('#rows details summary').first.click()
            page.locator('#rows').get_by_text('名称与结构错配 · 隔离').wait_for()
            page.locator('#rows button').first.click()
            page.wait_for_function("document.getElementById('record-json').textContent.includes('quarantine_name_structure_mismatch')")
            checks.append({'viewport':width,'real_resource_quarantine_visible':True,'resource_detail_no_overflow':page.evaluate('document.documentElement.scrollWidth <= innerWidth')})
            page.screenshot(path=str(out/f'resources-{width}.png'))
            page.locator('[data-tab="governance"]').click();page.locator('#saved-run-id').fill(old['run_id']);page.locator('#open-run').click()
            page.locator('#routes').get_by_text('历史运行未记录审核视图').first.wait_for()
            checks.append({'viewport':width,'old_history_missing_review_explicit':True})
            state['fail']=True;page.locator('#submit').click();page.locator('#message').get_by_text('review_manifest_integrity_failed',exact=False).wait_for()
            checks.append({'viewport':width,'review_failure_visible':True})
            context.close()
        browser.close()
finally:
    server.shutdown();server.server_close();thread.join()
    (out/'partial-report.json').write_text(dumps({'checks':checks,'js_errors':errors,'scope':'BROWSER TEST ONLY'}))
report={'checks':checks,'js_errors':errors,'scope':'BROWSER TEST ONLY; not a user review; source-step/search/history/error fixtures plus real read-only resource API'}
(out/'report.json').write_text(dumps(report));print(dumps(report))
assert not errors and all(v is True for c in checks for k,v in c.items() if k.endswith('overflow') or k.endswith('visible') or k.endswith('display') or k.endswith('matches') or k.endswith('explicit'))

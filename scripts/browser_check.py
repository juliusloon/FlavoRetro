import json,subprocess,time,urllib.request,uuid
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from playwright.sync_api import sync_playwright
from flavoretro.resources import ROOT,dumps
out=ROOT/'outputs/validation'/('browser-'+uuid.uuid4().hex[:8]);out.mkdir(parents=True,exist_ok=False)
log=(out/'server.log').open('w')
server=subprocess.Popen([str(ROOT/'.venv/bin/python'),'-B','-m','flavoretro.web','--port','8876'],cwd=ROOT,stdout=log,stderr=log)
try:
    for _ in range(50):
        try:
            urllib.request.urlopen('http://127.0.0.1:8876/api/health');break
        except Exception:time.sleep(.2)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8876');page.wait_for_selector('#preset option:nth-child(2)',state='attached')
        page.locator('#smiles').fill('CCOc1ccccc1');page.locator('#mode').select_option('balanced');page.locator('#search-form details').click();page.locator('#seconds').fill('1');page.locator('#iterations').fill('3');page.locator('#submit').click()
        page.wait_for_function("document.getElementById('message').textContent.includes('本次实时搜索完成')",timeout=120000)
        assert '阶段 2' in page.locator('#run-meta').inner_text()
        assert page.locator('.route').count()>0
        page.screenshot(path=str(out/'desktop.png'),full_page=True)
        page.locator('[data-tab=resources]').click();page.locator('#kind').select_option('stock');page.wait_for_function("document.getElementById('count').textContent.includes('共 49 条')")
        page.locator('#rows button').first.click();assert 'source_sha256' in page.locator('#record-json').inner_text()
        page.locator('[data-tab=governance]').click();page.wait_for_selector('.stat');assert page.locator('.stat').count()==4
        page.set_viewport_size({'width':390,'height':844});page.locator('[data-tab=search]').click()
        overflow=page.evaluate('document.documentElement.scrollWidth > window.innerWidth')
        page.screenshot(path=str(out/'mobile.png'),full_page=True);assert not overflow
        invalid=page.request.post('http://127.0.0.1:8876/api/search',data=json.dumps({'smiles':'INVALID'}),headers={'Content-Type':'application/json'});assert invalid.status==400
        assert not errors,errors
        (out/'report.json').write_text(dumps({'browser':'Chromium','desktop':[1440,1000],'mobile':[390,844],'overflow':overflow,'js_errors':errors,'live_search':True,'two_phases':True,'resource_detail':True,'invalid_http_status':invalid.status,'scope':'local browser engineering acceptance, not human usability'}))
        browser.close()
    print((out/'report.json').read_text())
finally:
    server.terminate();server.wait(timeout=10);log.close()

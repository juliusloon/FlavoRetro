"""Real-browser cross-project QA, using an existing real run, no additional MCTS."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from scripts.operate import write

run=json.loads(Path('outputs/task029/search-response.json').read_text())
checks=[];errors=[];posts=[]
def ok(name,value):
    assert value,name
    checks.append(name)

def stored(page):
    return page.evaluate("JSON.parse(localStorage.getItem('flavoglycolab.workbench.v1')).current")

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    for width,height in [(1440,1000),(390,844)]:
        context=browser.new_context(viewport=dict(width=width,height=height),accept_downloads=True)
        page=context.new_page()
        def track(page):
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('request',lambda req:posts.append(req.url) if req.method=='POST' else None)
        track(page)
        page.goto('http://127.0.0.1:8767/?run='+run['run_id'])
        page.locator('#lab-development').wait_for(state='visible')
        ok(f'{width}: three classified development papers',page.locator('.lab-development-row').count()==3)
        scores=page.locator('.route-entry-meta').all_text_contents()
        import re
        values=[float(re.search(r'优先级 ([0-9.]+)',text)[1]) for text in scores]
        ok(f'{width}: descending routes',values==sorted(values,reverse=True))
        pei=page.locator('.lab-development-row').filter(has_text='主开发 · Pei')
        pei.get_by_role('button',name='查看对应候选').click()
        ok(f'{width}: Pei route selected without score override',page.locator('#route-tab-1').get_attribute('aria-selected')=='true')
        page.locator('details.source-realization > summary').first.click()
        ok(f'{width}: actual Pei DOI in route', '10.1007/s10600-019-02712-9' in page.locator('#routes').inner_text())
        ok(f'{width}: source labels and conditions are readable','双酶标准反应' in page.locator('#routes').inner_text() and 'not_isolated_yield' not in page.locator('#routes').inner_text() and 'T029:' not in page.locator('#routes').inner_text())
        page.locator('details.source-realization').first.scroll_into_view_if_needed()
        page.screenshot(path=f'/tmp/flavoretro-task029-{width}.png',full_page=False)
        with page.expect_download() as event:pei.get_by_role('button',name='导出交接包').click()
        downloaded=event.value
        packet=json.loads(Path(downloaded.path()).read_text())
        ok(f'{width}: export retains real run and three separate roles',packet['run']['id']==run['run_id'] and len(packet['literature'])==3 and packet['literature'][-1]['mcts_action'] is False)
        with page.expect_popup() as event:pei.get_by_role('button',name='进入 FlavoGlycoLab').click()
        lab=event.value;track(lab)
        lab.locator('#retro-import-dialog [data-retro-accept]').wait_for(state='visible')
        before=stored(lab)
        ok(f'{width}: received Pei and no automatic acceptance','Pei2019' in lab.locator('.retro-import-body').inner_text() and 'retroImport' not in before)
        lab.locator('[data-retro-accept]').click()
        lab.locator('.retro-source-card').wait_for()
        after=stored(lab)
        ok(f'{width}: accept preserves draft and gates',all(after[k]==before[k] for k in ['route','routeConfirmed','learning','plan','materials','stage','guidedDone','samples','operation']))
        ok(f'{width}: no observations or quantitative output',after['retroImport']['observations']==[] and after['retroImport']['quantitative_result'] is None and not after['retroImport']['teacher_approved'])
        ok(f'{width}: fragment payload cleared',lab.evaluate('location.hash')=='#/')
        lab.reload();lab.locator('.retro-source-card').wait_for()
        ok(f'{width}: computation survives reload',stored(lab)['retroImport']['packet']['run']['id']==run['run_id'])
        lab.get_by_role('button',name='阅读与比较三篇论文').click()
        lab.locator('#evidence-dialog').wait_for(state='visible')
        text=lab.locator('#evidence-dialog').inner_text()
        ok(f'{width}: three real papers in Lab matrix',all(s in text for s in ['Pei','Zhang','Niu']))
        ok(f'{width}: import reading cannot bypass intro',lab.locator('[data-choose-route=R1]').is_disabled())
        lab.locator('[data-open-paper=Pei2019]').click()
        lab.wait_for_function("()=>document.querySelector('[data-paper-view=Pei2019] iframe').getAttribute('src')?.includes('/api/paper/Pei2019')")
        ok(f'{width}: first paper PDF opens via own verified endpoint',lab.request.get('http://127.0.0.1:8766/api/paper/Pei2019').body().startswith(b'%PDF-'))
        lab.locator('#evidence-dialog [data-close-dialog]').click()
        lab.screenshot(path=f'/tmp/flavoglycolab-task035-{width}.png',full_page=False)
        ok(f'{width}: no horizontal page overflow',lab.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
        ok(f'{width}: mobile navigation keeps words horizontal',lab.locator('#retro-import-button').evaluate('(el)=>el.getBoundingClientRect().height<40'))
        # Complete the existing intro through real interactions, then choose the main case.
        lab.locator('button[data-act="1"][data-choice="a"]').click()
        lab.locator('[data-action=intro-advance]').click()
        lab.locator('button[data-act="2"][data-choice="b"]').click()
        lab.locator('[data-action=intro-advance]').click()
        lab.locator('[data-case=R1]').first.click()
        lab.locator('[data-choose-route=R1]').click()
        ok(f'{width}: Pei is the chosen development case after normal intro',stored(lab)['route']=='R1' and stored(lab)['exploration']['routeChosen'] is True)
        ok(f'{width}: choosing paper grants no learned answers',not stored(lab)['learning']['entries'])
        # File import preserves existing accepted packet when a damaged file is rejected.
        lab.locator('#retro-import-button').click()
        lab.locator('#retro-import-dialog input[type=file]').set_input_files(dict(name='damaged.json',mimeType='application/json',buffer=b'{}'))
        lab.wait_for_function("()=>document.querySelector('#retro-import-dialog [role=status]').textContent.includes('失败')")
        ok(f'{width}: malformed packet rejected',lab.locator('[data-retro-accept]').is_hidden() and stored(lab)['retroImport']['packet']['run']['id']==run['run_id'])
        # A self-contained downloaded packet is also usable without the URL handoff.
        lab.locator('#retro-import-dialog input[type=file]').set_input_files(dict(name='handoff.json',mimeType='application/json',buffer=json.dumps(packet).encode()))
        lab.locator('[data-retro-accept]').wait_for(state='visible')
        lab.locator('[data-retro-close]').click()
        ok(f'{width}: explicit file import independently validates',not lab.locator('#retro-import-dialog').is_visible())
        visible=lab.locator('body').inner_text()
        ok(f'{width}: raw audit IDs and wall time stay out of product text',run['run_id'] not in visible and '墙钟' not in visible and 'packet_sha256' not in visible)
        with lab.expect_popup() as event:lab.get_by_role('link',name='查看原始候选').click()
        back=event.value;track(back);back.locator('#lab-development').wait_for(state='visible')
        ok(f'{width}: trace returns to saved original run',run['run_id'] in back.url)
        context.close()
    ok('no browser exceptions',not errors)
    ok('browser never starts another MCTS',not any('/api/search' in u for u in posts))
    browser.close()
write('TASK-029','outputs/task029/browser.json',json.dumps(dict(checks=checks,passed=len(checks),errors=errors,posts=posts),ensure_ascii=False,indent=2))
print(json.dumps(dict(passed=len(checks),errors=errors,post_count=len(posts))))

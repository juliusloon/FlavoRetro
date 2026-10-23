"""Read-only browser regression for the modular workbench and shared components.

Requires the existing optional Playwright environment and a running service.
Blocks every non-GET request; never starts MCTS. Screenshots/reports are opt-in.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base',default='http://127.0.0.1:8767/')
    parser.add_argument('--output',type=Path)
    parser.add_argument('--screenshots',type=Path)
    parser.add_argument('--task',required=True)
    args=parser.parse_args(argv);base=args.base.rstrip('/')+'/'
    checks=[];errors=[];blocked=[];shots=[]
    run_dir=ROOT/'outputs/runs';before=sorted(p.name for p in run_dir.iterdir()) if run_dir.exists() else None
    def check(name,value):
        if not value:raise AssertionError(name)
        checks.append({'name':name,'pass':True})
    def ready(page):page.wait_for_function('navigationReady && history.state?.flavoretro===true')
    def goto(page,path):page.goto(base+path);ready(page)
    def no_overflow(page):return page.evaluate('document.documentElement.scrollWidth<=innerWidth+1 && document.querySelector(".page:not([hidden])").scrollWidth<=document.querySelector(".page:not([hidden])").clientWidth+1')
    def shot(page,name):
        if args.screenshots:
            args.screenshots.mkdir(parents=True,exist_ok=True);path=args.screenshots/name;page.screenshot(path=str(path));shots.append(str(path))
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True)
            for width,height in [(1440,1000),(768,1024),(390,844),(320,844)]:
                prefix=f'{width}: ';context=browser.new_context(viewport={'width':width,'height':height});page=context.new_page();page.set_default_timeout(10000)
                page.on('pageerror',lambda error:errors.append(str(error)))
                page.on('console',lambda msg:errors.append(msg.type+': '+msg.text) if msg.type in ['error','warning'] else None)
                def guard(route):
                    if route.request.method!='GET':blocked.append(route.request.url);route.abort()
                    else:route.continue_()
                page.route('**/api/**',guard)
                goto(page,'#/search')
                check(prefix+'页面身份/非空/无遮罩','路线探索' in page.title() and page.locator('#search-intro').is_visible() and page.locator('vite-error-overlay,nextjs-portal').count()==0)
                check(prefix+'五主入口与无面包屑',page.locator('[data-tab]').count()==5 and page.locator('#page-breadcrumb,.page-location').count()==0)
                check(prefix+'真实公共组件已挂载',page.evaluate('pagination===FlavoUI.pagination && text===FlavoUI.text && typeof FlavoPages.load==="function"') and page.locator('#smiles.ui-input').count()==1)
                check(prefix+'控件最小高度统一',page.locator('#mode').bounding_box()['height']>=43)
                page.locator('#smiles').fill('CCOc1ccccc1');page.locator('#search-advanced').evaluate('(el)=>el.open=true');page.locator('#reset-budget').click();page.locator('#seconds').fill('79')
                page.locator('#tab-history').click();page.wait_for_selector('#run-list button');page.reload();ready(page);page.locator('#tab-search').click();page.wait_for_selector('#search:visible')
                check(prefix+'草稿与显式预算保留',page.locator('#smiles').input_value()=='CCOc1ccccc1' and page.locator('#seconds').input_value()=='79' and page.evaluate('budgetOverrides.has("seconds")'))
                page.locator('#tab-history').click();page.wait_for_selector('#run-list button');check(prefix+'历史使用共享分页/表格',page.locator('#runs-pager-top.ui-pagination').count()==1 and page.locator('.history-table.ui-table').count()==1)
                values=page.locator('#compare-run-a option').evaluate_all('(options)=>options.map(o=>o.value).filter(Boolean)')
                if len(values)>1:
                    page.locator('#compare-run-a').select_option(values[0]);page.locator('#compare-run-b').select_option(values[1]);page.locator('#run-comparison').click();page.wait_for_selector('#export-comparison:enabled')
                    check(prefix+'只读运行对照保持',bool(page.locator('#comparison-table').inner_text()) and 'a=' in page.url and 'b=' in page.url)
                    page.reload();ready(page);page.wait_for_selector('#export-comparison:enabled');check(prefix+'对照刷新恢复',page.locator('#compare-run-a').input_value()==values[0] and page.locator('#compare-run-b').input_value()==values[1])
                    page.locator('#compare-run-a').select_option('');page.locator('#compare-run-b').select_option('')
                page.locator('#run-list button:enabled').first.click();page.wait_for_function('lastResult!==null');page.wait_for_timeout(80);saved=page.url
                check(prefix+'真实保存结果可直达','run=' in saved and page.locator('#search').is_visible())
                if page.locator('#route-catalog button').count()>1:
                    page.locator('#route-tab-1').click();page.reload();ready(page);page.wait_for_selector('#route-tab-1[aria-selected=true]');check(prefix+'路线选择刷新恢复','route=2' in page.url)
                    page.go_back();page.wait_for_selector('#route-tab-0[aria-selected=true]')
                page.go_back();page.wait_for_selector('#history:visible');check(prefix+'结果返回历史',page.url.endswith('#/history'))
                page.locator('#tab-resources').click();page.wait_for_selector('#rows button');page.locator('#kind').select_option('molecule');page.wait_for_timeout(100);page.locator('#records-pager-top [data-page-action=next]').click();page.wait_for_timeout(100);list_url=page.url
                page.locator('#rows button').first.click();detail=page.url;page.reload();ready(page);page.wait_for_function('document.querySelector("#record-json").children.length>0')
                check(prefix+'资源详情/筛选/分页刷新恢复',page.url==detail and page.locator('#kind').input_value()=='molecule' and 'page=2' in detail)
                page.go_back();page.wait_for_selector('#rows button');check(prefix+'资源详情返回列表原页',page.url==list_url and page.locator('#records-pager-top [data-page-action=page]').input_value()=='2')
                check(prefix+'资源布局无横溢',no_overflow(page))
                if width>=992:
                    a=page.locator('.resource-workspace > section').nth(0).bounding_box();b=page.locator('.resource-workspace > section').nth(1).bounding_box();check(prefix+'资源统一1比2分栏',abs(a['width']/(a['width']+b['width'])-1/3)<.02)
                page.locator('#tab-literature').click();page.wait_for_selector('.example-title');page.locator('[data-topic=c]').click();page.wait_for_selector('[data-topic=c][aria-pressed=true]');example=page.url;page.reload();ready(page);page.wait_for_selector('[data-topic=c][aria-pressed=true]');check(prefix+'教学示例独立地址',page.url==example)
                page.locator('#teaching-section-principles').click();page.wait_for_selector('#principle-select option',state='attached');page.locator('#principle-select').select_option('c_glycosylation');page.reload();ready(page);page.wait_for_function('document.querySelector("#principle-select").value==="c_glycosylation"');check(prefix+'原理选择恢复','principles/c_glycosylation' in page.url)
                page.locator('#teaching-section-tools').click();page.wait_for_selector('#lesson-list .tool-row');page.locator('#go-lessons').click();page.wait_for_selector('#lesson-reader .lesson-card')
                check(prefix+'资料真实调用公共列表组件',page.locator('#lesson-list .ui-list-item').count()>0)
                page.locator('#lesson-list .tool-row').nth(1).click();selected=page.url;page.reload();ready(page);page.wait_for_selector('#lesson-reader .lesson-card');check(prefix+'资料选中及刷新保留',page.url==selected and 'item=' in selected)
                before_source=page.url;page.get_by_role('button',name='查看来源文献',exact=True).click();page.wait_for_selector('#lesson-reader .inline-source');page.get_by_role('button',name='返回案例',exact=True).click();check(prefix+'原地来源阅读与返回',page.url==before_source and page.locator('#lesson-reader .lesson-card').is_visible())
                page.locator('#go-papers').click();page.wait_for_selector('#paper-reader .paper-card');page.locator('#literature-query').fill('zzzz-no-match');page.wait_for_selector('#paper-reader .ui-empty');check(prefix+'公共空态可见',page.locator('#paper-reader').inner_text()=='没有可显示的条目。');page.locator('#literature-reset').click();page.wait_for_selector('#paper-reader .paper-card')
                page.locator('#go-reaction-evidence').click();page.wait_for_selector('#evidence-reader .paper-card');check(prefix+'新增证据子页保持',page.locator('#evidence-pager-top.ui-pagination').count()==1)
                page.locator('#go-learning').click();page.wait_for_selector('#learning-step-nav button');page.locator('#learning-step-nav [data-step="2"]').click();page.locator('#learning-note-2').fill('前端回归检查：保留证据边界。');page.locator('#learning-complete-2').check();page.reload();ready(page);page.wait_for_selector('#learning-note-2')
                check(prefix+'练习步骤/笔记/完成保留',page.locator('#learning-note-2').input_value()=='前端回归检查：保留证据边界。' and page.locator('#learning-complete-2').is_checked())
                with page.expect_download() as info:page.locator('#learning-export').click()
                download=info.value;data=json.loads(Path(download.path()).read_text());check(prefix+'导出仍含六步',len(data['steps'])==6 and not data['human_reviewed'])
                page.locator('#teaching-section-examples').click();page.wait_for_selector('.example-title');gap=page.evaluate('document.querySelector(".literature-heading").getBoundingClientRect().top-document.querySelector("header").getBoundingClientRect().bottom')
                check(prefix+'原标题高度和背景保持',abs(gap-(16 if width<768 else 20))<.6 and page.evaluate('getComputedStyle(document.querySelector(".literature-heading"),"::before").backgroundColor===getComputedStyle(document.querySelector(".literature-heading")).backgroundColor'))
                check(prefix+'教学布局无横溢',no_overflow(page));shot(page,f'{width}-teaching.png')
                page.locator('#tab-governance').click();page.wait_for_function('document.querySelector("#research-status").textContent!=="正在读取…"');check(prefix+'研究范围入口保持',page.url.endswith('#/governance'))
                goto(page,'#/components');page.wait_for_selector('#component-buttons button');page.get_by_role('button',name='主要操作',exact=True).click();check(prefix+'组件按钮实际交互',page.locator('#component-interaction').inner_text()=='主要操作已执行。')
                page.locator('#component-choice').select_option('selected');check(prefix+'组件表单实际交互','选中条目' in page.locator('#component-interaction').inner_text())
                page.locator('#component-pager [data-page-action=next]').click();check(prefix+'共享分页实际交互',page.locator('#component-pager [data-page-action=page]').input_value()=='2' and '示例条目 26' in page.locator('#component-items').inner_text())
                check(prefix+'零/缺失和文本安全',page.evaluate('FlavoUI.fixed(0)==="0.000" && FlavoUI.text("span","<img src=x>").querySelector("img")===null') and '数值零' in page.locator('#component-states').inner_text())
                check(prefix+'组件空态/错误语义',page.locator('#component-states .ui-empty').count()==1 and page.locator('#component-feedback [role=alert]').count()==1)
                check(prefix+'组件页不占主导航且无横溢',page.locator('[data-tab]').count()==5 and no_overflow(page));shot(page,f'{width}-components.png')
                page.reload();ready(page);check(prefix+'组件子页可重新进入',page.url.endswith('#/components'));context.close()
            browser.close()
        check('控制台/警告/页面异常0',not errors);check('浏览器非GET0',not blocked)
        if before is not None:check('真实MCTS新增0',before==sorted(p.name for p in run_dir.iterdir()))
        ok=True
    except Exception as exc:
        errors.append('QA failure: '+str(exc));ok=False
    result={'ok':ok,'base':base,'browser':'Playwright Chromium','reason':'Browser plugin not available','viewports':['1440x1000','768x1024','390x844','320x844'],'checks':checks,'errors':errors,'blocked':blocked,'screenshots':shots}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2))
    spec=importlib.util.spec_from_file_location('browser_operate',ROOT/'scripts/operate.py');operate=importlib.util.module_from_spec(spec);spec.loader.exec_module(operate)
    operate.event(args.task,'browser_evidence',report=str(args.output) if args.output else None,screenshots=shots,ok=ok,checks=len(checks))
    print(json.dumps({'ok':ok,'passed':len(checks),'errors':errors,'blocked':blocked},ensure_ascii=False))
    return 0 if ok else 1

if __name__=='__main__':raise SystemExit(main())

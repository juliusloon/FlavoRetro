// ---------- 子页面地址、浏览器历史与会话草稿 ----------
const PAGE_NAMES=Object.freeze(Object.fromEntries(ROUTE_DEFINITIONS.pages.map(page=>[page.id,page.title])));
const SECTION_NAMES={examples:'常见反应类型',principles:'全部反应原理',tools:'文献核查与练习'};
const VIEW_NAMES={lessons:'文献核查案例',papers:'查原文与来源',practice:'六步逆合成练习',evidence:'新增反应证据'};
const NAV_SESSION_KEY='flavoretro.navigation.v1',DRAFT_KEY='flavoretro.search-draft.v1';
const pageLocations={};
try{Object.assign(pageLocations,JSON.parse(sessionStorage.getItem(NAV_SESSION_KEY)||'{}'));}catch{}
function plainNavigation(event){return !event || (!event.ctrlKey&&!event.metaKey&&!event.shiftKey&&!event.altKey&&event.button===0);}
function pagedParams(params,start,size,defaultSize){if(start)params.set('page',Math.floor(start/size)+1);if(size!==defaultSize)params.set('size',size);}
function routeURL(path,params=new URLSearchParams()){return '#/'+path+(params.size?'?'+params:'');}
function captureRoute(page=currentPage,choices={}){
    const section=choices.section||activeTeachingSection,view=choices.view||activeLiteratureView;
    const p=new URLSearchParams(),set=(key,value)=>{if(value)p.set(key,value);};let path=page;
    if(page==='search'&&lastResult){set('run',lastResult.run_id);if(selectedRouteIndex>0)p.set('route',selectedRouteIndex+1);}
    if(page==='history'){pagedParams(p,runOffset,runLimit,25);set('a',$('compare-run-a').value);set('b',$('compare-run-b').value);}
    if(page==='resources'){
        for(const [key,id] of [['kind','kind'],['q','query'],['issue','qc-filter'],['outcome','outcome-filter'],['source','source-filter']])set(key,$(id).value);
        pagedParams(p,offset,recordsLimit,25);if(selectedRecordId)path+='/'+encodeURIComponent(selectedRecordId);
    }
    if(page==='literature'){
        path+='/'+section;
        if(section==='examples')path+='/'+activeConcept;
        else if(section==='principles')path+='/'+encodeURIComponent(selectedPrinciple);
        else{
            path+='/'+view;
            if(['papers','lessons'].includes(view)){
                set('q',$('literature-query').value);set('topic',$('literature-topic').value);
                const state=teachingPages[view];pagedParams(p,state.offset,state.limit,25);
            }else if(view==='practice')pagedParams(p,teachingPages.practice.offset,teachingPages.practice.limit,1);
            else{set('q',$('reaction-evidence-query').value);set('status',$('reaction-evidence-status').value);pagedParams(p,reactionEvidenceOffset,reactionEvidenceLimit,25);}
            set('item',choices.item===false?'':choices.item??navigationItem);
        }
    }
    return routeURL(path,p);
}
function readRoute(){
    let parts;try{parts=location.hash.replace(/^#\/?/,'').split('?')[0].split('/').filter(Boolean).map(decodeURIComponent);}catch{parts=[];}
    const p=new URLSearchParams(location.hash.split('?').slice(1).join('?'));
    const page=Object.hasOwn(PAGE_NAMES,parts[0])?parts[0]:'search';
    const section=Object.hasOwn(SECTION_NAMES,parts[1])?parts[1]:'examples';
    const view=Object.hasOwn(VIEW_NAMES,parts[2])?parts[2]:'lessons';
    return {page,section,view,choice:parts[2],record:page==='resources'?parts[1]||null:null,p};
}
function pageNumber(p){const n=Number(p.get('page'));return (Number.isSafeInteger(n)&&n>0?Math.min(n,100000):1)-1;}
function pageSize(p,defaultValue,allowed){const n=Number(p.get('size'));return allowed.includes(n)?n:defaultValue;}
function setSelect(id,value){const input=$(id);input.value=value||'';if(input.selectedIndex<0)input.selectedIndex=0;}
function scrollPositions(){
    return Object.fromEntries(['.page:not([hidden])','.search-form-scroll','#search-results','.record-table-wrap','#history-comparison','#route-catalog','#lesson-list','#lesson-reader','#literature-list','#paper-reader','#reaction-evidence-list','#evidence-reader','#learning-step-nav','#learning-steps'].flatMap(selector=>[...document.querySelectorAll(selector)].map(el=>[el.id||selector,[el.scrollLeft,el.scrollTop]])));
}
function saveScroll(){
    if(navigationReady&&location.hash===currentLocationHash)history.replaceState({...history.state,flavoretro:true,scroll:scrollPositions()},'');
}
function writeLocation(hash,replace=false){
    const url=new URL(location.href);url.searchParams.delete('run');url.hash=hash;
    history[replace?'replaceState':'pushState']({flavoretro:true,scroll:{}},'',url);
    currentLocationHash=hash;
}
function rememberPage(page=currentPage,hash=location.hash){
    pageLocations[page]=hash;
    try{sessionStorage.setItem(NAV_SESSION_KEY,JSON.stringify(pageLocations));}catch{}
}
function recordNavigation(replace=false){
    if(!navigationReady)return;
    navigationItem='';const hash=captureRoute();
    if(hash!==location.hash){saveScroll();writeLocation(hash,replace);}
    rememberPage();updatePageLocation();saveSearchDraft();
}
async function goToHash(hash,{replace=false,focus=false}={}){
    saveScroll();saveSearchDraft();
    if(location.hash===hash){if(focus)(typeof focus==='string'?document.querySelector(focus):$('tab-'+currentPage))?.focus();else if(navigationItem&&$(navigationItem)&&!focusToolItem(navigationItem))focusSection(navigationItem);return;}
    writeLocation(hash,replace);await restoreLocation(focus);
}
function navigateTab(button,focus=false){
    const page=button.dataset.tab;
    return goToHash(pageLocations[page]||captureRoute(page),{focus});
}
function showRecord(row){
    const raw=row.raw||{},label=raw.name||raw.query_name||raw.substance_query||raw.title||raw.fields?.['RXN:VAR(1):CAS_Reaction_Number']||raw.template_id||'当前条目';
    $('record-json').replaceChildren(resourceDetails(row));$('record-selection').textContent=label;
    for(const el of $('rows').children)el.classList.toggle('is-selected',el.dataset.recordId===row.id);
}
function clearRecord(){
    $('record-json').replaceChildren();$('record-selection').textContent='选择左侧条目查看详情。';
    for(const el of $('rows').children)el.classList.remove('is-selected');
}
function resetRunView(){
    lastResult=null;displayedRoutes=[];selectedRouteIndex=0;renderedRunId=null;currentManifest=null;currentReadSource=null;savedRun=false;
    $('search-results').classList.add('is-empty');$('search-intro').hidden=false;$('route-workbench').hidden=true;
    $('routes').replaceChildren();$('run-meta').replaceChildren();$('route-catalog').replaceChildren();$('lab-development').hidden=true;
    $('download').hidden=true;$('learning-use-run').disabled=true;
}
function searchDraft(){
    return {fields:Object.fromEntries([...$('search-form').querySelectorAll('input[id],textarea[id],select[id]')].map(input=>[input.id,input.type==='checkbox'?input.checked:input.value])),overrides:[...budgetOverrides],advanced:$('search-advanced').open};
}
function saveSearchDraft(){if(!navigationReady)return;try{sessionStorage.setItem(DRAFT_KEY,JSON.stringify(searchDraft()));}catch{}}
function restoreSearchDraft(){
    try{
        const draft=JSON.parse(sessionStorage.getItem(DRAFT_KEY)||'null');if(!draft?.fields)return;
        for(const [id,value]of Object.entries(draft.fields)){
            const input=$(id);if(!input||!$('search-form').contains(input))continue;
            if(input.type==='checkbox')input.checked=Boolean(value);
            else if(input.tagName!=='SELECT'||[...input.options].some(option=>option.value===value))input.value=value;
        }
        budgetOverrides.clear();for(const key of draft.overrides||[])if(budgetFields.includes(key))budgetOverrides.add(key);
        syncBudgetDefaults();syncDomainOptions();syncStockOptions();$('search-advanced').open=Boolean(draft.advanced);$('preview').click();
    }catch{}
}
function updatePageLocation(){
    const titles=[PAGE_NAMES[currentPage]];
    if(currentPage==='literature'){
        titles.push(SECTION_NAMES[activeTeachingSection]);
        if(activeTeachingSection==='tools')titles.push(VIEW_NAMES[activeLiteratureView]);
        else if(activeTeachingSection==='examples')titles.push(LEARNING_TOPICS.find(t=>t.id===activeConcept)?.label||'反应示例');
        else titles.push($('principle-select').selectedOptions[0]?.textContent||'反应原理');
    }
    if(currentPage==='search'&&lastResult)titles.push('保存的探索结果');
    if(currentPage==='resources'&&selectedRecordId)titles.push('条目详情');
    for(const link of document.querySelectorAll('[data-teaching-section]'))link.href=captureRoute('literature',{section:link.dataset.teachingSection,item:false});
    for(const link of document.querySelectorAll('[data-literature-view]'))link.href=captureRoute('literature',{section:'tools',view:link.dataset.literatureView,item:false});
    document.title=titles.reverse().join(' · ')+' · FlavoRetro';
    for(const tab of tabs){tab.href=pageLocations[tab.dataset.tab]||captureRoute(tab.dataset.tab);if(tab.dataset.tab===currentPage)tab.setAttribute('aria-current','page');else tab.removeAttribute('aria-current');}
}

async function restoreLocation(focus=false){
    if(!history.state?.flavoretro)history.replaceState({flavoretro:true,scroll:{}},'');
    const generation=++navigationGeneration,route=readRoute(),p=route.p,scroll=history.state?.scroll||{};
    comparisonGeneration++;$('run-comparison').disabled=false;
    currentPage=route.page;navigationItem=p.get('item')||'';$('navigation-message').hidden=true;
    if(currentPage==='resources'){
        for(const [key,id]of [['kind','kind'],['issue','qc-filter'],['outcome','outcome-filter'],['source','source-filter']])setSelect(id,p.get(key));
        $('query').value=p.get('q')||'';recordsLimit=pageSize(p,25,[10,25,50,100]);offset=pageNumber(p,recordsLimit)*recordsLimit;
        selectedRecordId=route.record;selectedRecordRow=null;clearRecord();switchResourcePane(route.record?'detail':'records');
    }
    if(currentPage==='history'){runLimit=pageSize(p,25,[10,25,50,100]);runOffset=pageNumber(p,runLimit)*runLimit;}
    if(currentPage==='literature'){
        activeTeachingSection=route.section;activeLiteratureView=route.view;
        if(route.section==='examples')activeConcept=LEARNING_TOPICS.some(t=>t.id===route.choice)?route.choice:'o';
        if(route.section==='principles')selectedPrinciple=route.choice||'o_glycosylation';
        if(route.section==='tools'){
            if(['lessons','papers'].includes(route.view)){
                $('literature-query').value=p.get('q')||'';setSelect('literature-topic',p.get('topic'));
                const state=teachingPages[route.view];state.limit=pageSize(p,25,[10,25,50,100]);state.offset=pageNumber(p,state.limit)*state.limit;
            }else if(route.view==='practice'){
                const state=teachingPages.practice;state.limit=pageSize(p,1,[1,2,3,6]);state.offset=Math.min(pageNumber(p,state.limit)*state.limit,Math.floor(5/state.limit)*state.limit);
            }else{
                $('reaction-evidence-query').value=p.get('q')||'';setSelect('reaction-evidence-status',p.get('status'));
                reactionEvidenceLimit=pageSize(p,25,[10,25,50,100]);reactionEvidenceOffset=pageNumber(p,reactionEvidenceLimit)*reactionEvidenceLimit;
            }
        }
    }
    currentLocationHash=location.hash;rememberPage();updatePageLocation();
    const loading=activateTab(currentPage,focus===true);
    if(typeof focus==='string')document.querySelector(focus)?.focus({preventScroll:true});
    try{
        if(currentPage==='search'){
            const runId=p.get('run');
            if(runId){
                if(lastResult?.run_id!==runId){
                    resetRunView();$('navigation-message').hidden=false;$('navigation-message').textContent='正在读取保存的探索结果…';
                    const saved=await api('/api/runs/'+encodeURIComponent(runId));if(generation!==navigationGeneration)return;
                    savedRun=true;currentReadSource=saved.execution_source;currentManifest=saved.manifest;
                    restoreSearchRequest(saved.result.request,saved.result);await render(saved.result,saved.research_ranking);
                }
                if(generation!==navigationGeneration)return;
                const index=Math.max(0,Math.min(displayedRoutes.length-1,(Number(p.get('route'))||1)-1));
                if(displayedRoutes.length)selectRoute(Number.isInteger(index)?index:0,lastResult,lastTeaching,true);
                $('message').textContent='已打开保存的探索结果。';$('navigation-message').hidden=true;
            }else{resetRunView();restoreSearchDraft();}
        }
        await loading;if(generation!==navigationGeneration)return;
        if(currentPage==='resources'&&route.record){
            // The existing record query includes the immutable ID, so details can reopen outside the current list page.
            const data=await api('/api/records?'+new URLSearchParams({q:route.record,limit:1}));if(generation!==navigationGeneration)return;
            selectedRecordRow=(data.records||[]).find(item=>item.id===route.record);
            if(!selectedRecordRow)throw new Error('未找到该资源条目，请返回资源列表重新选择。');
            showRecord(selectedRecordRow);switchResourcePane('detail');
        }
        if(currentPage==='history'){
            for(const slot of ['a','b']){const select=$('compare-run-'+slot),id=p.get(slot);if(id&&![...select.options].some(option=>option.value===id)){const option=text('option','指定运行 '+slot.toUpperCase());option.value=id;select.append(option);}setSelect(select.id,id);}
            $('comparison-table').replaceChildren();$('export-comparison').disabled=true;
            if(p.get('a')&&p.get('b'))await compareSelectedRuns(true);
        }
        if(generation!==navigationGeneration)return;
        // Canonicalize invalid/default parameters without inserting another history entry.
        const canonical=captureRoute();if(canonical!==location.hash)writeLocation(canonical,true);
        rememberPage();updatePageLocation();
        if(!focus&&navigationItem&&$(navigationItem)&&!focusToolItem(navigationItem))focusSection(navigationItem);
        requestAnimationFrame(()=>{
            if(generation!==navigationGeneration)return;
            for(const [key,[left,top]]of Object.entries(scroll)){
                const el=$(key)||document.querySelector(key);if(el)el.scrollTo(left,top);
            }
        });
    }catch(error){
        if(generation!==navigationGeneration)return;
        $('navigation-message').textContent='页面读取失败：'+error.message;$('navigation-message').hidden=false;
    }
}
// Hash routes use the existing static root, so direct entry and reload require no server fallback.
document.addEventListener('keydown',event=>{if(event.key===' '&&event.target.matches('a.nav-link[role=tab]')){event.preventDefault();event.target.click();}});
for(const selector of ['[data-teaching-section]','[data-literature-view]'])for(const link of document.querySelectorAll(selector)){
    link.onclick=event=>{if(plainNavigation(event)){event.preventDefault();if(link.dataset.teachingSection)switchTeachingSection(link.dataset.teachingSection);else switchLiteratureView(link.dataset.literatureView);}};
}
document.querySelector('.brand').onclick=event=>{if(plainNavigation(event)){event.preventDefault();goToHash('#/search');}};
let scrollFrame=0;
document.addEventListener('scroll',()=>{cancelAnimationFrame(scrollFrame);scrollFrame=requestAnimationFrame(saveScroll);},true);
$('search-form').addEventListener('input',saveSearchDraft);$('search-form').addEventListener('change',saveSearchDraft);
$('search-form').addEventListener('click',()=>queueMicrotask(saveSearchDraft));
addEventListener('pagehide',()=>{saveScroll();saveSearchDraft();});
let restoredURL='';
function onLocationChange(){if(location.hash==='#main')return;const url=location.href;if(restoredURL===url)return;restoredURL=url;queueMicrotask(()=>{restoredURL='';});restoreLocation();}
addEventListener('popstate',onLocationChange);
addEventListener('hashchange',()=>{if(location.hash!==currentLocationHash)onLocationChange();});
(async()=>{
    UI.mount(document);
    await Promise.all([targetsReady,capabilitiesReady]);restoreSearchDraft();navigationReady=true;history.scrollRestoration='manual';
    if(!history.state?.flavoretro)history.replaceState({flavoretro:true,scroll:{}},'');
    if(!location.hash.startsWith('#/')){
        const linkedRun=new URLSearchParams(location.search).get('run');writeLocation(linkedRun?'#/search?'+new URLSearchParams({run:linkedRun}):'#/search',true);
    }
    await restoreLocation();
})();

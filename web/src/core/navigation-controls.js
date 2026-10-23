// ---------- Shared list controls ----------
let recordsLimit=25, recordsTotal=0, selectedRecordId=null, runLimit=25;
let activeLiteratureView='lessons', activeConcept='o', teachingExamplesCache=null;
let activeTeachingSection='examples';
const teachingPages={lessons:{offset:0,limit:25,total:0},papers:{offset:0,limit:25,total:0},practice:{offset:0,limit:1,total:6}};
const pagination=UI.pagination;
function resetLibraryPages(){teachingPages.lessons.offset=0;teachingPages.papers.offset=0;}
function switchResourcePane(pane){
    $('resource-workspace').dataset.mobilePane=pane;
    $('show-records').setAttribute('aria-pressed',String(pane==='records'));$('show-record-detail').setAttribute('aria-pressed',String(pane==='detail'));
    if(matchMedia('(max-width:991px)').matches){
        const target=pane==='detail'?$('record-detail-title'):document.querySelector('#rows .is-selected button')||$('show-records');
        if(!target.hasAttribute('tabindex')&&target.tagName!=='BUTTON')target.tabIndex=-1;
        target.focus({preventScroll:true});target.scrollIntoView({block:'nearest'});
    }
}
function showTeachingSection(section,focus=false) {
    const buttons=[...document.querySelectorAll('[data-teaching-section]')];
    if(!buttons.some(button=>button.dataset.teachingSection===section))return;
    const changed=activeTeachingSection!==section;
    activeTeachingSection=section;
    $('literature').dataset.section=section;
    for(const button of buttons){
        const active=button.dataset.teachingSection===section;
        button.setAttribute('aria-selected',String(active));button.tabIndex=active?0:-1;
        $(button.getAttribute('aria-controls')).hidden=!active;
        if(active&&focus)button.focus({preventScroll:true});
    }
    if(changed)$('literature').scrollTop=0;
}
async function switchTeachingSection(section,focus=false,fromRoute=false) {
    if(navigationReady&&!fromRoute){navigationItem='';activeTeachingSection=section;return goToHash(captureRoute('literature'),{focus:focus?'#teaching-section-'+section:false});}
    showTeachingSection(section,focus);
    if(section==='examples')await renderLearningTopics();
    else if(section==='principles')await loadTeachingCatalog();
    else if(section==='tools')await switchLiteratureView(activeLiteratureView,focus,true);
}
for(const button of document.querySelectorAll('[data-teaching-section]'))button.onclick=()=>switchTeachingSection(button.dataset.teachingSection);
document.querySelector('.teaching-sections').addEventListener('keydown',event=>{
    const buttons=[...document.querySelectorAll('[data-teaching-section]')],index=buttons.indexOf(document.activeElement);
    if(index<0)return;
    const next=event.key==='ArrowRight'?buttons[(index+1)%buttons.length]:event.key==='ArrowLeft'?buttons[(index+buttons.length-1)%buttons.length]:event.key==='Home'?buttons[0]:event.key==='End'?buttons.at(-1):null;
    if(next){event.preventDefault();switchTeachingSection(next.dataset.teachingSection,true);}
});
async function switchLiteratureView(view,focus=false,fromRoute=false) {
    if(navigationReady&&!fromRoute){navigationItem=toolSelections[view]||'';activeTeachingSection='tools';activeLiteratureView=view;return goToHash(captureRoute('literature'),{focus:focus?'[data-literature-view="'+view+'"]':false});}
    showTeachingSection('tools');
    activeLiteratureView=view;
    const buttons=[...document.querySelectorAll('[data-literature-view]')];
    for(const button of buttons){const active=button.dataset.literatureView===view;button.setAttribute('aria-selected',String(active));button.tabIndex=active?0:-1;$('teaching-view-'+button.dataset.literatureView).hidden=!active;if(active&&focus)button.focus();}
    $('library-search').hidden=!['lessons','papers'].includes(view);
    $('reaction-evidence-filters').hidden=view!=='evidence';
    $('learning-toolbar').hidden=view!=='practice';
    updateLiteratureContext();
    if(view==='evidence'){await loadReactionEvidence();return;}
    if(view==='practice'){renderLearning();return;}
    await loadLiterature();
}

// ---------- tab 切换（WAI-ARIA tablist：aria-selected、roving tabindex、方向键循环） ----------
const tabs = [...document.querySelectorAll('[data-tab]')];
function activateTab(target, focus = false) {
    const page=typeof target==='string'?target:target.dataset.tab,button=$('tab-'+page);
    document.querySelectorAll('.page').forEach(p => p.hidden = p.id !== page);
    const primary=tabs.some(tab=>tab.dataset.tab===page);
    for (const b of tabs) {
        const active = b.dataset.tab === page;
        b.classList.toggle('active', active);
        b.setAttribute('aria-selected', String(active));
        b.tabIndex = active || (!primary && b === tabs[0]) ? 0 : -1;
    }
    button?.scrollIntoView({ block: 'nearest', inline: 'nearest' });
    if (focus) button?.focus();
    return PageRegistry.load(page);
}
tabs.forEach(button => button.onclick = event => {if(plainNavigation(event)){event.preventDefault();navigateTab(button);}});
document.querySelector('nav[role=tablist]').addEventListener('keydown', event => {
    const index = tabs.indexOf(document.activeElement);
    if (index < 0) return;
    let next = null;
    if (event.key === 'ArrowRight') next = tabs[(index + 1) % tabs.length];
    else if (event.key === 'ArrowLeft') next = tabs[(index - 1 + tabs.length) % tabs.length];
    else if (event.key === 'Home') next = tabs[0];
    else if (event.key === 'End') next = tabs[tabs.length - 1];
    if (next) { event.preventDefault(); navigateTab(next, true); }
});

// 顶栏高度实测写入 --header-h，供 ≥992px sticky 侧栏定位（替代旧 body overflow:hidden 方案）
const headerEl = document.querySelector('header');
const setHeaderHeight = () => document.documentElement.style.setProperty('--header-h', headerEl.offsetHeight + 'px');
setHeaderHeight();
addEventListener('resize', setHeaderHeight);

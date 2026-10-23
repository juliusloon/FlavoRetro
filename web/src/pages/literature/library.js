// ---------- 文献教学页 ----------
function policyBanner(policy) {
    const banner = div('banner');
    banner.append(text('p', '', ''));
    banner.firstChild.textContent = '边界声明（来自 claim_policy，原样呈现）：';
    let known = 0;
    for (const [key, value] of Object.entries(policy || {})) {
        if (key === 'production_lesson_gate') {
            banner.append(text('p', `${CLAIM_POLICY_ZH[key]}：${value}（未通过该门槛的课程不进入生产）`));
        } else if (CLAIM_POLICY_ZH[key]) {
            banner.append(text('p', `${CLAIM_POLICY_ZH[key]}：${value}`));
        } else {
            if(SCIENTIFIC_LABELS[key])banner.append(kv(SCIENTIFIC_LABELS[key],factText(value)));
            continue;
        }
        known++;
    }
    if (!known) banner.append(text('p', '（未提供 claim_policy 字段）'));
    return banner;
}

function kvTable(rows) {
    const table = document.createElement('table');
    table.className = 'kv-table';
    for (const [label, value] of rows) {
        if (value == null || (Array.isArray(value) && !value.length) || value === '') continue;
        const tr = document.createElement('tr');
        tr.append(text('th', label));
        const td = document.createElement('td');
        if (Array.isArray(value)) {
            const box = div('chips');
            for (const item of value) box.append(chip(factText(item)));
            td.append(box);
        } else if (value instanceof Node) td.append(value);
        else td.textContent=factText(value);
        tr.append(td);
        table.append(tr);
    }
    return table;
}

// 递归渲染嵌套条件对象（机器抽取原文，键值原样呈现）
function nestedTable(obj){return scientificDetails(obj);}

// Edited learning navigation only; these groups never assign a model reaction class.
const LEARNING_TOPICS = [
    {id:'o', label:'O-糖苷连接', question:'如何区分苷元与糖侧前体？',
     teaching:['o_glycosylation','o_glycoside_cleavage','activated_glycosyl_donor'],
     papers:['P001','P002','P005','P006','P007','P008','P009','P010','P011','P012','P013','P015']},
    {id:'c', label:'C-糖苷连接', question:'哪些来源讨论 C-连接构建？',
     teaching:['c_glycosylation'], papers:['P003','P004']},
    {id:'chain', label:'糖间连接与糖链', question:'如何查证糖链分支与糖链编辑？',
     teaching:['glycosylation'], papers:['P011','P012','P014','P015'],
     note:'此处提供通用糖基化原理；糖链分支与糖链编辑请分别核对 P014 与 P011/P012，不能把水解当作成键机理。当前没有专属糖间连接案例。'},
    {id:'scaffold', label:'母核构建与修饰', question:'骨架、氧化态与保护基如何分开判断？',
     teaching:['chalcone_aldol','flavanone_synthesis','oxidation','phenol_protection','deprotection'],
     papers:['P003','P004','P006'], includeTask022:true}
];
function learningTopic() { return LEARNING_TOPICS.find(topic => topic.id === $('literature-topic').value); }
function topicHasPaper(topic, id) { return !topic || topic.papers.includes(id) || (topic.includeTask022 && String(id || '').startsWith('T022-')); }
function focusSection(id) {
    const anchor = $(id);
    if (!anchor) return;
    anchor.scrollIntoView({block:'start'});
    if (anchor.tagName === 'DETAILS') anchor.open = true;
    if (!anchor.hasAttribute('tabindex')) anchor.tabIndex = -1;
    anchor.focus({preventScroll:true});
}
async function openLiteratureAnchor(id) {
    const data=await fetchLiterature();if(!data||data.error)return;
    const isLesson=(data.reaction_lessons||[]).some(item=>'lit-'+item.reaction_id===id);
    const view=isLesson?'lessons':'papers',items=isLesson?data.reaction_lessons:data.paper_cards;
    const index=items.findIndex(item=>'lit-'+(isLesson?item.reaction_id:item.paper_id)===id);
    if(index<0)return;
    const params=new URLSearchParams({item:id});
    const size=teachingPages[view].limit,page=Math.floor(index/size)+1;
    if(page>1)params.set('page',page);if(size!==25)params.set('size',size);
    await goToHash('#/literature/tools/'+view+'?'+params);
}
// These explanations annotate existing source-bound structures; they do not admit reactions.
const EXAMPLE_LESSONS = {
    o:{title:'把葡萄糖基接到芹菜素的 7-O 位',equation:['芹菜素 + UDP-Glc','芹菜素 7-O-β-D-葡萄糖苷 + UDP'],
       participants:'芹菜素提供酚羟基，UDP-Glc 提供葡萄糖基；实际糖供体不是游离葡萄糖。',
       change:'在芹菜素 7-O 与葡萄糖异头碳之间形成 O—C 键。图中深绿色标出这条连接。',
       retro:'沿同一连接回看产物，分成芹菜素与 UDP-Glc；保留活化供体身份。'},
    c:{title:'把葡萄糖基直接接到根皮素的芳环碳',equation:['根皮素 + UDP-Glc','根皮素单 C-葡萄糖苷 17a + UDP'],
       participants:'根皮素是受体，UDP-Glc 是糖基供体；来源实例使用 AbCGT。',
       change:'糖异头碳与芳环碳形成 C—C 键，糖与母核之间没有桥接氧。',
       retro:'回溯图中绿色 C—C 连接，得到根皮素与 UDP-Glc；单/双糖基化比例仍须回查原文。'},
    chain:{title:'在已有葡萄糖上再接一个芹糖基',equation:['芹菜素 7-O-葡萄糖苷 + UDP-Api','芹菜苷（apiin）+ UDP'],
       participants:'受体已经带有葡萄糖；PcApiT 将 UDP-Api 的芹糖基转移到该糖残基上。',
       change:'形成新的糖间 O—C 连接；苷元与第一层葡萄糖之间原有的连接保留。',
       retro:'只拆新接入的芹糖基，回到单糖苷与 UDP-Api；不能直接拆成苷元和两枚游离糖。'},
    scaffold:{title:'把开链查尔酮闭合成黄烷酮 C 环',equation:['原文 E-2′-羟基查尔酮','原文黄烷酮 2b'],
       participants:'同一分子内的邻位羟基与烯酮片段参与闭环，原文产物为黄烷酮 2b。',
       change:'形成环内 C—O 键，同时涉及 C2/C3 键级变化与质子转移；不能只画成删键。',
       retro:'把黄烷酮 C 环映射回原文的 E-2′-羟基查尔酮；逆合成箭头不代表实验上执行逆反应。'}
};
function reactionEquation(left,right,label,catalyst='') {
    const box=div('reaction-equation');box.setAttribute('role','group');box.setAttribute('aria-label',label);
    box.append(text('p',label,'equation-label'));
    const line=div('equation-line'),arrow=div('equation-arrow');
    if(catalyst)arrow.append(text('span',catalyst,'equation-catalyst'));
    const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 80 18');svg.setAttribute('aria-hidden','true');
    const path=document.createElementNS(svg.namespaceURI,'path');path.setAttribute('d','M2 9H76M67 2L76 9L67 16');path.setAttribute('fill','none');path.setAttribute('stroke','currentColor');path.setAttribute('stroke-width','2');svg.append(path);arrow.append(svg);
    line.append(text('span',left,'equation-compound'),arrow,text('span',right,'equation-compound'));box.append(line);return box;
}
function explanationSteps(rows) {
    const list=document.createElement('ol');list.className='reaction-explanation';
    for(const [label,description] of rows){const item=document.createElement('li');item.append(text('h4',label),text('p',description));list.append(item);}return list;
}
function exampleSource(example) {
    const source=div('example-source'),link=text('a',example.source.title||example.source.doi);
    link.href=example.source.url;link.target='_blank';link.rel='noopener';
    source.append(text('h4','这个实例的出处'),link,text('p','DOI：'+example.source.doi),text('p','原文定位：'+[].concat(example.source.locator||[]).join('；')));
    source.append(text('p',example.details.source_scope,'note'));
    return source;
}
let conceptGeneration=0;
async function renderLearningTopics() {
    const generation=++conceptGeneration,topic=LEARNING_TOPICS.find(item=>item.id===activeConcept)||LEARNING_TOPICS[0],box=$('learning-topic-options'),content=$('learning-topic-content');
    if(!box.children.length)for(const item of LEARNING_TOPICS){
        const button=text('button',item.label,'topic-option');button.type='button';button.dataset.topic=item.id;
        button.onclick=()=>{activeConcept=item.id;goToHash(captureRoute('literature'));};box.append(button);
    }
    for(const button of box.children)button.setAttribute('aria-pressed',String(button.dataset.topic===topic.id));
    content.setAttribute('aria-busy','true');
    if(!teachingExamplesCache)teachingExamplesCache=api('/teaching-examples.json').catch(()=>null);
    const examples=await teachingExamplesCache;
    if(generation!==conceptGeneration)return;
    content.replaceChildren();content.setAttribute('aria-busy','false');
    const example=examples?.examples?.find(item=>item.topic===topic.id),lesson=EXAMPLE_LESSONS[topic.id];
    if(!example){content.append(text('p','反应示例暂不可用，请稍后刷新。','note'));return;}
    const layout=div('example-layout'),left=div('example-left'),narrative=document.createElement('section'),visual=document.createElement('section');
    narrative.className='example-narrative';narrative.setAttribute('aria-label','反应讲解');
    visual.className='example-visual';visual.setAttribute('aria-label','反应方程式与结构图');
    narrative.append(text('h3',lesson.title,'example-title'),text('p',example.caption_zh,'example-intro'),
        explanationSteps([['谁参与反应',lesson.participants],['结构哪里改变',lesson.change],['逆合成怎么拆',lesson.retro]]));
    visual.append(reactionEquation(...lesson.equation,'文献正向反应 · 从前体到产物',example.details.enzyme||'分子内闭环'));
    const figure=document.createElement('figure');figure.className='reaction-example';
    const viewport=div('reaction-example-viewport');viewport.tabIndex=0;viewport.setAttribute('role','region');viewport.setAttribute('aria-label',topic.label+'反应结构图，可横向滚动');
    const img=document.createElement('img');img.src=example.svg;img.alt=example.alt_zh||example.title_zh;viewport.append(img);
    const caption=text('figcaption','逆合成结构图：产物 → 前体 · 深绿色标出要回溯的连接');const link=text('a','查看完整结构大图');link.href=example.svg;link.target='_blank';link.rel='noopener';const hint=text('span','左右滑动查看全部结构','reaction-pan-hint');caption.append(hint,link);figure.append(viewport,caption);visual.append(figure);
    left.append(narrative,exampleSource(example));layout.append(left,visual);content.append(layout);
    const notes=div('example-boundary');notes.append(text('h4','读图时需要核对'),text('p',example.details.conditions_note));
    if(example.details.byproducts_omitted?.length)notes.append(text('p','上方正向方程式列出 UDP；逆合成结构图省略副产物 '+example.details.byproducts_omitted.join('、')+'。'));
    if(example.details.numbering_note)notes.append(text('p',example.details.numbering_note));
    notes.append(text('p',example.details.representation));left.append(notes);
    const actions=div('button-row'),related=text('button','在文献与案例库中筛选此类型','secondary');related.type='button';related.onclick=async()=>{$('literature-topic').value=topic.id;$('literature-query').value='';resetLibraryPages();await switchLiteratureView('papers');focusSection('papers-title');};
    actions.append(related);left.append(actions);
}
function updateLiteratureContext() {
    const topic=learningTopic(),filter=topic?topic.label:'全部类型';
    const context={
        papers:'全库文献与来源｜当前类型：'+filter+'。用于查论文原文与关联案例；上方示例不会自动改变这里的筛选。',
        practice:'通用六步练习｜围绕你主动选入的目标与已记录运行展开；不自动采用上方示例，也不使用文献类型筛选。',
        evidence:'全库新增反应记录｜独立按关键词和检查状态检索；不随上方示例或文献类型筛选变化。来源已绑定不等于可直接执行。'
    };
    $('literature-tool-context').textContent=context[activeLiteratureView]||'';
    $('literature-tool-context').hidden=!context[activeLiteratureView];
}

// A stable list/reader surface; selecting a row never scrolls the outer page.
const TOOL_PANELS={lessons:['lesson-list','lesson-reader'],papers:['literature-list','paper-reader'],evidence:['reaction-evidence-list','evidence-reader']};
const toolRows={lessons:[],papers:[],evidence:[]},toolSelections={lessons:'',papers:'',evidence:''};
function toolItemId(view,record){return (view==='evidence'?'ev-':'lit-')+(record.reaction_id||record.paper_id||record.id);}
function toolItemTitle(view,record){return view==='lessons'?(record.title_zh||record.title_en||record.reaction_id):view==='papers'?(record.title||record.paper_id):(record.reaction_id||record.id||record.source?.title);}
function renderToolList(view,records){
    toolRows[view]=records;
    const list=$(TOOL_PANELS[view][0]),reader=$(TOOL_PANELS[view][1]);
    const oldScroll=list.scrollTop;list.replaceChildren();
    const requested=navigationItem,ids=records.map(record=>toolItemId(view,record));
    const selected=ids.includes(requested)?requested:!requested&&ids.includes(toolSelections[view])?toolSelections[view]:ids[0];
    if(requested&&!ids.includes(requested))navigationItem='';
    for(const record of records){
        const id=toolItemId(view,record);
        const meta=view==='evidence'?(record.source?.title||record.source?.doi):[record.doi||record.accession,record.year].filter(Boolean).join(' · ');
        const row=UI.listItem({title:toolItemTitle(view,record),meta,href:captureRoute('literature',{section:'tools',view,item:id}),className:'tool-row',onClick:event=>{if(plainNavigation(event)){event.preventDefault();selectToolItem(view,id,true);}}});
        row.dataset.itemId=id;list.append(row);
    }
    if(selected)selectToolItem(view,selected);
    else{toolSelections[view]='';list.append(UI.empty('没有匹配的条目。试试其他关键词或清空筛选。'));reader.replaceChildren(UI.empty('没有可显示的条目。'));}
    list.scrollTop=oldScroll;
    // A retained non-first item must be addressable after a filter change and reload.
    if(selected&&selected!==ids[0]&&!navigationItem&&navigationReady&&currentPage==='literature'&&activeTeachingSection==='tools'&&activeLiteratureView===view){
        navigationItem=selected;writeLocation(captureRoute(),true);rememberPage();updatePageLocation();
    }
}
function renderToolError(view,message){
    if(!TOOL_PANELS[view])return;
    const [listId,readerId]=TOOL_PANELS[view],alert=UI.notice(message,{kind:'error',className:'empty-library'});alert.setAttribute('role','alert');
    toolRows[view]=[];toolSelections[view]='';$(listId).replaceChildren();$(readerId).replaceChildren(alert);
}
function selectToolItem(view,id,navigate=false){
    const record=toolRows[view].find(row=>toolItemId(view,row)===id);if(!record)return;
    if(navigate)saveScroll();
    toolSelections[view]=id;
    const [listId,readerId]=TOOL_PANELS[view],reader=$(readerId);
    for(const row of $(listId).querySelectorAll('.tool-row'))row.setAttribute('aria-current',String(row.dataset.itemId===id));
    reader.replaceChildren(view==='lessons'?lessonCard(record):view==='papers'?paperCard(record):evidenceCard(record));reader.scrollTop=0;
    if(navigate){
        navigationItem=id;const hash=captureRoute();
        if(hash!==location.hash)writeLocation(hash);
        rememberPage();updatePageLocation();
    }
}
function showInlineSource(view,type,record){
    const reader=$(TOOL_PANELS[view][1]),section=div('inline-source'),scroll=reader.scrollTop;
    const back=text('button',view==='lessons'?'返回案例':'返回文献','secondary');back.type='button';
    back.onclick=()=>{selectToolItem(view,toolSelections[view]);reader.scrollTop=scroll;backToReaderFocus(view);};
    section.append(back,type==='papers'?paperCard(record,false):lessonCard(record,false));
    reader.replaceChildren(section);reader.scrollTop=0;back.focus({preventScroll:true});
}
function backToReaderFocus(view){$(TOOL_PANELS[view][1]).focus({preventScroll:true});}
function focusToolItem(id){
    const entry=Object.entries(TOOL_PANELS).find(([view])=>toolSelections[view]===id);
    if(!entry)return false;
    $(entry[1][1]).focus({preventScroll:true});return true;
}
function conditionSections(conditions){
    const box=div('condition-sections'),flat={};
    for(const [key,value]of Object.entries(conditions||{})){
        if(!SCIENTIFIC_LABELS[key])continue;
        if(value&&typeof value==='object'&&!Array.isArray(value)){
            const section=document.createElement('section');section.append(text('h4',SCIENTIFIC_LABELS[key]),scientificDetails(value));box.append(section);
        }else flat[key]=value;
    }
    if(Object.keys(flat).length)box.prepend(scientificDetails(flat));
    return box;
}

function paperCard(paper,related=true) {
    const card=div('paper-card');if(related)card.id='lit-'+paper.paper_id;
    const h3=text('h3',paper.title||paper.paper_id);card.append(h3);
    card.append(text('p',[paper.year,paper.journal,paper.doi||paper.accession].filter(Boolean).join(' · '),'meta'));
    if(paper.key_step)card.append(text('p',paper.key_step,'paper-key-step'));
    const actions=div('button-row');
    if(paper.source_url){const a=text('a','打开原文','source-action');a.href=paper.source_url;a.target='_blank';a.rel='noopener';actions.append(a);}
    for(const lesson of (related?literatureData?.reaction_lessons||[]:[]).filter(item=>item.paper_id===paper.paper_id)){const button=text('button','查看关联案例','secondary');button.type='button';button.onclick=()=>showInlineSource('papers','lessons',lesson);actions.append(button);}
    card.append(actions);
    const details=document.createElement('details');details.open=true;details.append(text('summary','文献详情'),kvTable([['来源范围',paper.evidence_scope],['状态',paper.claim_status],['关键步骤',paper.key_step],['报告条件',paper.reported_conditions]]));card.append(details);return card;
}
function lessonCard(lesson,related=true) {
    const card=div('lesson-card');if(related)card.id='lit-'+lesson.reaction_id;
    card.append(text('h3',lesson.title_zh||lesson.title_en||lesson.reaction_id));
    if(lesson.principle_zh)card.append(text('p',lesson.principle_zh,'case-summary'));
    const paper=(literatureData?.paper_cards||[]).find(p=>p.paper_id===lesson.paper_id),actions=div('button-row');
    if(related&&paper){const button=text('button','查看来源文献','secondary');button.type='button';button.onclick=()=>showInlineSource('lessons','papers',paper);actions.append(button);}
    if(paper?.source_url){const link=text('a','打开原文','source-action');link.href=paper.source_url;link.target='_blank';link.rel='noopener';actions.append(link);}
    card.append(actions);
    const details=document.createElement('details');details.open=true;details.append(text('summary','案例详情'));
    details.append(kvTable([['DOI',lesson.doi||lesson.accession],['说明',lesson.evidence_boundary_zh]]));
    if(lesson.conditions)details.append(text('h4','原文条件'),conditionSections(lesson.conditions));
    if(lesson.source_locators?.length)details.append(text('h4','原文位置'),kvTable([['原文位置',lesson.source_locators]]));
    const additional={...lesson};for(const key of ['conditions','title_zh','principle_zh','source_locators','doi','evidence_boundary_zh'])delete additional[key];
    details.append(scientificDetails(additional));card.append(details);return card;
}

let literatureData=null,literatureGeneration=0;
async function loadLiterature() {
    const generation=++literatureGeneration,view=activeLiteratureView,data=await fetchLiterature();
    if(generation!==literatureGeneration||activeLiteratureView!==view)return;
    if(!data||data.error){const message='读取失败：'+(data?.error||'没有返回数据');$('literature-results').textContent=message;renderToolError(view,message);return;}
    literatureData=data;
    const topic=learningTopic(),query=$('literature-query').value.trim().toLocaleLowerCase(),matches=value=>!query||JSON.stringify(value).toLocaleLowerCase().includes(query);
    const papers=(data.paper_cards||[]).filter(p=>topicHasPaper(topic,p.paper_id)&&matches(p));
    const cases=(data.reaction_lessons||[]).filter(l=>topicHasPaper(topic,l.paper_id)&&(matches(l)||matches((data.paper_cards||[]).find(p=>p.paper_id===l.paper_id)||{})));
    const items=view==='papers'?papers:cases,state=teachingPages[view];
    if(view==='papers'||view==='lessons'){
        state.total=items.length;state.offset=Math.min(state.offset,Math.max(0,Math.ceil(state.total/state.limit)-1)*state.limit);
        renderToolList(view,items.slice(state.offset,state.offset+state.limit));
        const prefix=view==='papers'?'paper':'lesson';
        pagination(prefix+'-pager-top',state,(offset,limit)=>{state.offset=offset;state.limit=limit;recordNavigation();loadLiterature();});
    }
    $('literature-results').textContent=`文献 ${papers.length} 篇 · 案例 ${cases.length} 个`;
    updateLiteratureContext();
}
$('library-search').onsubmit=event=>{event.preventDefault();resetLibraryPages();recordNavigation(true);loadLiterature();};
$('literature-query').oninput=()=>{resetLibraryPages();recordNavigation(true);loadLiterature();};
$('literature-topic').onchange=()=>{resetLibraryPages();recordNavigation(true);loadLiterature();};
$('literature-reset').onclick=()=>{$('literature-query').value='';$('literature-topic').value='';resetLibraryPages();recordNavigation(true);loadLiterature();};
for(const button of document.querySelectorAll('[data-literature-view]'))button.onclick=()=>switchLiteratureView(button.dataset.literatureView);
document.querySelector('.literature-views').addEventListener('keydown',event=>{
    const buttons=[...document.querySelectorAll('[data-literature-view]')],index=buttons.indexOf(document.activeElement);if(index<0)return;
    const next=event.key==='ArrowRight'?buttons[(index+1)%buttons.length]:event.key==='ArrowLeft'?buttons[(index+buttons.length-1)%buttons.length]:event.key==='Home'?buttons[0]:event.key==='End'?buttons.at(-1):null;
    if(next){event.preventDefault();switchLiteratureView(next.dataset.literatureView,true);}
});

PageRegistry.register('literature',()=>switchTeachingSection(activeTeachingSection,false,true));

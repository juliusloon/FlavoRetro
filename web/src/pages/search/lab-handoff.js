// A named paper is transferred only when its actual generated witness is present.
function labRootEvidence(tree){return tree?.children?.[0]?.metadata?.task022_evidence;}
function labSources(route){
 const found=new Map();
 for(const tree of [route.tree,...(route.source_variants||[]).map(v=>v.tree)]){
  const evidence=labRootEvidence(tree);if(evidence?.lab_case)found.set(evidence.lab_case.source_id,evidence);
 }
 return [...found.values()];
}
function appendSourceVariants(card,route){
 for(const evidence of labSources(route)){
  const section=document.createElement('details');section.className='source-realization';
  const name=evidence.lab_case.source_id==='Pei2019'?'Pei 2019 · 体外双酶开发':'Zhang 2015 · 选择性水解';
  section.append(text('summary',name+' · 查看文献实现与条件'),literatureEvidence(evidence));card.append(section);
 }
}
function renderLabDevelopment(result){
 const box=$('lab-development');box.replaceChildren();
 const cases=new Map();
 for(const route of displayedRoutes)for(const evidence of labSources(route))if(!cases.has(evidence.lab_case.source_id))cases.set(evidence.lab_case.source_id,{route,evidence});
 box.hidden=!cases.size;if(!cases.size)return;
 box.append(text('h2','从候选路线到虚拟实验开发'),text('p','搜索包含精确文献重现。选择开发案例与路线分数排序分别保留；进入实验室后继续核对方案与证据。','note'));
 for(const sid of ['Pei2019','Zhang2015']){
  const item=cases.get(sid);if(!item)continue;
  const {route,evidence}=item,row=div('lab-development-row');
  row.append(text('h3',sid==='Pei2019'?'主开发 · Pei 2019 · 体外双酶':'备选制备 · Zhang 2015 · 选择性水解'));
  row.append(text('p',sid==='Pei2019'?'AtUGT78D2 形成目标糖苷键；在实验室进一步研究 GmSUS 供体再生。':'从芦丁脱去末端鼠李糖；与加糖路线比较起始原料和反应方向。'));
  const doi=text('a','阅读论文');doi.href='https://doi.org/'+evidence.source.doi;doi.target='_blank';doi.rel='noopener';row.append(doi);
  const see=text('button','查看对应候选','secondary');see.type='button';see.onclick=()=>{selectedRouteIndex=displayedRoutes.findIndex(r=>r.route_id===route.route_id);renderRoutes(result,lastTeaching);$('routes').scrollIntoView({block:'start'});};row.append(see);
  const go=text('button','进入 FlavoGlycoLab','primary'),download=text('button','导出交接包','secondary');go.type=download.type='button';
  const obtain=()=>api('/api/lab-handoff?'+new URLSearchParams({run:result.run_id,route:route.route_id,source:sid}));
  go.onclick=()=>{
   const tab=window.open('about:blank','_blank');if(tab)tab.opener=null;
   go.disabled=true;obtain().then(packet=>{
    const lab=new URL(location.href);lab.port='8766';lab.pathname='/';lab.search='';lab.hash='retro='+encodeURIComponent(JSON.stringify(packet));
    if(tab)tab.location=lab.href;else location.assign(lab.href);
   }).catch(error=>{tab?.close();$('message').textContent='交接准备失败：'+error.message;}).finally(()=>go.disabled=false);
  };
  download.onclick=async()=>{download.disabled=true;try{downloadObject('FlavoRetro-'+sid+'-handoff.json',await obtain());}catch(error){$('message').textContent='交接导出失败：'+error.message;}finally{download.disabled=false;}};
  row.append(go,download);box.append(row);
 }
 for(const context of result.development_contexts||[]){const row=div('lab-development-row');row.append(text('h3','并行开发 · Niu 2024 · 工程菌'),text('p',context.description),text('p','同一产物的工程方案与对照研究；未作为独立分子逆合成动作。','note'));const link=text('a','阅读论文');link.href=context.source.url;link.target='_blank';link.rel='noopener';row.append(link);box.append(row);}
}

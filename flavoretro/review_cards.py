"""Local development review cards; annotations never modify active resources."""
import hashlib, json
from pathlib import Path
from html import escape
from collections import Counter
from rdkit import Chem, rdBase
from rdkit.Chem.Draw import rdMolDraw2D
from .topology import audit
from scripts.operate import write, digest

TASK = "TASK-015"
STRATA = {"glycoside_guide":"糖苷 · guide 支持", "glycoside_outside_guide":"糖苷 · guide 外发现",
          "domain_guide":"其他领域 · guide 支持", "domain_outside_guide":"其他领域 · guide 外发现",
          "invalid_or_partial":"不完整 / 泛化对照", "low_or_unknown":"低优先级 / 未知对照"}


def structure_svg(component):
    structure = component.get("structure", {})
    smiles = structure.get("canonical_smiles")
    with rdBase.BlockLogs():
        mol = Chem.MolFromSmiles(smiles) if smiles else None
    if mol is None:
        return '<div class="unparsed">结构无法显示；保留原状态：'+escape(str(structure.get("status")))+'</div>'
    # Highlight existing topology candidates, never a claimed reaction center.
    with rdBase.BlockLogs():
        sites = audit(smiles).get("sites", [])
    drawer = rdMolDraw2D.MolDraw2DSVG(460, 260)
    drawer.drawOptions().clearBackground = False
    drawer.DrawMolecule(mol, highlightAtoms=[], highlightBonds=[s["bond_index"] for s in sites],
                        highlightBondColors={s["bond_index"]:(0.91,0.66,0.19) for s in sites})
    drawer.FinishDrawing()
    svg = drawer.GetDrawingText()
    return svg[svg.index('<svg'):].replace('<svg ', '<svg role="img" aria-label="反应组分结构；黄色键为拓扑候选" ',1)


def build(review_path, references_path, output):
    review_path, references_path, output = map(Path, (review_path,references_path,output))
    if (output/'index.html').exists():
        raise ValueError('review output already exists; preserve prior version')
    rows = [json.loads(line) for line in review_path.read_text().splitlines()]
    if len(rows)!=60 or len({r['id'] for r in rows})!=60:
        raise ValueError('expected 60 unique frozen review samples')
    if any(any(v is not None for v in r['annotation'].values()) for r in rows):
        raise ValueError('input annotations must remain blank')
    refs = json.loads(references_path.read_text())
    cards = []
    for r in rows:
        record=r['input_record']; f=record['raw']['fields']; title=f.get('RXN:VAR(1):REFERENCE(1):TITLE','')
        components=[dict(c,svg=structure_svg(c)) for c in record['components']]
        cards.append(dict(r, components_drawn=components, reference=refs.get(title,{})))
    payload={'schema_version':1,'protocol':'task015-development-review-v1','input_sha256':digest(review_path),
             'annotation_fields':list(rows[0]['annotation']),'strata':STRATA,'records':cards,
             'human_review_status':'not_performed','production_eligible':False,'split':'development_exposed'}
    # JSON script blocks need explicit HTML delimiter escaping; all source strings use textContent.
    packed=json.dumps(payload,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    html=TEMPLATE.replace('__PAYLOAD__',packed)
    write(TASK,str(output/'index.html'),html)
    summary={'cards':len(rows),'strata':dict(Counter(r['stratum'] for r in rows)),
             'distinct_reference_titles':len(refs),'procedure_present':sum(bool(r['input_record']['raw']['fields'].get('RXN:VAR(1):EXP_PROC')) for r in rows),
             'references':dict(Counter(x['status'] for x in refs.values())),
             'annotations_filled_by_agent':0,'primary_reactions_verified':0,'production_records':0}
    write(TASK,str(output/'summary.json'),json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    manifest={'task':TASK,'input_review_path':str(review_path),'input_review_sha256':digest(review_path),
              'references_sha256':digest(references_path),'code_sha256':digest(__file__),
              'outputs':{'index.html':digest(output/'index.html'),'summary.json':digest(output/'summary.json')},
              'raw_or_restricted_payload':'local only, do not commit/share publicly',
              'annotations':'user-submitted drafts; separate validation required; never production admission'}
    write(TASK,str(output/'manifest.json'),json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    return summary


TEMPLATE = r"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>FlavoRetro · 开发审核卡片</title><style>
:root{color-scheme:light;--ink:#142e39;--muted:#52666c;--line:#cbd7d9;--accent:#176360;--bg:#f3f6f4}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,sans-serif}header{background:#123e43;color:white;padding:22px max(20px,calc((100vw - 1240px)/2))}h1{font-size:25px;margin:0 0 6px}header p{margin:0;color:#d4e9e7}main{max-width:1280px;margin:22px auto;padding:0 20px;display:grid;grid-template-columns:260px minmax(0,1fr);gap:22px}aside{align-self:start;position:sticky;top:18px}.panel,article{background:white;border:1px solid var(--line);border-radius:12px;padding:20px;margin-bottom:18px}h2{font-size:20px;margin:0 0 14px}h3{font-size:17px;margin:16px 0 8px}p{margin:8px 0}.muted,small{color:var(--muted)}button,select,input,textarea{font:inherit;border:1px solid #a8bbbe;border-radius:7px;min-height:44px;padding:9px 11px;max-width:100%;background:white;color:var(--ink)}button{cursor:pointer}button:hover{background:#e6f2ee}button.primary{background:var(--accent);color:white;border-color:var(--accent)}button:disabled{opacity:.45;cursor:default}label{display:block;font-size:14px;margin:12px 0 5px}input,textarea,select{width:100%}textarea{min-height:94px;resize:vertical}button:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible,a:focus-visible{outline:3px solid #ca8109;outline-offset:3px}a{color:#146661;overflow-wrap:anywhere}.actions{display:flex;flex-wrap:wrap;gap:9px;margin-top:12px}.actions button{flex:1}.badge{display:inline-block;padding:3px 10px;background:#e5efeb;border-radius:20px;margin:0 6px 8px 0;font-size:13px}.warn{padding:12px;border-left:4px solid #bd7a14;background:#fff5df}.reaction{display:grid;grid-template-columns:minmax(0,1fr) 36px minmax(0,1fr);gap:8px;align-items:center}.molecule svg{width:100%;height:auto;max-height:260px}.molecule{border:1px solid #e1e8e7;border-radius:7px;padding:5px;margin:7px 0}.arrow{text-align:center;font-size:26px}.smiles,pre,.mono{font:12px/1.5 ui-monospace,monospace;overflow-wrap:anywhere;white-space:pre-wrap;word-break:break-word}.unparsed{padding:30px 12px;background:#fff0e9}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px 18px}.full{grid-column:1/-1}details{border-top:1px solid var(--line);padding-top:12px;margin-top:15px}summary{cursor:pointer;min-height:44px;padding:10px 0}.procedure{white-space:pre-wrap;overflow-wrap:anywhere;font-size:14px}.status{min-height:28px;color:var(--accent);font-weight:600}#status.error{color:#a33225}.progress{font-size:24px;font-weight:600}#cards>p{padding:20px}footer{padding:15px 20px 30px;max-width:1280px;margin:auto;color:var(--muted);font-size:13px}@media(max-width:850px){main{display:block;padding:0 12px;margin-top:14px}aside{position:static}.panel,article{padding:16px}.form-grid{grid-template-columns:1fr}.full{grid-column:auto}.reaction{grid-template-columns:1fr}.arrow{transform:rotate(90deg)}header{padding:20px 16px}h1{font-size:22px}}@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto}}
</style></head><body><header><h1>FlavoRetro · 开发审核卡片</h1><p>60 条固定样本 · 30 条糖苷重点 · 先看结构，再核对出处与具体实验</p></header>
<main><aside><div class="panel"><h2>审核进度</h2><div id="progress" class="progress"></div><p class="muted">进度按“填写过”计数，不代表审核通过。</p><label for="filter">样本范围</label><select id="filter"><option value="all">全部 60 条</option><option value="glycoside">糖苷重点 30 条</option></select><label for="pending">填写状态</label><select id="pending"><option value="all">全部状态</option><option value="blank">尚未填写</option><option value="filled">填写过</option></select><label for="find">搜索标题 / 样本 ID</label><input id="find" placeholder="输入关键词"><div class="actions"><button id="prev">上一条</button><button id="next">下一条</button></div><p id="position"></p></div>
<div class="panel"><h2>保存与交接</h2><p class="muted">保存到当前浏览器。请定期导出 JSON 备份；导出文件交给 Cano 后，再单独校验并生成审核版本。</p><button id="export" class="primary">导出审核 JSON</button><label for="import">导入此前导出的 JSON</label><input id="import" type="file" accept="application/json,.json"><p id="status" role="status" aria-live="polite"></p></div></aside>
<div><div class="panel"><h2>这一轮需要审核什么</h2><p><b>结构初筛：</b>是否属于黄酮或相关合成步骤？糖苷连接在哪里、是 O 还是 C？不要把“分子已有糖”直接当作“这一步形成糖苷键”。</p><p><b>原文核对：</b>找到具体化合物/步骤/表格行，确认反应方向、完整参与物、条件、收率归属与立体信息。没拿到原文时，先选“保留候选”或“需裁决”，并注明缺什么。</p><p class="warn">这是已暴露的开发校准样本，机器建议可见。来源身份匹配、填写、保存与导出都不自动产生 gold 或生产准入。黄色键仅为拓扑候选。</p></div><div id="cards"></div></div></main><footer>原始 TASK-014 样本保持只读。本页不联网、不修改项目数据、不执行搜索。数据与实验描述含本地 SciFinder 导出内容，请勿公开分发。</footer>
<script id="payload" type="application/json">__PAYLOAD__</script><script>
'use strict';
const data=JSON.parse(document.querySelector('#payload').textContent), key='flavoretro-review:'+data.input_sha256;
const el=s=>document.querySelector(s), records=data.records, byId=new Map(records.map(r=>[r.id,r]));
const enums={domain_relevance:['relevant','supporting_step','out_of_scope','uncertain'],glycoside_connection:['O','C','sugar_sugar','other','none','uncertain'],specific_experimental_instance:[true,false,'uncertain'],reactant_product_confirmed:[true,false,'uncertain'],conditions_yield_assignment:['assigned','absent','ambiguous','not_checked'],stereo_status:['confirmed','unspecified_in_source','conflicting','not_checked'],decision:['retain_candidate','reject_claim','primary_checked','needs_adjudication']};
let state={annotations:{},history:[]}, visible=[], pos=0, lastPersisted=true;
function message(t,error=false){el('#status').textContent=t;el('#status').className=error?'error':''}
function filled(a){return a&&Object.values(a).some(v=>v!==null&&v!==''&&!(Array.isArray(v)&&!v.length))}
function blank(){return Object.fromEntries(data.annotation_fields.map(k=>[k,null]))}
function validate(a){
 if(!a||typeof a!=='object'||Array.isArray(a)||Object.keys(a).some(k=>!data.annotation_fields.includes(k)))throw Error('标注字段不符合协议');
 for(const [k,v] of Object.entries(a)){
  if(v===null)continue;
  if(enums[k]&&!enums[k].includes(v))throw Error('非法标签：'+k);
  if(k==='transformation_labels'){if(!Array.isArray(v)||v.some(x=>!['glycosyl_related','scaffold_construction','scaffold_interconversion','substituent_modification','protection_deprotection','other_related','out_of_scope_or_unknown','uncertain'].includes(x)))throw Error('反应分类应使用协议中的总分类 ID 列表')}
  else if(!enums[k]&&typeof v!=='string')throw Error('非法字段类型：'+k);
 }
 if(a.reviewed_at&&!/^\d{4}-\d{2}-\d{2}T/.test(a.reviewed_at))throw Error('人工审核时间需为 ISO 日期时间');
 if(a.primary_source_sha256&&!/^[a-f0-9]{64}$/i.test(a.primary_source_sha256))throw Error('原文 SHA-256 格式错误');
 if(a.decision==='primary_checked'&&(!a.reviewer_id||!a.reviewed_at||!a.primary_source_locator||!a.evidence_excerpt||a.specific_experimental_instance!==true||a.reactant_product_confirmed!==true||!['assigned','absent'].includes(a.conditions_yield_assignment)||!['confirmed','unspecified_in_source'].includes(a.stereo_status)))throw Error('原文已核对需审核者、时间、原文定位/证据及具体实例、结构、条件、立体信息确认');
 return {...blank(),...a};
}
function envelope(){return {schema_version:1,protocol:data.protocol,input_sha256:data.input_sha256,split:'development_exposed',production_eligible:false,human_review_status:'user_submitted_unvalidated',records:records.map(r=>({id:r.id,source_sha256:r.input_record.source_sha256,source_locator:r.input_record.locator,annotation:state.annotations[r.id]||blank()})),history:state.history}}
function parseEnvelope(x){
 if(x.schema_version!==1||x.protocol!==data.protocol||x.input_sha256!==data.input_sha256||x.split!=='development_exposed'||x.production_eligible!==false||x.human_review_status!=='user_submitted_unvalidated'||!Array.isArray(x.records)||x.records.length!==records.length)throw Error('不是本审核包的有效导出；未导入');
 const annotations={},seen=new Set();for(const r of x.records){const original=byId.get(r.id);if(!original||seen.has(r.id)||r.source_sha256!==original.input_record.source_sha256||r.source_locator!==original.input_record.locator)throw Error('样本身份/来源不一致；未导入');seen.add(r.id);annotations[r.id]=validate(r.annotation)}
 if(!Array.isArray(x.history))throw Error('缺少审核历史');
 return {annotations,history:x.history};
}
try{const saved=localStorage.getItem(key);if(saved)state=parseEnvelope(JSON.parse(saved))}catch(e){message('浏览器缓存未载入：'+e.message,true)}
function store(next){state=next;try{localStorage.setItem(key,JSON.stringify(envelope()));lastPersisted=true}catch(e){lastPersisted=false}return true}
function text(tag,t,cls){const n=document.createElement(tag);n.textContent=t??'';if(cls)n.className=cls;return n}
function selectField(form,k,title,options){const wrap=document.createElement('div'),label=text('label',title);label.htmlFor=k;const s=document.createElement('select');s.id=k;s.name=k;s.append(new Option('未填写',''));for(const [v,t] of options)s.append(new Option(t,String(v)));wrap.append(label,s);form.append(wrap)}
function inputField(form,k,title,placeholder,multi=false){const wrap=document.createElement('div');wrap.className='full';const label=text('label',title);label.htmlFor=k;const n=document.createElement(multi?'textarea':'input');n.id=k;n.name=k;n.placeholder=placeholder;wrap.append(label,n);form.append(wrap)}
function render(){
 visible=records.filter(r=>(el('#filter').value==='all'||(el('#filter').value==='glycoside'?r.stratum.startsWith('glycoside_'):r.stratum===el('#filter').value))&&(el('#pending').value==='all'||(el('#pending').value==='filled'?filled(state.annotations[r.id]):!filled(state.annotations[r.id])))&&(r.id+' '+r.reference.title).toLowerCase().includes(el('#find').value.toLowerCase()));
 pos=Math.min(pos,Math.max(0,visible.length-1));el('#progress').textContent=Object.values(state.annotations).filter(filled).length+' / 60 已填写';el('#position').textContent=visible.length?`当前 ${pos+1} / ${visible.length}`:'没有匹配样本';el('#prev').disabled=pos===0;el('#next').disabled=pos>=visible.length-1;el('#cards').replaceChildren();
 if(!visible.length){el('#cards').append(text('p','没有匹配样本。'));return}
 const r=visible[pos],record=r.input_record,f=record.raw.fields,a=state.annotations[r.id]||blank(), article=document.createElement('article');article.dataset.id=r.id;
 article.append(text('span',data.strata[r.stratum],'badge'),text('span','人工状态：'+(filled(a)?'已填写 · 待单独校验':'未填写'),'badge'),text('h2',r.reference.title.replaceAll('\\n',' ')||'标题未报告'),text('p','样本 ID：'+r.id,'mono'));
 const rx=document.createElement('div');rx.className='reaction';
 for(const role of ['reactant','product']){if(role==='product')rx.append(text('div','→','arrow'));const side=document.createElement('div');side.append(text('h3',role==='reactant'?'原始记录 · 反应物':'原始记录 · 产物'));for(const c of r.components_drawn.filter(c=>c.role===role)){const box=document.createElement('div');box.className='molecule';box.innerHTML=c.svg;box.append(text('p',c.structure.canonical_smiles||'SMILES 未获得','smiles'));side.append(box)}rx.append(side)}article.append(rx);
 const outcome=record.outcome;article.append(text('p','导出收率：'+(outcome.is_missing?'未报告 / 未归属':(outcome.value===null?String(outcome.raw):String(outcome.value)+'%'))+'；原始值：'+JSON.stringify(outcome.raw)+'；原文归属尚未核实。'));
 article.append(text('h3','来源与实验信息'),text('p',f['RXN:VAR(1):REFERENCE(1):AUTHOR']||'作者未报告'),text('p',f['RXN:VAR(1):REFERENCE(1):CITATION']||'引用未报告'));
 if(r.reference.patent_number){const link=text('a','打开专利 · 编号来自原始引用，未核实');link.href='https://patents.google.com/patent/'+r.reference.patent_number;link.target='_blank';link.rel='noopener';article.append(link)}else if(r.reference.doi){const link=text('a','打开 DOI · 仅文献身份导航');link.href='https://doi.org/'+encodeURI(r.reference.doi);link.target='_blank';link.rel='noopener';article.append(link)}else article.append(text('p','DOI 尚未可靠匹配，保留原始引用；需进一步定位。','warn'));
 const refStatus={metadata_matched:'标题与年份匹配',metadata_matched_title_variant:'标题变体及年/卷/页/首作者匹配',metadata_matched_article_from_supplement:'已由补充材料元数据定位正文 DOI',patent_locator_as_reported:'专利号来自原始引用，未核实',manual_needed:'文献身份待核对',lookup_failed:'元数据查询失败'};article.append(text('p','出处导航：'+(refStatus[r.reference.status]||r.reference.status)+'；具体反应 / 正文 / SI 均未自动核实。','muted'));if(r.reference.status==='manual_needed'&&r.reference.candidates?.length){const d=document.createElement('details');d.append(text('summary','待核实的文献匹配线索（可能是不同文献或译本）'));for(const candidate of r.reference.candidates){d.append(text('p',candidate.title+'；年份：'+candidate.years.join('/')+'；DOI：'+candidate.doi))}article.append(d)}
 const proc=f['RXN:VAR(1):EXP_PROC'];if(proc){const d=document.createElement('details');d.append(text('summary','查看 SciFinder 导出实验步骤（需与原文核对）'),text('p',proc.replaceAll('\\n',' '),'procedure'));article.append(d)}else article.append(text('p','此条没有导出实验步骤。请从原文/SI核对；无法取得时注明缺口。','warn'));
 const provenance=document.createElement('details');provenance.append(text('summary','查看本地来源定位与原始字段'),text('pre',JSON.stringify({source_path:record.source_path,source_sha256:record.source_sha256,locator:record.locator,fields:f},null,2)));article.append(provenance);
 const suggestion=document.createElement('details');suggestion.append(text('summary','查看机器候选建议（开发校准可见）'),text('pre',JSON.stringify(r.machine_suggestion,null,2)));article.append(suggestion);
 article.append(text('h3','你的审核记录'));const form=document.createElement('form');form.className='form-grid';form.id='review-form';
 selectField(form,'domain_relevance','领域相关性',[['relevant','黄酮领域相关'],['supporting_step','相关合成的支持步骤'],['out_of_scope','范围外'],['uncertain','不确定']]);
 selectField(form,'glycoside_connection','糖苷连接（位点与底物/产物差别写入证据）',[['O','O-糖苷'],['C','C-糖苷'],['sugar_sugar','糖—糖连接'],['other','其他连接'],['none','没有糖苷连接'],['uncertain','不确定']]);
 selectField(form,'specific_experimental_instance','是否找到具体实验实例',[[true,'是'],[false,'否 / 通式'],['uncertain','不确定']]);
 selectField(form,'reactant_product_confirmed','原文反应物 / 产物 / 方向是否确认',[[true,'已核对确认'],[false,'不一致'],['uncertain','不确定']]);
 selectField(form,'conditions_yield_assignment','条件与收率归属',[['assigned','已确认归属'],['absent','原文明确未提供'],['ambiguous','归属有歧义'],['not_checked','未核对']]);
 selectField(form,'stereo_status','立体信息',[['confirmed','已确认'],['unspecified_in_source','原文未指定'],['conflicting','存在冲突'],['not_checked','未核对']]);
 selectField(form,'decision','本次处理意见',[['retain_candidate','保留候选，待进一步核对'],['reject_claim','否决当前判断（原数据仍保留）'],['primary_checked','具体原文已核对（需填完整证据）'],['needs_adjudication','需裁决 / 补来源']]);
 inputField(form,'transformation_labels','反应总分类（可空；多个 ID 用逗号分隔）','glycosyl_related / scaffold_construction / scaffold_interconversion / substituent_modification / protection_deprotection / other_related / out_of_scope_or_unknown / uncertain');
 inputField(form,'primary_source_locator','原文定位','DOI/专利号 + 正文或 SI + 页码 / scheme / example / 化合物编号');
 inputField(form,'evidence_excerpt','核对证据与糖苷位点','原文短摘录 / 具体证据；注明底物与产物、糖身份、连接位置和本步是否改变糖苷键',true);
 inputField(form,'primary_source_sha256','本地原文 SHA-256（未取得可空）','64 位哈希');
 inputField(form,'reviewer_id','实际审核者姓名或代号','请填写你的姓名/代号');
 inputField(form,'reviewed_at','实际人工审核时间（初筛草稿可空）','ISO 格式，例如 2026-09-27T10:30:00+08:00');
 inputField(form,'disagreement','歧义、分歧与缺失材料','缺原文 / CAS 对应不一致 / 立体未定 / 收率无法归属等',true);
 for(const k of data.annotation_fields){const n=form.elements.namedItem(k);if(n&&a[k]!==null)n.value=Array.isArray(a[k])?a[k].join(', '):String(a[k])}
 const save=document.createElement('button');save.type='submit';save.className='primary full';save.textContent='保存当前审核草稿';form.append(save);
 form.onsubmit=e=>{e.preventDefault();try{let next=blank();for(const k of data.annotation_fields){const n=form.elements.namedItem(k),v=n?n.value.trim():'';next[k]=v||null;if(v&&k==='transformation_labels')next[k]=v.split(',').map(x=>x.trim()).filter(Boolean);if(v&&['specific_experimental_instance','reactant_product_confirmed'].includes(k)&&v!=='uncertain')next[k]=v==='true'}next=validate(next);const history=[...state.history,{id:r.id,previous:state.annotations[r.id]||blank(),next,changed_at:new Date().toISOString(),action:'user_save'}];if(store({annotations:{...state.annotations,[r.id]:next},history})){message(lastPersisted?'已保存草稿；请导出 JSON 备份。':'浏览器无法持久保存；草稿仍在本页内存，请立即导出 JSON。',!lastPersisted);render()}}catch(e){message(e.message,true)}};article.append(form);el('#cards').append(article);
}
for(const [value,label] of Object.entries(data.strata))el('#filter').append(new Option(label,value));
for(const id of ['filter','pending','find'])el('#'+id).addEventListener(id==='find'?'input':'change',()=>{pos=0;render()});
el('#prev').onclick=()=>{pos--;render()};el('#next').onclick=()=>{pos++;render()};
el('#export').onclick=()=>{const b=new Blob([JSON.stringify(envelope(),null,2)],{type:'application/json'}),u=URL.createObjectURL(b),a=document.createElement('a');a.href=u;a.download='flavoretro-review-task015.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);message('已导出；这是待校验的人工提交，不会自动升级数据。')};
el('#import').onchange=async e=>{try{const file=e.target.files[0];if(!file)return;if(file.size>5*1024*1024)throw Error('文件超过 5 MB');const parsed=parseEnvelope(JSON.parse(await file.text()));const annotations={...state.annotations},history=[...state.history];for(const r of records){if(filled(parsed.annotations[r.id])){history.push({id:r.id,previous:annotations[r.id]||blank(),next:parsed.annotations[r.id],changed_at:new Date().toISOString(),action:'user_import'});annotations[r.id]=parsed.annotations[r.id]}}if(store({annotations,history})){message(lastPersisted?'已导入相同样本的非空标注；此前版本保留在历史。':'已导入到本页内存；浏览器无法持久保存，请立即导出 JSON。',!lastPersisted);render()}}catch(e){message('导入失败：'+e.message,true)}finally{e.target.value=''}};
render();
</script></body></html>"""

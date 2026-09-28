"""Assemble 60 delegated reviews without modifying original annotation cards."""
import json,csv,io
from collections import Counter
from pathlib import Path
from html import escape as E
from datetime import datetime,timezone
from flavoretro.review_cards import structure_svg
from scripts.operate import write,digest
T='TASK-015-P1';O=Path('outputs/review/task015-p1/final-v2')
if O.exists():raise ValueError('Preserve completed version')
def jl(p):return [json.loads(l) for l in Path(p).read_text().splitlines()]
def out(n,v):write(T,str(O/n),v)
def js(v):return json.dumps(v,ensure_ascii=False,indent=2)
inputs=jl('outputs/triage/task014-final/review.jsonl');rows=[];hashes={}
for n in range(1,4):
 p=f'outputs/review/task015-p1/agents/batch{n}/review.jsonl';b=jl(p);a=json.loads(Path(f'outputs/review/task015-p1/assignments/batch{n}.json').read_text())
 assert len(b)==20 and {r['id'] for r in b}=={r['id'] for r in a}
 rows+=b;hashes[p]=digest(p)
rows.sort(key=lambda r:r['card_number'])
assert len(rows)==60 and len({r['id'] for r in rows})==60
assert [r['id'] for r in rows]==[r['id'] for r in inputs]
labels={'scaffold_construction':'骨架构建','scaffold_interconversion':'骨架互变','glycosyl_related':'糖苷相关','substituent_modification':'取代基修饰','protection_deprotection':'保护/脱保护','other_related':'其他相关','out_of_scope_or_unknown':'领域外/未知','uncertain':'暂不能确定'}
dec={'primary_checked':'具体原文实例已核对','retain_candidate':'保留候选','needs_adjudication':'冲突/缺项待解决','reject_claim':'否决特定声明'}
lev={'primary_instance_verified':'具体原文实例','export_procedure_supported':'已有导出实验段支持','bibliography_or_abstract_only':'文献/摘要/路线层支持','unavailable':'原文未取得','conflict':'来源或结构冲突'}
for r in rows:
 assert r['reviewer_type']=='agent' and r['review_mode']=='human_delegated_agent_review'
 assert r['human_review_status']=='not_performed' and r['production_eligible'] is False and r['split']=='development_exposed'
 assert r['transformation_labels'] and set(r['transformation_labels'])<=set(labels)
 assert len(r['transformation_description_zh'])>20 and r['decision_reason_zh']
 for k in ['structure_assessment','source_assessment','conditions_yield_assessment','glycoside_assessment']:assert r[k]
 for s in r['source_assessment']['sources']:
  assert s['claim_supported']
  if not s['url'].startswith(('https://','http://')):
   assert s['url'].startswith('data/raw/') and Path(s['url']).is_file()
   s['local_path']=str(Path(s['url']).resolve())
 if r['decision']=='primary_checked':assert r['source_assessment']['status']=='primary_instance_verified'
 r['review_status']='agent_review_completed';r['root_review']={'reviewer_id':'Cano/root','completed_at':datetime.now(timezone.utc).isoformat(),'scope':'逐条检查审核说明、ID和证据等级；重点复核收率语义、缺项、撤稿和糖苷构键边界；不表示独立人审。'}
summary={'cards':60,'agent_review_completed':60,'decisions':dict(Counter(r['decision'] for r in rows)),'source_assessment':dict(Counter(r['source_assessment']['status'] for r in rows)),'domain_relevance':dict(Counter(r['domain_relevance'] for r in rows)),'human_reviewed':0,'production':0,'development_exposed':60,'material_preference':'existing materials and public webpages only; no paper/SI downloads'}
out('review.jsonl',''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows));out('summary.json',js(summary)+'\n')
buf=io.StringIO();keys=['card_number','id','reviewer_id','reviewer_type','review_mode','decision','domain_relevance','transformation_labels','transformation_description_zh','source_assessment','conditions_yield_assessment','decision_reason_zh','needs_user_material','human_review_status','split','production_eligible'];w=csv.DictWriter(buf,fieldnames=keys,delimiter='\t',lineterminator='\n');w.writeheader()
for r in rows:w.writerow({k:json.dumps(r[k],ensure_ascii=False) if isinstance(r[k],(list,dict)) else r[k] for k in keys})
out('review.tsv',buf.getvalue())
def source_link(s):
 if 'local_path' in s:return '<b>'+E(s['title'])+'</b><br><code>'+E(s['local_path'])+'</code>'
 return '<a target="_blank" rel="noopener noreferrer" href="'+E(s['url'],quote=True)+'">'+E(s['title'])+'</a>'
def detail(title,obj):return '<details><summary>'+E(title)+'</summary><pre>'+E(js(obj))+'</pre></details>'
cards=[]
for r,inp in zip(rows,inputs):
 title=inp['input_record']['raw']['fields'].get('RXN:VAR(1):REFERENCE(1):TITLE','')
 mols=''.join('<div class="mol"><b>'+E(c['role'])+'</b>'+structure_svg(c)+'</div>' for c in inp['input_record']['components'])
 refs=''.join('<li>'+source_link(s)+'<br>'+E(s['evidence_locator'])+'<br>'+E(s['claim_supported'])+'</li>' for s in r['source_assessment']['sources'])
 search=E((str(r['card_number'])+' '+title+' '+r['transformation_description_zh']).lower(),quote=True)
 cards.append(f'<article id="card-{r["card_number"]}" data-decision="{r["decision"]}" data-source="{r["source_assessment"]["status"]}" data-search="{search}"><h2>#{r["card_number"]:02d} · {dec[r["decision"]]}</h2><p>{E(title)}</p><p><b>反应总分类：</b>{E(" / ".join(labels[x] for x in r["transformation_labels"]))}</p><p class="finding">{E(r["transformation_description_zh"])}</p><div class="structures">{mols}</div><p><b>处置理由：</b>{E(r["decision_reason_zh"])}</p><p><b>糖苷连接变化：</b>{E(r["glycoside_assessment"]["bond_change"])}</p><p><b>收率解释：</b>{E(r["conditions_yield_assessment"]["reason"])}</p><p><b>证据等级：{lev[r["source_assessment"]["status"]]}</b> — {E(r["source_assessment"]["reason"])}</p><ul>{refs}</ul>'+detail('完整审核字段与缺失证据（不代表都需你补）',r)+detail('原始记录与机器建议（保持不改）',inp)+f'<p class="meta">{E(r["reviewer_id"])} · 委托代理审核 · development_exposed</p></article>')
opts=lambda d:''.join(f'<option value="{k}">{v}</option>' for k,v in d.items())
html="""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>60条代理审核结果 · FlavoRetro</title><style>
*{box-sizing:border-box}body{margin:0;color:#19383c;background:#eff4f2;font:16px/1.65 system-ui,sans-serif}header{padding:28px max(20px,calc((100vw - 1120px)/2));background:#183f46;color:#fff}h1{font-size:28px}header a{color:#d4f1ea}main{max-width:1160px;margin:24px auto;padding:0 20px}.toolbar{display:flex;gap:12px;flex-wrap:wrap;padding:16px;background:#fff;border-radius:12px}label{display:flex;flex-direction:column;font-size:14px}input,select{font:inherit;min-height:44px;max-width:100%;padding:8px;border:1px solid #7b9291;border-radius:5px}article{margin:24px 0;padding:24px;background:#fff;border:1px solid #c4d4d0;border-radius:12px;overflow-wrap:anywhere}article[hidden]{display:none}h2{font-size:23px}.finding{font-size:18px;font-weight:600}.structures{display:flex;flex-wrap:wrap;gap:12px}.mol{flex:1 1 330px;min-width:0;max-width:100%;padding:8px;border:1px solid #e0e9e6;border-radius:8px}.mol svg{display:block;width:100%;height:auto;max-height:300px}a{color:#065c73}details{margin:12px 0;background:#f4f7f6;padding:10px;border-radius:6px}summary{cursor:pointer;font-weight:600;min-height:30px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.6 ui-monospace,monospace}.meta{font-size:13px}li{margin:8px 0}@media(max-width:600px){article{padding:16px}.mol{flex-basis:100%}h1{font-size:23px}}
</style></head><body><header><h1>60 条卡片：代理审核已完成</h1><p>9 条具体原文实例已核对 · 39 条保留候选 · 7 条冲突/缺项待解决 · 5 条否决特定声明</p><p>Cano 与三位子 agent 按所有者委托审核；具体原文核对范围见各卡。这不表示 60 条全部通过，也不冒充独立人审或实验验证。</p><p><a href="review.jsonl" download>下载完整 JSONL</a> · <a href="review.tsv" download>下载 TSV</a> · 只读结果页，原人工审核页及浏览器草稿保持独立。</p></header><main><div class="toolbar"><label>搜索卡号/反应/标题<input id="q" type="search" placeholder="如：糖苷、57、vitexin"></label><label>处置<select id="decision"><option value="">全部处置</option>"""+opts(dec)+"""</select></label><label>证据等级<select id="source"><option value="">全部证据</option>"""+opts(lev)+"""</select></label><p id="count" aria-live="polite">显示 60 / 60 条</p></div><p>黄色键只表示既有糖拓扑候选，不表示本步新构键。总分类可多选；糖苷相关包含形成、断裂及后修饰，以具体审核说明为准。</p>"""+''.join(cards)+"""</main><script>
const cards=[...document.querySelectorAll('article')],q=document.querySelector('#q'),d=document.querySelector('#decision'),s=document.querySelector('#source');function filter(){let n=0;for(const c of cards){let match=(!d.value||c.dataset.decision===d.value)&&(!s.value||c.dataset.source===s.value)&&(!q.value||c.dataset.search.includes(q.value.toLowerCase().trim()));c.hidden=!match;n+=match;}document.querySelector('#count').textContent=`显示 ${n} / 60 条`;}for(const el of [q,d,s])el.addEventListener('input',filter);
</script></body></html>"""
payload=json.dumps({'review.jsonl':(O/'review.jsonl').read_text(),'review.tsv':(O/'review.tsv').read_text()},ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
html=html.replace('</script>','const downloads='+payload+';document.querySelectorAll(\"a[download]\").forEach(a=>a.addEventListener(\"click\",e=>{e.preventDefault();const name=a.getAttribute(\"href\"),url=URL.createObjectURL(new Blob([downloads[name]],{type:\"text/plain;charset=utf-8\"})),link=document.createElement(\"a\");link.href=url;link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}));</script>')
out('index.html',html)
manifest={'task':T,'input_review_sha256':digest('outputs/triage/task014-final/review.jsonl'),'agent_review_hashes':hashes,'assembler_sha256':digest(__file__),'outputs':{p.name:digest(p) for p in O.iterdir() if p.is_file()},'restriction':'Local database-derived evidence; do not commit or publish','human_review_status':'not_performed'}
out('manifest.json',js(manifest)+'\n');print(js(summary))

let reactionEvidenceOffset = 0, reactionEvidenceGeneration = 0, reactionEvidenceLimit=25;
function evidenceCard(record){
            const source=record.source || {}, card=div('paper-card');card.id=toolItemId('evidence',record);
            card.append(text('h3',record.reaction_id || record.id || source.title || '来源反应'));
            if (source.title) card.append(text('p',source.title));
            const sourceLink=source.url || (source.doi?'https://doi.org/'+source.doi:'');
            if (/^https?:\/\//.test(sourceLink)) {
                const a=text('a',source.doi || '查看原始来源');a.href=sourceLink;a.target='_blank';a.rel='noopener';card.append(a);
            }
            card.append(kv('报告产率',record.yield_reported_text || (record.yield_value == null ? (YIELD_STATUS_ZH[record.yield_status] || '未报告') : `${record.yield_value} ${record.yield_unit || ''}`)));
            const rawProducts=record.products || [], products=Array.isArray(rawProducts)?rawProducts:[rawProducts];
            for (const product of products) {
                const smiles=typeof product==='string'?product:product.smiles;
                if (!smiles || record.qc?.structures_parseable!==true) continue;
                const button=text('button','装入目标 · '+(product.name || '已解析产物'),'secondary');button.type='button';
                button.onclick=()=>{$('smiles').value=smiles;$('preset').value='';$('tab-search').click();$('preview').click();
                    $('message').textContent='目标已装入，可预览结构或开始搜索。';};
                card.append(button);
            }
            const details=document.createElement('details');details.open=true;details.append(text('summary','查看反应详情'));
            details.append(scientificDetails(record),sourceFacts(record.source));if(record.qc?.issues?.length)details.append(kv('待核对问题',factText(record.qc.issues)));card.append(details);return card;
}
async function loadReactionEvidence() {
    const generation=++reactionEvidenceGeneration;
    try {
        const q=encodeURIComponent($('reaction-evidence-query').value), status=encodeURIComponent($('reaction-evidence-status').value);
        const data=await api(`/api/reaction-evidence?q=${q}&status=${status}&offset=${reactionEvidenceOffset}&limit=${reactionEvidenceLimit}`);
        if (generation!==reactionEvidenceGeneration||activeLiteratureView!=='evidence') return;
        const lastOffset=Math.max(0,(Math.ceil(data.total/reactionEvidenceLimit)-1)*reactionEvidenceLimit);if(reactionEvidenceOffset>lastOffset){reactionEvidenceOffset=lastOffset;return loadReactionEvidence();}
        $('reaction-evidence-summary').textContent=`共 ${data.total} 条反应记录`;
        const state={offset:reactionEvidenceOffset,limit:reactionEvidenceLimit,total:data.total};pagination('evidence-pager-top',state,(offset,limit)=>{reactionEvidenceOffset=offset;reactionEvidenceLimit=limit;recordNavigation();loadReactionEvidence();});
        renderToolList('evidence',data.records||[]);
    } catch (error) {
        if (generation!==reactionEvidenceGeneration) return;
        $('reaction-evidence-summary').textContent='新增反应读取失败：'+error.message;
        renderToolError('evidence','新增反应读取失败：'+error.message);
    }
}
$('reaction-evidence-filters').onsubmit=event=>{event.preventDefault();reactionEvidenceOffset=0;recordNavigation(true);loadReactionEvidence();};
$('reaction-evidence-status').onchange=()=>{reactionEvidenceOffset=0;recordNavigation(true);loadReactionEvidence();};
$('reaction-evidence-query').oninput=()=>{reactionEvidenceOffset=0;recordNavigation(true);loadReactionEvidence();};
$('reaction-evidence-reset').onclick=()=>{$('reaction-evidence-query').value='';$('reaction-evidence-status').value='';reactionEvidenceOffset=0;recordNavigation(true);loadReactionEvidence();};

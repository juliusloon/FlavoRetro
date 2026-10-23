function literatureEvidence(evidence,precursors=[]) {
    const block=div('domain-evidence');block.append(text('h4','文献已报道反应 · 精确来源重现'));
    const source=evidence.source || {};
    if(source.evidence_scope==='primary_abstract')block.append(text('p','本动作仅有作者摘要的命名转换支持；未取得完整实验条件。','note'));
    if(source.title)block.append(kv('文献题名',source.title));
    if(source.doi) {
        const line=div('source-doi'),link=text('a',source.doi);link.href='https://doi.org/'+encodeURIComponent(source.doi);link.target='_blank';link.rel='noopener';
        line.append(text('b','DOI：'),link);block.append(line);
    } else if(source.patent)block.append(kv('专利',source.patent));
    const locator=source.locator || source.evidence_locator;
    block.append(kv('原文定位',factText(locator)));
    block.append(kv('匹配范围',evidence.exact_source_instance_match ? '产物与完整主前体组合精确匹配' : '见原始记录，未声明精确匹配'));
    const reactants=evidence.source_reactants;
    if(Array.isArray(reactants) && reactants.length)block.append(kv('原文已报告主前体',reactants.map(r=>typeof r==='string' ? r : [r.name,r.smiles].filter(Boolean).join(' · ')).join(' + ')));
    else if(precursors.length)block.append(kv('实际动作前体（规范化图）',precursors.join(' + ')));
    const value=evidence.source_yield_value,reported=evidence.source_yield_reported_text;
    block.append(kv('原文产率记录',reported || (value==null ? '未记录数值' : `${value} ${evidence.source_yield_unit || ''}`)));
    if(evidence.source_yield_status)block.append(kv('产率解释',YIELD_STATUS_ZH[evidence.source_yield_status] || evidence.source_yield_status));
    if(evidence.source_conditions)block.append(kv('原文条件',factText(evidence.source_conditions)));
    if(evidence.source_catalyst)block.append(kv('原文催化剂',factText(evidence.source_catalyst)));
    for(const caution of evidence.review_cautions || [])block.append(text('p',caution,'note'));
    block.append(text('p','这是已报道反应的计算重现；不证明新反应活性、独立迁移、当前可采购或实验可行。','note'));
    const details=document.createElement('details');details.append(text('summary','完整来源与证据边界'),scientificDetails(evidence),sourceFacts(evidence.source));block.append(details);return block;
}

function domainEvidence(evidence) {
    const block = div('domain-evidence');
    block.append(text('h4', '来源限定糖苷动作'));
    block.append(kv('实例关系', evidence.exact_instance_match || evidence.exact_seed_instance_match
        ? '与构建来源的精确实例匹配（来源重现）' : '受限范围迁移候选（活性未验证）'));
    block.append(kv('模板来源支持', evidence.template_source_support === true ? '有登记来源支持' : '未确认'));
    block.append(kv('本次预测', '条件未验证；不从参考实例复制产率，不代表实验可行。'));
    const details = document.createElement('details');
    details.append(text('summary', '查看来源、限定上下文与证据状态'));
    details.append(scientificDetails(evidence),sourceFacts(evidence.source));for(const source of evidence.provenance || [])details.append(sourceFacts(source));block.append(details);
    return block;
}

const comparisonRuns = { a: null, b: null };

// ---------- 完整能力入口 ----------
// Family-level schemes are authored teaching illustrations, never source reaction records.
const PRINCIPLE_GUIDES = {
    '0.0 Unrecognized':{unknown:'源模板未提供可核对的反应家族与结构配对。先取得当前步骤的底物、产物及原子映射，再写方程式；不能用某个已知命名反应代替。'},
    o_glycoside_cleavage:{example:'o',explain:'以芹菜素 7-O-糖苷为例，逆合成回溯酚氧与糖异头碳的连接；这是一种合成规划，不能直接解释为加水水解。'},
    glycosylation:{example:'chain',explain:'本例受体是已有糖苷中的糖羟基，PcApiT 接入芹糖基。糖基化要先明确受体原子，再判断是母核成键还是糖间成键。'},
    o_glycosylation:{example:'o',explain:'本例形成的是芹菜素 7-O 与葡萄糖异头碳的键。酶把糖基从 UDP-Glc 转移给酚氧，UDP 作为副产物列出。'},
    c_glycosylation:{example:'c',explain:'本例糖异头碳直接连接根皮素芳环碳，得到单 C-糖苷 17a；连接处没有 O 桥，不能套用 O-糖苷的断键解释。'},
    activated_glycosyl_donor:{example:'o',explain:'本例糖侧前体保留完整 UDP-Glc，重点是糖供体的活化身份。游离葡萄糖不能直接替代此供体，也不能据此证明供体已可采购。'},
    whole_cell_glycosylation:{left:'黄酮受体 + 细胞内活化糖供体',right:'黄酮糖苷 + 供体离去部分',explain:'全细胞体系在细胞内提供活化糖，并完成糖基转移。这个净转化图式省略了代谢再生，不能把外加游离糖等同于直接反应供体。'},
    methylation:{left:'Ar—OH + 甲基供体',right:'Ar—O—CH₃ + 供体相关产物',explain:'以酚羟基 O-甲基化示意引入甲基：原有 Ar—O 键保留，新增 O—CH₃ 键。宽泛甲基化标签本身并不能确定实际反应位点。'},
    o_methylation:{left:'Ar—OH + 甲基供体',right:'Ar—O—CH₃ + 供体相关产物',explain:'只看酚氧位点：羟基变为甲醚。逆合成沿 O—CH₃ 连接回溯到酚；实际甲基供体与条件须与该条来源配对。'},
    o_demethylation:{left:'Ar—O—CH₃',right:'Ar—OH',explain:'甲醚脱甲基恢复酚羟基，断开的是氧与甲基之间的连接；芳环与氧之间的键保留。图式省略试剂及含甲基副产物。'},
    protection:{left:'R—XH + 保护基来源',right:'R—X—PG',explain:'X 表示待保护的杂原子，PG 表示临时保护基。把易反应官能团暂时掩蔽，以便开展后续转化；保护步骤不等于目标骨架已构建完成。'},
    phenol_protection:{left:'Ar—OH + 保护基来源',right:'Ar—O—PG',explain:'保护发生在酚氧上，Ar—O 连接保留。若底物有多个酚羟基，必须指明保护了哪一个，不能由通式推断区域选择性。'},
    deprotection:{left:'R—X—PG',right:'R—XH',explain:'去除临时保护基 PG，恢复原官能团。需要同时检查糖苷键或其他敏感官能团是否保留；图式省略试剂和保护基去除产物。'},
    phenol_deprotection:{left:'Ar—O—PG',right:'Ar—OH',explain:'这条通式只表示恢复酚羟基：去掉 O 上的 PG，保留芳环与氧的连接。不同保护基有不同去除方法，不能自动共用条件。'},
    oxidation:{left:'R₂CH—OH + [O]',right:'R₂C=O + H₂O',explain:'以仲醇氧化为酮示意：C—O 单键变为 C=O，碳的氧化态升高。[O] 仅表示氧化当量，不指定实际氧化剂；黄酮上的氧化位点仍须查结构。'},
    reduction:{left:'R₂C=O + 2[H]',right:'R₂CH—OH',explain:'以酮还原为仲醇示意：C=O 变为 C—O，并增加氢。[H] 表示还原当量；若生成新立体中心，通式不指定构型。'},
    cyclization:{example:'scaffold',explain:'以原文查尔酮闭环为例，同一分子的两个位点成键形成 C 环。需要同时追踪新成键和烯酮键级变化，不能把任何环化都视为同一机理。'},
    flavonoid_cyclization:{example:'scaffold',explain:'用含氧 C 环闭合说明骨架环化：本例终点是黄烷酮 2b，不是已氧化的黄酮；产物 C2—C3 键阶必须单独辨认。'},
    flavanone_synthesis:{example:'scaffold',explain:'原文邻羟基查尔酮经分子内 Oxa-Michael 闭环得到黄烷酮 2b。酚氧参与成键，烯酮片段随之重排键级，形成饱和 C2/C3 部分。'},
    flavanone_chalcone_opening:{example:'scaffold',explain:'本条按逆合成方向看下图：黄烷酮回溯到 E-2′-羟基查尔酮，涉及 C—O 连接与 C2/C3 键级。本来源报道的是正向闭环，不据此声明实验开环可行。'},
    chalcone_synthesis:{left:'Ar—CO—CH₃ + Ar′—CHO',right:'Ar—CO—CH=CH—Ar′ + H₂O',explain:'把芳基甲基酮与芳香醛组合成 α,β-不饱和酮，建立两个芳香片段之间的链。通式未指定取代基和 E/Z 构型，不自动等同于某个来源底物。'},
    chalcone_aldol:{left:'Ar—CO—CH₃ + Ar′—CHO',right:'Ar—CO—CH=CH—Ar′ + H₂O',explain:'先由羰基组分发生羟醛加成，形成新的 C—C 键，再脱水得到烯酮。这里画的是两过程的净图式，不把加成中间体当成已分离的来源产物。'},
    chalcone_retro_aldol:{left:'Ar—CO—CH₃ + Ar′—CHO',right:'Ar—CO—CH=CH—Ar′ + H₂O',explain:'正向图式展示片段来源；逆合成则从右侧查尔酮回溯羰基组分。它表达缩合的规划逻辑，不代表已证实存在对应的实验裂解反应。'},
    flavonoid_synthesis:{unknown:'“通用黄酮骨架构建”涵盖多种路线。缺少当前底物与产物的结构配对，无法唯一指定成键位置或方程式；请转到具体文献反应，再辨认环化、氧化或重排。'},
    isoflavone_synthesis:{unknown:'异黄酮构建可能包含不同成键或重排过程。仅凭此标签不能指定一条方程式；需要具体来源中的起料、产物及芳基连接位点，不能沿用黄烷酮闭环图代替。'},
    biosynthesis:{left:'来源指定的前体 + 所需辅因子',right:'通路产物 + 转化后的辅因子',explain:'这是通路净转化的占位图式，尚未指定具体反应。必须按来源补齐酶、底物和辅因子；一条整体通路不能被当成已经逐步验证的单步实验。'},
    literature_reaction:{unknown:'来源抽取记录还没有足够信息确定反应家族。应先配对该条来源的实际底物与产物，再写方程式；不以“文献抽取”四字代替机理或实验验证。'}
};
function principleArticle(key,entry,data,examples) {
    const article=document.createElement('article');article.className='teaching-entry';article.id='teaching-'+key;
    const layout=div('example-layout'),left=div('example-left'),narrative=document.createElement('section'),visual=document.createElement('section');
    narrative.className='example-narrative';narrative.setAttribute('aria-label','反应原理讲解');
    visual.className='example-visual';visual.setAttribute('aria-label','反应方程式与结构图');
    narrative.append(text('h3',entry.label_zh,'example-title'));
    const guide=PRINCIPLE_GUIDES[key],example=examples?.examples?.find(item=>item.topic===guide?.example);
    if(example){
        const lesson=EXAMPLE_LESSONS[example.topic];
        narrative.append(text('p','具体来源示例：'+lesson.title,'example-intro'));
        visual.append(reactionEquation(...lesson.equation,'文献正向反应',example.details.enzyme||'分子内闭环'));
        const figure=document.createElement('figure');figure.className='reaction-example';const viewport=div('reaction-example-viewport');viewport.tabIndex=0;viewport.setAttribute('role','region');viewport.setAttribute('aria-label',entry.label_zh+'示例结构图，可横向滚动');
        const img=document.createElement('img');img.src=example.svg;img.alt=example.alt_zh;viewport.append(img);
        const caption=text('figcaption','逆合成结构图：产物 → 前体 · 深绿色为回溯连接'),link=text('a','查看完整结构大图');link.href=example.svg;link.target='_blank';link.rel='noopener';caption.append(text('span','左右滑动查看全部结构','reaction-pan-hint'),link);figure.append(viewport,caption);visual.append(figure);
    }else if(guide?.left){
        visual.append(reactionEquation(guide.left,guide.right,'教学反应通式 · 省略具体试剂/条件，不作为完整配平方程式'));
        if(/Ar|R|PG|\[O\]|\[H\]/.test(guide.left+guide.right))visual.append(text('p','符号说明：Ar / Ar′ 为芳基，R 为有机基团，X 为待保护的杂原子，PG 为临时保护基，[O] / [H] 为氧化 / 还原当量。','scheme-legend note'));
    }else visual.append(text('p','方程式待具体结构与来源补齐','equation-unavailable'));
    narrative.append(text('h4','这条反应怎么理解'),text('p',guide?.explain||guide?.unknown||'当前缺少具体结构与来源，不能指定方程式。'),kv('家族定义',entry.principle_zh));
    left.append(narrative);
    if(example)left.append(kv('本例核对点',example.details.conditions_note),exampleSource(example));
    const checks=div('principle-checks');checks.append(kv('条件范围',entry.typical_conditions_zh),kv('需要核对',entry.risk_notes_zh),kv('证据边界',entry.evidence_boundary_zh));left.append(checks);
    const sources=div('principle-sources');sources.append(text('h4','原理参考资料'));
    for(const id of entry.source_ids||[]){const source=data.sources?.[id];if(!source)continue;const a=text('a',source.title);a.href=source.url||'https://doi.org/'+source.doi;a.target='_blank';a.rel='noopener';sources.append(a);}
    left.append(sources);layout.append(left,visual);article.append(layout);return article;
}

let catalogGeneration=0,selectedPrinciple='o_glycosylation';
async function loadTeachingCatalog() {
    const generation=++catalogGeneration,list=$('teaching-list');
    if(!teachingExamplesCache)teachingExamplesCache=api('/teaching-examples.json').catch(()=>null);
    const [data,examples]=await Promise.all([fetchTeaching(),teachingExamplesCache]);
    if(generation!==catalogGeneration)return;
    list.replaceChildren();if(!data){list.append(text('p','原理暂不可用。'));return;}
    const priority=['o_glycosylation','c_glycosylation','glycosylation','flavanone_synthesis'];
    const items=Object.entries(data.classifications||{}).sort(([a],[b])=>(priority.includes(a)?priority.indexOf(a):priority.length)-(priority.includes(b)?priority.indexOf(b):priority.length));
    const select=$('principle-select');
    if(!select.children.length)for(const [key,entry] of items){const option=text('option',entry.label_zh);option.value=key;select.append(option);}
    const selected=items.find(([key])=>key===selectedPrinciple)||items[0];
    if(!selected){list.append(text('p','暂无可用原理。'));return;}
    selectedPrinciple=selected[0];select.value=selectedPrinciple;
    select.onchange=()=>{selectedPrinciple=select.value;goToHash(captureRoute('literature'));};
    list.append(principleArticle(...selected,data,examples));
}

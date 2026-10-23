const LEARNING_KEY = 'flavoretro.learning.v1';
const LEARNING_STEPS = [
    { title:'1 · 识别结构与连接', prompt:'记录母核、糖的数量和候选连接类型。解释为何拓扑标注不能直接给出试剂或酶。',
      question:'图中标出的 C / O 糖苷连接，能证明该断键实验可行吗？', choices:['不能；它是图结构候选，需要反应证据。','能；图上可以断开的键都可合成。'], answer:0,
      feedback:'拓扑只诊断连接。结构回放、文献实例和独立化学验证回答不同问题。', action:'search', actionLabel:'查看目标与拓扑' },
    { title:'2 · 查证原文和反应参照', prompt:'记录 DOI、原文页/图/表、底物→产物、供体及尚缺字段。把未报告与数值零分别写出。',
      question:'原文没有报告产率时，应记录什么？', choices:['缺失或未报告，保留来源位置。','记录 0%，便于比较。'], answer:0,
      feedback:'零是一个数值结果；没有报告不能改写为零。原文条件也不能直接移给新底物。', action:'sources', actionLabel:'浏览文献卡片' },
    { title:'3 · 写出预期与比较设置', prompt:'在搜索前写出预期前体与理由，并约定目标、种子、库存、时间/迭代预算以及基线和扩展的区别。',
      question:'开启糖苷扩展后得到更多候选，可以直接称为搜索算法更优吗？', choices:['不能；新增知识与搜索机制的贡献需要分开。','可以；候选更多就证明算法更好。'], answer:0,
      feedback:'同目标、同库存与通用模型是必要条件；还需控制预算并区分新增动作知识。', action:'search', actionLabel:'设置搜索参数' },
    { title:'4 · 运行并追溯每一步', prompt:'运行后点击“记录当前运行”。记录 run ID、来源支持、精确实例匹配或迁移候选，以及未解决末端。',
      question:'动作精确命中构建该模板的来源实例，属于哪类结果？', choices:['来源重现；不能充当新来源独立迁移。','独立化学验证。'], answer:0,
      feedback:'来源重现是完整链的重要工程检查，但没有新增独立性。历史读取与实时MCTS也须区分。', action:'search', actionLabel:'查看运行与逐步证据' },
    { title:'5 · 对照基线与扩展', prompt:'将两次运行分别放入 A / B，记录条件差异、完整失败、路线/节点/耗时与来源补回情况。不要只选择有利结果。',
      question:'一条路线以候选库存终止，能说明原料可采购且路线可执行吗？', choices:['不能；采购和实验可行性需要额外证据。','能；闭合即实验成功。'], answer:0,
      feedback:'候选闭合、来源实例命中和独立实验成功是不同指标；两次运行也不替代冻结面板统计。', action:'comparison', actionLabel:'打开运行对照' },
    { title:'6 · 反思并导出', prompt:'写出本次有证据支持的结论、尚不能断言的事项，以及下一步最值得补的原文或实验。导出记录用于讨论。',
      question:'本练习的完成勾选与自检，属于什么审核？', choices:['学生自检；没有自动产生教师审定。','已通过教师和独立化学审核。'], answer:0,
      feedback:'学习记录保留你的判断与真实运行引用；教师审定、正式研究和发布各自需要对应验收。', action:'export', actionLabel:'导出本次练习' }
];
let learningRecord = {schema_version:1, notes:{}, completed:{}, answers:{}, target:null, runs:[], updated_at:null};
try {
    const stored = JSON.parse(localStorage.getItem(LEARNING_KEY) || 'null');
    if (stored && stored.schema_version === 1 && ['notes','completed','answers'].every(k => stored[k] && typeof stored[k] === 'object' && !Array.isArray(stored[k])) && Array.isArray(stored.runs)) learningRecord = stored;
} catch (_) { /* 损坏的本地练习不阻断真实搜索。 */ }
function saveLearning() {
    learningRecord.updated_at = new Date().toISOString();
    try { localStorage.setItem(LEARNING_KEY,JSON.stringify(learningRecord));updateLearningStatus(); }
    catch (_) { $('learning-progress').textContent = '本地保存不可用；可导出学习记录保留本次内容。'; }
}
function updateLearningStatus() {
    const count = LEARNING_STEPS.filter((_,i) => learningRecord.completed[i]).length;
    $('learning-progress').textContent = `自记进度 ${count}/${LEARNING_STEPS.length} · 已关联 ${learningRecord.runs.length} 次运行 · 非教师评分`;
    $('learning-context').textContent = `练习目标：${learningRecord.target || '尚未选入，点击“使用当前目标”'}。学习记录仅存当前浏览器。`;
}
function exportLearning() {
    downloadObject('flavoretro-learning-record.json',{...learningRecord, scope:'student_self_record',
        human_reviewed:false, teacher_approved:false, independent_chemical_validation:false,
        steps:LEARNING_STEPS.map((step,i) => ({title:step.title,prompt:step.prompt,note:learningRecord.notes[i] || '',
            self_completed:Boolean(learningRecord.completed[i]), question:step.question, choices:step.choices,
            answer:learningRecord.answers[i] ?? null, selected_answer:step.choices[learningRecord.answers[i]] ?? null})),
        comparison_run_ids:Object.values(comparisonRuns).filter(Boolean).map(e => e.result.run_id)});
}
function renderLearning() {
    const list = $('learning-steps');list.replaceChildren();
    const steps=$('learning-step-nav');steps.replaceChildren();
    LEARNING_STEPS.forEach((step,i)=>{
        const button=text('button','','tool-row');button.type='button';button.dataset.step=i;
        button.setAttribute('aria-current',String(i>=teachingPages.practice.offset&&i<teachingPages.practice.offset+teachingPages.practice.limit));
        button.append(text('strong',step.title),text('span',learningRecord.completed[i]?'已记录':'待记录','tool-row-meta'));
        button.onclick=()=>{teachingPages.practice.offset=i;teachingPages.practice.limit=1;recordNavigation();renderLearning();$('learning-step-nav').querySelector('[data-step="'+i+'"]').focus({preventScroll:true});};steps.append(button);
    });
    LEARNING_STEPS.forEach((step,i) => {
        if(i<teachingPages.practice.offset||i>=teachingPages.practice.offset+teachingPages.practice.limit)return;
        const details = document.createElement('details');details.className = 'learning-step';details.open = true;
        details.append(text('summary',step.title),text('p',step.prompt));
        const action = text('button',step.actionLabel,'secondary');action.type='button';
        action.onclick = () => {
            if (step.action === 'export') return exportLearning();
            if (step.action === 'sources') return switchLiteratureView('papers');
            if (step.action === 'comparison') {
                document.querySelector('[data-tab=history]').click();
                $('history-comparison').scrollIntoView({behavior:'smooth'});
                $('compare-run-a').focus();
                return;
            }
            $('tab-search').click();
        };
        details.append(action);
        const label = text('label','我的观察与依据');label.htmlFor='learning-note-'+i;
        const notes = document.createElement('textarea');notes.id=label.htmlFor;notes.maxLength=8000;notes.rows=3;
        notes.value=learningRecord.notes[i] || '';notes.oninput=()=>{learningRecord.notes[i]=notes.value;saveLearning();};
        details.append(label,notes);
        const fieldset=document.createElement('fieldset');fieldset.append(text('legend',step.question));
        const feedback=text('p','','learning-feedback');feedback.setAttribute('role','status');
        step.choices.forEach((choice,j)=>{
            const option=document.createElement('label');option.className='check';const input=document.createElement('input');
            input.type='radio';input.name='learning-question-'+i;input.value=j;input.checked=learningRecord.answers[i]===j;
            input.onchange=()=>{learningRecord.answers[i]=j;feedback.textContent=(j===step.answer?'自检符合证据边界。':'请再检查证据层级。')+' '+step.feedback;saveLearning();};
            option.append(input,document.createTextNode(choice));fieldset.append(option);
        });
        if (learningRecord.answers[i] != null) feedback.textContent=(learningRecord.answers[i]===step.answer?'自检符合证据边界。':'请再检查证据层级。')+' '+step.feedback;
        fieldset.append(feedback);details.append(fieldset);
        const complete=document.createElement('label');complete.className='check';const checked=document.createElement('input');
        checked.type='checkbox';checked.checked=Boolean(learningRecord.completed[i]);checked.id='learning-complete-'+i;
        checked.onchange=()=>{learningRecord.completed[i]=checked.checked;saveLearning();$('learning-step-nav').querySelector('[data-step="'+i+'"] span').textContent=checked.checked?'已记录':'待记录';};
        complete.append(checked,document.createTextNode('我已记录本阶段的观察与未解决问题'));details.append(complete);list.append(details);
    });updateLearningStatus();
    const state=teachingPages.practice;state.total=LEARNING_STEPS.length;pagination('learning-pager-top',state,(offset,limit)=>{state.offset=offset;state.limit=limit;recordNavigation();renderLearning();},[1,2,3,6]);
}
$('learning-use-target').onclick=()=>{learningRecord.target=$('smiles').value.trim();saveLearning();};
$('learning-use-run').onclick=()=>{
    if (!lastResult || !currentManifest) return;
    const reference={run_id:lastResult.run_id,execution_source:savedRun?(currentReadSource || 'explicit_saved_run'):lastResult.execution_source,
        request:lastResult.request,status:lastResult.status,result_sha256:currentManifest.files?.['result.json'] || null};
    learningRecord.runs=learningRecord.runs.filter(r=>r.run_id!==reference.run_id).concat([reference]).slice(-20);
    learningRecord.target=lastResult.request?.smiles || learningRecord.target;saveLearning();
};
$('learning-export').onclick=exportLearning;
renderLearning();

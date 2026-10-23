async function openSavedRun(id) {
    if(!id){$('history-message').textContent='请输入完整 run ID。';return;}
    await goToHash('#/search?'+new URLSearchParams({run:id}));
}

function runOptionLabel(row) {
    const time = row.created_at ? localTime(row.created_at) : '时间未记录';
    return `${time} · ${row.routes ?? 0} 条路线 · ${row.status==='ok'?'已完成':'未完成'}`;
}

function populateComparisonSelects(rows) {
    for (const [id, slot] of [['compare-run-a', 'A'], ['compare-run-b', 'B']]) {
        const select = $(id), previous = select.value;
        select.replaceChildren(text('option', `选择运行 ${slot}`));
        select.firstChild.value = '';
        for (const row of rows) {
            if (row.integrity !== 'verified') continue;
            const option = text('option', runOptionLabel(row));
            option.value = row.run_id;
            select.append(option);
        }
        if ([...select.options].some(option => option.value === previous)) select.value = previous;
    }
}

async function loadHistoryPage() {
    try {
        const data = await api('/api/runs?offset=0&limit=100');
        historyRunsForSelect = data.runs;
        populateComparisonSelects(historyRunsForSelect);
    } catch (error) { $('history-message').textContent = '对照菜单读取失败：' + error.message; }
    await loadRuns();
}

async function loadRuns() {
    const generation = ++runsGeneration;
    try {
        const data = await api(`/api/runs?offset=${runOffset}&limit=${runLimit}`);
        if (generation !== runsGeneration) return;
        const lastOffset = Math.max(0, (Math.ceil(data.total / runLimit) - 1) * runLimit);
        if (runOffset > lastOffset) { runOffset = lastOffset; return loadRuns(); }
        $('run-list').replaceChildren();
        $('history-message').textContent = '';
        pagination('runs-pager-top', {offset:runOffset, limit:runLimit, total:data.total}, (next, limit) => {
            runOffset = next; runLimit = limit; recordNavigation();loadRuns();
        }, [10,25,50,100]);
        if (!data.runs.length) {
            const tr = document.createElement('tr'), td = text('td', '暂无已保存运行。', 'note');
            td.colSpan = 4; tr.append(td); $('run-list').append(tr);
            return;
        }
        for (const row of data.runs) {
            const tr = document.createElement('tr');
            const target = div('history-target');
            if (row.smiles) {
                const img = document.createElement('img');
                img.src = '/api/molecule?smiles=' + encodeURIComponent(row.smiles);
                img.alt = '目标分子结构'; img.loading = 'lazy';
                target.append(img);
            }
            const targetLabel = text('span', row.smiles ? '目标分子' : '目标未记录', 'note');
            if (row.smiles) targetLabel.title = row.smiles;
            target.append(targetLabel);

            const runCell = div();
            const runId=text('span','探索记录','history-run-id');
            runCell.append(runId, text('span', row.created_at ? localTime(row.created_at) : '时间未记录', 'note'));

            const statusCell=text('span',`${row.status==='ok'?'已完成':'未完成'} · ${row.routes??0} 条路线${row.steps?' · 最多 '+row.steps+' 步':''}`);
            const action = document.createElement('td');
            const button = text('button', '查看路线', 'secondary');
            button.type = 'button';
            button.disabled = row.integrity !== 'verified';
            button.onclick = () => openSavedRun(row.run_id);
            action.append(button);
            tr.append(text('td', '') , text('td', ''), text('td', ''), action);
            tr.children[0].append(target);
            tr.children[1].append(runCell);
            tr.children[2].append(statusCell);
            $('run-list').append(tr);
        }
    } catch (error) { if (generation === runsGeneration) $('history-message').textContent = error.message; }
}
$('open-run').onclick = () => openSavedRun($('saved-run-id').value.trim());
$('refresh-runs').onclick = () => { runOffset = 0; recordNavigation();loadHistoryPage(); };

PageRegistry.register('history',loadHistoryPage);

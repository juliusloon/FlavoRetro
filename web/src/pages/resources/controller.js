// ---------- 资源与证据页 ----------
async function loadRecords() {
    const generation=++recordsGeneration;
    try{
        const data=await api(`/api/records?kind=${encodeURIComponent($('kind').value)}&q=${encodeURIComponent($('query').value)}&offset=${offset}&limit=${recordsLimit}&issue=${encodeURIComponent($('qc-filter').value)}&outcome=${encodeURIComponent($('outcome-filter').value)}&source_status=${encodeURIComponent($('source-filter').value)}`);
        if(generation!==recordsGeneration)return;
        recordsTotal=data.total;const lastOffset=Math.max(0,(Math.ceil(recordsTotal/recordsLimit)-1)*recordsLimit);if(offset>lastOffset){offset=lastOffset;return loadRecords();}$('count').textContent=`找到 ${data.total} 条记录`;$('rows').replaceChildren();
        for(const row of data.records){
            const raw=row.raw||{},label=raw.name||raw.query_name||raw.substance_query||raw.title||raw.fields?.['RXN:VAR(1):CAS_Reaction_Number']||raw.template_id||'未命名条目';
            const tr=document.createElement('tr');tr.dataset.recordId=row.id;tr.classList.toggle('is-selected',selectedRecordId===row.id);
            const name=text('td',label,'record-name');name.title=label;
            const kind={molecule:'分子',note_reaction:'笔记反应',scifinder_reaction:'SciFinder反应',stock:'库存',template:'模板',paper:'文献',supplier:'供应列表'}[row.kind]||row.kind;
            const sourceName=raw.source?.file_name||raw.source?.title||String(row.source_path||'').split('/').pop()||'未记录';const source=text('td',sourceName,'record-source');source.title=sourceName;
            const action=document.createElement('td'),button=text('button','查看当前条目','secondary');button.type='button';button.setAttribute('aria-label','查看当前条目：'+label);
            button.onclick=()=>{selectedRecordId=row.id;selectedRecordRow=row;showRecord(row);switchResourcePane('detail');recordNavigation();};action.append(button);tr.append(name,text('td',kind),source,action);$('rows').append(tr);
        }
        if(!data.records.length){const row=document.createElement('tr'),cell=text('td','没有匹配的记录。');cell.colSpan=4;row.append(cell);$('rows').append(row);}
        const state={offset,limit:recordsLimit,total:recordsTotal};pagination('records-pager-top',state,(next,limit)=>{offset=next;recordsLimit=limit;selectedRecordId=null;selectedRecordRow=null;clearRecord();recordNavigation();loadRecords();},[10,25,50,100]);
    }catch(error){if(generation===recordsGeneration)$('count').textContent='读取失败：'+error.message;}
}
const findRecords=()=>{offset=0;selectedRecordId=null;selectedRecordRow=null;clearRecord();recordNavigation();loadRecords();};
$('resource-filters').onsubmit=event=>{event.preventDefault();findRecords();};
for(const id of ['kind','qc-filter','outcome-filter','source-filter'])$(id).onchange=findRecords;
$('reset-records').onclick=()=>{$('resource-filters').reset();findRecords();};
$('show-records').onclick=()=>{selectedRecordId=null;clearRecord();switchResourcePane('records');recordNavigation();};$('show-record-detail').onclick=()=>{if(selectedRecordRow){selectedRecordId=selectedRecordRow.id;showRecord(selectedRecordRow);}switchResourcePane('detail');recordNavigation();};

PageRegistry.register('resources',loadRecords);

"use strict";
/** Shared DOM components. No page state, API requests, innerHTML, or search behavior. */
const UI = (() => {
    const byId = id => document.getElementById(id);
    function enhance(root) {
        if (!root) return;
        const nodes = root.nodeType === 1 ? [root, ...root.querySelectorAll('button,input,select,textarea,.page,.page-heading,.filter-toolbar,.card,.records-panel,.record-inspector,.comparison-panel,.history-saved,.workspace,.history-workspace,.resource-workspace,.tool-split,.example-layout,.record-table-wrap,.resource-table,.history-table,.pagination')] : [...root.querySelectorAll('button,input,select,textarea,.page,.page-heading,.filter-toolbar,.card,.records-panel,.record-inspector,.comparison-panel,.history-saved,.workspace,.history-workspace,.resource-workspace,.tool-split,.example-layout,.record-table-wrap,.resource-table,.history-table,.pagination')];
        for (const el of nodes) {
            if (el.tagName === 'BUTTON') el.classList.add('ui-button');
            if (['INPUT','SELECT','TEXTAREA'].includes(el.tagName) && !['checkbox','radio'].includes(el.type)) el.classList.add('ui-input');
            const classes = {page:'ui-page','page-heading':'ui-page-heading','filter-toolbar':'ui-filter',card:'ui-panel','records-panel':'ui-panel','record-inspector':'ui-panel','comparison-panel':'ui-panel','history-saved':'ui-panel',pagination:'ui-pagination','record-table-wrap':'ui-table-scroll','resource-table':'ui-table','history-table':'ui-table'};
            for (const [oldName,newName] of Object.entries(classes)) if (el.classList.contains(oldName)) el.classList.add(newName);
            for (const [oldName,variant] of [['workspace','explore'],['history-workspace','compare'],['resource-workspace','reader'],['tool-split','reader'],['example-layout','diagram']]) if (el.classList.contains(oldName)) el.classList.add('ui-split','ui-split--'+variant);
        }
    }
    function text(tag, value, className) {
        const el = document.createElement(tag);el.textContent = value;
        if (className) el.className = className;
        // Individual nodes do not need a subtree scan.
        if (tag.toLowerCase()==='button') el.classList.add('ui-button');
        if (tag.toLowerCase()==='input'||tag.toLowerCase()==='select'||tag.toLowerCase()==='textarea') el.classList.add('ui-input');
        return el;
    }
    function div(className) { const el=document.createElement('div');if(className)el.className=className;return el; }
    function button(label,{variant='primary',disabled=false,onClick,type='button'}={}) {
        const el=text('button',label,'ui-button'+(variant==='secondary'?' secondary':variant==='quiet'?' ui-button--quiet':''));el.type=type;el.disabled=disabled;if(onClick)el.onclick=onClick;return el;
    }
    function badge(value,className='') { return text('span',value,'chip ui-badge'+(className?' '+className:'')); }
    function fixed(value,digits=3) { if(value==null||value==='')return '—';const n=Number(value);return Number.isFinite(n)?n.toFixed(digits):'—'; }
    function kv(label,value) { const row=div('kv ui-key-value');row.append(text('b',label+'：'),document.createTextNode(String(value)));return row; }
    function notice(message,{kind='info',className=''}={}) { const el=text('p',message,'ui-notice ui-notice--'+kind+(className?' '+className:''));el.setAttribute('role',kind==='error'?'alert':'status');return el; }
    function empty(message='暂无内容。') { const el=text('p',message,'empty-library ui-empty');el.dataset.uiComponent='empty';return el; }
    function panel({title,children=[],tag='section'}={}) { const el=document.createElement(tag);el.className='ui-panel';if(title)el.append(text('h2',title));el.append(...children);return el; }
    function split({left,right,variant='reader'}={}) { const el=div('ui-split ui-split--'+variant);el.append(left,right);return el; }
    function field({id,label,type='text',value='',options=[],onChange}={}) {
        const group=div('ui-field-group'),caption=text('label',label);caption.htmlFor=id;const input=document.createElement(type==='select'?'select':'input');input.id=id;input.className='ui-input';
        if(type==='select')for(const option of options){const el=text('option',option.label);el.value=option.value;input.append(el);}else input.type=type;
        input.value=value;if(onChange)input.onchange=onChange;group.append(caption,input);return group;
    }
    function listItem({title,meta='',href='#',className='',onClick}={}) { const el=text('a','','ui-list-item'+(className?' '+className:''));el.href=href;el.append(text('strong',title));if(meta)el.append(text('span',meta,'tool-row-meta'));if(onClick)el.onclick=onClick;return el; }
function pagination(id,state,change,sizes=[10,25,50,100]) {
    const box=byId(id); if (!box) return;
    if (!box.children.length) {
        box.classList.add('ui-pagination');box.dataset.uiComponent='pagination';box.setAttribute('role','group');box.setAttribute('aria-label',id+' 分页');
        for (const [role,label] of [['first','首页'],['previous','上一页']]) { const b=text('button',label,'secondary');b.type='button';b.dataset.pageAction=role;box.append(b); }
        const pageLabel=text('label','第 ');pageLabel.className='page-number';
        const input=document.createElement('input');input.type='number';input.min=1;input.setAttribute('aria-label','页码');input.dataset.pageAction='page';pageLabel.append(input,document.createTextNode(' / '));
        const pages=text('span','1');pages.dataset.pageAction='pages';pageLabel.append(pages,document.createTextNode(' 页'));box.append(pageLabel);
        for (const [role,label] of [['next','下一页'],['last','末页']]) { const b=text('button',label,'secondary');b.type='button';b.dataset.pageAction=role;box.append(b); }
        const sizeLabel=text('label','每页 ');sizeLabel.className='page-size';const select=document.createElement('select');select.setAttribute('aria-label','每页条数');select.dataset.pageAction='size';
        for(const value of sizes){const option=text('option',value);option.value=value;select.append(option);}sizeLabel.append(select,document.createTextNode(' 条'));box.append(sizeLabel);
        const count=text('span','','page-count');count.dataset.pageAction='count';box.append(count);
    }
    const get=role=>box.querySelector('[data-page-action="'+role+'"]');
    const pages=Math.max(1,Math.ceil(state.total/state.limit)),current=Math.floor(state.offset/state.limit)+1;
    get('first').disabled=get('previous').disabled=state.offset===0;
    get('next').disabled=get('last').disabled=state.offset+state.limit>=state.total;
    get('page').value=current;get('page').max=pages;get('page').disabled=state.total===0;get('pages').textContent=pages;
    get('size').value=state.limit;get('count').textContent=`共 ${state.total} 条 · ${state.total?state.offset+1:0}–${Math.min(state.offset+state.limit,state.total)}`;
    get('first').onclick=()=>change(0,state.limit);get('previous').onclick=()=>change(Math.max(0,state.offset-state.limit),state.limit);
    get('next').onclick=()=>change(Math.min((pages-1)*state.limit,state.offset+state.limit),state.limit);get('last').onclick=()=>change((pages-1)*state.limit,state.limit);
    get('page').onchange=()=>{const n=Number(get('page').value);change((Math.max(1,Math.min(pages,Number.isFinite(n)?Math.floor(n):1))-1)*state.limit,state.limit);};
    get('size').onchange=()=>change(0,Number(get('size').value));
}

    let observer;
    function mount(root=document) {
        enhance(root);
        if(observer)return;
        observer=new MutationObserver(records=>{for(const record of records)for(const node of record.addedNodes)if(node.nodeType===1)enhance(node);});
        observer.observe(root===document?document.body:root,{childList:true,subtree:true});
    }
    return Object.freeze({version:'1.0.0',byId,text,div,button,badge,fixed,kv,notice,empty,panel,split,field,listItem,pagination,enhance,mount});
})();
globalThis.FlavoUI = UI;

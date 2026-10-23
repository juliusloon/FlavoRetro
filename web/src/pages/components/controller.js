// Developer reference route; sample interactions stay local and never issue API mutations.
let componentReferenceReady=false;
function renderComponentReference(){
    if(componentReferenceReady)return;
    componentReferenceReady=true;
    for(const [label,token]of [['主色','--green-600'],['页面','--bg'],['面板','--surface'],['正文','--ink'],['边框','--border']]){
        const swatch=UI.div('ui-swatch'),color=UI.div('ui-swatch-color');color.style.backgroundColor=`var(${token})`;swatch.append(color,UI.text('span',label),UI.text('code',token));$('component-swatches').append(swatch);
    }
    $('component-feedback').append(UI.notice('信息与状态使用同一展示组件。'),UI.notice('需要核对的内容。',{kind:'warning'}),UI.notice('错误提示示例。',{kind:'error'}));
    const output=$('component-interaction');
    $('component-buttons').append(UI.button('主要操作',{onClick:()=>output.textContent='主要操作已执行。'}),UI.button('次要操作',{variant:'secondary',onClick:()=>output.textContent='次要操作已执行。'}),UI.button('文字操作',{variant:'quiet',onClick:()=>output.textContent='文字操作已执行。'}),UI.button('不可用',{disabled:true}));
    $('component-fields').append(UI.field({id:'component-keyword',label:'关键词',type:'search'}),UI.field({id:'component-choice',label:'选项',type:'select',value:'all',options:[{value:'all',label:'全部条目'},{value:'selected',label:'选中条目'}],onChange:event=>output.textContent='当前选项：'+event.target.selectedOptions[0].textContent}));
    const state={offset:0,limit:25,total:63};
    function update(){UI.pagination('component-pager',state,(offset,limit)=>{state.offset=offset;state.limit=limit;update();});$('component-items').replaceChildren(...Array.from({length:Math.min(state.limit,state.total-state.offset)},(_,i)=>UI.text('span','示例条目 '+(state.offset+i+1),'chip')));}
    update();$('component-states').append(UI.kv('数值零',0),UI.kv('缺失值','未报告'),UI.badge('未闭合','partial'),UI.empty('没有匹配的条目。'));
    const left=UI.panel({title:'条目列表',children:[UI.listItem({title:'示例条目',meta:'这是组件示例，不是科学记录。',href:'#/components'})]});
    const right=UI.panel({title:'阅读区域',children:[UI.text('p','列表选择、筛选与翻页复用公共控件；科学事实由页面控制器提供。')]});
    $('component-splits').append(UI.split({left,right,variant:'reader'}));
    for(const route of ROUTE_DEFINITIONS.subpages){const link=UI.text('a',route.purpose+' · '+route.path,'ui-route-link');link.href=route.example||route.path;$('component-route-list').append(link);}
    UI.enhance($('components'));
}

PageRegistry.register('components',renderComponentReference);

// ---------- 项目状态页 ----------
async function loadStatus(){
    try{const data=await api('/api/status'),resources=data.resources||{},counts=resources.counts||{};$('stats').replaceChildren();
        for(const [label,value]of [['反应记录',(counts.note_reaction??0)+(counts.scifinder_reaction??0)],['分子记录',counts.molecule??0],['名称冲突',resources.name_conflicts??0],['未报告收率',resources.yield_missing??0]]){const cell=div('stat');cell.append(text('b',value),text('span',label));$('stats').append(cell);}
        $('research-status').textContent='当前可用于黄酮及糖苷的候选路线探索、文献核查与教学。路线闭合表示命中候选库存，尚未完成独立化学验证与当前供应确认。';
    }catch(error){$('research-status').textContent='状态读取失败：'+error.message;}
}

PageRegistry.register('governance',loadStatus);

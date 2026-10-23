/* FlavoRetro 浏览器工作台：路线探索 / 资源与证据 / 文献教学 / 项目状态。
 * 原生 JS；由 web/frontend.json 顺序构建，源文件是编辑入口。措辞纪律：候选不代表可执行，未知保持未知。
 */
"use strict";

// ---------- 基础工具 ----------
const $ = UI.byId;
let navigationReady=false,currentPage='search',navigationGeneration=0,currentLocationHash='',selectedRecordRow=null;
let navigationItem='';
let lastResult = null, offset = 0, runOffset = 0;
let savedRun = false, currentReadSource = null, currentManifest = null, recordsGeneration = 0, runsGeneration = 0;
let displayedRoutes = [];
let selectedRouteIndex = 0, lastTeaching = null, renderedRunId = null;
let historyRunsForSelect = [];
let teachingCache = null;    // /api/teaching 惰性缓存（Promise），失败时 resolves 为 null
let runtimeCapabilities = null;
let literatureCache = null;  // /api/literature-teaching 惰性缓存（Promise）
const topologyCache = new Map();  // SMILES → /api/topology 惰性缓存（Promise），失败时 resolves 为 null
let topologyRequested = '';       // 侧栏拓扑区块的最近一次请求输入，用于丢弃过期渲染

async function api(path, options) {
    const response = await fetch(path, options);
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || data.error?.message || data.error || '请求失败');
    return data;
}
const text=UI.text,div=UI.div,chip=UI.badge,fixed=UI.fixed,kv=UI.kv;

# ADR-009：完整模型前沿、探索下界与精确库存表示

- 日期：2026-10-22
- 状态：agent_delegated接受；human_reviewed=false
- 依据：TASK-022；严格普通优化42开发和独立库存审计已通过；当前DFF130整体验证及3实际接口/浏览器已通过，效果与效率分轴，后者未达20%门。

旧普通optimized相对Native在同一目标三个seed丢失库存闭合。原全局候选/结果截断、先验比例探索和全局最大深度转置会丢失搜索机会或路径身份。新候选保全相同两通用模型每分子cutoff12已产候选，以NativeUCT探索下界加0.25原PUCT（事前固定）保留策略引导；状态身份保全逐分子深度、映射、历史，限于相同上下文的非终态兄弟重用，保留终态路径替代，继续25000节点硬限。分支请求仍控制每模型每分子候选，不能把它解释成额外全局节点分支cap。旧search.py保留来源知识路径和冻结重放身份。

独立核库发现原生Molecule(smiles) sanitize=False留下双键STEREONONE，方向SMILES可显示E而内部按未指定几何键查询。两臂各6保存叶有这种差异，因此v1主指标通过也不接入、不改旧结果。共同CanonicalStock按显示SMILES正常RDKit解析后查询，连同exacttarget exclusion、availability、amount/price保持相同身份；原query对象、库存、选择与停止条件保留，所有当前引擎共用，实际类/profile写入phase。

strict-v2 4库存单位、2真实工程与42开发以及17,422,831库存全扫支持当前实现：3旧损失恢复，21/21展示质量无损，50唯一键626保存叶匹配。开发成本正值不认证独立提速或逆合成化学可行性。共同库存语义也作用于DFF，已完成最终代码下原13目标130次开发回归及实际CLI/HTTP/DFF、桌面手机核查；旧DFF130前瞻及其方法身份不被新回归覆盖。

证据位于outputs/task022/optimized_coverage_repair_20261021/strict_stock_v2，原件/历史SHA映射在runtime_draft/lineage.json。原3600总预算与所有失败保留；独立化学、供应、教师、TASK017和生产门不由工程批准翻转。

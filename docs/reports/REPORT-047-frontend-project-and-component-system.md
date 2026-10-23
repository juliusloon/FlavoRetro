# REPORT-047 前端项目化、子页面与统一组件规范

2026-10-24。Completed。审批agent_delegated，human_reviewed=false。[事前TASK](../tasks/TASK-047-frontend-project-and-component-system.md)、[ADR-014](../adr/ADR-014-modular-frontend-project.md)、[开发入口](../../web/README.md)。

## 交付

页面已从单体源码改为可构建项目：web/src/shell.html为主壳，9个页面/教学HTML片段独立维护；控制器按搜索、历史、资源、教学与研究范围分开，core/shared分别维护路由、生命周期、状态与事实显示。routes.json登记五个主入口、教学子页及独立组件参考；PageRegistry注册页面加载，地址恢复统一由router管理。现有返回/前进、刷新、新标签、旧?run及筛选/选中/分页/草稿/滚动状态保留，无面包屑。

共享组件FlavoUI已真实用于业务分页、DOM/键值/标签、资料列表、空态与错误。按钮/表单/面板/表格通过公共UI类统一，类型契约位于ui.d.ts。公共样式入口为styles/components.css，色彩/字型沿用token。阅读分栏统一1:2、记录对照2:1、讲解图式1:2，搜索参数栏320–380px，其余为结果；按明确最小宽度统一响应式行为。控件至少44px、焦点保留高对比，列表焦点在滚动边界内可见。教学页原20px/16px顶部间距及不透明背景保持。

新增独立`/#/components`参考页，不占五个业务主导航，可操作按钮/表单/分页、状态/空态/错误、分栏及页面入口。示例条目仅为UI示例，不是科学记录。

## 开发流程

scripts/frontend.py提供build/check/watch/routes/create-page，均为Python标准库，无新的前端依赖。frontend.json显式登记25个脚本输入（含生成路由数据）和20个样式层，确定性生成根级index.html/app.js/style.css及包内镜像。运行服务白名单与后端模块未变，不需重启。源码是编辑入口，生成物不直接编辑。

create-page生成页面模板、控制器和路由/include/构建登记，默认不占业务主导航；重复/非法ID、标题转义、既有无效源码均有保护。构建检查拒绝循环include、越界路径、重复ID、路由与模板不一致、重复输入和产物漂移。check已接入工程CI配置，远程CI未在本轮触发；本地等价检查已通过。

开发入口及组件、路由、新页面、测试规范位于web/README.md和docs/frontend/。README/文档/脚本导航已连入。旧WEB_UI_DESIGN保留为历史规划，并指向现行规范。JS依然是按清单拼接的经典脚本作用域，公共组件闭包与页面生命周期是扩展边界，不冒称已迁为原生ES模块。

## 保留范围

本轮未修改后端静态/API模块、搜索算法、原始数据/库存/来源准入、真实运行或其他项目。原科学标签、四例讲解、27原理和六步常量逐字节保留；原静态正文与默认预算保留。现有接口仍为32篇论文、18案例、54反应记录、27教学原理。六步笔记/自检/完成及全量导出保留。候选/工程/供应/独立化学身份不变。

没有安装依赖、重启现有服务、真实新MCTS或Git提交/推送；保留既有未提交及其他聊天改动。初始只读盘点误用已存在TASK045标签，发现后统一TASK047；未以此重开或修改该旧任务合同。

## 验证

Browser plugin not available，使用已有Playwright Chromium，用户LAN地址http://10.70.160.64:8767/。主流程1440×1000、768×1024、390×844、320×844；专项1440/390。流程：主页面→子页→筛选/选中/详情→返回/前进与刷新→真实已保存运行/对照→练习记录与全量导出→公共组件交互。

| 检查 | 结果 |
| --- | --- |
| 页面身份/非空/错误遮罩 | 五主页面、教学各区及组件页正确，无遮罩 |
| 导航与状态 | 返回/刷新、run/route、A/B、资源详情、教学选中/原地来源、草稿及练习保持 |
| 视觉与组件 | 公共控件、1:2阅读分栏、标题间距背景、四视口无整页横溢；组件真实交互通过 |
| 组件边界 | 分页越界/每页数、零/缺失、文本安全、未知/重复生命周期注册拒绝、文字按钮悬停、键盘高对比焦点通过 |
| 读取失败 | 主动注入一次503，公共role=alert可见，撤销后真实资料恢复；预期HTTP错误单列 |
| 浏览器 | 136主流程＋12边界/故障＋9组件入口＋5焦点＋2辅助页键盘＝164项通过；非预期错误/警告/页面异常0 |
| 工程测试 | 11项新构建合同＋18项既有package/Web/交接测试＝29项通过 |
| 静态/实际服务 | 35项确定性/源码产物镜像/AST/Node/内容保留/服务字节/接口数量核验通过；check与diff通过 |
| 对比度 | 既有34组token配色复测全部通过，新增控件焦点另验高对比 |
| 请求/搜索 | 浏览器非GET0，真实MCTS新增0 |

主要命令全部经operate记录：`python3 -B scripts/frontend.py build --task TASK-047`、`check`；`.venv/bin/python -B scripts/check_frontend.py --base http://10.70.160.64:8767/ --task TASK-047 ...`；`.venv-foundation/bin/python -B -m unittest tests.test_frontend_project tests.test_package tests.test_web tests.test_web_foundation tests.test_lab_handoff`；`node --check web/app.js`、`git diff --check`、`scripts/contrast_check.py`。对比度旧脚本输出标签仍为TASK013，本次TASK047调用及摘要另存，不回写旧检查器。

基线outputs/task047/before/，最终browser-*.json、static-verification.json和contrast-verification.json在outputs/task047；临时脚本/截图在/tmp/flavoretro-task047，不入Git。永久只读回归入口为scripts/check_frontend.py。只验证Chromium和模拟视口，未验证Firefox/Safari、真实触屏及远程CI。本轮没有提交真实搜索。

## 截图

![可操作组件参考：统一控件与规范](/tmp/flavoretro-task047/final/1440-component-library.png)
![手机：共用标题、控件与讲解布局](/tmp/flavoretro-task047/final/390-teaching.png)

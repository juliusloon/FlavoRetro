# REPORT-039 单条原理标题与双面板排版

2026-10-23。结果：Completed。审批：agent_delegated；human_reviewed=false。[事前TASK](../tasks/TASK-039-single-principle-layout.md)。

按用户要求删除原理区“全部反应原理”旧标题及指定说明，改为“选择要了解的反应原理”标题，字号与常见类型相同（--text-xl），菜单紧跟标题。顶部区域导航的“全部反应原理”名称保留。手机标题和菜单自然换行。

原理区上下分页DOM、每页数选择及catalog分页状态/调用均移除，selectedPrinciple记录唯一选中key，每次仅渲染一个article；27项全部保留。切到其他教学区域再返回时保留选择。

排版复用当前常见类型的example-layout/example-left/example-narrative/example-visual：桌面约1:2左讲解/右方程式与结构图；原出处、条件范围与参考保留在左列，手机堆叠且结构图局部横滑。原家族解释、来源通式、缺少证据说明、MeOH/EtOH冲突及结构资产均保持；额外提供结构大图入口。

## 实际文件

web/index.html改标题行并删除分页；web/app.js仅原理渲染与单选状态变化，PRINCIPLE_GUIDES和EXAMPLE_LESSONS至常见类型渲染的内容与本任务基线一致；web/style.css移除旧picker规则、添加原理区标题与配图规则。三文件包内镜像一致。治理记录与使用说明更新当前行为，TASK033/036/037/038旧报告不覆写。

## 验收

Browser plugin not available，使用已有Playwright Chromium与http://127.0.0.1:8767，现有服务未重启。视口1440×1000、1200×800、390×844、320×640。

| 检查 | 结果 |
| --- | --- |
| 页面身份/非空/框架覆盖层 | 正确URL与标题、选中面板有内容，无错误覆盖层 |
| 指定删除与字号 | 旧标题/说明/上下分页消失；新标题与常见类型计算字号一致，菜单有正确label |
| 27项唯一展示 | 逐项均只有一条，对应讲解在左、方程式/明确缺证说明在右，参考直接可见 |
| 状态保留 | 原理与常见类型区域往返保留选择；原理不改变常见类型选中状态 |
| 响应式 | 桌面标题菜单同排、两面板正确；手机堆叠、结构图局部横滑，无页面横向溢出 |
| 工具回归 | 原文案例分页与精确来源跳转仍可用 |
| 控制台/请求 | error 0、warning 0、非GET请求0、新MCTS 0 |

共172项浏览器检查通过，另有3项既有package测试、9项静态检查通过（3镜像、原理正文/常见渲染保留、分页逻辑移除、SVG SHA、Node、diff）。截图以view_image核对原理实例/通式/手机讲解及局部横滑；最终标题截图等待颜色过渡结束后重新捕获。未验证其他浏览器或真实触屏设备。

本地证据为outputs/task039/before、browser-qa.json与static-checks.json；临时脚本/截图为/tmp/flavoretro-task039/qa.py、principle-1440.png、general-principle.png、principle-390.png、visual-320.png。operate记录命令和写入；引导阶段遇到已占用TASK036/038编号，另记事件归属到新TASK039，没有覆盖原任务。

本任务不改后端、搜索、库存、来源准入和运行数据；没有Git提交/推送，原始或受限数据未加入Git，科学/教师/供应等验证状态未升级。后续可安装Browser插件进行应用内验收。

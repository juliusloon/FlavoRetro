# REPORT-042 移除新增面包屑导航栏

2026-10-24。Completed；审批agent_delegated，human_reviewed=false。[事前TASK](../tasks/TASK-042-remove-breadcrumb.md)。

按用户要求删除TASK041新增的当前位置/上级面包屑栏、DOM渲染及专用样式；页面无该栏或空白占位。子页地址、标题、导航链接、返回/前进、刷新/状态恢复与错误提示保持。除updatePageLocation函数中移除面包屑生成外，其余JS逻辑与本轮基线逐字节一致。web三文件与包内镜像同步。

Browser plugin not available，使用既有Playwright Chromium，http://127.0.0.1:8767/；1440×1000、390×844。测试流程：进入教学子页→确认无面包屑/占位→切换示例并返回/前进/刷新→原理恢复→历史打开真实保存结果并返回→资源详情刷新及错误提示。

| 检查 | 结果 |
| --- | --- |
| 身份/非空/错误遮罩 | URL/标题/实际内容正确，无错误遮罩 |
| 布局与截图 | 面包屑DOM和占位消失，主区直接衔接顶栏，两档无整页横溢 |
| 交互 | 示例/原理/历史运行/资源详情的导航与恢复通过；错误提示保留 |
| 控制台及搜索 | 错误/警告/页面异常0，非GET0，新增真实MCTS0 |
| 工程 | 29项浏览器、3项既有package测试、12项语法/镜像/最小变更/diff静态检查通过 |

操作均经operate记录。主要命令：`.venv/bin/python -B /tmp/flavoretro-task042/qa.py`、`.venv-foundation/bin/python -B -m unittest tests.test_package`、`node --check web/app.js`和`git diff --check`。基线及摘要保存在outputs/task042；截图/临时脚本放/tmp/flavoretro-task042，不入Git。未改科学内容/数据/搜索/API，未重启服务、安装或提交/推送。只验证Chromium及模拟手机视口，其他浏览器和真实触屏未测。

## 截图

![桌面：面包屑已移除](/tmp/flavoretro-task042/1440-without-breadcrumb.png)
![手机：无面包屑占位](/tmp/flavoretro-task042/390-without-breadcrumb.png)

# FlavoRetro 前端开发入口

当前前端是原生JS、CSS和HTML组成的可构建项目。开发源码位于src/与styles/；routes.json登记页面地址，frontend.json登记依赖顺序。根目录index.html、app.js、style.css及包内镜像是生成产物，**修改源码后构建，不直接编辑产物**。

现有绿色视觉体系与五个业务主入口保留；子页可复制地址、刷新、新标签直接进入，支持浏览器返回/前进。禁止加入面包屑（breadcrumb/crumble）栏。教学页顶部原20px/16px间距及背景遮挡保持。

## 常用命令

在仓库根目录运行，TASK-NNN替换为本次已批准的任务编号。构建不安装包、不联网、不重启服务、不启动搜索。

```bash
# 编辑源码后生成三份服务资产及包镜像
python3 scripts/operate.py TASK-NNN python3 -B scripts/frontend.py build --task TASK-NNN

# 检查模板/路由/产物/镜像是否一致；不写文件
python3 scripts/operate.py TASK-NNN python3 -B scripts/frontend.py check

# 开发监听：保存源文件后自动重建，浏览器手动刷新
python3 scripts/operate.py TASK-NNN python3 -B scripts/frontend.py watch --task TASK-NNN

# 列出地址合同
python3 scripts/operate.py TASK-NNN python3 -B scripts/frontend.py routes

# 新建页面、控制器、登记路由并构建；默认不占五个业务主导航
python3 scripts/operate.py TASK-NNN python3 -B scripts/frontend.py create-page --id reports --title 报告 --task TASK-NNN

# 只读浏览器回归：使用已有Playwright环境及运行中的服务
python3 scripts/operate.py TASK-NNN .venv/bin/python -B scripts/check_frontend.py --base http://127.0.0.1:8767/ --task TASK-NNN --output /tmp/flavoretro-frontend.json

# 构建合同与相关包/API检查
python3 scripts/operate.py TASK-NNN .venv-foundation/bin/python -B -m unittest tests.test_frontend_project tests.test_package tests.test_web tests.test_web_foundation tests.test_lab_handoff
```

组件参考地址：当前服务的`/#/components`。它不占业务主导航，示例只修改本地界面状态。按钮、输入、分页、状态、空态和分栏均可实际操作；示例条目不是科学数据。

## 目录与修改职责

| 目录/文件 | 职责 |
| --- | --- |
| src/shell.html | 主header、主导航、main与页面include；不放业务详情 |
| src/pages/search/ | 搜索表单、结果、历史请求恢复与Lab交接 |
| src/pages/history/ | 运行列表与描述性对照 |
| src/pages/resources/ | 资源筛选、分页、详情 |
| src/pages/literature/ | 示例、原理、文献工具、来源阅读、练习、反应证据 |
| src/pages/governance/ | 研究范围 |
| src/pages/components/ | 独立组件参考页 |
| src/components/ui.js / ui.d.ts | 统一组件API及编辑器类型契约 |
| src/core/ | 状态、页面生命周期、导航、能力绑定与启动 |
| src/shared/ | 科学白名单、标签、来源事实及下载共用逻辑 |
| styles/tokens.css | 色彩、字体、间距的基础token |
| styles/components.css | 公共UI类、分栏模板、控件与响应式合同 |
| styles/pages/ | 领域内容与页面特有样式，保留既有必要的显示语义 |
| routes.json / frontend.json | 路由事实源、构建顺序和输出合同 |

[组件规范](../docs/frontend/components.md) · [页面/路由规范](../docs/frontend/routing.md) · [新增页面](../docs/frontend/adding-pages.md) · [测试与交付](../docs/frontend/testing.md)。

## 模块与构建约定

构建器按frontend.json依赖顺序将源文件拼成单个经典脚本作用域，浏览器无需模块服务器或框架运行时；这是显式顺序模块，不使用ES import/export。现有业务函数名保留以减少科学展示与请求语义的风险。新页面将私有状态放在PageRegistry.register回调或闭包内，跨页面通过路由或共享组件合同交互；不读取另一页的私有DOM来发起副作用。

PageRegistry只负责页面加载；路由负责地址和浏览器历史。FlavoUI只负责界面，不读取化学API、不改变搜索参数。构建器会拒绝重复DOM ID、路由与模板不匹配、路径越界、include循环和产物漂移。所有编辑与构建仍遵守AGENTS.md的TASK和operate记录规则。

## 服务与打包

现有Python服务继续只提供原来的根级静态资产，部署/安装包不需要src目录、Node包或新的静态路由配置。开发时用原有服务刷新即可；需要独立本地服务时按已批准TASK使用`python -B -m flavoretro.web --host 127.0.0.1 --port 8877 --workspace /home/ljx/FlavoRetro`。Python环境与业务资产准备见environment/及项目安装说明。

浏览器回归拦截所有非GET请求，不启动真实MCTS。真实搜索、来源准入与科学评价继续按原项目合同单独授权；组件示例和工程通过不提升任何科学证据等级。

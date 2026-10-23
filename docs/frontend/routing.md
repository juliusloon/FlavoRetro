# 页面与地址规范

路由事实源为web/routes.json，模板与主导航由构建器交叉验证。`python3 -B scripts/frontend.py routes`列出当前地址；开发时仍通过operate运行。

现有地址保持：`#/search`、`#/history`、`#/resources/<记录ID>`、`#/literature/examples/<类型>`、`#/literature/principles/<分类>`、`#/literature/tools/<lessons|papers|practice|evidence>`、`#/governance`。组件参考使用`#/components`，不占五个业务主导航。旧`?run=<ID>`自动规范化为`#/search?run=<ID>`。

## 三层职责

| 层 | 位置 | 职责 |
| --- | --- | --- |
| 地址与恢复 | src/core/router.js | push/replace、popstate/hashchange、直接进入、过期请求保护、滚动与会话恢复 |
| 页面生命周期 | src/core/pages.js | register(id,load)/load(id)，拒绝未知或重复注册 |
| 页面控制器 | src/pages/各页 | 读取、渲染、筛选、领域内容；无面包屑 |

搜索结果的实际只读恢复由router按run处理，搜索表单/结果控制器保留原行为。其他页面在自己的源文件注册load函数，router通过PageRegistry.load加载，新增页面无需向主导航条件链增加分支。

## 状态放置

| 状态 | 存放与理由 |
| --- | --- |
| 当前主/子页面、示例/原理、run/route、资源记录 | URL；复制、刷新、新标签可进入同一内容 |
| 关键词、类型、检查状态、分页/每页数、A/B、选中item | URL；返回/前进恢复筛选与阅读上下文 |
| 搜索草稿与budgetOverrides | 当前会话；完整输入不强制公开到分享URL，保留预算默认/显式覆盖区别 |
| 列表/阅读/页面滚动 | 浏览器history.state；回退恢复位置 |
| 六步练习记录 | 原浏览器存储schema/key；导出仍为全六步 |
| 真实运行、来源、科学结果 | 原后端与校验文件；前端导航不改其身份 |

点击导航使用已有goToHash/navigateTab或原生hash链接。点击同一地址不重复压栈；搜索输入替换当前地址，避免每个按键新增历史。来源关联在当前reader读取，跨工具深链继续遵守item合同。异步读取必须保留原generation或等效过期响应保护。

禁止通过浏览器返回拦截来循环留住用户；初次入口之前的返回仍会正常离站。读取、刷新、返回保存结果只使用GET，不启动新MCTS。

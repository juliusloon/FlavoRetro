# 新增页面与组件

先按AGENTS.md建立并批准TASK。最短路径如下，TASK-NNN必须替换为活动任务：

```bash
python3 scripts/operate.py TASK-NNN python3 -B scripts/frontend.py create-page --id reports --title 报告 --task TASK-NNN
```

命令创建src/pages/reports/view.html与controller.js，将页面登记到routes.json、模板shell和构建脚本顺序，并生成运行资产。默认不占业务主导航，可直接打开`/#/reports`。重复页面、危险ID及覆盖已有源会被拒绝。页面标题被HTML转义。

## 页面控制器

```js
PageRegistry.register('reports', () => {
  const container = UI.byId('reports-content');
  container.replaceChildren(UI.empty('暂无可显示的报告。'));
});
```

页面DOM包含唯一id、page类及aria-labelledby；标题用page-heading，面板用ui-panel。使用UI组件和ui-split变体，组件只负责呈现，数据读取/状态归页面。私有状态放闭包；不要把跨页面草稿隐式混入来源或运行身份。

若确实需要业务主导航，修改src/shell.html加入带data-tab/id/ARIA的真实a链接，并将routes.json中primary设true；构建检查会同时要求二者一致。不要加面包屑。现有教学子页在literature的各HTML/控制器维护，保持原地址兼容。

## 组件扩展

1. 先检查FlavoUI是否已覆盖需求；公共分页/状态/列表不要复制实现。
2. 新组件放src/components/ui.js并给出ui.d.ts契约；纯UI组件不得发起API请求。
3. 公共样式放styles/components.css，色彩与尺寸用token；领域布局细节放对应styles/pages文件。
4. 在独立components页增加可操作实例，覆盖空/禁用/错误或其他必要状态。
5. 构建，执行check、Node语法、聚焦测试及浏览器回归；核对桌面/小屏截图，再更新组件说明。

```bash
python3 scripts/operate.py TASK-NNN python3 -B scripts/frontend.py build --task TASK-NNN
python3 scripts/operate.py TASK-NNN python3 -B scripts/frontend.py check
python3 scripts/operate.py TASK-NNN node --check web/app.js
```

所有源通过frontend.json显式排序编译为同一经典脚本作用域；不在源文件直接使用ES import/export。共享组件模块已封装在闭包并通过FlavoUI暴露；现有业务全局名称属于兼容边界，新代码通过PageRegistry和UI调用，不依赖生成物行号。

# 界面组件与视觉规范 v1

状态：TASK047 agent_delegated批准并执行；human_reviewed=false。可运行参考：当前服务`/#/components`。实现位于web/src/components/ui.js、web/styles/components.css，类型位于ui.d.ts；以实现和构建检查为准，不复制某个页面的样式来新增控件。

## 设计基础

沿用绿色/琥珀/灰绿主题。颜色、字体与基础间距统一来自styles/tokens.css。公共组件使用语义变量与以下布局token；页面不再创建同义颜色或控件尺寸。

| Token | 合同 |
| --- | --- |
| --ui-page-block | 桌面/平板20px，手机16px；教学页保留并由sticky背景覆盖 |
| --ui-page-inline | 默认24px，1800及以上40px，手机16px |
| --ui-gap | 桌面20px、手机16px |
| --ui-panel-padding | 桌面20px、手机16px |
| --ui-control-height | 输入/选择/按钮至少44px |
| --ui-radius | 公共控件与面板8px |
| --text-2xl / --text-lg / --text-sm | 页面标题 / 面板标题 / 标签与元信息 |

## 可调用组件

页面源中使用UI别名；独立代码可调用window.FlavoUI。文本组件一律textContent，不把来源文本当HTML执行。

| API | 输入与行为 |
| --- | --- |
| text(tag,value,className) / div(className) | 安全创建DOM；按钮/输入自动获得共享类 |
| button(label,options) | variant为primary/secondary/quiet；disabled、type、onClick；默认type=button，表单提交须明确指定 |
| field(options) | id、label、type、value、options、onChange；生成关联label与输入 |
| badge(value,className) | 紧凑标签；状态仍使用完整文字，不能仅靠颜色 |
| kv(label,value) / fixed(value,digits) | 字段与格式化；0必须显示为0，null/空值与数值零分开 |
| notice(message,options) | info/warning/error；错误role=alert，其余role=status |
| empty(message) | 可读空态；不能把读取失败当作没有数据 |
| pagination(id,state,onChange,sizes) | state={offset,limit,total}；回调(offset,limit)；默认10/25/50/100，翻页边界与无数据禁用统一 |
| listItem(options) | title/meta/href/onClick；真实a链接；选中状态用aria-current |
| panel(options) | title/children/tag；统一面板边框、圆角与padding |
| split(options) | left/right/variant；统一分栏模板 |
| enhance(root) / mount(root) | 将静态/新增DOM纳入共享类；mount只安装一个子树观察器 |

实际业务已使用同一pagination、text/div/kv/标签及列表条目；静态表单/表格/面板经mount纳入同一视觉合同，不维护第二套控件实现。

```js
const submit = UI.button('查询', { onClick: loadItems });
const state = { offset: 0, limit: 25, total: 80 };
UI.pagination('items-pager', state, (offset, limit) => {
  state.offset = offset;
  state.limit = limit;
  loadItems(); // 读取行为由页面负责，组件不请求API
});
container.replaceChildren(UI.notice('读取失败，请重试。', { kind: 'error' }));
```

## 分栏与布局合同

所有分栏外容器使用ui-split和明确的variant，子元素min-width:0/min-height:0。禁止在各页散写近似比例。

| 变体 | 用途与桌面比例 | 紧凑行为 |
| --- | --- | --- |
| reader | 资源/教学列表与阅读，共同1:2 | 小于992px单列；资源保留现有面板切换，教学短列表在上、详情在下 |
| compare | 历史记录与运行对照，共同2:1 | 小于1100px上下堆叠 |
| diagram | 讲解与科学图式，共同1:2 | 小于1100px上下堆叠，图在局部区域横滑 |
| explore | 参数固定宽320–380px，结果占剩余 | 小于992px上下排列，原提交按钮和滚动语义保留 |

768px用于手机控件/标题换行，992px为阅读/搜索工作区切换，1100px为密集对照/图式切换。不同模板使用明确的最小可用宽度，而非临时新增断点。

统一类包括ui-page、ui-page-heading、ui-panel、ui-filter、ui-pagination、ui-table/ui-table-scroll、ui-button、ui-input、ui-list-item、ui-notice和ui-empty。业务class可继续标记科学语义，但不重新实现公共按钮/分页。

## 状态与无障碍

提供默认、选中、禁用、焦点、读取、空态和错误。原生button/a/input语义保留；主导航与教学tabs保留方向键、Home/End、Enter/Space，真实链接可原生新标签进入。小屏分页隐藏首页/末页快捷键，保留上一页/下一页、页码和每页条数。表格在明确区域横滑，不制造整页横溢。

不加入面包屑。教学固定标题上方用不透明背景补齐原页面间距；背景pointer-events:none，不截获点击。科学条件、未知值、冲突、来源定位及边界必须保持可读，不用视觉精简删除科学字段。

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

一个 Chrome MV3 扩展，注入 `claude.ai`，自动点击 Continue / 继续生成 类按钮。给作者自己用的小工具，准备发到 Chrome Web Store。无构建系统、无测试框架、无依赖管理——所有源码就是浏览器最终运行的代码。

## Commands

```bash
# 校验 manifest JSON
node -e "JSON.parse(require('fs').readFileSync('manifest.json','utf8'))"

# 校验 JS 语法
node --check content.js && node --check popup.js

# 重新生成图标（Python 需要 Pillow）
python3 make_icons.py
```

**安装 / 调试循环**：在 `chrome://extensions` 启用开发者模式 → 「加载未打包的扩展程序」选本目录。改完代码后必须做两步：① 在 `chrome://extensions` 点本扩展卡片的 ⟳ 刷新；② `Cmd+R` 已打开的 claude.ai 标签页。content script 只在页面加载时注入，旧标签不会自动获得新代码。

## Architecture

三块组件，**不通过 message passing 通信，而是通过 `chrome.storage.local` 当共享状态总线**：

```
content.js  ←──── chrome.storage.local ────→  popup.js
   │                                              │
   └─ MutationObserver + 间隔扫描                 └─ 用户改设置 → 写 storage
   └─ 命中按钮 → 点击 → 写 storage 计数            └─ storage 变化 → UI 更新
```

两边都订阅 `chrome.storage.onChanged`，所以 popup 改了开关或匹配规则，content script 立刻生效，无需重载。

### Detection strategy（核心设计）

Claude.ai 是 React 应用，class 名是构建时 hash，DOM 结构频繁变。**不能靠 CSS selector 定位按钮**，所以：

- 选择器只筛 `button, [role="button"]` 这两个粗范围
- 真正的判断在 `matchesButton()`：基于按钮**可见文本内容**做 allowlist + exclude 匹配
- Allowlist 命中就点；exclude 包含子串就跳过（防误点 `Continue with Google`、`Cancel`、`删除` 等）

这是这个扩展能在 Claude.ai 改版时仍然工作的原因。如果改版改了**文案**，扩展会失效——这种情况让用户在 popup 里加新文案即可，不需要改代码。

### Safety mechanisms

content.js 里几个看起来"过度"的检查都是有原因的，不要随手删：

- **`recentlyClicked` WeakMap + `cooldownAfterClickMs`**：防止 React 重新渲染同一个按钮节点时被反复点。WeakMap 让节点 GC 后条目自动清理。
- **`minIntervalMs`（1.5s）全局节流**：避免 MutationObserver 触发风暴时连点导致页面卡死。
- **可见性检查（`offsetParent` + `getBoundingClientRect`）**：跳过 DOM 中存在但不可见的按钮（如 React 没卸载的旧弹窗）。
- **MutationObserver + `setInterval(scan, 2000)` 双触发**：某些 React 渲染不会冒泡到我们 observe 的根，间隔扫描兜底。

### Default patterns 位于两处

`DEFAULTS.include` / `DEFAULTS.exclude` 在 `content.js` 和 `popup.js` 各有一份。`popup.js` 那份只在用户点「重置默认」时使用；`content.js` 那份是 storage 没值时的 fallback。**改默认值要两边一起改**。

## Manifest 注意点

- 是 MV3，`host_permissions` 限定 `claude.ai`。不要为了"通用"扩成 `*://*/*`，会触发 Chrome Web Store 更严格的审核。
- 图标必须是 **PNG**。Chrome 拒绝 manifest 里的 SVG，早期版本踩过这个坑。`make_icons.py` 一次产 16/32/48/128 四个尺寸。
- 没有 `background` service worker——content script + popup 已经够用，加 background 只会增加权限审查面。

## Publishing checklist (Chrome Web Store)

- $5 一次性开发者注册费
- 截图 1280×800（≥1，≤5）
- 隐私描述：本扩展不收集数据、不发网络请求、仅注入单一域名——这些都是必填字段的好答案
- 打包：`chrome://extensions` → 「打包扩展程序」→ 选本目录 → 生成 `.crx` + `.pem`。**`.pem` 必须保留**，下次更新需要它签名

## Workspace context

本项目在多项目 workspace `/Users/jiaruili/Downloads/claude-space/tools/` 下，与 `claude-share-fetcher` 等并列。每个工具是独立项目，没有共享构建/依赖。

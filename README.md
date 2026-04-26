# Claude Auto Continue

[![Chrome Web Store](https://img.shields.io/chrome-web-store/v/dmgebhjdnndbihlldbdgafaafgepmhgj?color=facc15&label=Chrome%20Web%20Store)](https://chrome.google.com/webstore/detail/dmgebhjdnndbihlldbdgafaafgepmhgj)
[![Users](https://img.shields.io/chrome-web-store/users/dmgebhjdnndbihlldbdgafaafgepmhgj?color=facc15)](https://chrome.google.com/webstore/detail/dmgebhjdnndbihlldbdgafaafgepmhgj)
[![Rating](https://img.shields.io/chrome-web-store/rating/dmgebhjdnndbihlldbdgafaafgepmhgj?color=facc15)](https://chrome.google.com/webstore/detail/dmgebhjdnndbihlldbdgafaafgepmhgj)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Release](https://img.shields.io/github/v/release/lijiarui/claude-auto-continue?color=facc15)](https://github.com/lijiarui/claude-auto-continue/releases)
[![GitHub stars](https://img.shields.io/github/stars/lijiarui/claude-auto-continue?style=flat&color=facc15)](https://github.com/lijiarui/claude-auto-continue/stargazers)
[![Manifest V3](https://img.shields.io/badge/Manifest-V3-4285F4)](manifest.json)

自动点击 claude.ai 上的 Continue / 继续生成 按钮。

![icon](icons/icon128.png)

> 落地页：https://rui.juzi.bot/claude-auto-continue/

## 它解决什么

在 claude.ai 用得久的人都见过这几条提示：

- `Claude reached its tool-use limit for this turn.` + Continue
- 长回复被 max_tokens 截断 + Continue generating
- 长会话警告 + Continue anyway

每次都得手动戳一下。这个扩展用 MutationObserver 守在页面上，看到符合规则的 Continue 按钮就替你点掉。

## 安装（开发者模式）

```bash
git clone https://github.com/lijiarui/claude-auto-continue.git
```

1. 打开 `chrome://extensions`
2. 右上角打开 **开发者模式**
3. 点 **加载未打包的扩展程序**，选 clone 下来的 `claude-auto-continue/` 目录
4. 打开（或刷新）任意 claude.ai 标签即可

> 已发布版本上线后会更新这里的 Chrome Web Store 链接。

## 工作原理

- **MutationObserver** 监听整个 `document.documentElement` 的子树变化，按钮一出现就检测
- **Allowlist 优先**：必须精确等于或前缀匹配 `Continue` / `继续` 等才会点
- **Exclude 兜底**：包含 `Continue with` / `Cancel` / `删除` 等子串的按钮直接跳过，不会误点登录或破坏性操作
- **频率限制**：两次点击至少 1.5s 间隔，同一按钮 3s 内只点一次
- **可视化校验**：跳过 `disabled` / `aria-disabled` / 不可见的按钮

## 配置

点扩展图标打开 popup：

| 字段 | 作用 |
|---|---|
| 启用自动点击 | 总开关 |
| 匹配按钮文本 | 每行一个，命中即点（大小写不敏感） |
| 排除含这些子串的按钮 | 防误点 |
| 已自动点击 N 次 | 计数器 + 上次点击时间 |

默认匹配：`continue`、`continue generating`、`continue anyway`、`继续`、`继续生成`
默认排除：`continue with`、`continue as`、`cancel`、`discard`、`delete`、`log out`、`sign out`、`取消`、`删除`、`退出`

## 隐私

- 不收集任何数据
- 不发任何网络请求
- 仅在 `claude.ai` 域名下注入
- 配置和计数存在 `chrome.storage.local`，留在你本机

## 文件结构

```
claude-auto-continue/
├── manifest.json     # MV3 manifest
├── content.js        # 注入页面，扫按钮 + 点
├── popup.html        # 设置面板
├── popup.js          # 设置读写 + 计数显示
├── make_icons.py     # 生成图标的脚本
├── icons/            # 16/32/48/128 PNG
└── docs/             # 落地页（GitHub Pages 自动部署）
```

## 开发

修改代码后：

1. 去 `chrome://extensions` 点这个扩展的 **⟳** 刷新
2. `Cmd+R` 已打开的 claude.ai 标签

重新生成图标：

```bash
python3 make_icons.py
```

## 发布到 Chrome Web Store

需要：

- 一次性 $5 开发者注册费
- 截图 1280×800（至少 1 张，最多 5 张）
- 宣传图块 440×280（可选但推荐）
- 隐私说明（见上方）
- 商店描述：可基于这个 README 改写

打包：在 `chrome://extensions` 用 **打包扩展程序**，选根目录，会生成 `.crx` 和 `.pem`。**`.pem` 私钥要保管好**，下次更新需要它。

## License

MIT — 给自己用的小工具，欢迎抄。

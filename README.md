# 课程笔记

把 B 站 / YouTube / 抖音上的长视频课程，整理成**可以反复翻的书**，并且用一个自己的网站发布出来。

- 写作在 [Obsidian](https://obsidian.md/) 里完成（`content/` 就是你的库）
- 发布用 [Quartz 4](https://quartz.jzhao.xyz/)（Obsidian 官方推荐的发布工具之一）
- 推送到 GitHub 后由 GitHub Actions 自动构建，站点托管在 GitHub Pages

笔记本身可以来自 [video2book](https://github.com/LINJIANG12/video2book) 的产物，也可以完全手写。

> **完整的操作手册见 [GUIDE.md](GUIDE.md)**：Obsidian 设置、video2book 实操、部署与回滚、仓库注意事项、排查表。

## 目录结构

```text
.
├── content/                     ← Obsidian 库，只在这里写东西
│   ├── index.md                 首页（课程列表在 <!-- COURSES:START --> 块里，脚本会自动重建）
│   ├── 课程/
│   │   ├── index.md
│   │   └── 计算机网络/            ← 一门课一个文件夹（示例课程，可删）
│   │       ├── index.md         课程总览
│   │       ├── 01-分层模型与协议栈.md
│   │       └── 02-分层模型速记.md
│   ├── templates/               ← Obsidian 模板，构建时被忽略
│   └── 附件/                     ← 图片
├── quartz/                      ← Quartz 引擎（不用改）
├── quartz.config.ts             ← 站点名、域名、主题、插件
├── quartz.layout.ts             ← 页面布局（页脚 GitHub 链接在这里）
├── tools/import_video2book.py   ← 把 video2book 产物导进来的脚本
└── .github/workflows/deploy.yml ← 自动构建 + 发布
```

## 本地预览

需要 Node.js ≥ 22（`node -v` 检查）。

```powershell
npm.cmd install                     # 第一次跑一次就够
node quartz/bootstrap-cli.mjs build --serve
```

打开 <http://localhost:8080>。改 `content/` 里的任意文件，浏览器会自动刷新。

只构建不启服务：`node quartz/bootstrap-cli.mjs build`，产物在 `public/`。

> Windows 的 PowerShell 会拦截 `npx.ps1` / `npm.ps1`（"禁止运行脚本"），所以这里统一用 `npm.cmd` 和 `node` 直调入口。

## 写笔记

1. 用 Obsidian 打开 **`content/` 目录**（不是仓库根目录）作为 vault。
2. 新建课程：`content/课程/<课程名>/`，先写一份 `index.md` 当课程总览。
3. 新笔记从 `content/templates/` 里复制模板，文件名用 `01-主题.md` 这种编号，左侧目录会自动排序。
4. 支持的写法：`[[双链]]`、`> [!note]` callout、` ```mermaid ` 图表、`$公式$`、GFM 表格、代码高亮——Obsidian 里什么样，网站上就是什么样。

每篇笔记开头建议保留 frontmatter：

```yaml
---
title: 分层模型与协议栈
description: 一句话说清这篇解决什么问题（会出现在列表和搜索里）
tags:
  - 精读长文
date: 2026-11-03
---
```

## 导入 video2book 的产物

先把 video2book 跑出结果，得到类似这样的目录：

```text
output/计算机网络/
├── articles/     模块XX_..._精读长文.md
├── textbooks/    模块01_..._精读全书.md
├── notes/        笔记XX_..._笔记.md
└── subtitles/    （默认不导入，体积很大）
```

在仓库根目录运行：

```bash
python tools/import_video2book.py --src "路径/output/计算机网络"
# 连逐字稿一起导入：加 --with-subtitles
# 只看计划不写盘：加 --dry-run
```

脚本会：

- 把 `articles / textbooks / notes` 映射到 `content/课程/<课程名>/精读长文|整编教材|复习笔记`
- 给每篇补 `title / tags / date` 的 frontmatter（已有的只做合并，不覆盖）
- 图片等附件按原相对路径一起搬，笔记里的相对链接不会断
- 重建课程 `index.md` 和首页的课程列表（只动 `<!-- AUTO:START -->`、`<!-- COURSES:START -->` 之间的内容，你自己写的东西不会被覆盖）

## 发布到 GitHub Pages

仓库已经初始化好、也做好了第一次提交，只剩"建远程仓库 + 推送"。

### 1. 建仓库

在 GitHub 上新建一个仓库，名字填 **`notes`**（public 才能免费用 Pages）。
**不要**勾选自动生成 README / .gitignore，保持空仓库。

地址会是 `https://github.com/YanOneX/notes`。如果你换了名字，记得同步改下面的 remote。

### 2. 推送

```bash
git remote add origin https://github.com/YanOneX/notes.git
git push -u origin main
```

第一次 push 会要求认证：[Personal Access Token](https://github.com/settings/tokens) 当密码用（GitHub 早已不支持账号密码）。
Windows 上也会弹浏览器让你登录 GitHub，跟着走更省事。

### 3. 打开 Pages

仓库 → **Settings → Pages → Build and deployment → Source 选 "GitHub Actions"**。
之后每次 `git push`，Actions 会自动构建并发布，地址是：

```text
https://yanonex.github.io/notes/
```

`baseUrl` 不用手改：`quartz.config.ts` 会读 Actions 注入的 `GITHUB_REPOSITORY` 自动推算。

### 4. 日常更新

```bash
git add -A && git commit -m "add: 第 3 章笔记" && git push
```

大约 1 分钟后线上就更新了。在 Actions 页面能看到构建日志。

## 自定义域名

1. 域名 DNS 加一条 CNAME 指向 `yanonex.github.io`。
2. 仓库 Settings → Pages → Custom domain 填域名。
3. 在 `deploy.yml` 的构建步骤里加环境变量 `QUARTZ_BASE_URL: notes.example.com`（`baseUrl` 会优先读它）。

## 常见问题

**中文搜索搜不到？**
Quartz 自带 FlexSearch 对中文是按字切分的，单词搜索没问题；如果搜不到，试着只输入关键词的前两个字。

**字体加载慢 / 打不开 Google Fonts？**
`quartz/styles/custom.scss` 已经给正文和标题配了中文字体回退栈（PingFang SC / 微软雅黑 / 思源黑体），Google Fonts 挂了也能正常显示，只是字形不是 Noto。

**图片放哪？**
统一放 `content/附件/`，笔记里用相对路径引用，例如 `![](../../附件/图1.png)`。Obsidian 设置里把"附件默认位置"指到这个目录即可。

**想换主题 / 加评论 / 加统计分析？**
看 [Quartz 文档](https://quartz.jzhao.xyz/configuration)，改 `quartz.config.ts` 和 `quartz.layout.ts` 两个文件就够。

**Quartz 升级**

```bash
git remote add upstream https://github.com/jackyzha0/quartz.git   # 只需一次
git fetch upstream && git merge upstream/v4
```

冲突一般只出现在 `quartz.config.ts` / `quartz.layout.ts`，按提示保留你的配置即可。

## 许可

站点引擎 [Quartz](https://github.com/jackyzha0/quartz) 采用 MIT 许可，见 `LICENSE.txt`。
`content/` 下的笔记版权归你所有，想开源就加个 CC BY-NC-SA 之类的声明。

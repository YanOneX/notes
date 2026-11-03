# 使用指南

这份指南覆盖四件事：**Obsidian 写作 → 视频转笔记 → 发布部署 → 仓库维护**。
把它当作操作手册，遇到问题先看最后一节的「排查表」。

- 站点：<https://yanonex.github.io/notes/>
- 仓库：<https://github.com/YanOneX/notes>
- 架构：`content/`（Markdown）→ Obsidian 编辑 → `git push` → GitHub Actions 构建 → GitHub Pages 托管

---

## 0. 一页速查

| 想做的事 | 命令 / 操作 |
| --- | --- |
| 本地预览 | `node quartz/bootstrap-cli.mjs build --serve`，开 <http://localhost:8080> |
| 只构建 | `node quartz/bootstrap-cli.mjs build`（产物在 `public/`） |
| 第一次装依赖 | `npm.cmd install` 或 `node <npm-cli.js> install` |
| 发布 | `git add -A && git commit -m "..." && git push` |
| 导入一门课 | `python tools/import_video2book.py --src <目录> --course <课程名>` |
| 看部署状态 | 仓库 → Actions 标签页 |
| 手动重新部署 | Actions → 选 workflow → Run workflow（或 `git commit --allow-empty`） |

> Windows 上 **不要**在 PowerShell 里直接敲 `npx` / `npm`：执行策略会拦 `.ps1`。
> 用 `node quartz/bootstrap-cli.mjs ...` 和 `npm.cmd ...` 这两个写法最稳。

---

## 1. 本地环境

已经装好的东西（免管理员、用户级安装，不需要你再折腾）：

| 工具 | 版本 | 位置 |
| --- | --- | --- |
| Git | 2.56.0.windows.4 | `C:\Users\Miles\AppData\Local\Programs\Git\cmd\git.exe` |
| Node.js | 26.13.0 | `C:\Users\Miles\AppData\Local\Programs\nodejs` |
| npm | 11.20.0 | 跟着 Node 一起 |
| Python | 3.15.2 | 系统已装，导入脚本只用标准库 |

几条已经设好的全局配置，换机器时要记得补：

```powershell
git config --global init.defaultBranch main
git config --global core.quotepath false      # 让中文路径正常显示
git config --global core.autocrlf false       # 避免 CRLF 污染
# 你本机走 127.0.0.1:10808 的代理，git 默认不走系统代理，必须单独指定：
git config --global http.https://github.com.proxy http://127.0.0.1:10808
```

> 代理端口是会变的。如果哪天 `git push` 又出现 `Failed to connect to github.com:443 after 21000 ms`，
> 先确认代理软件当前的 HTTP 端口，再改上面这条配置（或者 `git config --global --unset http.https://github.com.proxy` 直连试试）。

---

## 2. Obsidian 使用

### 2.1 打开仓库

Obsidian → 「打开本地仓库」→ 选 **`course-notes/content`**（不是 `course-notes` 根目录）。

原因：`content/` 才是你的笔记库，`quartz/` 是引擎源码、`public/` 是构建产物，Obsidian 不需要看到它们。

### 2.2 建议的设置（设置 → 文件与链接）

| 设置项 | 建议值 | 为什么 |
| --- | --- | --- |
| 新附件的默认位置 | 「当前文件夹下的子文件夹」+ 名称 `附件` | 图片统一进 `附件/`，Quartz 能正确解析 |
| 使用 `[[Wiki 链接]]` | **关闭**（用 Markdown 链接） | 关掉后链接在 GitHub 网页上也能点，Obsidian 与 Quartz 表现一致 |
| 新建笔记的存放位置 | `课程/` | 免得到处散落 |

设置完成后，粘贴截图会自动存成 `附件/xxx.png` 并在正文插入 `![](附件/xxx.png)`。

### 2.3 写一篇新笔记（标准流程）

1. 在 `content/课程/<课程名>/` 里新建文件，命名 `NN-主题.md`（`NN` 是两位编号，目录自动按名排序）。
2. 从 `content/templates/` 复制模板：`精读长文模板.md` 或 `复习笔记模板.md`。
3. 填 frontmatter（文件开头 `---` 之间的部分）：

```yaml
---
title: 分层模型与协议栈          # 必填：浏览器标签页、OG 卡片、侧边栏都用它
description: 一句话说明这篇讲什么   # 建议填：搜索摘要
tags:
  - 计算机网络
  - 分层模型
date: 2026-11-03               # 建议填：列表页会显示
---
```

4. 正文**只写一个一级标题** `# 分层模型与协议栈`，后面全用 `##` / `###`。

> 为什么强调「只写一个 h1」：Quartz 默认会再渲染一次 frontmatter 标题，两个 h1 会让页面结构和 SEO 都变难看。
> 本仓库已经从布局里移除了 `ArticleTitle` 组件，所以现在**只认正文里的 h1**——正文不写 h1 的页面会没有主标题。

### 2.4 支持的语法

| 语法 | 写法 | 备注 |
| --- | --- | --- |
| 内部链接 | `[分层模型](01-分层模型与协议栈.md)` | 相对路径；构建后自动变成无 `.html` 的漂亮链接 |
| 图片 | `![说明](附件/图.png)` | 路径相对当前文件 |
| 数学公式 | 行内 `$U \approx W/RTT$`，块级 `$$ ... $$` | KaTeX 渲染，`$` 两侧留空格 |
| 流程图 | ` ```mermaid ` 代码块 | 支持 flowchart / sequence / gantt |
| 提示块 | `> [!note] 标题` / `> [!warning]` / `> [!tip]` | Obsidian callout 语法 |
| 表格、脚注、代码高亮 | 标准 Markdown / GFM | 表格过宽会自动横向滚动 |

### 2.5 不要做的事

- **不要提交 `.obsidian/`**：它已在 `.gitignore` 里，属于「本机偏好」，跨设备同步反而会打架。
- **不要手改首页 `<!-- COURSES:START -->` 到 `<!-- COURSES:END -->` 之间的内容**：导入脚本会整块重写。
- **不要把笔记写到 `content/templates/`**：该目录被 `ignorePatterns` 排除，不会出现在网站上。
- **不要在 `content/` 里放超过几十 MB 的视频/音频**：仓库会变得很重，Pages 也有体积限制。

### 2.6 可选插件

- **Templater**：模板变量更灵活（日期、标题自动填）。
- **Dataview**：本地做索引很方便，但**网页端不会渲染**，重要信息别只放在 Dataview 查询里。
- **Excalidraw**：画图后导出 PNG 放 `附件/`，网页端才能看到。

---

## 3. 视频 → 笔记（video2book）

### 3.1 它是什么

[video2book](https://github.com/LINJIANG12/video2book) 是一个**AI 编程助手的技能包**（Claude Code / Codex / OpenCode 都能装），不是独立软件。
它把一门长视频课程按 **40–60 分钟**切成「知识块」，每块产出：

- `articles/`：一篇精读长文（这是主体）
- `textbooks/`：整门课串成的教材（有目录、章节递进）
- `notes/`：跨模块复习笔记（速记、易错点、公式表）
- `subtitles/`：逐字稿（可选，体积大）

取字幕优先；某块没有字幕时才用 `ffmpeg` 抽音频再做转录——所以**有字幕的课几乎不花转录时间**。

### 3.2 安装

按作者仓库 README 的说明，把 skill 装进你用的 AI 助手（Claude Code 放 `~/.claude/skills/`，Codex / OpenCode 各有对应目录）。
依赖：`yt-dlp`、`requests`、`ffmpeg`（只在需要转录时用得上 ffmpeg）。

### 3.3 跑一门课

对 AI 助手说清楚三件事就够了：

```text
用 video2book 把下面这门课做成笔记：
- 课程：计算机网络（B 站合集，共 32 讲）
- 链接：https://www.bilibili.com/video/BVxxxxxxx
- 输出到 D:\notes\output\计算机网络
要求：按 40–60 分钟切知识块，先做精读长文，再整编教材，最后出复习笔记。
```

跑完后你会得到一个 `output/计算机网络/` 目录，里面有 `articles/`、`textbooks/`、`notes/`、`block_plan.json`。

> video2book 交付前有自检门禁（拦套话填充、空壳标题、分集平铺标题、行内残缺引用、分集口吻）。
> 如果它报了这类问题，让它按提示重写对应段落，不要直接拿来用。

### 3.4 导入到站点

导入脚本会把 video2book 的目录结构翻译成本站的结构，并补 frontmatter、复制附件、重建首页课程列表。

```powershell
cd C:\Users\Miles\Documents\deepseek-harness\default-workspace\course-notes

# 1) 先干跑一遍，看它打算写哪些文件
python tools/import_video2book.py --src "D:\notes\output\计算机网络" --course 计算机网络 --dry-run

# 2) 确认无误后正式导入
python tools/import_video2book.py --src "D:\notes\output\计算机网络" --course 计算机网络

# 3) 需要逐字稿时（体积很大，默认不导）
python tools/import_video2book.py --src "D:\notes\output\计算机网络" --course 计算机网络 --with-subtitles
```

分类映射：

| video2book | 本站目录 | 说明 |
| --- | --- | --- |
| `articles/` | `content/课程/<课程>/` | 精读长文，一个知识块一篇 |
| `textbooks/` | `content/课程/<课程>/整编教材/` | 整门课成书 |
| `notes/` | `content/课程/<课程>/复习笔记/` | 跨模块速记 |
| `subtitles/` | `content/课程/<课程>/逐字稿/` | 仅 `--with-subtitles` 时导入 |

常用参数：

| 参数 | 作用 |
| --- | --- |
| `--src` | video2book 的课程工作区（必填） |
| `--course` | 课程名，默认取 `--src` 的目录名 |
| `--vault` | 目标库目录，默认 `content` |
| `--with-subtitles` | 连逐字稿一起导入 |
| `--dry-run` | 只打印计划，不写文件 |

### 3.5 导入后必做的三件事

1. **在 Obsidian 里通读一遍**：AI 生成的长文常有「分集口吻」（"上一节课我们…"）、空泛总结、断裂的引用，改成书面语。
2. **补 `title` / `description` / `tags`**：脚本会补默认值，但默认标题往往是文件名，改成有信息量的说法。
3. **本地预览一遍**：`node quartz/bootstrap-cli.mjs build --serve`，重点看公式、mermaid、图片、表格有没有渲染错。

---

## 4. 发布与部署

### 4.1 日常发布三步

```powershell
cd C:\Users\Miles\Documents\deepseek-harness\default-workspace\course-notes
git add -A
git commit -m "笔记: 新增计算机网络第 3 讲"      # 提交信息写清楚改了什么
git push
```

push 之后到仓库 **Actions** 标签页能看到一次新运行：`build` → `deploy`，全绿后 1–2 分钟内站点更新。

### 4.2 本地预览

```powershell
node quartz/bootstrap-cli.mjs build --serve
```

打开 <http://localhost:8080>，改 `content/` 里的文件会自动重建并刷新浏览器。

> 直接双击 `.md` 或用 `file://` 打开 HTML 是不行的：站点用的是「无扩展名」的目录式链接，必须通过 HTTP 服务器访问。

### 4.3 Actions 做了什么

`.github/workflows/deploy.yml`：

1. `actions/checkout@v4`（`fetch-depth: 0`，为了读到真实 git 提交时间）
2. `actions/setup-node@v4`（Node 22 + npm 缓存）
3. `npm ci`（严格按 `package-lock.json` 安装）
4. `node quartz/bootstrap-cli.mjs build`
5. `actions/upload-pages-artifact@v3` 上传 `public/`
6. `actions/deploy-pages@v4` 发布到 Pages

权限：`contents: read`、`pages: write`、`id-token: write`。**不要**加 `actions/configure-pages` 的 `enablement: true`——`GITHUB_TOKEN` 没有创建 Pages 站点的权限，加了只会让构建失败。

### 4.4 Pages 设置（只需做一次）

仓库 → Settings → Pages → **Source 选 “GitHub Actions”**。

这一步必须人工点一次。之后每次 push 都是全自动的。

### 4.5 域名是怎么算的

`quartz.config.ts` 会读 `GITHUB_REPOSITORY`（形如 `YanOneX/notes`）自动推：

- 仓库名等于 `<用户名>.github.io` → `username.github.io`
- 否则 → `username.github.io/<仓库名>`

当前结果：`https://yanonex.github.io/notes/`。

**换自定义域名**：

1. Settings → Pages → Custom domain 填 `notes.example.com`（GitHub 会自动生成 CNAME 记录要求）
2. 给 workflow 的 build 步骤加环境变量（deploy.yml 里已有注释位）：
   ```yaml
   env:
     QUARTZ_BASE_URL: notes.example.com
   ```
3. DNS 加一条 `CNAME notes → yanonex.github.io`，等生效后勾上 Enforce HTTPS。

### 4.6 手动触发 / 回滚

- **重新部署**：Actions → `Deploy notes to GitHub Pages` → Run workflow；或 `git commit --allow-empty -m "ci: 重跑" && git push`。
- **回滚内容**：`git revert <坏提交>` 再 push（推荐，保留历史）；不要在 Pages 界面折腾。
- **回滚到某个版本**：`git checkout <commit> -- content/` 再提交。

---

## 5. 仓库使用注意事项

### 5.1 目录职责（谁能改，谁别碰）

| 路径 | 职责 | 能不能改 |
| --- | --- | --- |
| `content/` | 笔记正文、附件、模板 | ✅ 随便改 |
| `quartz.config.ts` | 站点名、语言、主题、插件 | ✅ 可以改（改完本地构建验证） |
| `quartz.layout.ts` | 页面布局 | ✅ 可以改 |
| `quartz/styles/custom.scss` | 中文字体栈、表格样式 | ✅ 可以改 |
| `quartz/` 其余 | Quartz 引擎源码 | ⚠️ 已改过 `quartz/components/Head.tsx`（标题去重），升级时注意 |
| `tools/import_video2book.py` | 导入脚本 | ✅ 可以改，改完用 `--dry-run` 验证 |
| `public/`、`node_modules/` | 构建产物 | ❌ 已被忽略，别提交 |

### 5.2 `.gitignore` 的三条底线

当前忽略了：`node_modules/`、`public/`、`.quartz-cache/`、`.obsidian/`、`prof/`、`tsconfig.tsbuildinfo`、`private/`。

> 上游 Quartz 模板的 `.gitignore` 第一行会忽略 `.gitignore` 自己，直接 clone 下来会把 `node_modules` 一起提交。本仓库已经改掉了，**不要从上游重新拷这个文件**。

### 5.3 中文路径与编码

- 全部文件用 UTF-8（无 BOM）保存。
- 文件名可以带中文，但**不要带空格和 `#`、`?`、`%`**——链接里的转义会很难看。
- `git config core.quotepath false` 已设，否则 `git status` 会把中文显示成 `\346\226\207`。

### 5.4 提交信息

建议前缀，方便以后翻历史：

```text
笔记: 新增计算机网络第 3 讲
fix: 修正公式渲染错误
style: 调整中文行距
ci: 调整构建步骤
docs: 更新使用指南
```

### 5.5 大文件

- 逐字稿（`subtitles/`）动辄几十 MB，默认不导。确实要导，先确认仓库总大小（Pages 单站建议 < 1 GB，单文件 < 100 MB）。
- 视频、音频一律不要进仓库，用 `.gitignore` 或放到网盘。

### 5.6 私有内容

`quartz.config.ts` 的 `ignorePatterns` 默认排除 `private/`。想藏草稿：

- 放 `content/private/` 下 → 不进站点，但仍会被 git 追踪（**仓库是公开的，等于公开**）。
- 真要保密：用私有仓库、或把草稿放在仓库外，发布前再拷进来。

### 5.7 升级 Quartz 的代价

`quartz/` 是 vendored 源码（不是 npm 依赖），本仓库已经改过：

- `quartz.config.ts`：站点名、语言、baseUrl 推算、关掉 CustomOgImages
- `quartz.layout.ts`：页脚仓库链接、移除 `ArticleTitle`
- `quartz/styles/custom.scss`：中文字体回退栈、表格滚动
- `quartz/components/Head.tsx`：标题与站点名相同时不拼后缀

升级时别直接覆盖，先用 `git diff` 看上游改了什么，再手工合并这几处。

### 5.8 网络与代理

- 本机 git 走 `127.0.0.1:10808` 代理（已配置）。换网络环境若 push 超时，先查代理端口。
- PowerShell 的 `Invoke-WebRequest` 走系统代理（WinINET），而 git / curl 不走——所以「浏览器能开 GitHub，git 却超时」是正常的，不是网络坏了。

### 5.9 备份与多机

- 仓库本身就是备份。多机写作：`git clone` → 用 Obsidian 打开 `content/` → 写完 `pull --rebase` 再 push。
- 不要把 `.obsidian/` 纳入版本控制；多机想同步设置，用 Obsidian Sync 或自己另建一个私有仓库。

---

## 6. 排查表

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| push 报 `Failed to connect to github.com:443` | git 没走代理 | 设置 `http.https://github.com.proxy`，或用手机热点试 |
| Actions 报 `Get Pages site failed` / `Resource not accessible` | Pages 没启用 | Settings → Pages → Source 选 GitHub Actions |
| Actions 报 `sh: 1: quartz: Permission denied` | 用了 `npx quartz build`，Linux 上脚本没有可执行位 | 改成 `node quartz/bootstrap-cli.mjs build` |
| 站点 404 | 部署还没跑完 / baseUrl 不对 / 文件名大小写不符 | 看 Actions 是否全绿；核对 `quartz.config.ts` 的 baseUrl |
| 页面更新了但浏览器还是旧的 | Pages CDN 缓存 | 等 1–2 分钟，或强制刷新（Ctrl+F5） |
| 图片不显示 | 附件路径写成了绝对路径 | 改成相对路径 `附件/xxx.png` |
| 公式不渲染 | `$` 紧贴正文 / 跨了段落 | `$` 两侧留空格，公式不要跨空行 |
| mermaid 不出图 | 代码块语言写成 `mermaidjs` | 改成 ` ```mermaid ` |
| 页面出现两个大标题 | 正文写了 h1，组件又渲染了一次 | 已从 `quartz.layout.ts` 移除 `ArticleTitle`，若复现检查该文件 |
| 中文文件名在 `git status` 里显示乱码 | 没关 quotepath | `git config --global core.quotepath false` |
| 本地 `npm install` 提示脚本被拦 | npm 11 的 allowScripts 策略 | 可以忽略，`esbuild`/`sharp` 的平台二进制走 optionalDependencies |

---

## 7. 许可

站点内容由你（YanOneX）创作，建议保留一份 `LICENSE`（如 CC BY-NC-SA 4.0 用于文字、MIT 用于脚本）。
Quartz 引擎本身是 MIT，保留其版权声明即可。

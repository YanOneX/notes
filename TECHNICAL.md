# 从零开始：把一门 B 站课程变成自己的笔记网站

> **本指南的贯穿案例**：[黑马程序员 Python+AI 零基础入门到大神全套视频课程](https://www.bilibili.com/video/BV1sHU9BmEne)
> BV 号 `BV1sHU9BmEne`，185 个分 P，总时长 **51.6 小时**，会被切成 **71 个知识块**。
> 每一步的命令都是真在这台机器上跑过的，可以直接复制粘贴。

站点：<https://yanonex.github.io/notes/> ｜ 仓库：<https://github.com/YanOneX/notes>

---

## 目录

- [第 0 章 全局地图：这套组合由四个东西组成](#第-0-章-全局地图这套组合由四个东西组成)
- [第 1 章 环境：哪些已经装好了](#第-1-章-环境哪些已经装好了)
- [第 2 章 安装并配置 video2book](#第-2-章-安装并配置-video2book)
- [第 3 章 第一步：把课程切成知识块（pipeline）](#第-3-章-第一步把课程切成知识块pipeline)
- [第 4 章 第二步：拿逐字稿（字幕优先，缺了才听音）](#第-4-章-第二步拿逐字稿字幕优先缺了才听音)
- [第 5 章 第三步：一个块写一篇精读长文](#第-5-章-第三步一个块写一篇精读长文)
- [第 6 章 第四步：过机器门禁](#第-6-章-第四步过机器门禁)
- [第 7 章 第五步：跨块归并笔记与整编教材](#第-7-章-第五步跨块归并笔记与整编教材)
- [第 8 章 第六步：导入你的 Obsidian 仓库](#第-8-章-第六步导入你的-obsidian-仓库)
- [第 9 章 Obsidian 实操](#第-9-章-obsidian-实操)
- [第 10 章 第七步：发布到 GitHub Pages](#第-10-章-第七步发布到-github-pages)
- [第 11 章 仓库维护注意事项](#第-11-章-仓库维护注意事项)
- [第 12 章 故障排查表](#第-12-章-故障排查表)
- [附录 A 命令速查](#附录-a-命令速查)
- [附录 B 一次跑通的检查清单](#附录-b-一次跑通的检查清单)
- [附录 C 时间与成本预估](#附录-c-时间与成本预估)

---

## 第 0 章 全局地图：这套组合由四个东西组成

| 工具 | 干的事 | 你什么时候碰它 |
| --- | --- | --- |
| **video2book** | 把长视频课程切成 40–60 分钟的知识块，每块产出逐字稿 + 精读长文，再整编成教材和复习笔记 | 第 3–7 章 |
| **Obsidian** | 在本地读、改、组织这些 Markdown 文件 | 第 9 章 |
| **Quartz** | 把 Markdown 文件夹编译成一个静态网站（搜索、目录、图谱、反链、暗色模式） | 第 10 章 |
| **GitHub** | 存代码/笔记 + 自动构建 + 托管网站 | 第 10、11 章 |

数据是从左往右单向流动的：

```text
B 站链接
   │  video2book pipeline       （元数据 → 分集 → 切块，不改内容）
   ▼
block_plan.json  ← 71 个知识块（唯一事实源，锁定后不再变）
   │  queue_tracker --next-transcribe
   ▼
subtitles/BLK01..71_*_逐字稿.md   ← 逐字稿（长文的唯一事实来源）
   │  queue_tracker --next-module
   ▼
articles/模块XX_*_精读长文.md      ← 一块一篇，71 篇
   │  cluster-articles / cluster-notes
   ▼
textbooks/模块N_*_精读全书.md + notes/笔记XX_*_笔记.md
   │  tools/import_video2book.py   （改目录结构、补 frontmatter、重建首页）
   ▼
course-notes/content/课程/<课程名>/…
   │  git push
   ▼
GitHub Actions → GitHub Pages → 你的网站
```

**一句话心法**：video2book 负责「把视频榨成文字」，Obsidian 负责「把文字变成你的理解」，Quartz + GitHub 负责「让理解可以被访问」，`git` 负责「所有改动都可回滚」。

---

## 第 1 章 环境：哪些已经装好了

这台机器上已经就绪的部分（**不用重装**，只要会验证）：

| 组件 | 版本 | 位置 |
| --- | --- | --- |
| Python | 3.15.2 | `C:\Program Files\Python315\python.exe` |
| ffmpeg / ffprobe | N-128293（2026-11-02 构建） | `C:\Users\Miles\AppData\Local\Programs\ffmpeg\ffmpeg-master-latest-win64-gpl\bin` |
| yt-dlp | 2026.10.26 | pip 用户级安装 |
| requests | 2.34.2 | pip 用户级安装 |
| Git | 2.56.0.windows.4 | `C:\Users\Miles\AppData\Local\Programs\Git\cmd\git.exe` |
| Node.js / npm | 26.13.0 / 11.20.0 | `C:\Users\Miles\AppData\Local\Programs\nodejs` |
| Obsidian | 1.15.0 | `C:\Users\Miles\AppData\Local\Programs\Obsidian\Obsidian.exe` |

### 1.1 一条命令验证全部

开一个 **新的** PowerShell 窗口（新窗口才会加载刚更新的 PATH），然后：

```powershell
python -V
ffmpeg -version | Select-Object -First 1
node -v
git --version
```

预期输出类似：

```text
Python 3.15.2
ffmpeg version N-128293-gb034eb5e7e-20261102 ...
v26.13.0
git version 2.56.0.windows.4
```

> **如果 ffmpeg 找不到**：说明当前窗口是旧的 PATH。新开窗口；仍有问题就把这一行加进用户 PATH：
> `C:\Users\Miles\AppData\Local\Programs\ffmpeg\ffmpeg-master-latest-win64-gpl\bin`

### 1.2 PowerShell 的两个坑（必读）

1. **不要直接敲 `npm` / `npx`**：系统执行策略禁止运行 `.ps1`，会报「在此系统上禁止运行脚本」。用 `npm.cmd`，或直接 `node <入口文件>`。
2. **git 与 PowerShell 的代理不是同一条路**：`git push` 超时的时候，先确认代理端口（本机是 `127.0.0.1:10808`）：
   ```powershell
   git config --global http.https://github.com.proxy http://127.0.0.1:10808
   ```

---

## 第 2 章 安装并配置 video2book

### 2.1 它装在哪

已经克隆在：

```text
C:\Users\Miles\Documents\deepseek-harness\default-workspace\video2book\
└── skills\video2book\          ← 这一整个目录才是「技能本体」（含工具链）
    ├── SKILL.md                ← 技能说明书（唯一真源）
    ├── src\cli.py              ← 主命令入口
    ├── scripts\queue_tracker.py← 派发/排队的命令入口
    ├── scripts\selfcheck.py    ← 环境自检
    ├── references\             ← 细则文档（workflow / runtime / cli-cookbook …）
    └── output\                 ← 产物默认写在这里
```

**安装单元 = `skills\video2book\` 整个目录**。换机器时不要只复制 `SKILL.md`，工具链 `src/`、`scripts/` 必须一起带走。

### 2.2 依赖检查

```powershell
cd C:\Users\Miles\Documents\deepseek-harness\default-workspace\video2book\skills\video2book
python src/cli.py info
```

这条命令会打印五个区块：系统环境、多平台采集引擎、听音通道、三域路径、WBI/凭证状态。
看到这些就说明装对了：

```text
• Python 运行环境: v3.15.2
• FFmpeg 状态   : ✓（有版本号）
• 哔哩哔哩 (Bilibili) : [✓] 就绪
```

如果显示 `FFmpeg 状态: ✗ 未找到`，回到第 1.1 节检查 PATH。

### 2.3 登录 B 站（决定你能不能「白嫖字幕」）

**为什么必须登录**：B 站的字幕（含 AI 生成字幕）接口对未登录用户基本不给数据。没登录时 video2book 只能对每个块下载音频再做听音转录——慢十倍不止，而且需要额外的听音通道（见 2.4）。

**取 SESSDATA 的步骤**（3 分钟）：

1. 浏览器登录 bilibili.com。
2. 按 `F12` 打开开发者工具 → 顶部选 **Application（应用）** → 左侧 **Cookies** → `https://www.bilibili.com`。
3. 在列表里找 `SESSDATA`，复制它的 **Value**（形如 `6f1c...%2C1793...` 的一长串，可能带 `%2C`）。
4. 存进 video2book：

```powershell
python src/cli.py login --sessdata "把刚才复制的值粘在这里"
```

5. 验证：

```powershell
python src/cli.py info
# 应看到：• SESSDATA：已配置（来自本地存档）
```

> SESSDATA 等于你的登录态，**不要提交到任何仓库、不要发给别人**。它存在 video2book 自己的配置里，不进 git。
> 有效期通常几个月，失效后重新取一次即可。

### 2.4 可选：听音通道（只在「整块都没有字幕」时才需要）

字幕链路的两个来源：B 站自带字幕（含 AI 字幕）→ 有就直接用；没有才走音频：

```text
ffmpeg 抽音/切片 → read_audio（宿主原生听音） 或 read_media（外部模型代读）
```

后者由配套仓库 [omni-media](https://github.com/LINJIANG12/omni-media) 提供，装在 `video2book/omni-media/`。
**没有它也能跑**：只要课程带字幕。你这门课先按「有字幕」跑，跑不动再补这一步。

---

## 第 3 章 第一步：把课程切成知识块（pipeline）

### 3.1 先干跑，只看拓扑

```powershell
cd C:\Users\Miles\Documents\deepseek-harness\default-workspace\video2book\skills\video2book
python src/cli.py pipeline "https://www.bilibili.com/video/BV1sHU9BmEne" --all --article-type learning --dry-run
```

`--dry-run` 只解析元数据与分集，不写计划、不下音频。你会看到 185 行分集清单，最后一行是工作区路径：

```text
[✓] 工作区: ...\output\黑马程序员Python+AI零基础入门到大神全套视频课程..._BV1sHU9BmEne
```

> 链接里的 `?spm_id_from=...&vd_source=...` 这些跟踪参数可以整个删掉，只保留 `https://www.bilibili.com/video/BV1sHU9BmEne`。video2book 会自己识别「这是一个 185 P 的合集」。

### 3.2 正式跑：生成 BlockPlan

```powershell
python src/cli.py pipeline "https://www.bilibili.com/video/BV1sHU9BmEne" --all --article-type learning
```

这一步做的事（顺序固定）：

1. 拉视频元数据、全部 185 个分 P 的标题与时长 → `parts.json`
2. 按 **50 分钟**为一块（可调）把分 P 打包 → `block_plan.json`
3. 逐块查字幕：有字幕的直接落 `subtitles/`，没字幕的记下来准备物化音频
4. 导出「转录任务书」和「模块长文任务书」

`--article-type` 有两个值：`learning`（推荐，讲透概念、贴课程实际）和 `legacy`（老风格，偏罗列）。不传会直接以退出码 4 终止，这是故意的。

**这门课的实际结果**（本文写作时已跑出真实计划）：

| 指标 | 数值 |
| --- | --- |
| 分集 | 185 |
| 总时长 | 3098.5 分钟 = **51.6 小时** |
| 知识块 | **71 个** |
| 单块时长 | 14.0 – 62.1 分钟（多数 40–50） |

按课程自带的章节分组是这样的：

| 模块 | 分集 | 集数 | 时长 |
| --- | --- | --- | --- |
| Python+AI 课程导学 | P001 | 1 | 0.2 h |
| Python 启航 | P002–P008 | 7 | 1.6 h |
| 核心语法 | P009–P087 | 79 | 21.2 h |
| AI 应用 | P088–P119 | 32 | 9.3 h |
| 网络机器人 | P120–P136 | 17 | 5.7 h |
| 数据分析 | P137–P158 | 22 | 6.5 h |
| Web 应用 | P159–P184 | 13 | 3.8 h |
| 面向对象高级 | P160–P172 | 13 | 3.2 h |
| 感恩同行 | P185 | 1 | 0.1 h |

前 10 个块长这样（可以直接对照着看它是怎么打包的）：

| 块 | 标题 | 覆盖分集 | 时长 |
| --- | --- | --- | --- |
| #1 | 01. Python+AI课程导学 | P01–P03 | 36.3 min |
| #2 | 04. Python启航-环境准备-Python | P04–P06 | 47.5 min |
| #3 | 07. Python启航-入门程序 | P07–P09 | 44.5 min |
| #4 | 10. 核心语法-数据存储与运算-变量 | P10–P12 | 40.5 min |
| #5 | 13. 核心语法-数据存储与运算-数据类型 | P13–P15 | 46.6 min |
| #6 | 16. 核心语法-数据存储与运算-字符串格式化 | P16–P18 | 49.9 min |
| #7 | 19. 核心语法-数据存储与运算-运算符-赋值运 | P19–P21 | 33.9 min |
| #8 | 22. 核心语法-流程控制语句-if基础语法 | P22–P24 | 44.1 min |
| #9 | 25. 核心语法-流程控制语句-if进阶 | P25–P26 | 38.1 min |
| #10 | 27. 核心语法-流程控制语句-match模式匹 | P27–P29 | 48.8 min |

### 3.3 调块大小

```powershell
# 每块 30 分钟：块多、篇短，适合碎片时间读
python src/cli.py pipeline "<链接>" --all --article-type learning --block-minutes 30

# 每块 60 分钟：块少、篇长，适合一次读透一个主题
python src/cli.py pipeline "<链接>" --all --article-type learning --block-minutes 60
```

### 3.4 关于 `block_plan.json`（重要）

- 它是**逻辑块的唯一事实源**：块号、标题、覆盖分集、时间区间全在里面。
- **一旦生成就不再变**。连载课程只允许「往后追加新块」，旧分集/边界改动会直接报错，不会偷偷重排。
- 想换个切法？不要改这个文件，换一个新的工作区名重跑：

```powershell
python src/cli.py pipeline "<链接>" --all --article-type learning --task 黑马Python-30min --block-minutes 30
```

---

## 第 4 章 第二步：拿逐字稿（字幕优先，缺了才听音）

### 4.1 两条路

| 情况 | 走哪条 | 成本 |
| --- | --- | --- |
| 该块所有分 P 都有字幕 | B 站字幕直接转成 `subtitles/BLKxx_*.md` | 几十秒 |
| 有一个分 P 没字幕 | ffmpeg 抽音 + `read_audio`/`read_media` 转录 | 按音频时长算 token |

默认的听音 token 估算：`时长(秒) × BVB_AUDIO_TOKENS_PER_SEC`，后者默认 **32**。也就是 50 分钟的块大约 9.6 万 token 的音频输入——所以**有字幕的课程一定要把 SESSDATA 配上**。

### 4.2 用队列取任务

```powershell
python scripts/queue_tracker.py --next-transcribe --json
```

它只返回「缺字幕、且音频已经物化好」的块。`--json` 输出里有关键字段：块号、标题、音频或字幕路径、任务书全文。

拿到任务后，**转录角色只做一件事**：读音频（或已有字幕）→ 写 `subtitles/BLKxx_<块标题>_逐字稿.md` → 回报一行状态。**不要在这一步写文章**。

### 4.3 检查进度

```powershell
(Get-ChildItem output\*\subtitles -Filter *.md | Measure-Object).Count   # 已经有多少块有逐字稿
```

- 逐字稿是**长文的唯一事实来源**，写作阶段不允许再听音频。
- 每块逐字稿会带「本块身份校验」（来自哪几个 P、时间区间），后面 `check --stage1` 会核对覆盖率。

---

## 第 5 章 第三步：一个块写一篇精读长文

### 5.1 取任务

```powershell
python scripts/queue_tracker.py --next-module 5 --json
```

`5` 是最多返回几块（一次批量拿 5 个）。

返回的 JSON 里有 `dispatch_prompt` —— **这是写好的一整段任务书，必须原样透传给写作的子智能体**，不要自己改写、不要复述。任务书里已经写死了：读哪个逐字稿、输出到哪个文件、标题怎么写、禁止哪些套话。

### 5.2 写作角色只读逐字稿

对每一块：

1. 读 `subtitles/BLKxx_*_逐字稿.md`
2. 按任务书的骨架写成 **≥ 1000 字节**的精读长文
3. 写到 `articles/模块XX_<块标题>_精读长文.md`
4. 回报一行状态（不回传正文）

写作纪律（写在任务书里，也是门禁会查的）：

- 标题**不带序号**（不要「01.」「第 3 讲」）
- 不使用 GitHub 告警块语法（`> [!NOTE]` 这类在交付物里会被拦）
- 公式里 `\neq` 不能断成换行 + `eq`，否则公式真值被改、还会吞掉后文
- 不要出现模型自我对话式的英文推理（`I'm producing garbage…`），会被判「思维链泄漏」，必须重写该篇

### 5.3 人工抽检（强烈建议）

机器只能查「有没有料」，查不出「讲得对不对」。**先只跑 3 个块**（比如 #1–#3），自己从头读到尾，确认风格是你想要的，再放量到 71 块。否则 71 篇写完才发现风格不对，返工代价极大。

---

## 第 6 章 第四步：过机器门禁

```powershell
# 依据级校验：长文是否真的基于本块逐字稿（双层实体覆盖率）
python src/cli.py check --stage1 --strict

# 交付体检：致命项、公式断裂、思维链泄漏、重复标题…
python src/cli.py check --deliver --strict
```

`--strict` 会把提示项也当作失败，适合「准备发布」时跑；日常迭代可以先去掉。

常见修法：

```powershell
# 标题带序号 → 批量去掉（默认只报告，加 --apply 才写盘）
python src/cli.py check --fix-numbering --apply

# 公式断裂（\neq 被折成换行+eq）→ 修回
python src/cli.py check --fix-formula-breaks --apply

# 专名核对：列出逐字稿里查不到的英文专名，产出「专名核对.md」
python src/cli.py audit-names
```

`audit-names` 解决的是 AI 幻觉重灾区：`Pandas` 写成 `Panda`、`FastAPI` 写成 `Fast API`、人名/库名瞎编。它是**只报告不改**，你按清单在长文里逐个核对。

---

## 第 7 章 第五步：跨块归并笔记与整编教材

```powershell
# 1) 块 → 笔记归并：按知识主题分篇（不是一块一篇！）
python src/cli.py cluster-notes "https://www.bilibili.com/video/BV1sHU9BmEne"
python scripts/queue_tracker.py --next-note 5 --json

# 2) 模块长文 → 整编教材：册 = 书，章 = 块
python src/cli.py cluster-articles "https://www.bilibili.com/video/BV1sHU9BmEne"
```

- `notes/笔记XX_<主题>_笔记.md`：标题是纯知识主题（如「字典与其他容器的选择」），**不得含讲师名、课次、块号**；篇数由知识结构决定，不跟块数成比例。
- `textbooks/模块1_<册名>_精读全书.md`：把连续若干块整编成有目录的书，适合打印/通读。

收尾清理：

```powershell
python src/cli.py cleanup    # 回收已完成任务书，每类留 1 份范本
python src/cli.py sync       # 以磁盘产物回填 manifest.json
```

---

## 第 8 章 第六步：导入你的 Obsidian 仓库

### 8.1 先干跑

```powershell
cd C:\Users\Miles\Documents\deepseek-harness\default-workspace\course-notes

# 工作区名很长，用变量取，避免手打
$src = (Get-ChildItem "..\video2book\skills\video2book\output" -Directory | Select-Object -First 1).FullName

python tools/import_video2book.py --src $src --course "Python+AI" --dry-run
```

### 8.2 正式导入

```powershell
python tools/import_video2book.py --src $src --course "Python+AI"
```

脚本做四件事：

1. 按类型映射到站点目录（见下表），补齐 `title / tags / date` frontmatter
2. 复制附件，保持相对路径
3. 重建首页的课程列表块（`<!-- COURSES:START -->`）
4. 生成课程总览页 `content/课程/Python+AI/index.md`（已存在则保留）

| video2book 产物 | 站点位置 |
| --- | --- |
| `articles/*.md` | `content/课程/Python+AI/` |
| `textbooks/*.md` | `content/课程/Python+AI/整编教材/` |
| `notes/*.md` | `content/课程/Python+AI/复习笔记/` |
| `subtitles/*.md` | 默认**不导**（加 `--with-subtitles` 才导到 `逐字稿/`） |

导入后目录长这样：

```text
content/课程/Python+AI/
├── index.md                    课程总览（自动生成）
├── 模块01_…_精读长文.md
├── 模块02_…_精读长文.md
├── …（71 篇）
├── 整编教材/
│   └── 模块1_…_精读全书.md
└── 复习笔记/
    └── 笔记01_…_笔记.md
```

> **为什么不导逐字稿**：71 个块的逐字稿动辄几十 MB，仓库会变得很重，而且网页上没人会读。真要备份，就单独放一个私有仓库或网盘。

---

## 第 9 章 Obsidian 实操

### 9.1 打开仓库

已经帮你注册好了：启动 Obsidian，「打开本地仓库」里应该直接有 **content**。

如果没看到，手动打开：

1. 点「打开本地仓库」
2. 粘贴路径：`C:\Users\Miles\Documents\deepseek-harness\default-workspace\course-notes\content`
3. 点「打开」，弹「是否信任该仓库的作者」时选**信任**（本库只用了核心插件）

**为什么是 `content` 而不是 `course-notes`**：`course-notes` 里还有 `quartz/`（几万个引擎源文件）和 `node_modules/`，Obsidian 会把它们也索引进去，又慢又乱。

### 9.2 界面速览

| 区域 | 是什么 | 常用操作 |
| --- | --- | --- |
| 左侧文件树 | 你的笔记目录 | 右键新建/重命名；拖动改位置 |
| 左侧搜索（放大镜） | 全文搜索 | `Ctrl+Shift+F` 全局搜，支持 `tag:#xx` |
| 左侧图谱 | 笔记之间的链接关系 | 大型图谱在网站上也有一份，这里用于找孤立笔记 |
| 中间编辑区 | Markdown 所见即所得 | `Ctrl+E` 切换编辑/阅读模式 |
| 右侧反链 | 谁链接到了这篇 | 点开就能跳 |
| 右侧大纲 | 本文标题层级 | 长文快速跳转 |

### 9.3 改一篇 AI 生成的长文（最常用）

打开 `content/课程/Python+AI/模块04_…_精读长文.md`，按这个顺序过一遍：

1. **看标题**：`# 标题` 只有一个，且不带序号；下面的 `##` 是知识分节，不是「第一集、第二集」。
2. **删「分集口吻」**：`上一节课我们…` `接下来我们看…` `同学们`——这是从逐字稿带出来的，改成书面语或直接删。
3. **补「为什么」**：AI 容易写成「是什么 + 怎么用」，缺「为什么这么设计、什么场景不该用」。这是笔记和字幕的区别所在。
4. **校对代码块**：变量名、缩进、输出结果。AI 会编造运行结果。
5. **核对专名**：`Pandas` / `FastAPI` / `Streamlit` 的大小写。
6. **加自己的话**：用 `> [!tip]` 写「我的理解/踩坑」，这是把课程变成自己东西的地方。

### 9.4 frontmatter 规范（每篇都要有）

```yaml
---
title: 列表的切片与推导式        # 必填：浏览器标签、搜索、OG 卡片都用它
description: 一句话说清这篇解决什么问题
tags:
  - Python
  - 核心语法
date: 2026-11-03
---
```

### 9.5 常用语法

| 想要 | 写法 |
| --- | --- |
| 内部链接 | `[列表切片](模块05_列表list-切片_精读长文.md)` |
| 图片 | 直接粘贴（自动存进 `附件/`，插入 `![](附件/xxx.png)`） |
| 公式 | 行内 `$O(1)$`，块级 `$$\sum_{i=1}^{n} i$$` |
| 流程图 | ` ```mermaid ` 代码块 |
| 提示块 | `> [!note] 结论` / `> [!warning] 易错` / `> [!tip] 我的理解` |
| 代码 | ` ```python ` 代码块，会语法高亮 |

### 9.6 批量整理技巧

- **改一类标题**：`Ctrl+Shift+F` 搜 `^## `，逐篇检查分节名。
- **找没写完的**：搜索 `TODO` 或 `待补`。
- **按标签聚合**：搜索框输入 `tag:#Python`，或在网站上看标签页。
- **书签**：把「课程总览」加书签，`Ctrl+O` 快速跳转。
- **模板**：`设置 → 核心插件 → 模板` 已指向 `templates/`；`Ctrl+P` → `插入模板`。

### 9.7 改完的检查清单

- [ ] 每篇只有一个 `#` 一级标题
- [ ] frontmatter 有 `title`（没有的话浏览器标签会显示文件名）
- [ ] 图片能显示（路径是相对的 `附件/xxx.png`）
- [ ] 公式前后有空格（`$x$` 不要写成 `$x$和`）
- [ ] mermaid 代码块的语言标记是 `mermaid`
- [ ] 没有残留的「本集/上一集/同学们」

---

## 第 10 章 第七步：发布到 GitHub Pages

### 10.1 本地预览

```powershell
cd C:\Users\Miles\Documents\deepseek-harness\default-workspace\course-notes
node quartz/bootstrap-cli.mjs build --serve
```

打开 <http://localhost:8080>。改 `content/` 里任何文件，浏览器自动刷新。

> 不要用 `file://` 直接打开 `public/index.html`：站内链接是「无扩展名」的目录式链接，必须走 HTTP 服务。

### 10.2 发布

```powershell
git add -A
git commit -m "笔记: 导入 Python+AI 前 10 个模块"
git push
```

push 之后：

1. 打开 <https://github.com/YanOneX/notes/actions>
2. 看到新的一次运行：`build` → `deploy`，两个绿勾
3. 等 1–2 分钟，刷新站点

### 10.3 验证线上真的更新了

```powershell
# 首页是否出现新课程
(Invoke-WebRequest https://yanonex.github.io/notes/ -TimeoutSec 30).Content -match 'Python'
```

### 10.4 回滚

```powershell
git revert <坏提交的哈希>     # 生成一个反向提交，历史保留
git push
```

或者手动重跑一次部署：Actions → 选 workflow → Run workflow。

---

## 第 11 章 仓库维护注意事项

### 11.1 目录职责

| 路径 | 能不能改 |
| --- | --- |
| `content/` | ✅ 随便改（这是你的笔记） |
| `quartz.config.ts` / `quartz.layout.ts` / `quartz/styles/custom.scss` | ✅ 可以改，改完本地构建验证 |
| `quartz/components/Head.tsx` | ⚠️ 改过（标题去重），升级 Quartz 时注意合并 |
| `quartz/` 其余 | ⚠️ 是 vendored 源码，不要随手改 |
| `tools/import_video2book.py` | ✅ 可以改，改完用 `--dry-run` 验证 |
| `public/` `node_modules/` `.obsidian/` | ❌ 已被忽略，不要提交 |

### 11.2 三条底线

1. **不要把 `node_modules/` 和 `public/` 提交进 git**：`.gitignore` 已经写好，别从上游 Quartz 模板重新拷（上游那份会忽略 `.gitignore` 自己，导致 node_modules 混进仓库）。
2. **中文文件名可以，但不要带空格和 `# ? %`**：URL 转义会很难看。
3. **仓库是公开的，`private/` 不等于保密**：`content/private/` 只是不进网站，但依然会被 git 追踪。真要保密只能用私有仓库。

### 11.3 提交信息

```text
笔记: 新增核心语法 10 篇精读长文
fix: 修正 3 处公式渲染
docs: 更新使用指南
ci: 调整构建步骤
```

### 11.4 大文件

- 逐字稿默认不导。真要导，单个文件别超 100 MB，仓库总量别超 1 GB。
- 视频、音频、数据集一律不进仓库。

### 11.5 升级 Quartz

```powershell
# 别直接覆盖。先 diff 上游，再手工合并这四处：
#   quartz.config.ts / quartz.layout.ts / quartz/styles/custom.scss / quartz/components/Head.tsx
```

---

## 第 12 章 故障排查表

### 12.1 video2book 侧

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `FFmpeg 状态: ✗` | PATH 里没有 ffmpeg | 新开窗口；仍不行就把 `...\ffmpeg\bin` 加进用户 PATH |
| `pipeline` 在音频阶段失败 | 缺 ffmpeg 或缺听音通道 | 先装 ffmpeg；再确认该块是否真的没字幕 |
| 字幕全是空的 / 403 | 没登录或 SESSDATA 过期 | 重新 `login --sessdata "<新值>"` |
| `--article-type` 退出码 4 | 没传或传了不支持的值 | 用 `learning` |
| 想改切法但计划已锁定 | BlockPlan 不可改 | 换新工作区重跑（`--task`） |
| `check --stage1` 不通过 | 长文没真正基于逐字稿 | 重写该篇，不要绕门禁 |
| `check --deliver` 报公式断裂 | `\neq` 被折成换行 + `eq` | `check --fix-formula-breaks --apply` |
| 报「思维链泄漏」 | 模型把自我推理写进正文 | 必须重写该篇 |

### 12.2 Quartz / GitHub 侧

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `git push` 报 `Failed to connect to github.com:443` | git 没走代理 | 配置 `http.https://github.com.proxy`，或换网络 |
| Actions 报 `sh: 1: quartz: Permission denied` | 用了 `npx quartz build` | 改成 `node quartz/bootstrap-cli.mjs build` |
| Actions 报 `Get Pages site failed` | Pages 没启用 | Settings → Pages → Source 选 GitHub Actions |
| 站点 404 | 部署没跑完 / baseUrl 不对 | 看 Actions 是否全绿；核对仓库名与 `baseUrl` |
| 页面两个大标题 | 正文写了 `#`，组件又渲染一次 | 已移除 `ArticleTitle`；若复现检查 `quartz.layout.ts` |
| 图片不显示 | 用了绝对路径 | 改成相对路径 `附件/xxx.png` |
| 更新了但浏览器是旧的 | Pages CDN 缓存 | 等 1–2 分钟，`Ctrl+F5` |

---

## 附录 A 命令速查

```powershell
# ==== video2book（工作目录：...\video2book\skills\video2book）====
python src/cli.py info                                     # 环境自检
python src/cli.py login --sessdata "<值>"                   # B 站登录
python src/cli.py pipeline "<链接>" --all --article-type learning [--dry-run] [--block-minutes 50]
python scripts/queue_tracker.py --next-transcribe --json   # 取转录任务
python scripts/queue_tracker.py --next-module 5 --json      # 取写作任务
python src/cli.py check --stage1 --strict                  # 依据级门禁
python src/cli.py cluster-notes "<链接>"                    # 笔记归并
python scripts/queue_tracker.py --next-note 5 --json
python src/cli.py cluster-articles "<链接>"                 # 整编教材
python src/cli.py check --deliver --strict                  # 交付体检
python src/cli.py check --fix-numbering --apply             # 去标题序号
python src/cli.py check --fix-formula-breaks --apply        # 修公式断裂
python src/cli.py audit-names                               # 专名核对
python src/cli.py cleanup                                   # 回收任务书

# ==== 导入（工作目录：...\course-notes）====
python tools/import_video2book.py --src "<工作区>" --course "<课程名>" --dry-run
python tools/import_video2book.py --src "<工作区>" --course "<课程名>" [--with-subtitles]

# ==== 预览与发布 ====
node quartz/bootstrap-cli.mjs build --serve     # http://localhost:8080
node quartz/bootstrap-cli.mjs build             # 只构建到 public/
git add -A; git commit -m "笔记: …"; git push
```

---

## 附录 B 一次跑通的检查清单

**Day 1：跑通 3 个块（先验证风格）**

- [ ] `python src/cli.py info` 里 FFmpeg 是 ✓
- [ ] `login --sessdata` 成功
- [ ] `pipeline … --dry-run` 能看到 185 个分 P
- [ ] `pipeline …` 生成 `block_plan.json`（71 块）
- [ ] `queue_tracker --next-transcribe` 能取到块 1
- [ ] 块 1 的逐字稿落在 `subtitles/`
- [ ] `queue_tracker --next-module 5` 能取到写作任务
- [ ] 块 1–3 的 `articles/` 长文写完
- [ ] `check --stage1 --strict` 通过
- [ ] 通读 3 篇，确认风格 OK（**不满意就停下改任务书，别继续**）

**Day 2：放量**

- [ ] 逐块跑完 71 块（可分批、可中断，任务书记录进度）
- [ ] `check --deliver --strict` 全绿
- [ ] `cluster-notes` + `cluster-articles` 产出教材与笔记
- [ ] `audit-names` 的清单逐条核对

**Day 3：上线**

- [ ] `import_video2book.py --dry-run` 看计划
- [ ] 正式导入，Obsidian 打开 `content/` 通读
- [ ] `build --serve` 本地检查公式/mermaid/图片
- [ ] `git push`，Actions 全绿
- [ ] 打开 <https://yanonex.github.io/notes/> 确认新课程出现

---

## 附录 C 时间与成本预估

这门课 51.6 小时、71 个块。粗略量级（机器/模型不同会有差异）：

| 阶段 | 耗时 | 备注 |
| --- | --- | --- |
| `pipeline` 生成计划 | 1–3 分钟 | 主要是拉 185 个分 P 元数据 |
| 字幕落盘（有 SESSDATA） | 10–30 分钟 | 185 个分 P 逐个查字幕 |
| 音频物化（无字幕时） | 与音频总时长同量级 | 51.6 小时音频，很慢 |
| 逐块写作（71 块） | 数小时到一天 | 取决于并发；一块一篇 40–60 分钟视频 |
| 笔记归并 + 教材整编 | 半小时 | 篇数远少于块数 |
| 导入 + 预览 + 发布 | 10 分钟 | 全自动 |

**省钱省时的三条经验**：

1. **先跑 3 个块**，风格不对就改，别 71 块全跑完再返工。
2. **能拿字幕就别听音**：字幕是几十秒的事，听音是几分钟到十几分钟的事。
3. **分模块推进**：核心语法（21.2 小时）最大，可以先只做它，网站先上线，后面再补 AI 应用/数据分析/Web 应用。

---

## 结语

这套组合的价值不在「自动生成 71 篇文章」，而在于：**视频里的知识被拆成可检索、可引用、可版本管理、可长期增补的文件**。

AI 负责把 51.6 小时的语音压成 71 篇草稿；你的工作是从草稿到「自己的理解」这一步——那一步没人能替你做，但前面的搬运已经省掉了。

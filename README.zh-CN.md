# AgentScout

AgentScout 是一个可复用的 Codex Skill，用来发现、核验、排序、摘要和归档值得关注的 AI Agent 技术工作。

它把持续追踪 Agent 前沿变成一套本地、透明、可继续积累的 Markdown 研究工作流：

- 搜集近期论文、技术报告、工程文章、产品发布和开源项目；
- 优先使用一手来源，核验发布日期与原始链接；
- 生成带稳定编号的中文或英文研究摘要；
- 将用户明确选中的工作写成独立、完整的技术文章；
- 根据最近 60 天的明确归档选择维护兴趣记忆；
- 推荐相邻且具有可延续性的研究方向；
- 配合 Codex 定时任务运行，但不把调度逻辑写进 Skill。

[English README](README.md)

## 为什么做 AgentScout

普通信息流擅长告诉我们什么正在流行，却不擅长保存以下信息：这项工作解决了什么痛点、证据是否充分、方法为什么有效、与以前读过的内容有什么关系，以及下一步还能研究什么。

AgentScout 将过程分为四步：

1. **发现**：在明确日期区间内搜索近期一手技术来源。
2. **判断**：去重，并按技术新颖性、证据质量、兴趣相关性、延续价值和来源可靠性排序。
3. **归档**：只归档用户明确选择的内容，并写成完整技术文章，而不是书签式短笔记。
4. **延续**：分析最近 60 天的归档选择，寻找相邻方向，同时保留探索比例，避免兴趣闭环。

## 仓库结构

```text
agent-scout/
├── SKILL.md                 # 核心执行流程
├── agents/openai.yaml       # Codex 展示与默认提示
├── references/
│   ├── configuration.md     # 研究范围配置
│   ├── schemas.md           # 摘要、归档和 memory 格式
│   └── technical-writing.md # 技术文章写作与证据规范
├── scripts/workspace.py     # 本地研究库管理工具
├── README.md
├── README.zh-CN.md
└── LICENSE
```

## 安装

把仓库克隆到个人 Codex Skills 目录：

```bash
git clone https://github.com/wxhhxn/agent-scout.git ~/.codex/skills/agent-scout
```

如果没有立即识别到 Skill，请重启 Codex。也可以先克隆到其他位置，再复制到 `~/.codex/skills/agent-scout`。

## 快速开始

对 Codex 说：

```text
使用 $agent-scout，搜集最近两个完整自然周值得关注的 5 项 Agent
技术工作，生成中文技术摘要和原始链接。
```

首次使用时，AgentScout 会在你指定或确认的位置初始化研究库：

```text
research-root/
├── config.md          # 研究范围和推荐策略
├── memory.md          # 最近 60 天兴趣记忆
├── archive-index.md   # 可直接跳转的归档索引
├── inbox/             # 每次搜集结果
├── archive/           # 完整技术文章
└── state/seen.jsonl   # 已投递链接，用于去重
```

## 常用指令

### 搜集近期工作

```text
使用 $agent-scout 搜索最近 14 个完整自然日值得关注的 5 项 Agent 工作。
优先关注 OpenAI、Google/DeepMind、DeepSeek、GLM、Anthropic、Meta、
Microsoft、阿里和字节的一手技术报告、论文、工程文章和官方仓库。
只生成候选摘要，不要自动归档。
```

### 归档选中的工作

```text
归档 AS-20260817-01、AS-20260817-05，写成完整技术文章。
```

归档文章会解释：工作面向的痛点、如何证明痛点存在、方法或系统设计、实验或事件证据、痛点解决到什么程度、证据边界、工程启示，以及后续可延续方向。

### 打开本地索引

```text
打开 AgentScout 归档索引。
```

### 更新兴趣记忆

```text
使用 $agent-scout，根据最近 60 天我明确归档的文章更新 memory，
并推荐三个相邻的可延续方向。
```

## 与定时任务配合

简单理解：**AgentScout 负责怎么找，Codex 定时任务负责什么时候找。**

你不需要把定时器写进 Skill，也不需要在提示词里操作 `seen.jsonl`。这些本地文件由 AgentScout 自己维护。

### 第一步：先手动运行一次

先在 Codex 中执行：

```text
使用 $agent-scout，为我初始化 AgentScout 研究库，以后用它保存摘要、归档文章和兴趣记忆。
```

Codex 会让你确认研究库放在哪里。初始化成功后，在同一个本地项目中创建定时任务即可。

### 第二步：创建定时任务

例如设置为每两周运行一次，并把下面这段话作为任务内容：

```text
使用 $agent-scout 搜集最近两周值得关注的 5 项 Agent 技术工作。
重点关注 OpenAI、Google/DeepMind、DeepSeek、智谱 GLM、Anthropic、
Meta、Microsoft、阿里和字节等工业界团队的一手技术报告、论文、
工程文章和官方项目。

请用中文说明每项工作的核心贡献、解决的痛点、关键证据、局限，
并附上原始链接。把本次结果保存到已经初始化的 AgentScout 研究库。
只生成候选清单，不要自动归档；等我回复要归档的编号。
```

这就是普通用户需要填写的全部内容。日期计算、链接去重、摘要文件保存等内部操作由 Skill 完成。

两者的职责是：

- 定时任务决定什么时候运行、运行频率以及在哪个项目目录运行；
- AgentScout 决定搜什么、如何核验、怎样排序、如何写摘要和更新状态；
- 归档仍由用户明确确认，不由定时任务自动决定。

推荐建立两个任务：

1. 每周两次运行“工业界 Agent 雷达”，每次给出 5 个候选。
2. 每月运行一次“兴趣记忆与方向复盘”，分析最近 60 天的归档选择。

如果定时任务需要访问本地研究库，需要保持电脑开机、Codex 桌面应用运行，并让任务在能够访问研究库的本地项目中执行。

## 核心设计原则

- **一手来源优先**：二手文章只用于发现线索或补充背景。
- **明确同意后归档**：看到摘要或没有回复，都不代表同意归档。
- **日期区间可验证**：相对时间使用完整自然日，相邻区间不重叠也不留空。
- **证据分层**：区分来源事实、作者主张和 AgentScout 的推断。
- **拒绝浅归档**：重要来源必须写成可以独立阅读的技术文章。
- **兴趣记忆但不形成茧房**：默认 70% 兴趣匹配、20% 相邻内容、10% 主动探索。
- **本地透明**：摘要、索引、文章、记忆和去重状态都使用 Markdown 或 JSONL。

## 本地研究库工具

```bash
python3 scripts/workspace.py init /研究库路径
python3 scripts/workspace.py seen /研究库路径 --digest /摘要文件路径
python3 scripts/workspace.py index /研究库路径
python3 scripts/workspace.py open-index /研究库路径
```

使用 `python3 scripts/workspace.py --help` 查看当前命令说明。

## 隐私说明

你的研究库可能包含私人阅读偏好和笔记。除非已经仔细检查，请不要把个人研究库提交到这个公开仓库。AgentScout Skill 本身不包含任何个人归档或 memory 数据。

## 参与贡献

欢迎提交 Issue 和 Pull Request，尤其是来源核验、排序机制、技术文章质量门槛、memory 设计和可复现评测方面的改进。

修改 Skill 时请保持 `SKILL.md` 精简，把详细或按需使用的规则放进 `references/`；修改 `scripts/workspace.py` 后应先运行测试。

## 开源协议

[MIT License](LICENSE)

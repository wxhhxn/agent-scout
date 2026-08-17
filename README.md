# AgentScout

AgentScout is a reusable Codex skill for discovering, verifying, ranking, summarizing, and archiving high-signal work about AI agents.

It turns a recurring research habit into a local, inspectable Markdown library:

- scout recent papers, technical reports, engineering posts, product releases, and open-source projects;
- prioritize primary sources and verify publication dates and canonical links;
- produce concise Chinese or English digests with stable archive keys;
- turn user-selected items into standalone technical articles;
- maintain a rolling 60-day preference memory from explicit archive decisions;
- recommend adjacent and continuable research directions;
- work with Codex Scheduled Tasks while keeping scheduling outside the skill.

[中文说明](README.zh-CN.md)

## Why AgentScout

Research feeds are good at showing what is popular. They are less effective at preserving why a piece of work matters, what evidence supports it, how it relates to earlier reading, and what should be investigated next.

AgentScout separates the workflow into four stages:

1. **Discover** — search recent primary sources within an explicit date window.
2. **Evaluate** — deduplicate and rank candidates by novelty, evidence, relevance, continuation potential, and source reliability.
3. **Archive** — only archive items explicitly selected by the user, then write a substantive technical article rather than a bookmark-sized note.
4. **Extend** — learn from the last 60 days of archive choices and propose adjacent, testable directions without collapsing into a filter bubble.

## Repository structure

```text
agent-scout/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── configuration.md
│   ├── schemas.md
│   └── technical-writing.md
├── scripts/
│   └── workspace.py
├── README.md
├── README.zh-CN.md
└── LICENSE
```

`SKILL.md` contains the core workflow. Detailed schemas and writing guidance are loaded only when needed, keeping the skill context compact.

## Installation

Clone the repository into your personal Codex skills directory:

```bash
git clone https://github.com/wxhhxn/agent-scout.git ~/.codex/skills/agent-scout
```

Restart Codex if the skill is not discovered immediately.

You can also clone elsewhere and copy the skill folder into `~/.codex/skills/agent-scout`.

## Quick start

Ask Codex:

```text
Use $agent-scout to collect five noteworthy agent research or engineering works
published during the last two completed weeks. Write Chinese technical summaries
and include the original links.
```

For the first run, AgentScout can initialize a research workspace after you choose or approve its location. A workspace contains:

```text
research-root/
├── config.md
├── memory.md
├── archive-index.md
├── inbox/
├── archive/
└── state/
    └── seen.jsonl
```

## Common prompts

### Scout recent work

```text
Use $agent-scout to find five high-signal Agent works from the last 14 completed
calendar days. Prefer technical reports, papers, engineering posts, and official
repositories from OpenAI, Google/DeepMind, DeepSeek, GLM, Anthropic, Meta,
Microsoft, Alibaba, and ByteDance. Do not auto-archive anything.
```

### Archive selected items

```text
Archive AS-20260817-01 and AS-20260817-05 as full technical articles.
```

Each archived article explains the operating pain point, evidence that the problem exists, method or system design, results, resolution status, limitations, engineering implications, and continuation questions.

### Open the local index

```text
Open the AgentScout archive index.
```

### Refresh preference memory

```text
Use $agent-scout to refresh memory from my explicit archive choices in the last
60 days, then recommend three adjacent research directions.
```

## Scheduled use

The simple model is: **AgentScout decides how to scout; Codex Scheduled Tasks decide when to scout.** You do not need to mention internal files such as `seen.jsonl` in the scheduled prompt.

First, initialize the research workspace once in a regular Codex conversation:

```text
Use $agent-scout to initialize my AgentScout research workspace for digests,
archived articles, and preference memory.
```

After Codex confirms the workspace location, create the scheduled task in the same local project. For example, run every two weeks with this task prompt:

```text
Use $agent-scout to collect five noteworthy Agent works from the last two weeks.
Focus on primary technical reports, papers, engineering posts, and official
projects from industrial teams including OpenAI, Google/DeepMind, DeepSeek,
GLM, Anthropic, Meta, Microsoft, Alibaba, and ByteDance.

For each item, explain its core contribution, pain point, key evidence, and
limitations in Chinese, and include the original link. Save the result in the
AgentScout research workspace that has already been initialized. Return only
a candidate list and wait for me to choose which item numbers to archive.
```

That is all a regular user needs to provide. AgentScout handles date calculation, deduplication, digest persistence, and internal state updates.

A recommended setup is:

- a twice-weekly scouting task that produces five candidates and never archives automatically;
- a monthly synthesis task that reads the rolling 60-day memory and proposes continuations.

When a scheduled task needs local files, keep the computer on and the Codex desktop app running, and run the task in a project that can access the research root.

## Design principles

- **Primary sources first.** Secondary sources are discovery aids, not evidence substitutes.
- **Explicit archive consent.** Delivery is not treated as approval to archive.
- **Calendar-correct windows.** Relative lookbacks use completed calendar days and adjacent windows do not overlap.
- **Evidence-aware writing.** Source facts, source claims, and AgentScout inferences are separated.
- **No shallow archive notes.** Substantive sources become standalone technical articles.
- **Preference without lock-in.** Recommendations default to 70% recent-interest matches, 20% adjacent work, and 10% deliberate exploration.
- **Local and inspectable.** Digests, archives, state, and memory remain plain Markdown or JSONL files.

## Workspace utility

The bundled script provides deterministic workspace operations:

```bash
python3 scripts/workspace.py init /path/to/research-root
python3 scripts/workspace.py seen /path/to/research-root --digest /path/to/digest.md
python3 scripts/workspace.py index /path/to/research-root
python3 scripts/workspace.py open-index /path/to/research-root
```

Run `python3 scripts/workspace.py --help` for the current command reference.

## Privacy

Your research workspace may contain private reading preferences and notes. Do not commit that workspace to this public repository unless you have reviewed it carefully. The skill repository itself contains no personal archive or memory data.

## Contributing

Issues and pull requests are welcome, especially for source verification, ranking rubrics, archive quality gates, memory design, and reproducible evaluation examples.

When changing the workflow, keep `SKILL.md` concise and place detailed or conditional guidance in `references/`. Test deterministic changes to `scripts/workspace.py` before submitting them.

## License

[MIT](LICENSE)

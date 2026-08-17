# Configuration

Create `config.md` in the research root with the following shape. Preserve user edits and omit unused topics rather than inventing preferences.

```md
# AgentScout Configuration

## Delivery
- Language: zh-CN
- Cadence: twice-weekly
- Items per digest: 5
- Summary depth: technical

## Scope
- Topics: memory, planning, tool use, computer use, evaluation, safety, multi-agent systems, agent infrastructure
- Content types: technical reports, papers, engineering posts, official repositories
- Lookback: since last successful run; otherwise 14 completed calendar days ending yesterday
- Retrospective windows: adjacent, with no overlap or gaps

## Source Lanes
- Industrial AI labs: 60%
- Academic research: 25%
- Open-source community: 15%

## Priority Organizations
- OpenAI
- Google DeepMind
- DeepSeek
- Zhipu AI / GLM
- Anthropic
- Meta AI
- Microsoft Research
- Alibaba
- ByteDance

## Recommendation Mix
- Recent-interest match: 70%
- Adjacent: 20%
- Exploration: 10%

## Source Policy
- Prefer primary sources: true
- Allow secondary sources: for context only
- Require canonical URL: true
- Organization prominence affects coverage, not ranking score: true

## Exclusions
- Marketing-only announcements
- Unsourced reposts
```

Source lanes control search coverage, not candidate scores. Priority organizations should receive deliberate coverage, but company prominence must never substitute for technical novelty or evidence quality.

On first use, offer a small set of choices for topic focus, cadence, item count, summary depth, source lanes, and exploration level. Recommend the defaults above when the user has no preference.

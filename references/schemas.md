# Output schemas

## Digest

```md
---
generated_at: 2026-08-17T09:00:00+08:00
window_start: 2026-08-03
window_end: 2026-08-17
item_count: 5
---

# AgentScout Digest — 2026-08-17

## AS-20260817-01 — Original title

- Source: Organization or authors
- Published: YYYY-MM-DD
- Type: technical report
- Tags: memory, evaluation
- Recommendation lane: recent-interest | adjacent | exploration
- Why it matters: one concise sentence
- Summary: 150–300 Chinese characters by default
- Technical contribution: specific mechanism or evidence
- Caveat: limitation, uncertainty, or missing evidence
- Related memory: named interest or `none`
- Link: https://canonical.example/

Archive by replying with keys such as `AS-20260817-01`.
```

## Archive note

```md
---
title: "Original title"
canonical_url: "https://canonical.example/"
source: "Organization or authors"
published_at: "YYYY-MM-DD"
archived_at: "2026-08-17T10:30:00+08:00"
digest_key: "AS-20260817-01"
article_type: "research-paper"
central_claim: "One sentence stating what a technical reader should believe or reconsider."
evidence_level: "controlled-experiment"
resolution_status: "partial"
summary: "One-sentence technical summary used by the local archive index."
tags: [memory, evaluation]
---

# Original title

## Executive summary and central judgment

## Why this work matters

## 面向的痛点

## 如何证明痛点存在

## 方法设计

## 结果与结论

## 痛点是否被解决

## Limitations

## Reusable design ideas

## Relation to my interests

## Continuation questions

## Source
- [Canonical source](https://canonical.example/)
```

Write the archive as a standalone technical article, not a short note. Use source evidence to explain the causal chain from pain point to method to result. State explicitly when the source only demonstrates a problem, reports preliminary evidence, or leaves the pain unresolved.

Allowed metadata values:

- `article_type`: `research-paper`, `system-design`, `model-report`, `benchmark-evaluation`, `security-incident`, `industry-practice`
- `evidence_level`: `problem-observed`, `prototype`, `controlled-experiment`, `cross-setting-validation`, `real-world-evidence`, `production-longitudinal`
- `resolution_status`: `unresolved`, `partial`, `substantial`, `unclear`

## Memory

```md
# AgentScout Memory

Updated: YYYY-MM-DD
Evidence window: YYYY-MM-DD to YYYY-MM-DD

## Stable interests
- Topic — confidence: high; evidence: 5 archives

## Recent strong signals
- Signal — evidence: `archive-file.md`, `archive-file.md`

## Emerging interests

## Fading interests

## Negative preferences

## Open questions

## Promising continuation directions
- Direction
  - Based on:
  - Gap:
  - Next searches:
  - Suggested output:

## Recommendation policy
- Match / adjacent / exploration: 70 / 20 / 10
```

## Ranking rubric

Score each dimension from 0–3, for a maximum of 15:

- Technical novelty
- Evidence quality
- Relevance to configured topics
- Continuation potential
- Source reliability

Use company prominence only as context, never as a scoring dimension. Break ties in favor of primary sources and diversity across topics.

# Technical article workflow

Use this workflow whenever archiving a selected item. Adapt the article to the source type instead of forcing every source into one rigid outline.

## 1. Classify the source

Choose one primary `article_type`:

- `research-paper`: frame research question, hypothesis, method, experiment, and conclusion.
- `system-design`: frame operating constraints, failed alternatives, architecture, trade-offs, and runtime evidence.
- `model-report`: frame capability target, data and architecture, post-training, evaluation, cost, and limitations.
- `benchmark-evaluation`: frame flaws in prior measurement, task and metric design, findings, and validity.
- `security-incident`: frame expected boundary, event chain, failed controls, root causes, remediation, and residual risk.
- `industry-practice`: frame original workflow, agent intervention, human-agent division of labor, gains, and maintenance burden.

If a source spans types, select the type that best matches its central claim and mention secondary aspects in prose.

## 2. Build an evidence ledger before drafting

Internally separate:

- directly observed or documented facts;
- quantitative results reported by the source;
- the authors' causal explanations;
- AgentScout inferences;
- unknown, unavailable, or disputed information;
- contradictions across sources.

Do not silently upgrade a company claim into an independently verified fact. Attribute measurements and causal explanations to their source.

## 3. State one central claim

Write a single sentence that answers: “After reading this article, what should a technical reader believe or reconsider?” Store it as `central_claim` in frontmatter. Exclude side findings that do not support this claim.

## 4. Reconstruct the causal chain

Explain:

1. the real operating constraint;
2. why the prior approach fails;
3. the authors' hypothesis about that failure;
4. how the method implements the hypothesis;
5. how the experiment or incident distinguishes this explanation from alternatives;
6. what changed in the result;
7. the strongest conclusion the evidence supports;
8. where the conclusion may stop generalizing.

Do not confuse correlation with a causal demonstration. State when an ablation, control group, counterfactual, or independent replication is absent.

## 5. Extract the engineering design

When applicable, identify:

- inputs and outputs;
- core modules and their responsibilities;
- where state is stored;
- online and offline paths;
- module interactions and control flow;
- failure detection and recovery;
- dominant latency, compute, data, or operational costs;
- dependencies on a particular model, tool, benchmark, or infrastructure layer.

Use a compact table, sequence, or diagram only when it clarifies relationships better than prose.

## 6. Rate evidence maturity

Set `evidence_level` to one of:

- `problem-observed`: demonstrates a problem but not a solution.
- `prototype`: shows a plausible implementation or proof of concept.
- `controlled-experiment`: works under controlled comparisons.
- `cross-setting-validation`: holds across multiple tasks, models, or environments.
- `real-world-evidence`: includes real users, operations, or incidents.
- `production-longitudinal`: includes sustained production-scale evidence over time.

Set `resolution_status` to `unresolved`, `partial`, `substantial`, or `unclear`. Explain the rating in the article rather than treating it as a score.

## 7. Draft for technical understanding

Use this default narrative, adapting headings to the source type:

1. Executive summary and central judgment
2. Why the work matters
3. Operating context and pain point
4. Evidence that the pain is real
5. Core hypothesis
6. Method or architecture
7. Evaluation or incident evidence
8. What the results actually establish
9. What remains unresolved
10. Reusable engineering implications
11. Relationship to archived interests and adjacent work
12. Continuation questions
13. Sources and evidence boundary

Prefer connected explanation over a list of paper sections. Define specialized terms on first use. Preserve important numbers with their metric, baseline, and evaluation setting.

## 8. Run the quality gate

Before saving, verify:

- A reader can understand the system without reopening the digest.
- The article has one identifiable central claim.
- Important numbers include a baseline and metric.
- The mechanism explains why the method may work, not only which modules exist.
- Source claims and AgentScout inferences are visibly separated.
- Generalization limits and missing controls are explicit.
- The resolution status matches the strength of evidence.
- Engineering implications are actionable rather than generic.
- The frontmatter summary accurately represents the finished article.


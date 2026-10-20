# M1: scope, evaluation contract, and local model feasibility

Created: 2026-10-17 16:18:43 GMT+7
Updated: 2026-10-19 08:46:58 GMT+7

Parent plan: [PoC milestones](milestones-poc.md).

Status: M1 in progress; M1.1 done per the user's instruction on 2026-10-18.
The scope audit implementation and approved fixes are implemented. Ruff lint
checks, package import, YAML loading, and construction of five queries with a
40-entry limit passed. The user then ran audit `20261018T121721Z-e1aff014`: five POST
requests returned 40 entries and 38 unique papers, with no retries, parse
failures, missing controls, or recorded issues. Its status is
`awaiting_manual_review`; no manual decisions are saved. This establishes
execution, not filter accuracy or corpus completeness. Local Kev-9B Q8
classification is the requested follow-up and is not implemented or measured.
No model downloads, remote inspection, or model performance measurements have
been completed. The PC was last reported off by the user. Subsequent work
follows the repository's approval workflow.

## 1. What M1 must establish

M1 turns the agreed product direction into a small, reproducible experiment.
It must answer:

1. Which papers and dates are in scope, and how will we detect collection gaps?
2. Which questions should the PoC answer, and how will usefulness be judged?
3. What configuration and records must later stages share?
4. Can the Ubuntu PC run the chosen embedding/reranking candidates and
   Qwen3.8-27B with at least 65,536 tokens of effective context?
5. What actual memory, storage, and latency does the selected setup require?
   Record latency without making a numeric response-time target an M1 gate.

M1 ends with an evidence-backed readiness decision, not a working RAG product.
The first cited answer remains M4. PostgreSQL schema/index implementation,
LangChain retrieval, and LangGraph conversation implementation belong to later
milestones; M1 records the contracts they will consume.

## 2. Confirmed inputs, proposals, and unresolved inputs

### Confirmed

- LLM research within NLP, covering RAG, agents, reasoning, and evaluation.
- Ten years of history, popularity signals, and comparison of the latest
  complete 90 days with the preceding 90 days.
- Text first, English first, CLI interaction, follow-ups that remember context.
- PostgreSQL/pgvector and LangChain/LangGraph.
- Largest Qwen3 variants: Qwen/Qwen3-Embedding-8B and Qwen/Qwen3-Reranker-8B.
- Evaluate local open-source decision models for paper relevance and topic
  classification. Start with Kev-9B Q8 (`kev:9b-q8_0`); the user permits alternatives
  in pursuit of the best suitable open-source classifier. Keep model selection
  provisional until local, human-labeled comparisons. Runtime compatibility,
  memory, quantized accuracy, and probability calibration remain unmeasured.
- Local Qwen3.8-27B generation at 4-bit quantization, with context >=65,536;
  CPU offload is permitted. The user accepted 4-bit; local operation is unmeasured.
- Ubuntu PC: 64GB RAM and RTX 5070 Ti with 16GB VRAM; heavy work runs here.
- The PoC starts with 10GB of data, replacing the earlier 100GB ambition
  for this PoC. $8 OpenRouter credit was reported; M1 paid inference stays disabled.
- The 20 draft evaluation questions are accepted. Targets are 18/20 useful
  responses and at least 95% factual accuracy in the reviewed claims.
- Ubuntu project root: ~/Documents/cs-radar, to be created later by the user;
  keep paper data, models/caches, database files, logs, and results under it.
- Answer length is deferred by the user. No numeric latency target is agreed;
  measure it and revisit later rather than blocking M1 on a threshold.
- uv/YAML, JSONL logging, and approval before edits. Agent documents stay
  locally excluded; planning documents under `docs/` are intended for Git.

### Verified during plan preparation

The official [Qwen/Qwen3.8-27B repository](https://huggingface.co/Qwen/Qwen3.8-27B)
exists. Its model card lists a native 262,144-token context and Transformers
artifacts. This establishes model availability and the published context claim;
it does not establish that a selected quantization/runtime works on this PC.

### Proposed starting choices

| Item | Proposal | Decision point |
| --- | --- | --- |
| Categories | `cs.CL`, `cs.AI`, `cs.LG`, `cs.IR`, combined with LLM relevance filters | M1.1 sample review |
| Embedding runtime/precision | Keep the confirmed 8B model; start with a small batch and select supported loading/offload settings after inventory | M1.5 |
| Reranker runtime/precision | Keep the confirmed 8B model; load separately and measure actual resource use | M1.5 |
| Generation runtime | First evaluate llama.cpp with a traceable 4-bit GGUF of the requested model | M1.4–M1.6; verify artifact and backend support |
| GPU use | One model workload at a time; measure reload cost | M1.5–M1.6 |
| Paid inference | Disabled; M1 incurs $0 OpenRouter usage | Entire milestone |
| Initial metadata probe | At most 40 records, cached; no PDF collection | M1.1 implemented and run |
| Metadata classifier | Kev-9B Q8 baseline; compare Imajev-4B, with Clef-Flash Q8 as a runtime alternative | M1.1 follow-up; select using local paper judgments |
| Initial corpus | 10GB PoC dataset; use a small debug sample before scaling toward it | M2 pilot, then expansion before final evaluation |

llama.cpp is a candidate because its official documentation describes
quantization, CUDA, and CPU/GPU hybrid inference. Compatibility of the exact
Qwen3.8 artifact and build must still be demonstrated. Do not select a different
base model or install several competing serving stacks as a shortcut.

### Remote profile, paths, and remaining execution prerequisites

The SSH target has been supplied and is recorded in locally excluded AGENTS.md.
Use that local record; keep the public plan free of the personal connection
address. The PC is currently off, and the user will create ~/Documents/cs-radar
later. Do not attempt a connection or create the remote project during planning.

Working path layout, all relative to that Ubuntu project root:

| Path | Use |
| --- | --- |
| `data/sources/` | Retained PDFs, HTML, and metadata responses. |
| `data/extracted/` | Normalized paper text and section records. |
| `data/postgres/` | Database files when M3 is implemented. |
| `models/` | Selected local model artifacts. |
| `models/cache/` | Model-specific caches redirected into the project. |
| `outputs/` and `logs/` | Run artifacts and JSONL events. |

**10GB accounting assumption for this draft:** the initial dataset target/cap
is 10,000,000,000 bytes of retained paper inputs (PDF, HTML, and metadata combined).
Derived text, vectors/indexes, PostgreSQL working space, temporary artifacts, and
model weights are measured separately against the machine's available storage.
This is a proposed interpretation of the user's phrase "10GB of data," not a
confirmed total-project disk cap. Include the accounting rule and actual bytes
in the concrete acquisition proposal before downloading the corpus. Stop intake
at the cap; do not delete sources automatically. The 10GB dataset remains the
PoC scale target; a tiny debug sample does not satisfy it by itself.

Remaining prerequisites are operational evidence: PC availability and checkout,
observed disk/RAM/VRAM, exact artifact/revision/runtime pinning, and a reviewed
installation/download/probe batch. No further product question is needed to
prepare M1.1–M1.3 on the Mac. Resolve the absolute remote home path after
connection and keep artifacts beneath the selected project root.

## 3. Work packages and order

| Work package | Output | Depends on | Gate |
| --- | --- | --- | --- |
| M1.1 | Scope/date/topic rules and a filter audit | Existing requirements | Data scope is explicit |
| M1.1 follow-up | Local decision-model selection, starting with Kev-9B Q8 | Existing audit records; pinned local runtime | Human-reviewed model comparison and abstention evidence |
| M1.2 | 20 fixed query records and scoring rubric | M1.1 | Evaluation is reviewable |
| M1.3 | Minimal configuration, records, and JSONL contract | M1.1–M1.2 | Later stages share unambiguous inputs |
| M1.4 | Ubuntu inventory and pinned artifact/runtime proposal | PC available and user-created checkout | Safe, feasible probe configuration |
| M1.5 | Individual embedding and reranking measurements | M1.3–M1.4; approved setup | Retrieval models work on a small batch |
| M1.6 | Local generation and real 64K context measurements | M1.3–M1.4; approved setup | Generator feasibility established |
| M1.7 | Decisions, limitations, and readiness report | All available evidence | Explicit handoff to M2/M3/M4 |

M1.1–M1.3 can proceed before PC access. M1.5 and M1.6 run sequentially on the
same GPU; their memory measurements must not assume simultaneous residency.

### M1.1 — Freeze the data scope

**Status: Done** per the user's instruction on 2026-10-18.

Implementation: `configs/scope-audit.yaml` and `src/cs_radar/scope_audit/`.
The audit uses POST requests, paced retries, checksum-validated response caches,
validated paper and provenance records, deduplication, review JSONL, a summary
manifest, and JSONL logs. Ruff uses a 120-character line length with E501 enabled.
Checks passed: lint, package import, configuration loading, five-query schedule,
40 planned entries, and the configured date-window calculations.
The user executed run `20261018T121721Z-e1aff014`: 40 entries became 38 unique
papers; all five response checksums matched, and no retries, parsing failures,
missing controls, or recorded issues occurred. Automatic decisions: 7 include,
12 exclude, 19 review. All 38 manual decisions remain unset. Three of eight
controls received their expected definitive decision and five were deferred;
none received a wrong definitive decision. This is execution evidence, not
filter-quality, discovery-recall, or corpus-coverage evidence.

Run from the repository root when ready to perform the audit:

```bash
uv run python -m cs_radar.scope_audit.audit_scope --config configs/scope-audit.yaml
```

**Date semantics**

- Use timezone-aware UTC timestamps internally. Save the report cutoff explicitly;
  never let a reproducibility run silently substitute today's date.
- Proposed first snapshot: `T = 2026-10-17T00:00:00Z`.
- History: `[2016-10-17T00:00:00Z, T)` for this snapshot. Calculate ten calendar
  years, not 3,650 days; define a February 29 anniversary as February 28.
- Recent window: `[2026-07-19T00:00:00Z, T)`.
- Previous window: `[2026-04-20T00:00:00Z, 2026-07-19T00:00:00Z)`.
- First submission determines membership in a publication window. Store revision,
  ingestion, and popularity-observation dates separately.
- arXiv API date filters use GMT minute precision. Fetch a safe superset at
  partition boundaries and apply the exact half-open timestamp filter locally.
- An elapsed time window is not proof of complete metadata coverage. Record
  source lag, partitions/pages checked, partial failures, and snapshot status.
- Historical as-of answers must not use post-cutoff revisions or popularity
  observations as though they were available at that earlier time. If historical
  versions are unavailable, explicitly label retrospective evidence or abstain.

**Relevance and topic rules**

1. Form the candidate pool from the proposed categories and title/abstract
   indicators: large language models, language models, LLMs, and related model
   families. Preserve raw search expressions and a filter version.
2. Review historical terminology such as transformer/pretrained language models;
   a filter requiring the literal term "LLM" would miss earlier relevant work.
   Keep any manually included historical papers explicit and within ten years.
3. Assign zero or more topic labels after establishing LLM relevance:
   RAG, agents/tool use, reasoning, evaluation. Bare words such as "agent" or
   "evaluation" are insufficient evidence of LLM relevance.
4. Store matched rules and reviewed inclusion/exclusion reasons. Category membership
   alone does not prove topic relevance; topic labels may overlap.
5. Maintain a few known-relevant controls, including the previously discussed
   Attention Is All You Need (`1706.03762`), plus excluded non-LLM examples.
   Discover/verify further IDs rather than inventing a seed bibliography.

**Small audit, if approved:** inspect up to 40 cached metadata records across
recent, preceding, and historical periods. Include both accepted and rejected
candidates. Sample size is for debugging the filter, not estimating population
recall or declaring corpus completeness. Repeated API calls use a single paced
client with at least the documented three-second delay; full text access is a
separate policy and separate M2 work.

**Done when:** bounds, candidate expression, inclusion rules, label rules, and
audit limitations can be reproduced. No broad trend claim is made from this probe.

### M1.1 follow-up — Select a local decision model, starting with Kev-9B Q8

**Status: Requested; implementation, runtime probe, and quality evaluation pending.**
The completed audit remains M1.1 evidence. M1.2 can proceed while this follow-up
is prepared. Validate classifier decisions before automated corpus intake and
use the same frozen classification policy in both growth windows.

**Research finding and model selection**

The user clarified on 2026-10-19 that the goal is the best suitable open-source
Jev-like decision model, with alternatives allowed. Kev-9B Q8 exists, but its
availability does not establish that it is the strongest paper classifier.

| Candidate | Verified availability | Role in this experiment |
| --- | --- | --- |
| Kev-9B Q8 | `kev:9b-q8_0`, approximately 9.5GB, Apache-2.0; Ollama decision/MLX route | Requested baseline; first runtime probe on the Mac |
| Imajev-4B | `mohit67890/imajev-4b`, Apache-2.0; publisher supplies MLX weights and calibration | Main quality challenger; verify its native runtime and selected precision |
| Clef-Flash 9B Q8 | `ggml-org/Clef-Flash-GGUF`, Q8_0 approximately 9.66GB; Apache-2.0 source | Runtime alternative if Kev portability blocks the intended Ubuntu setup |

The independent DecideBench repository reports 95.0% for Imajev-4B, 85.2% for
Clef-Flash, and 72.8% for Kev-9B on its 400-item suite. These are reported results
from that benchmark, not Q8 arXiv-paper classification measurements. Inputs were
synthetically authored, and runtimes, model revisions, and served precision
must be checked before interpreting differences. Do not claim a universal winner
or compare these percentages directly to a different benchmark release.

Start with Kev Q8 and one challenger (Imajev-4B), sequentially. This is a proposed
comparison, not authorization to download or install both. Retain Clef-Flash as
an alternative instead of expanding to a model tournament. Pin the exact
checkpoint, decision head, calibration file, runtime, and quantization for each.
A generic chat/GGUF conversion is insufficient unless it preserves and exercises
the model's actual decision interface and probability outputs.

Use identical scope definitions, metadata, question semantics, and human labels
for comparisons; adapt only the encoding required by each native runtime. State
any differences in examples, input limits, precision, or question support. Rank
primarily by inclusion precision/recall and topic quality; compare review rate
and automatic coverage at an agreed error tolerance, then latency and memory.
Choose the model on development judgments, freeze it and its thresholds, then
confirm once on an untouched holdout. Do not select or tune using holdout scores.
The existing 38 records are diagnostic only and cannot establish the best model
for the entire corpus. If the challenger cannot run locally, record that gap
rather than transferring its published score to an untested quantized build.

**Model and runtime**

- First probe Kev-9B at Q8 precision for bounded paper classification. The proposed
  source is `jaredpalmer/kev-9b`, with runtime tag `kev:9b-q8_0`. Avoid the moving
  `kev`/`latest` aliases. Record the resolved base/adapter/head revisions, artifact
  digests, quantization details, tokenizer, runtime version, and platform.
- Kev scores caller-supplied options rather than generating text. Use its
  `POST /v1/systemone` decision interface through one focused adapter. Do not
  expect generated explanations, summaries, evidence quotes, or chat responses.
- The documented Ollama route uses Apple Silicon and requires Ollama >=0.40.4.
  Propose the Mac as the first probe host; verify installed support and measure
  Q8 peak memory and latency. A roughly 9.5GB download is not peak runtime memory.
  Ubuntu/CUDA Q8 support must be established separately; do not infer it from
  the publisher's BF16 CUDA path or silently substitute another precision/model.
- Keep model artifacts beneath the selected project root and record this Mac
  probe exception to the usual Ubuntu-heavy-processing arrangement. No weights,
  services, installations, or downloads are authorized by approving this plan.

**Decision pipeline**

1. Preserve acquisition, raw metadata, reference expectations, and keyword-rule
   outputs as an independent baseline. Keywords discover candidates and provide
   diagnostic hints; they are not definitive semantic acceptance/rejection.
2. Apply date, category, identity, and revision-availability checks in code.
   Kev cannot override these scope constraints. Missing abstracts or unavailable
   as-of evidence remain visible review cases. Do not ask Kev to calculate dates.
3. Classify every otherwise eligible candidate, including keyword-rule rejects,
   so relevant papers missed by the local rule can be recovered. Input is the
   title, complete abstract, categories, and explicit scope definitions. Treat
   paper text as data, not instructions. Keep inclusion expectations, manual
   labels, and the rule decision out of the model's input.
4. Ask one `choice` question with defined options: relevant language-model
   research/foundation, outside scope, and insufficient metadata to decide.
   Distinguish research contributions from incidental use of an existing model;
   route ambiguous application-only cases to review. Relevant foundations may
   belong to none of the four topic families.
5. Ask independent yes/no questions for RAG, agents/tool use, reasoning, and
   evaluation. Define each label by the paper's main contribution, not a bare
   mention. Permit overlapping labels and an empty set. Publish topic membership
   only for accepted papers; retain uncertain topic decisions for manual review.
6. Validate response shape, option names, finite probabilities, and normalization.
   Preserve the full option distributions. Reported confidence is not a proven
   probability of correctness. Select separate inclusion, exclusion, and topic
   thresholds using human labels; do not invent universal calibrated thresholds.
   Map insufficient evidence, ambiguous scores, invalid outputs, timeouts,
   unsupported inputs, and runtime failures to review/error records, not rejection.
7. Keep requests bounded, initially one paper at a time. Count input tokens and
   set explicit state/question limits; never silently truncate an abstract or
   assume the generator's 64K requirement applies to this classifier. Failures
   remain resumable without changing the original audit or manual decisions.

**Configuration, records, and artifacts**

- Plan a dedicated `classify` YAML section consumed only by its command: input
  snapshot, output paths, runtime endpoint, pinned model, input limits, timeout,
  decision definitions/versions, threshold policy, and manual-review behavior.
  Do not add unused configuration to the existing audit command.
- Save separate classification JSONL and a manifest under
  `outputs/classification/<run_id>/`, plus structured events under `logs/`.
  Link paper ID/version, input checksum, source audit/snapshot, classification
  schema, model/runtime identity, question/taxonomy versions, raw probabilities,
  applied thresholds, final decisions, failure/review reasons, and latency.
  Reasons describe policy/routing outcomes; do not fabricate model rationales.
- Cache on paper content/version plus model artifact, quantization, questions,
  tokenizer/runtime behavior, and taxonomy. Keep threshold-based routing
  separate so changing thresholds can reuse raw model scores. Keep raw outputs
  and manual overrides separate; a rerun must not erase reviewed decisions.
- Retain metadata for excluded papers for auditing. No PDF deletion or full text
  acquisition occurs in this classification experiment.

**Evaluation and completion evidence**

- Start with the existing 38 papers as a diagnostic set. Manually establish
  inclusion and topic labels without viewing Kev predictions first; the eight
  reference expectations are controls, not prompts or model training examples.
- Compare the keyword baseline, Kev Q8, and the selected challenger on those
  same papers. Examine corrected
  mistakes, new mistakes, deferred decisions, and missed topic labels, including
  Grid-Bench, evaluation awareness, and API-calling agents. Record ambiguity and
  adjudication instead of forcing a reference label from insufficient metadata.
- Report an inclusion confusion matrix, precision/recall, automatic-decision
  coverage, review/error rates, and per-topic metrics with denominators. Deferred
  cases stay visible; report both accepted-case errors and whole-input coverage.
  Do not call agreement on this tiny diagnostic set population accuracy.
- Before a quality claim or scaled automation, freeze definitions and thresholds
  and evaluate a separate human-labeled holdout spanning recent, preceding,
  historical, relevant, irrelevant, and ambiguous records. Disclose sample size,
  uncertainty, and judgment coverage. Additional data acquisition is a separate
  approved batch. The RAG answer targets (18/20, 95%) are not classifier targets.
- Completion requires a pinned working Kev Q8 runtime or an explicitly selected
  supported alternative, inspectable validated outputs, comparative diagnostic
  results (or a recorded challenger runtime blocker), measured local resources, and an explicitly
  accepted threshold/review policy supported by holdout evidence. Otherwise keep
  decisions human-reviewed and record the remaining limitation.

Sources checked on 2026-10-19:
[Kev-9B model card](https://huggingface.co/jaredpalmer/kev-9b),
[Kev implementation](https://github.com/jaredpalmer/kev),
[explicit Kev Q8 tag](https://ollama.com/library/kev:9b-q8_0),
[Imajev-4B publisher card](https://huggingface.co/mohit67890/imajev-4b),
[Clef-Flash source](https://huggingface.co/Cloudflare/clef-flash),
[Clef-Flash GGUF](https://huggingface.co/ggml-org/Clef-Flash-GGUF), and
[DecideBench results and method](https://github.com/choyiny/decidebench).
Runtime listings and published calibration do not establish accuracy on our papers.

### M1.2 — Define questions and acceptance before tuning

The user accepted these 20 questions. Create stable records without changing
their content. Substitute frozen cutoff/windows when rendering queries; do not
continuously change "recent" between experiments.

| ID | Question | Required behavior |
| --- | --- | --- |
| G01 | Which three collected LLM topics grew most in the recent 90 days? | Counts, comparison window, coverage, reading recommendations. |
| G02 | Did RAG grow in absolute paper count and share of this corpus? | Distinguish absolute growth from share change. |
| G03 | How did agents/tool-use research change between the two windows? | Traceable topic membership and representative papers. |
| G04 | Which reasoning/evaluation directions have the strongest growth evidence? | Explain taxonomy overlap and support size. |
| G05 | Which apparent fast-growing topic has too small a baseline to trust? | Handle low/zero baselines without inflated conclusions. |
| G06 | Which growing topics have popular papers, and which are too recent to judge? | Separate growth, popularity, paper age, and missing counts. |
| H01 | How did agentic LLM research evolve within the collected ten years? | Dated, cited milestones; no unsupported origin claim. |
| H02 | What is the timeline of RAG approaches within the allowed period? | Explain related approaches with supporting papers. |
| H03 | How did tool-use approaches develop into multi-step LLM agents? | Distinguish explicit connections from inferred ones. |
| H04 | How have LLM reasoning approaches changed within this collection? | Explain changes rather than list dates only. |
| H05 | How has evaluation of LLM agents changed over this period? | Name what is measured and cite supporting papers. |
| H06 | Which earlier papers explain the foundations of a recent RAG approach? | Respect ten-year bounds and disclose older missing context. |
| T01 | What should I read to build a RAG system that cites supporting passages? | Task-specific recent and earlier reading with reasons. |
| T02 | What approaches improve the reliability of agents that use tools? | Ground recommendations; disclose evidence limits. |
| T03 | Among collected papers reporting HotpotQA full-wiki F1, what results are comparable? | Verify benchmark/protocol/date; avoid global SOTA claims. |
| T04 | What does this collection say about long-context prompting versus RAG? | Compare evidence and conditions without a universal winner. |
| T05 | How should I evaluate a RAG prototype for answer support and retrieval quality? | Separate retrieval, generation, and evidence support. |
| T06 | What is the best LLM agent architecture? | Ask for task/benchmark constraints before ranking. |
| U01 | What score will my unpublished private model get next month? | Explain that the corpus cannot establish it. |
| U02 | Which method is guaranteed to beat every future LLM paper? | Reject an unsupported guarantee; avoid invented evidence. |

**Split proposal:** G01–G04, H01–H04, and T01–T04 are the 12 diagnostic queries
used for comparisons. G05–G06, H05–H06, T05–T06, and U01–U02 are eight final
holdout queries; do not use their outputs for tuning. Report diagnostic and
holdout results separately, even when quoting a combined 20-query result.
Use separate ad hoc prompts for debugging abstention and follow-up handling.

Each record contains `schema_version`, `query_id`, `workflow`, `split`,
`question_template`, `cutoff`, `required_behavior`, and `required_evidence`.
Add judged passage/paper IDs after a corpus exists. M1 must not fabricate gold
answers, known relevant IDs, popularity counts, or benchmark results.

**Accepted success targets and proposed scoring procedure**

- Usefulness 1: unusable/unsupported; 2: major gaps; 3: partly useful;
  4: useful with minor gaps; 5: directly useful and clearly supported.
- Accepted final PoC target: usefulness >=4 for at least 18/20 queries,
  including appropriate abstention on both U queries. Score correct clarification
  on T06 as useful, rather than rewarding an unsupported confident ranking.
- All citation IDs must resolve. Separately review at least 30 factual claims
  across workflows, or all claims if fewer exist; require >=95% of reviewed
  factual claims to be accurate and supported by cited evidence. Check dates,
  counts, calculations, and reported results; unsupported, contradicted, or
  unverified claims do not pass. Add every material comparative/growth claim
  to review regardless of the sample. Report the numerator and denominator.
  This is factual review against evidence, not independent replication of each
  paper's scientific conclusions. Qualify author-reported results accordingly.
- Report invalid citations, unsupported claims, partial coverage, and no-answer
  cases separately. Traceable citations alone do not prove factual support.
- Retrieval metrics later use paper/passage precision@5 and nDCG@10 on a pooled
  judged set, with judgment coverage disclosed; avoid claiming exhaustive recall.
- Record latency from M1.6 without a numeric pass/fail target. The user
  deferred answer length; keep the capacity probe's technical output reserve
  separate from any future user-facing report-length preference.

**Done when:** the accepted 20 questions and 18/20, 95% targets are faithfully
recorded; split, scoring procedure, and assumptions are reviewable. Acceptance
of the questions and targets is not evidence of a successful evaluation run.

### M1.3 — Specify the smallest usable configuration and records

**Configuration contract**

Propose one `prepare` section in `configs/poc.example.yaml`; its first command
loads only that section. The initial execution validates configuration and
collects local/read-only readiness information. Network probes and model loads
are explicit selections in an approved run configuration, never side effects
of parsing YAML or importing the package.

| Group | Fields/behavior to define |
| --- | --- |
| Run | Stable run name/ID, output root under `outputs/`, selected checks. |
| Scope | Fixed UTC cutoff, ten-year rule, window days, categories, filter/taxonomy versions. |
| Paths | Ubuntu root ~/Documents/cs-radar; data/model/cache/database/log/result paths stay beneath it; relative paths resolve against the YAML file directory. |
| Budgets | Initial dataset 10,000,000,000 bytes; provisional retained-source accounting above; derived/model/run storage measured separately; paid inference disabled. |
| Generator | Official base ID, pinned revision, selected artifact/checksum, backend/build, context >=65,536, output reserve, offload, reasoning/sampling mode. |
| Embedding/reranker | Base IDs, revisions, devices, dtype/quantization, documented formatting, batch/input limits; embedding dimensions/normalization. |
| Classifier | Selected decision model (Kev Q8 baseline), artifact/head/calibration/runtime identity, native endpoint, versioned questions, input limits, routing policy; separate classification stage. |
| Probe | Prompt targets, repetitions, per-request timeout, sampling interval, stop thresholds. |
| Logging | JSONL destination, level, schema version, host alias; no credentials or full prompts. |

Reject unknown keys, invalid dates, negative budgets, unsupported checks, and a
generator context below 65,536. Validate cross-field token budgets. Use safe YAML
loading and Pydantic v2. Separate structural validation from runtime checks such
as file existence, GPU capability, network availability, and model loading.
An example with unresolved artifact paths can pass structural validation but
cannot pass the model feasibility gate.

Only add settings that the M1 stage actually consumes. Record future-stage
requirements as the following contracts; do not create unused pipeline classes,
database tables, retrieval code, or no-op CLI commands for them.

**Records and lineage**

| Record | Minimum fields and invariant |
| --- | --- |
| Paper identity | Base arXiv ID; separate positive version number. Cross-listings share a paper ID. |
| Paper metadata | Title, authors, categories, first submission, revision date, URLs, retrieval time, inclusion/label reasons. |
| Source artifact | Paper/version, format, source URL, local reference, content checksum, acquisition time. Unknown fields stay null until acquisition. |
| Classification | Paper/input/model/question/taxonomy identity, raw option distributions, threshold policy, inclusion/topic decisions, review/error reason, latency; separate from human labels. |
| Section/chunk contract | Artifact/extraction version, section path, anchor or page span, chunk text/offsets, parser and chunk configuration hash. |
| Snapshot manifest | Cutoff/bounds, filters, query partitions/pages, record counts, failures, completeness state, manifest hash. |
| Readiness result | Run/config hash, check, status, observed metrics, artifact references, blocker/reason; unmeasured values are null. |

Define contracts first; instantiate only the records M1 uses. Hash canonical,
non-secret behavior settings and content separately. Do not use an ingestion
timestamp as content identity or allow transient run paths to invalidate every
content cache. An explicit input change must produce a new appropriate version.

**JSONL example (illustrative, not a measurement)**

```json
{"schema_version":1,"timestamp":"2026-10-17T16:18:43+07:00","level":"INFO","event":"check_completed","run_id":"m1-example","stage":"prepare","host":"ubuntu-pc","check":"generator_context","status":"blocked","duration_ms":0,"reason":"runtime_not_checked","metrics":null}
```

Use the standard-library logger with one JSON formatter, and separate log events
from human CLI output and result JSON. Measure durations with a monotonic clock.
Persist one result manifest per run; never convert skipped or failed measurements
to zero-valued success metrics. Avoid full config/prompt/credential dumps.

**Done when:** example configuration and minimal records validate, output and
path semantics are documented, and checks have actionable failure messages.
Any automated checks are proposed with the implementation batch; no tests are
added or run merely by approving this planning document.

### M1.4 — Inspect the PC and choose a reproducible probe setup

1. Once the user makes the PC and project available, use the local SSH profile
   and resolve ~/Documents/cs-radar. Inspect read-only OS/architecture,
   CPU/RAM, GPU/driver/free VRAM, disk/filesystem space, existing uv/runtime
   installs, and competing GPU processes. Do not stop unrelated processes.
2. Typical inventory commands include `uname -m`, `lscpu`, `free -h`,
   `nvidia-smi`, and `df -B1` on each selected path. Capture relevant output,
   command failures, and timestamp; do not infer installed CUDA support from the
   GPU name or from the driver's advertised maximum CUDA version alone.
3. Review the exact generator quantization: publisher, upstream base/revision,
   conversion recipe, file list/size/checksum, embedded tokenizer/template,
   and compatibility with a pinned runtime build. Prefer the requested model's
   unmodified behavior; do not substitute a fine-tuned derivative by name alone.
4. Select one supported CUDA/CPU runtime configuration. For Python inference
   dependencies, use uv and a documented compatible wheel/index choice after
   checking this host. Do not install a CUDA stack by guessing version tags.
5. Calculate space for selected weights, caches, temporary downloads, and build
   artifacts. Resolve an explicit per-run disk/memory budget from observed free
   resources before downloads. Avoid keeping full-precision originals alongside
   quantizations unless needed and included in that budget.
6. Review the concrete setup/download batch. Keep model files out of Git.
   Record native inference binary/build provenance separately from Python's lock.

**Done when:** a bounded, reproducible setup is ready to approve, or an explicit
hardware/artifact/runtime blocker is recorded. Read-only inventory alone does
not establish model execution readiness.

### M1.5 — Probe embedding and reranking separately

1. Load only Qwen/Qwen3-Embedding-8B. Use a tiny controlled set of short
   paper-like passages and relevant/unrelated queries. Follow the official
   query instruction, document formatting, pooling, and normalization recipe.
2. Confirm output count, dimensions, finite values, deterministic settings where
   supported, and a basic relevant-versus-unrelated ranking sanity check. Probe
   batch sizes one and four with bounded input lengths; record real token counts,
   input truncation, elapsed time, peak RAM/VRAM, and throughput.
3. Start the small exact-search baseline with the 8B model's native 4,096
   dimensions. HNSW supports at most 2,000 dimensions for vector and 4,000 for
   halfvec, so native 4,096 dimensions cannot use either HNSW type directly.
   Before ANN indexing, compare a model-supported reduced output (for example
   2,048 dimensions with halfvec) with the full-dimensional exact baseline.
   Record normalization, precision, dimension, and quality effects. Reducing
   output dimension keeps the selected 8B model; never switch to 4B silently.
4. Unload/release the embedding workload; observe whether memory is actually
   available. Load Qwen/Qwen3-Reranker-8B alone and score a bounded
   query/passage pool
   using its documented pair formatting and scoring recipe.
5. Record simple ordering checks and candidate-count latency. This establishes
   adapter behavior, not retrieval quality on the future paper corpus.
6. Measure one transition back to embedding or generation. Persist the model
   load/unload time and expected interactive cost of sequential operation.
   Do not assume either 8B model fits fully on the GPU; choose compatible
   precision/offload/batch settings from actual measurements.

**Done when:** selected models produce valid inspectable results, recorded
settings/revisions and memory use, and no unexplained truncation. A failed
reranker does not block M3's retrieval baseline; it remains a prerequisite for
M6's reranker experiment. Do not silently switch to a smaller model on failure.

### M1.6 — Demonstrate the required generation context

**Baseline setup**

- Keep the selected 4-bit Qwen3.8-27B artifact, tokenizer/template, runtime build,
  exact quantization format, cache precision, CPU/GPU allocation, threads, and reasoning mode
  explicit. Start with one request/slot so total server context is not divided
  among several parallel sessions.
- Use a recorded non-thinking baseline if the selected backend correctly honors
  the model's documented control; otherwise record the effective mode. Count
  any generated reasoning tokens in output and memory budgets.
- Use text input only. The model's vision capability is not part of this gate.
- Do not silently shorten, shift, summarize, or drop old input to make the
  declared context fit. A GPU-fit convenience setting must not reduce 65,536.

**Token accounting example**

For a 65,536-token context, reserve 2,048 output tokens and 512 safety tokens.
The maximum final formatted input is then 62,976 tokens. Count system text,
chat-template tokens, history, evidence, and question together. Cross-check the
runtime's admitted token count with the selected tokenizer; record differences.
Reserving output is separate from forcing the model to generate all 2,048 tokens.

| Probe | Proposed input | Purpose |
| --- | --- | --- |
| Short | About 2K final input tokens; bounded output | Establish load, first-token, and decode behavior. |
| Intermediate | About 8K then 32K if needed | Locate a resource/latency problem before a costly long trial. |
| Required long | At least 60K final input tokens within the computed budget | Demonstrate actual near-64K input followed by generation. |
| Repeat | One warm long request if the first completes within the agreed time budget | Distinguish cold/reload and warm costs. |

Use reproducible paper-shaped synthetic sections with known facts at the
beginning, middle, and end. Save seed/content hash and expected facts. Confirm
all positions were admitted and ask for the controlled facts. Passing is a
capacity/sanity result, not proof of scientific reasoning or long-context quality.
Real retrieved-paper answer quality is evaluated from M4 onward.

**Measurements per request**

- Model load time; cold/warm/cache state; final admitted input and output tokens.
- Time to first token, prompt-processing time/rate, decode time/rate, total time.
- Peak host RAM and GPU memory, offloaded components, cache settings, and swap
  activity. Fix resource sampling cadence and record it with the result.
- Finish reason, errors/timeouts, input truncation/context shift, and the
  controlled-fact result. Unknown metrics remain null.

Set timeouts and memory/disk stop thresholds after the inventory and short
probe, before the long trial. Long trials need progress reporting and cancellation;
an aborted or timed-out trial is not a pass. Do not extrapolate the short trial's
speed as though it were the measured 64K speed.

**Done when:** a >=65,536 effective context is verified, a >=60K-token input
is actually processed without hidden truncation, and generation completes with
recorded resource use. Demonstrate the controlled facts and review observed
interactive latency without requiring a numeric SLA or an answer-length
preference. If model/context execution is not feasible, report a blocker and options while
preserving the requested model/context requirement until the user changes it.

### M1.7 — Record decisions and hand off

Write a concise `docs/m1-readiness.md` after execution, with:

1. Final scope/date/taxonomy version and remaining collection biases.
2. Accepted 20 questions and 18/20, 95% targets; scoring/split procedure;
   answer-length preference deferred and latency recorded without a threshold.
3. Exact selected model artifacts, revisions, runtime builds, and settings.
4. A result table linking measured JSON/JSONL artifacts by run ID/hash.
5. Storage locations, download footprint, RAM/VRAM peaks, timings, reload cost.
6. Explicit passed, failed, blocked, skipped, and not-run checks.
7. What can proceed and what cannot, followed by the next proposed edit batch.

Keep runtime outputs under ignored `outputs/`/`logs/`; a tracked summary can
include compact non-secret results. M1 artifacts must not imply that full text
ingestion, database integration, retrieval quality, or end-to-end answers passed.

## 4. Expected implementation artifacts

Paths below are a proposed change map, not files to scaffold during planning.
Show exact content/diffs before each implementation batch.

| Artifact | Purpose |
| --- | --- |
| `configs/poc.example.yaml` | First consumed `prepare` settings and documented path/budget semantics. |
| `eval/poc-queries.jsonl` | The 20 versioned query records with explicit split and required behavior. |
| `src/cs_radar/config.py` | Validated M1 configuration and safe YAML loading. |
| `src/cs_radar/records.py` | Only the compact records/results actually used by M1. |
| `src/cs_radar/logging.py` | Standard-library JSONL formatter/configuration. |
| `src/cs_radar/cli.py` | Thin `prepare` command and clear failure exits. |
| Focused readiness/model helpers | Add only for actual inventory/probe behavior; choose names in the relevant batch. |
| `pyproject.toml`, `uv.lock` | Add consumed dependencies and console entry point together through uv. |
| `README.md` | Actual setup/run commands and honest limits, after those commands exist. |
| `docs/m1-readiness.md` | Selected decisions and measured readiness summary after execution. |
| `outputs/prepare/<run_id>/` | Local manifest, resource/model metrics, and compact probe references. |
| `logs/<run_id>.jsonl` | Local structured diagnostic events, separate from CLI output. |

Proposed first command shape: `uv run cs-radar prepare --config configs/poc.example.yaml`.
It is not implemented yet. Start with Pydantic/PyYAML only if consumed; add model
inference packages in the approved hardware-specific batch. LangChain/LangGraph
remain selected, with their integration implemented in M3/M4/M7 as appropriate.

## 5. Review batches and readiness gates

### Suggested implementation batches

1. **Scope/evaluation:** agreed scope/filter/date rules and 20 query records.
2. **Contracts/CLI:** minimum YAML validation, result records, JSONL logging,
   and the first useful `prepare` behavior. Propose any automated checks here.
3. **PC setup:** read-only inventory, then a concrete pinned installation and
   model download proposal using observed available resources.
4. **Model probes:** sequential embedding/reranking and generation/context runs,
   with actual run settings, caps, and output locations shown in advance.
5. **Close M1:** publish measured summary, update parent milestone evidence/status,
   and propose the bounded M2 implementation.

### Gate checklist

- [ ] Scope and time bounds are explicit; filters/taxonomy have versions.
- [ ] Accepted query records and 18/20, 95% targets are saved; scoring/split procedure is reviewed.
- [ ] Consumed YAML/record/log contracts work with clear validation failures.
- [ ] Ubuntu inventory and selected paths are observed, not assumed.
- [ ] Exact generator artifact and runtime are pinned and traceable.
- [ ] Embedding small-batch probe passes with recorded dimensions/resources.
- [ ] Reranker probe has a recorded outcome; a failure remains visible for M6.
- [ ] Required generator context and real near-64K request pass, or remain blocked.
- [ ] Actual latency is recorded; no numeric response-time or answer-length gate is imposed.
- [ ] Disk and paid usage remain within agreed caps; M1 paid usage is zero.
- [ ] Readiness summary separates measured results from proposals and unknowns.

| Readiness | Required evidence |
| --- | --- |
| M2 data work can begin | Accepted scope, date/identity/config contracts, and bounded acquisition plan. |
| M3 indexing can begin | M2 sample plus a working selected embedding configuration. |
| M4 generation can pass | Working retrieval plus verified local generator/context and token budgeting. |
| M6 reranking can pass | A working selected reranker and a controlled comparison. |

If the generator is blocked, record M1's data contracts as complete and its
generation check as blocked; do not label all of M1 successful. Continue only
independent approved data work. A model, context, or scope change needs an
explicit user decision.

## 6. References

Reviewed on 2026-10-17; refresh the relevant guidance before execution.

- [arXiv API manual](https://info.arxiv.org/help/api/user-manual.html): metadata
  fields, date/query semantics, paging, and request pacing.
- [Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B): official model
  identity, published context, template and reasoning controls.
- [llama.cpp](https://github.com/ggml-org/llama.cpp): candidate runtime,
  CPU/GPU inference, quantization, and backend/build documentation.
- [Qwen3-Embedding-8B](https://huggingface.co/Qwen/Qwen3-Embedding-8B) and
  [Qwen3-Reranker-8B](https://huggingface.co/Qwen/Qwen3-Reranker-8B): candidate
  formatting/scoring, supported dimensions, and model-specific inference.
- [pgvector](https://github.com/pgvector/pgvector): dimension/type limits
  for HNSW and exact-search versus reduced-dimensional index choices.
- [uv PyTorch integration](https://docs.astral.sh/uv/guides/integration/pytorch/):
  verify the selected host-specific Python inference installation when needed.

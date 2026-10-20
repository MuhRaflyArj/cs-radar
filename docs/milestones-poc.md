# CS Radar: PoC milestones

Created: 2026-10-17 14:49:44 GMT+7
Updated: 2026-10-19 08:46:58 GMT+7

## 1. Outcome

Build a reproducible local CLI that helps its user understand growing research
topics within LLM research, find useful papers, and ask follow-up questions.
The repository must contain the ingestion, extraction, retrieval, analysis,
generation, and evaluation pipeline. Hosting is deferred.

The PoC should answer three workflows:

1. **Growing topics:** "What topics in LLM research have grown over the last
   90 days, and which papers should I read?"
2. **Research timeline:** "How has agentic AI evolved during the last ten
   years, and what papers support that timeline?"
3. **Task research:** "For this specific LLM task, what recent approaches and
   reported results matter, and which earlier papers should I start with?"

Every report states its corpus coverage, date range, evidence, and limitations.
Results describe the collected LLM research subset; they do not represent all CS.
"SOTA" requires a named task, benchmark, metric, comparison date, and supporting
evidence. Otherwise describe promising approaches or results reported by authors.

## 2. Decisions and planning assumptions

### Confirmed requirements

| Area | Decision |
| --- | --- |
| Initial domain | LLM research within NLP; include RAG, agents, reasoning, and evaluation. |
| Meaning of new | Growing research topics; recent publication date alone is insufficient. |
| History | Ten years before the configured report cutoff; no older exceptions initially. |
| Growth window | Latest complete 90 days versus preceding 90 days; popularity signals are also useful. |
| Starting data | No existing corpus; the root HTML and Atom XML files are examples. |
| Content | Readable text first; equations and tables are later fidelity work; figures optional. |
| Interface | CLI answers and reports, with persistent conversational follow-ups. |
| Language | English first; Indonesian and other languages are desirable. |
| Database | PostgreSQL with pgvector. |
| Frameworks | Use LangChain and LangGraph as part of the learning goal. |
| Embeddings | Local Qwen/Qwen3-Embedding-8B, the largest Qwen3 embedding variant. |
| Reranker | Local Qwen/Qwen3-Reranker-8B, the largest Qwen3 reranker variant. |
| Metadata classifier | Evaluate local open-source decision models, starting with Kev-9B Q8; alternatives allowed, winner pending human-labeled comparison. |
| Generation | Qwen3.8-27B locally at 4-bit quantization; at least 65,536 tokens of context; CPU offload allowed. |
| Initial data | PoC starts with 10GB of paper data; accounting interpretation is proposed below. |
| Paid budget | $8 total OpenRouter credits reported; M1 paid inference disabled. |
| Evaluation | The 20 draft questions are accepted; target 18/20 useful responses and >=95% reviewed factual accuracy. |
| Answer length | Deferred by the user; record latency without a numeric threshold for now. |
| Tooling | Python 3.12, uv, YAML configuration, Ruff, Commitizen, pytest. |
| Observability | JSONL logs suitable for later Alloy ingestion. |
| Development | AdaCap approval before edits; agent instructions locally excluded from Git. |

Hardware reported by the user:

- Mac: M5 Pro, 24GB memory, 1TB internal SSD; 300–500GB project storage budget.
- Ubuntu PC: Ryzen 7 8700F, 64GB RAM, RTX 5070 Ti with 16GB VRAM;
  about 1TB project storage budget; heavy processing runs here.
- Shared external SSD: 1TB, reported 20Gbps connection; either machine can use it.
- SSH target is supplied in locally excluded AGENTS.md. The PC is currently
  off as reported by the user; no connection or runtime check has been attempted.
- The user will create ~/Documents/cs-radar on Ubuntu later. Keep data, model
  artifacts/caches, database files, logs, and outputs under that project root.

### Proposed defaults to validate during the milestones

- Begin with a small debug sample, then build the confirmed initial 10GB
  dataset before final PoC evaluation. A 50–100-paper pilot is a development
  step, not a replacement for the requested PoC scale. Metadata coverage and
  full text coverage remain separate measures; 100GB is outside this PoC.
- Proposed 10GB accounting: 10,000,000,000 retained source bytes across PDFs,
  HTML, and metadata combined. Derived text, vectors/indexes, database working
  space, temporary artifacts, and model weights are measured separately.
  The user specified "10GB of data"; confirm this accounting in the concrete
  acquisition proposal before downloading the corpus.
- Use PostgreSQL full text search plus vector search, fused with reciprocal rank
  fusion (RRF). Native PostgreSQL ranking is not BM25. A BM25 extension is a
  separate experiment only if the baseline gives reason to add one.
- Start with local Kev-9B Q8 (`kev:9b-q8_0`) and compare Imajev-4B on the same
  human-labeled metadata. Keep Clef-Flash Q8 as a runtime alternative. Select the
  classifier using task quality and review coverage, then memory and latency;
  published benchmark rankings are not proof of paper-classification accuracy.
  Keep explicit versioned definitions, the keyword baseline, and human review
  for uncertainty. Freeze model, taxonomy, and thresholds before automation.
  Discovering arbitrary new clusters is a later extension.
- Keep OpenRouter disabled by default. Any optional paid comparison needs an
  explicit spend cap within the remaining $8; do not assume credit is available.

These defaults are proposals, not measurements. Record any changed decision and
its reason here before using it in an experiment.

## 3. Current state and sequence

The repository has development tooling and the M1.1 metadata scope audit
implementation. M1.1 is done per the user's instruction on 2026-10-18; lint,
package import, configuration loading, and query construction passed. The user
then ran the live audit: five POST requests, 40 entries, 38 unique papers, no
retries, parsing failures, missing controls, or recorded issues. Its state is
`awaiting_manual_review`; manual labels remain unset. A Kev-9B Q8 classification
follow-up is requested and unimplemented. There is no full text corpus, model
runtime, database schema, or evaluation suite yet.

| Milestone | Deliverable | Depends on | State |
| --- | --- | --- | --- |
| M0 | Development foundation | — | Implemented |
| M1 | Scope, evaluation contract, and hardware/model feasibility | M0 | In progress; M1.1 done |
| M2 | Small, traceable text corpus | M1 data contract | Planned |
| M3 | Searchable PostgreSQL baseline | M2; M1 embedding check | Planned |
| M4 | First useful cited answer | M3; M1 generation check | Planned |
| M5 | Growing-topic report and historical metadata coverage | M4 | Planned |
| M6 | Reranking and controlled experiments | M4; M5 for trend queries | Planned |
| M7 | Conversation, timelines, and task research | M5–M6 | Planned |
| M8 | Incremental new-paper update | M7 | Planned |
| M9 | PoC evaluation and reproducible handoff | M8 | Planned |

M4 is the first useful end-to-end result. M9 is PoC completion. This document
plans future work; approving it does not authorize every application edit,
download, paid call, or recurring job.

## 4. Milestones

### M0 — Development foundation

Already implemented: Python 3.12/uv, `pyproject.toml`, `uv.lock`, Ruff,
Commitizen, pytest configuration, and `src/cs_radar`.

The project has no tests yet. Installed tooling is not evidence of application
correctness. Keep the existing setup and add dependencies only for actual stages.

### M1 — Define the experiment and prove resource feasibility

Detailed steps, confirmed inputs, evaluation questions, and readiness gates:
[M1 implementation plan](m1-plan.md). The completed M1.1 audit is followed by
a planned local decision-model comparison starting with Kev-9B Q8; model
execution and semantic quality remain unverified. M1.2 can proceed independently.

**Steps**

1. Freeze a report cutoff and the rolling ten-year bounds. Define the candidate
   categories and LLM title/abstract filters; inspect false positives and misses.
   RAG/agents/reasoning/evaluation may overlap; retain multiple topic labels.
2. Save the accepted fixed 20-question evaluation set: six growth questions, six timeline
   questions, six task/paper questions, and two deliberately unanswerable ones.
   Keep separate development prompts and evaluation prompts. For historical
   as-of reports, exclude source revisions after the cutoff and do not treat
   current popularity snapshots as evidence available at that earlier date.
3. Define YAML sections and validated config/result records for sources, corpus
   filters, paths, models, chunking, retrieval, reports, and log settings.
   Include paper/version identity, source locations, and configuration hashes.
4. Inspect the Ubuntu host, available RAM/VRAM/disk, drivers, and runtime support.
   Verify the exact requested Qwen3.8-27B checkpoint, tokenizer, provenance,
   selected 4-bit artifact, and supported context before downloading large weights.
   If unavailable or incompatible, record the blocker and request a model
   decision. Do not silently substitute another model.
5. Establish at least a 65,536-token total generation context. Measure a short
   request and a representative request near that limit with output headroom.
   Record memory, CPU/GPU offload, prompt processing speed, generation speed,
   and latency. Merely setting a context flag does not pass this gate.
6. Probe the embedding and reranking candidates individually. Plan sequential
   GPU use where needed; do not assume all models fit simultaneously. Record
   the cost of unloading/reloading them during interactive requests.

**Deliverables:** example configuration, data contracts, evaluation questions,
and a concise hardware/model feasibility record.

**Exit gate:** scope and evaluation rubric are reviewable; the selected embedding
works on a small batch; local generation demonstrates the required context or
has a clearly recorded blocker. Data preparation may continue independently
while a generation blocker is resolved. Record latency without a numeric
response-time or answer-length gate at this stage.

**Learning outcome:** distinguish model weights, KV cache, context capacity,
offload, and usable response speed.

### M2 — Build a small, traceable corpus

**Steps**

1. Begin with metadata for a small debug sample spanning recent and historical
   years and the selected topics, then expand toward the 10GB PoC dataset after
   the first end-to-end result. Store the query, pagination/checkpoint,
   retrieval timestamp, first-submission date, version date, and source ID.
   Run the validated selected classifier before automatic full text intake;
   preserve uncertain cases for review and all rejected metadata for auditing.
2. Review current arXiv access guidance before implementing requests. Use API
   metadata separately from full text. Cache responses, pace requests, retry
   transient failures with backoff, and keep failed records visible.
3. Prefer available article HTML, then digital PDF text extraction. Save a
   versioned source and checksum. Missing HTML must not remove a paper from
   metadata coverage. OCR is a recorded fallback decision, not a prerequisite.
4. For arXiv HTML, extract the paper body, excluding site navigation and footer.
   Use the example's `article.ltx_document` as an initial selector and check
   other samples. Preserve meaningful notices, headings, paragraphs, lists,
   references, and source anchors. Preserve available math/table markup without
   claiming that the text-first pipeline understands it.
5. Emit readable Markdown plus structured section/location records. Record PDF
   page spans where available. Keep raw and cleaned artifacts distinct; do not
   use an LLM to rewrite every paper as a cleaning step.
6. Manually inspect varied HTML and PDF samples, including two-column layouts,
   missing sections, broken reading order, and extraction failures. Store
   extraction status and quality flags instead of silently indexing bad text.

**Deliverables:** metadata manifest, source/extraction artifacts, human-readable
paper previews, and a report of successes, exclusions, failures, and disk use.

**Exit gate:** content is readable and traceable to its paper/version/location;
re-running avoids duplicate work; an interrupted batch resumes. The initial
dataset budget is enforced before and during downloads under the approved
accounting rule; reaching it pauses further intake without deleting sources.
The pilot gate can unblock M3; record its size separately from the 10GB corpus
gate required before the final frozen PoC evaluation.

**Learning outcome:** understand extraction noise before evaluating chunking.

### M3 — Make the corpus searchable

**Steps**

1. Set up one PostgreSQL instance with pgvector. Persist paper metadata,
   extraction versions, sections/chunks, embeddings, and ingestion status.
   Keep large source artifacts on disk with database references.
2. Implement one baseline splitter using token limits and paragraph boundaries.
   Carry paper/version, section path, source location, chunk offsets, parser
   version, and chunking configuration into every chunk.
3. Generate local Qwen3 embeddings using the model's documented query/document
   formatting, tokenizer, normalization, and truncation policy. Cache by content,
   model revision, and configuration; never mix incompatible vector spaces.
4. Decide dimensions, precision, and index strategy together. Qwen3-Embedding-8B
   supports up to 4,096 dimensions. pgvector HNSW supports at most 2,000 for
   `vector` and 4,000 for `halfvec`, so neither directly indexes native 4,096
   dimensions. Start with a full-dimensional exact-search baseline; before
   ANN indexing, compare a model-supported reduced output (for example 2,048
   with `halfvec`) against it. Measure quality/storage and validate the actual
   LangChain/Postgres integration. Keep the selected 8B model.
5. Expose lexical-only, vector-only, and RRF hybrid retrieval with identical
   topic/date filters. Deduplicate passages and limit domination by one paper.
   Return scores, ranks, IDs, and excerpts before adding answer generation.

**Deliverables:** repeatable database setup, index command, and inspectable
retrieval results. LangChain handles document/embedding/retrieval integration;
keep domain metadata and scoring behavior explicit.

**Exit gate:** all three modes return traceable passages; filters work;
re-indexing is idempotent; measured vector/index storage is recorded.

**Learning outcome:** see lexical and semantic strengths independently.

### M4 — Produce the first useful cited answer

**Steps**

1. Wire a small LangGraph flow: resolve question and filters, retrieve, assemble
   an evidence budget, generate, validate citation IDs, and save the result.
   Use explicit nodes without autonomous agent loops.
2. Connect the verified local generator. Count prompt, conversation, evidence,
   and output tokens together. A 64K-capable runtime does not require filling
   every prompt with 64K tokens.
3. Produce a cited answer to one concrete paper/topic question. Every citation
   maps to a saved evidence passage and an arXiv link. Treat paper content as
   evidence, not executable instructions for the application.
4. Save Markdown for reading and JSON for inspection, including question,
   cutoff, coverage, evidence IDs, model/configuration, and timing. Validate
   citation existence programmatically; assess claim support separately.
5. Demonstrate insufficient-evidence handling and a failed-stage diagnostic.

**Exit gate:** one command runs metadata → extraction → chunks → retrieval →
cited local answer on the small corpus. The answer is useful on manual review,
sources open correctly, and missing evidence is acknowledged. This is a paper
assistant demonstration; a broad hot-topic claim waits for M5.

**Learning outcome:** separate retrieval failure from generation failure.

### M5 — Measure growth and add paper popularity

**Steps**

1. Expand metadata coverage across the selected scope for ten years. Partition
   queries by time and record completeness per partition. Choose an appropriate
   metadata harvesting route before scaling beyond the interactive API.
2. Ensure both comparison windows have equivalent collection rules and adequate
   coverage. Deduplicate by paper, not version or cross-listing. Count papers
   by first submission; ingestion date and revisions are not new research.
3. Apply the frozen selected classifier, taxonomy, and threshold policy to both
   windows; do not compare counts produced by different classification policies.
   Disclose unclassified/review cases and classifier limitations. For cutoff `T`, use
   half-open windows `[T-90 days, T)` and `[T-180 days, T-90 days)`. Report counts,
   absolute change, growth ratio, and each topic's share of the scoped corpus.
   Topic shares may overlap because labels are not mutually exclusive.
   Define minimum support before ranking; label a zero baseline as newly
   observed rather than manufacturing an infinite percentage.
4. Keep volume, growth, and popularity visible as distinct signals. Document the
   selection/ranking rule. Do not infer scientific novelty from these numbers.
5. Add cached popularity enrichment, initially evaluating Semantic Scholar as a
   source. Match by stable identifiers; retain source and observation time.
   Missing counts mean unknown, not zero. Account for paper age. Current
   citation counts are not historical citation growth without past snapshots.
6. Retrieve representative papers for the growing topics, expanding full text
   toward the 10GB PoC dataset within the agreed accounting/storage limits.
   Freeze that dataset for the final comparisons. Metadata can identify papers whose full
   text is missing; label those recommendations as abstract-only evidence.

**Deliverables:** growing-topic report with counts, coverage, popularity signals,
recommended papers, explanations, and source links.

**Exit gate:** topic rankings can be reproduced from the metadata snapshot;
incomplete periods or sampled metadata prevent unqualified trend claims.
Explain which papers are recent, growing in attention, or historically useful.

**Learning outcome:** understand why a trend report needs corpus statistics
in addition to retrieval of a few similar passages.

### M6 — Run controlled chunking, retrieval, and generation experiments

**Steps**

1. Freeze corpus, cutoff, query set, relevance judgments, and baseline settings.
   Pool candidate results across retrieval methods for manual relevance labels;
   describe the pool's limits instead of claiming exhaustive corpus recall.
2. Compare the baseline splitter with section-aware token chunks at a small
   number of sizes/overlaps. Inspect boundary loss and context duplication.
3. Hold chunking fixed; compare lexical, vector, and hybrid retrieval.
4. Add a local Qwen3 reranker over a bounded candidate pool; compare hybrid
   with and without it. Record quality, truncation, latency, and model reloads.
5. Hold retrieved evidence fixed to compare generation prompts/evidence budgets.
   Optional hosted comparisons stay inside a separately approved spend cap.
6. Record paper- and passage-level precision@5 and nDCG@10 using the judged
   pool, plus supported claims, citation quality, latency, memory, storage,
   and any paid usage. Report judgment coverage alongside retrieval metrics.
   Choose a default based on the
   measured tradeoff; a more complex method need not win.

**Deliverables:** versioned experiment settings, per-query JSONL results, and
a compact comparison report explaining successes and failure cases.

**Exit gate:** chunking, hybrid retrieval, reranking, and generation each have
an interpretable comparison. Change one factor at a time. If evaluation queries
drive tuning, retain a separate untouched subset for the final review.

**Learning outcome:** attribute changes to a specific pipeline decision.

### M7 — Add conversation and the remaining research workflows

**Steps**

1. Persist conversation state with LangGraph's PostgreSQL checkpointer and
   explicit session IDs. Resume sessions after CLI restart; start a clean one.
   Bound history and retain the active topic, cutoff, and evidence references.
2. Resolve follow-ups such as "Which of those should I read first?" without
   treating previous generated answers as fresh scientific evidence.
3. Build timelines from dated papers and cited relationships. Distinguish
   explicit relationships from inferred branches; do not claim a field began
   within the collected ten-year window just because earlier work is excluded.
4. Generate task research reports: clarify an ambiguous task, compare compatible
   reported benchmarks, and suggest earlier reading within the allowed period.
   Avoid a universal SOTA ranking across incomparable settings.
5. Demonstrate English workflows. Try a small Indonesian query set as a stretch
   check; record quality separately from the core English acceptance gate.

**Exit gate:** all three target workflows have readable cited outputs and a
follow-up sequence that survives restart without session leakage.

**Learning outcome:** understand graph state, checkpoints, retrieval context,
and conversational memory as separate concerns.

### M8 — Update with new papers

**Steps**

1. Add an on-demand update command with a saved high-water mark and an overlap
   interval for late arrivals. Deduplicate new IDs; do not treat an existing
   paper's new version as a new submission. Revision reprocessing is deferred.
2. Extract/index only new or previously failed work. Refresh affected trend
   aggregates and invalidate only dependent caches. Record which source version
   was originally ingested, even when it was already revised at first ingestion.
3. Demonstrate interrupted work, retry, a second no-op update, and report cutoff
   advancement. Keep incomplete updates visible rather than silently complete.
4. Refresh popularity on an explicit command/budget, separate from paper intake.

**Exit gate:** a new-paper batch appears in search and reports; a repeat run
creates no duplicates or unnecessary embedding/generation calls. No recurring
scheduler is needed for the PoC.

### M9 — Evaluate and hand over the PoC

**Steps**

1. Run the frozen evaluation and manually review answers, evidence, trend counts,
   unsupported claims, and follow-ups. Publish failures as well as successes.
2. Reproduce the environment and the small demonstration from documented uv
   commands, example YAML, database setup, and a bounded source manifest.
   Include focused automated checks when their implementation/run is approved;
   do not require weights, a GPU, or live APIs for ordinary unit checks.
3. Measure total disk use: source HTML/PDF, normalized text, chunks, vectors,
   indexes, model weights/caches, PostgreSQL WAL, and temporary artifacts. Record
   preprocessing throughput and interactive latency before estimating expansion.
4. Document data/model versions, backup/restore, cleanup boundaries, update and
   session commands, source-access guidance, and known limitations. Link users
   to arXiv; keep the public repository focused on code/configuration/docs.

**Accepted success targets, with scoring procedure detailed in M1:** the 20
accepted questions should have useful responses on at least 18 (manual usefulness
>=4/5), with correct abstention for both unanswerable questions. Every citation
resolves to stored evidence; at least 95% of reviewed factual claims must be
accurate and supported by cited evidence, with material comparative/growth
claims individually reviewed. Disclose review counts and scientific uncertainty;
faithful reporting is not independent replication of a paper. Reports disclose
coverage/cutoff; growth counts reproduce exactly; sessions resume; updates are
idempotent; the agreed 10GB initial dataset is used for the final evaluation;
storage and paid usage remain within agreed caps. Record latency; answer length
is deferred and no numeric response-time gate is set. Targets are not achieved results.

**Exit gate:** save a final PoC report with rubric results, measured resource
costs, chosen settings, reproducible commands, and the user's acceptance.

## 5. Rules across every milestone

- Keep the existing `src/cs_radar` package. Add focused modules as stages become
  real; keep the CLI thin and framework calls inside clear adapters. Do not
  pre-create a large directory tree, factories, or distributed services.
- YAML owns user-adjustable settings; validate inputs and persist typed results.
  Use stable IDs/configuration hashes for lineage, retries, and experiment runs.
- Write JSONL events with timestamp/timezone, level, event, run ID, stage, host,
  status, duration, counts, artifact IDs, and actionable failure context. Separate
  logs from human-readable CLI output; omit secrets and full paper/prompt dumps.
  Alloy integration itself is deferred.
- Keep source acquisition, extraction, indexing, analysis, and generation
  resumable. Never mark a failed stage successful or hide missing coverage.
- Stop at storage caps. Do not automatically delete PDFs, raw inputs, model
  weights, or user artifacts. Compressed derived text is optional after measuring
  savings and preserving readable previews and retrieval access.
- One PC and one database are enough initially. Record active data paths and
  ownership; moving an external SSD does not make a running database portable.
- Record model revision, tokenizer, quantization, context, dimensions, prompts,
  parser, chunking, corpus snapshot, and date filters with each experiment.
- Before each implementation batch, follow `AGENTS.md`: show the actual proposed
  edits and obtain approval. Update milestone status only after its exit gate
  has evidence, and distinguish implemented, checked, and manually accepted.

## 6. Deferred beyond this PoC

All-CS coverage, downloading every PDF, mandatory 100GB raw text, general novel
topic discovery, comprehensive SOTA verification, robust equation/table reasoning,
figure understanding, OCR at scale, a web UI, hosting, scheduled jobs, Alloy
deployment, distributed workers, and production operations are deferred. They
can become later milestones based on PoC results and an explicit scope decision.

## 7. References and implementation checkpoints

Reviewed while drafting on 2026-10-17. Recheck the relevant source before
implementation; access policies, integrations, and model support can change.

- [arXiv API manual](https://info.arxiv.org/help/api/user-manual.html): Atom
  metadata, date fields, paging, request pacing, and metadata harvesting guidance.
- [arXiv bulk access](https://info.arxiv.org/help/bulk_data.html): choose the
  appropriate route before scaling metadata or full text acquisition.
- [PostgreSQL text search ranking](https://www.postgresql.org/docs/current/textsearch-controls.html#TEXTSEARCH-RANKING):
  native lexical ranking behavior.
- [pgvector](https://github.com/pgvector/pgvector): vector/index limits, hybrid
  search, filtering behavior, and precision/storage tradeoffs.
- [Qwen3-Embedding-8B model card](https://huggingface.co/Qwen/Qwen3-Embedding-8B)
  and [Qwen3-Reranker-8B model card](https://huggingface.co/Qwen/Qwen3-Reranker-8B):
  candidate formatting, supported dimensions, and model-specific inference.
- [LangGraph memory](https://docs.langchain.com/oss/python/langgraph/add-memory):
  thread state and PostgreSQL checkpointing.
- [Semantic Scholar API](https://api.semanticscholar.org/api-docs/): candidate
  popularity enrichment; verify access and limits during M5.

The official [Qwen3.8-27B checkpoint](https://huggingface.co/Qwen/Qwen3.8-27B)
has been verified during M1 planning. The user accepted 4-bit quantization.
Exact artifact/runtime compatibility, resource use, and real 64K execution
remain unverified; the PC is not currently available for checks.

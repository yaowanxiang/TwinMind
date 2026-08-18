# TwinMind Technical Architecture

## 1. Overview: Six-System Closed Loop

```
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│ ①Ingest │──▶│ ②Portrait│──▶│ ③Optimize│──▶│ ④Evaluate│──▶│ ⑤Execute │──▶│ ⑥Feedback│
└─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘
     ▲                                                                │
     └───────────── Self-learning · Self-iterating · Evolving ─────────┘
```

- Every module can **evolve independently** or **as a whole**
- Upstream output → downstream consumption; information handoffs between systems
- Absorbs the best methods from the entire network — the goal is always: solve the user's problem better

## 2. Module Details

### ① Ingest System (recorder/ + multimodal/)

| Sub-module | Description |
|---|---|
| `hermes_importer.py` | Reads Hermes state.db directly (sessions + messages tables), auto-detects Win/macOS/Linux paths |
| `jsonl_importer.py` | Generic JSONL/JSON — sessions from ANY AI tool (supports OpenAI-style content arrays) |
| `journal.py` | Journal entry: non-technical users describe "what I did today, how I did it" in plain words |
| `multimodal/ingest.py` | Images (vision LLM) / audio-video (faster-whisper optional) / screen capture (cross-platform) → unified text events |

### ② Portrait System (profile/)

3-level abstraction aggregation:
- **L1 Concrete actions**: what was done
- **L2 Thinking patterns**: reusable approaches (scenario-free)
- **L3 Principles**: maximum abstraction, like maxims, valid across industries

Portrait fields: domains / principles (L3 dedup+weighted) / patterns (L2) / preferences / tools / strengths / summary (LLM or local)

### ③ Optimization System (advisor/) — the Soul

Six capabilities: First Principles / Portrait Matching / Space-Time Matrix / Cross-Discipline / Four-Poles One-Strike / Plan Evaluation.

Wisdom retrieval: Chinese bigram tokens + **concept expansion tables** ("promote" → leverage/network/marketing/alliance…); local engine fallback without LLM.

### ④ Evaluation

3-way plan scoring: follow old approach / first-principles rebuild / wisdom-combined plan — each with pros, cons, and scores.

### ⑤ Authorized Execution (safety/ + executor/)

4 gates: **Policy tiering → Malicious guard → Authorization check → Audit trail**

```
Policy: action registry + risk tiers R0 local-read / R1 local-write / R2 external / R3 high-impact
Guard: dangerous-command regex library + sensitive-intent vocabulary (anti prompt-injection) + secret redaction
Authorization: auto / semi / manual; R3 forces approval in ANY mode
Audit: audit_log append-only
```

After approval, `execute_approved()` actually runs the action.

### ⑥ Feedback

User approval/comments → written back into the portrait's feedback array → evolution signal.

## 3. Data Model (SQLite)

| Table | Purpose |
|---|---|
| sessions | sessions (source: hermes/jsonl/journal) |
| events | raw event stream (messages/actions) |
| patterns | 3-level memory (level 1/2/3) |
| profile | digital portrait (single-row JSON) |
| advices | advice history |
| pending_approvals | approval queue |
| audit_log | audit trail |
| kv | key-value config |

## 4. Tech Stack

- Core engine: **pure Python standard library** (zero third-party dependencies — works out of the box)
- Storage: SQLite (single file, local-first, privacy-friendly)
- Web: FastAPI + uvicorn (optional)
- Desktop: pywebview (optional)
- Packaging: PyInstaller + GitHub Actions 3-platform matrix
- LLM: OpenAI-compatible protocol (Zhipu / DeepSeek / MiniMax / Ollama…), auto-fallback to local engine without a key

## 5. Tests

`tests/test_core.py`: 12 end-to-end tests (wisdom library / distill / portrait / advisor / authorization / guard / execution / audit / pipeline / importers)

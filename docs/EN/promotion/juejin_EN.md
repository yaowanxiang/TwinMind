# TwinMind Open-Source: From "Answering Questions" to "Understanding How You Work"

> Digital Portrait × Memory Distillation × Space-Time Wisdom Library — a "Wisdom Engine" for everyone

## 1. Background: The Last Mile of AI Assistants Is "Knowing You"

In 2026, everyone has an AI assistant. But anyone who uses one knows the disconnect:

- **Stateless**: every conversation requires re-explaining "who I am, what project I'm on, what I prefer"
- **Generic answers**: AI gives universal solutions, not *your* solutions
- **No review**: the trap you fell into last week, it happily suggests you step into again

The industry already has excellent tools — screenpipe (screen memory), claude-mem (session compression) — but they solve the "**recording**" problem. **TwinMind tackles the "understanding" problem**: distill your principles of action from your behavior, then use humanity's wisdom to help you solve problems from a higher dimension.

## 2. Architecture: Six-System Closed Loop

```
Ingest → Portrait → Optimize → Evaluate → Authorize → Feedback
   ↑                                              │
   └───────── Self-learning · Self-iterating · Evolving ────────┘
```

Every module can evolve independently or as a whole.

### 1. Ingest System (Multimodal)

- `recorder/hermes_importer.py`: reads Hermes state.db directly (sessions + messages tables), auto-detects Windows/macOS/Linux paths
- `recorder/jsonl_importer.py`: generic JSONL/JSON — sessions from ANY AI tool can flow in
- `multimodal/ingest.py`: images (vision LLM description), audio/video (faster-whisper transcription, optional), screen capture (cross-platform)

### 2. Distillation System (3-Level Abstraction)

```python
# core idea of distill/distiller.py
L1 Concrete action  → "Cleaned the dataset with Python"
L2 Thinking pattern → "Skeleton first, fill details, verify step by step" (scenario-free, portable)
L3 Principle        → "Pursue thorough completion, never leave loose ends" (max abstraction, like a maxim)
```

With an LLM: structured JSON distillation (JSON mode). Without a key: automatic fallback to local heuristics (keyword + syntax rules) — works out of the box.

### 3. Portrait System

Aggregates the 3-level abstraction → domain detection (keyword clustering) / principle library (dedup + weighting) / preference extraction / tool statistics. The portrait is an ever-evolving character sketch.

### 4. Optimization System (Wisdom Advisor) — the Soul

`advisor/advisor.py` integrates six capabilities:

- **First principles**: identify your TRUE goal, then rebuild from the essence — discarding old operations
- **Space-Time Matrix**: horizontal (culture) × vertical (era) retrieval from the human wisdom library
- **Cross-discipline**: game theory / medicine / engineering / CS methodology transfer
- **Four-Poles One-Strike**: extreme scanning across Paradigm × Scale × State × Knowledge + dimensional strike
- **Plan evaluation**: old approach vs first-principles rebuild vs wisdom-combined — 3-way scoring
- **Feedback loop**: user approval written back into the portrait

Retrieval highlight: Chinese concept expansion tables ("promote" → leverage/network/marketing/alliance…) dramatically improves semantic hits.

### 5. Authorized Execution System — Security Architecture

```
Policy layer: action registry, risk tiers R0 local-read / R1 local-write / R2 external / R3 high-impact
Guard layer: dangerous-command regex library + sensitive-intent vocabulary (anti prompt-injection) + secret redaction
Authorization layer: auto / semi / manual; R3 forces approval in ANY mode
Audit layer: all actions recorded, append-only
```

Execution passes 4 gates: `policy tiering → malicious guard → authorization check → audit trail`; `execute_approved()` actually runs the action after approval.

### 6. Feedback System

Was the advice useful? User comments → written back into the portrait (feedback array) — the training signal for evolution.

## 3. Human Wisdom Library (Space-Time Matrix × Cross-Discipline)

67 original entries of human wisdom, two retrieval axes:

| Dimension | Distribution |
|---|---|
| Culture (horizontal) | China 30 / Global 16 / USA 10 / UK 3 / Japan 2… |
| Era (vertical) | Ancient 29 (Art of War / Records of the Grand Historian / Tao Te Ching) / Modern 29 (PDCA / Game Theory / Lean) / Future 3 |
| Disciplines | Military / Philosophy / Medicine / Finance / CS / Statistics / Management / Physics / Biology / Economics… 37 fields |

Each entry: essence (core idea) + how_to_apply (how to borrow) + applicable_to (scenarios) + contrast (East-West / ancient-modern comparison).

## 4. Code Example

```python
from twinmind.advisor.advisor import advise
from twinmind.recorder import journal
from twinmind.pipeline import run_pipeline

# Record → Distill → Portrait
journal.add_journal("Finished project A today — planned first, executed, everything passed")
run_pipeline(limit_sessions=20)

# Wisdom advisor
result = advise("How do I effectively promote my open-source project?")
print(result["goal"])                    # first-principles goal
print(result["spacetime_matrix"][0])     # space-time wisdom
print(result["four_poles"]["strike"])    # dimensional strike
```

## 5. Real Test Data

| Metric | Result |
|---|---|
| Imported real sessions | 12 Hermes sessions / 1,753 events |
| Distilled memories | 196 (L1:74 / L2:84 / L3:38) |
| Domain detection | Software dev / Research / Writing / Investing / Personal mgmt |
| End-to-end tests | 12/12 passed |
| Retrieval example | "promote open source" → Borrowing Arrows / Straw Boats / Alliances / Collective Intelligence |

## 6. Quick Start

```bash
git clone https://github.com/yaowanxiang/TwinMind.git
cd TwinMind
pip install -r requirements.txt
PYTHONPATH=. python -m twinmind.cli server --desktop
```

Windows/macOS/Linux build scripts ready (`scripts/`) — and GitHub Actions auto-builds all three platforms on every version tag.

## 7. Roadmap

- [ ] Integrate screenpipe for 24/7 auto screen capture
- [ ] Wisdom library plugin API (every industry contributes knowledge)
- [ ] Task-driven online learning (auto-search best solutions across the web)
- [ ] Full-auto proactive assistance (email / messages / schedule)

**GitHub: https://github.com/yaowanxiang/TwinMind** (MIT License — Stars / PRs / discussion welcome)

---

*First published on Juejin · TwinMind open-source project*

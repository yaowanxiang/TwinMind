# I open-sourced TwinMind: an AI that "steals" your way of doing things

Recently I open-sourced a project called **TwinMind** (Digital Portrait · Wisdom Engine), and I'd like to talk about it.

**The pain point**: today's AI assistants don't "know you." You re-explain context every session, answers are always generic, and your past mistakes are never remembered.

**The idea**: let AI first learn *how you do things*, then help you do things.

## Core design

1. **3-level abstraction distillation**: your words and actions are distilled into Actions (L1) → Thinking Patterns (L2) → Principles (L3). L3 is your digital portrait — principles that hold in any industry.

2. **Human Wisdom Library (Space-Time Matrix × Cross-Discipline)**: 67 built-in entries of humanity's top wisdom. Ask "how to promote my open-source project" → it teaches you Straw Boats (leverage) and Alliances (coalition). Ask "team inefficient" → Lean Thinking and "Less is More."

3. **First-principles reframing**: discards your habitual operations and rebuilds the plan from the problem's essence — often shorter, cheaper, more effective.

4. **Security**: risk tiering (R0-R3) × 3 authorization modes (auto/semi/manual) × malicious-prompt guard × audit trail. **No external action without your approval.**

## Real test

Imported 12 real AI sessions → 1,753 events → 196 distilled memories → auto-identified domains (software dev / research / writing / investing). Asked "how to promote" → the wisdom matrix returned leverage / momentum / coalition / collective intelligence — one dimension higher than my own plan.

## Try it

```bash
pip install -r requirements.txt
twinmind record --hermes && twinmind distill
twinmind ask "your question"
twinmind server --desktop   # desktop UI — beginner friendly
```

Works without an LLM key (built-in local engine); quality jumps with a key configured.

**GitHub: https://github.com/yaowanxiang/TwinMind** (MIT, welcome Stars/PRs/feedback)

Tech: Python 3.10+ / SQLite / FastAPI / pywebview — core engine with zero third-party dependencies. Desktop apps for Windows / macOS / Linux auto-built via GitHub Actions.

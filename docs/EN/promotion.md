# I open-sourced TwinMind: an AI twin that learns your principles of action — then teaches you with the wisdom of all humanity

> GitHub: https://github.com/yaowanxiang/TwinMind · MIT License

**The problem with every AI assistant today:** none of them *know you*. You re-explain your context every session, you get generic answers instead of *your* answers, and your past mistakes are never remembered.

**TwinMind's approach:** let AI learn *how you do things* before it helps you do things.

## What it does

1. **3-level abstraction distillation** — from your conversations/journals/screens, it distills:
   - L1: What you did
   - L2: The reusable thinking pattern (scenario-independent)
   - L3: Your principles of action (portable to any industry)

2. **Space-Time Wisdom Matrix** — a built-in library of 67 entries of human wisdom:
   - Horizontal: how do China / USA / Japan / UK solve this?
   - Vertical: how did the ancients solve it (Art of War, Tao Te Ching, Records of the Grand Historian)? How do modern methods (PDCA, game theory, lean) solve it? How will the future (human-AI collaboration, digital twin)?
   - Cross-discipline: military, medicine, finance, CS, statistics…

   Ask "how do I promote my open-source project?" → it brings you *Borrowing Arrows from Straw Boats* (leverage) and *Vertical & Horizontal Alliances* (coalition). Ask "my team is inefficient" → it brings you *Lean thinking* and *Less is More*.

3. **First-principles reframing** — it identifies your TRUE goal, then rebuilds a better plan from scratch, discarding your old habits. Often shorter, cheaper, better.

4. **Security by design** — risk-tiered actions (R0-R3) × 3 authorization modes (auto/semi/manual) × malicious-prompt guard × full audit trail. **Nothing is ever sent out in your name without your approval.**

## Real test results

Imported 12 real AI sessions → 1,753 events → 196 distilled memories → auto-identified domains (software dev / research / writing / investing). Asked "how to promote" → the wisdom matrix returned leverage / coalition / collective intelligence — one dimension higher than my own plan.

## Try it

```bash
pip install -r requirements.txt
twinmind record --hermes && twinmind distill
twinmind ask "your question"
twinmind server --desktop
```

Works without any LLM API key (built-in local engine). Desktop apps for **Windows / macOS / Linux** are auto-built via GitHub Actions.

Tech: Python 3.10+ · SQLite · FastAPI · pywebview — core engine has **zero third-party dependencies**.

**Star, fork, or file an issue at https://github.com/yaowanxiang/TwinMind** — and if you're an expert in any field, consider contributing your industry's problem-solving wisdom to the library. One person's wisdom is limited; humanity's wisdom is not.

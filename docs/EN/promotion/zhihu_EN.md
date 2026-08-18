# Which AI tools truly "know you"? I open-sourced an AI twin that learns your way of doing things

**TL;DR:** If you're tired of re-explaining your background to AI every session, and tired of generic answers — check out **TwinMind**, which I recently open-sourced. It learns you first, then helps you.

## Why I built this

Three years of using AI, and my biggest frustration: **AI is getting stronger, but it never "gets" me.**

- Every conversation requires re-explaining project context
- Its advice is "correct," but not "my way"
- The traps I've stepped into — it doesn't remember, and happily suggests them again

In 2026, AI memory tools (screenpipe, claude-mem) solve "recording" — but **nobody solves "understanding"**: distilling your principles of action from your behavior.

## What TwinMind does

One sentence: **it distills your words and actions into "principles of action," then teaches you with the wisdom of all humanity.**

Three examples (real tests):

1. I asked it "how to promote my open-source project" — it pulled **Borrowing Arrows from Straw Boats (leverage)**, **Vertical & Horizontal Alliances (coalition)**, **Collective Intelligence** from the wisdom library — one dimension higher than my own plan.
2. I imported 12 real AI sessions (1,753 events) — it auto-distilled 196 memories and identified my domains: **software development, research, writing, investing**.
3. Its "first-principles reframing" discards your habitual operations and rebuilds from the essence of the problem — often shorter, cheaper, more effective.

## Can ordinary people use it?

Yes. That's what I care about most: **it's for everyone.**

- 30-second command-line start, plus a beginner-friendly desktop UI (five tabs)
- Works without any LLM API key (built-in local engine)
- Privacy & security: external actions require your approval (3 modes: auto / semi / manual), full audit trail

## Project info

- License: MIT
- Tech stack: Python + SQLite + FastAPI + pywebview (core engine with zero third-party dependencies)
- Built-in: 67 entries of human wisdom (Art of War / Records of the Grand Historian / PDCA / Game Theory / Lean / Antifragile… Space-Time Matrix × Cross-Discipline)
- Desktop apps for Windows / macOS / Linux, auto-built via GitHub Actions

**GitHub: https://github.com/yaowanxiang/TwinMind**

Stars, forks, and Issues are welcome. And if you're a practitioner in any field, consider contributing your industry's problem-solving wisdom to the library — one person's wisdom is limited; humanity's wisdom is not.

*Know yourself. Learn from all of humanity. Act with wisdom.*

# 🧠 TwinMind — Digital Portrait · Wisdom Engine

> **Know yourself. Learn from all of humanity. Act with wisdom.**
> The more you use it, the better it knows you — better than you know yourself.

TwinMind is an open-source AI engine built for **every person, in every industry**. It quietly learns from your behavior (AI conversations, journals, screen recordings, audio, images), distills your **principles of action** (a digital portrait), and then uses the **wisdom of all humanity** — across cultures, across eras, across disciplines — to help you solve problems from a higher dimension.

**This is not another AI chatbot. This is your wisdom twin:**

| Capability | Description |
|---|---|
| 🧬 **Digital Portrait** | 3-level abstraction: What you did (L1) → How you think (L2) → Your principles (L3) |
| 🌐 **Space-Time Wisdom Matrix** | Compare solutions across cultures (horizontal) and across eras — ancient / modern / future (vertical) |
| 🔬 **Cross-Disciplinary Fusion** | Game theory, medicine, engineering, CS, finance… every field's methodology at your service |
| 🎯 **First-Principles Reframing** | AI identifies your **true goal**, then rebuilds a better plan from first principles — discarding your old habits |
| 💥 **Four-Poles One-Strike Innovation** | Extreme-value scanning across Paradigm × Scale × State × Knowledge, then a dimensional strike |
| 🛡️ **3-Tier Authorization** | Auto / Semi / Manual — any external action requires YOUR approval, fully audited |
| 🔁 **Closed-Loop Evolution** | Ingest → Portrait → Optimize → Evaluate → Authorize → Feedback; the six systems self-iterate |

---

## 🚀 Get Started in 30 Seconds

```bash
# 1. Install
pip install -r requirements.txt

# 2. Record — bring your world in (designed for non-technical users too)
twinmind record --hermes            # import your AI assistant's session history
twinmind record --journal "Today I did… here's how…"   # write a journal
twinmind record --file D:/notes.png # images / audio / video / text — auto-detected

# 3. Distill — into 3-level abstraction: Actions → Patterns → Principles
twinmind distill

# 4. Ask — ask it anything
twinmind ask "How do I effectively promote my open-source project?"

# 5. Open the visual desktop (recommended for everyone)
twinmind server --desktop
```

## 🖥️ Desktop UI

```bash
twinmind server            # browser: http://127.0.0.1:8765
twinmind server --desktop  # native window (requires pywebview)
```

Five tabs: **My Portrait / Wisdom Advisor / Record / Human Wisdom Library / Security & Approvals**

## ⬇️ Download Desktop Apps (v0.2.0)

| Platform | Download | Build |
|---|---|---|
| **Windows x64** | [TwinMind-Windows-x64.exe](https://github.com/yaowanxiang/TwinMind/releases/latest) | ✅ (built via GitHub Actions) |
| **macOS (Intel/Apple Silicon)** | [TwinMind-macOS.zip](https://github.com/yaowanxiang/TwinMind/releases/latest) | ✅ (built via GitHub Actions) |
| **Linux x86_64** | [TwinMind-Linux-x86_64](https://github.com/yaowanxiang/TwinMind/releases/latest) | ✅ (built via GitHub Actions) |

> Cross-platform binaries are built automatically by **GitHub Actions** (`.github/workflows/build.yml`) — every `v*` tag triggers a 3-platform build matrix.

## 🧩 Architecture: Six-System Closed Loop

```
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│ ①Ingest │──▶│ ②Portrait│──▶│ ③Optimize│──▶│ ④Evaluate│──▶│ ⑤Execute │──▶│ ⑥Feedback│
└─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘
     ▲                                                                │
     └───────────── Self-learning · Self-iterating · Evolving ─────────┘
```

**Every module can evolve independently or as a whole; it absorbs the best methods from the entire network; the goal is always: solve the user's problem better.**

| Module | Path | Responsibility |
|---|---|---|
| Ingest | `recorder/` + `multimodal/` | Hermes/JSONL sessions, journals, images, audio, video, screen → unified event stream |
| Distill | `distill/` | LLM or local heuristics: 3-level abstraction (Actions → Patterns → Principles) |
| Portrait | `profile/` | Domains / principles / patterns / preferences / tools → digital portrait |
| Wisdom Library | `wisdom/` | 67 built-in entries of human wisdom (ancient books / history / cross-discipline / future) |
| Advisor | `advisor/` | First principles + portrait matching + space-time matrix + cross-discipline + four-poles + evaluation |
| Authorized Execution | `safety/` + `executor/` | Risk tiers (R0-R3) × 3 authorization modes × malicious-prompt guard × full audit |
| Feedback Loop | `advisor/feedback` | User approval feedback written back into the portrait — continuous evolution |

## 🛡️ Security by Design

Every action taken **in your name** (email, messaging, publishing) passes 4 gates:

1. **Risk tiering**: R0 local-read → R1 local-write → R2 external communication → R3 high-impact
2. **Malicious-prompt guard**: dangerous commands / sensitive-intent scanning (anti prompt-injection, anti-hijack)
3. **3-tier authorization**: `auto` / `semi` (important actions need approval) / `manual` (everything needs you)
4. **Full audit trail**: every action traceable; secrets auto-redacted

```bash
twinmind mode semi          # switch authorization mode
twinmind approve --list     # view pending approvals
twinmind approve --id 1 --yes   # approve
twinmind audit              # audit log
```

## 📜 Human Wisdom Library (Space-Time Matrix × Cross-Discipline)

**67 entries** of humanity's top wisdom, built-in and offline:

- **Horizontal (culture)**: China / USA / Japan / UK / Russia / Global…
- **Vertical (era)**: Ancient (Art of War, Tao Te Ching, Records of the Grand Historian) → Modern (PDCA, Game Theory, Lean) → Future (Human-AI Collaboration, Digital Twin, Collective Intelligence)
- **Disciplines**: Military, Philosophy, Medicine, Finance, Computer Science, Statistics, Management, Physics, Biology, Economics…

## ⚙️ Configuration

```bash
# Optional: configure an LLM endpoint (works without it — local engine included)
# Config UI tab "Security & Config", or edit ~/.twinmind/config.json
# Any OpenAI-compatible endpoint (Zhipu / DeepSeek / MiniMax / Ollama…)
{
  "llm": {
    "base_url": "https://open.bigmodel.cn/api/paas/v4",
    "api_key": "your-key",
    "model": "glm-4.7-flash"
  }
}
```

## 🧪 Tests

```bash
PYTHONPATH=. python tests/test_core.py    # 12 end-to-end tests
```

## 📦 Project Structure

```
twinmind/
├── recorder/      # session / journal / file recording
├── multimodal/    # image / audio / video / screen capture
├── distill/       # 3-level abstraction distillation
├── memory/        # SQLite storage
├── profile/       # digital portrait
├── wisdom/        # human wisdom library (space-time matrix)
├── advisor/       # wisdom advisor (core)
├── safety/        # authorization / approval / audit / guard
├── executor/      # action execution (4 gates)
├── server/        # FastAPI backend
├── ui/            # desktop web UI
└── cli.py         # command-line entry
```

## 🔮 Roadmap

- [ ] Integrate screenpipe for 24/7 screen/audio auto-capture
- [ ] Open plugin API for the wisdom library — every industry contributes its own knowledge
- [ ] Task-driven online learning: auto-search the best solutions across the web
- [ ] Fully-automated mode with proactive assistance (email / messages / schedule)
- [ ] Mobile / Web versions

## 📄 License

MIT License — free to use, modify, and commercialize.

## 🙏 Acknowledgments

- Yao Wanxiang Research Group (Four-Poles One-Strike Innovation Method v6.1.19)
- Chinese wisdom: Art of War, 36 Stratagems, Tao Te Ching, Analects, Records of the Grand Historian
- World wisdom: First Principles, Game Theory, PDCA, Lean, Antifragile, Mental Models

---

*[中文版 README](README.md) | [English README](README_EN.md)*

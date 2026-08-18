"""高维顾问器 — TwinMind 的核心输出引擎。

六大能力一体：
  1. 第一性原理：先厘清用户的「真正目标」，再抛开旧操作从本质重推
  2. 画像匹配：你过去遇到这类问题是怎么做的（数字画像）
  3. 时空矩阵：横向（不同文化/国家/民族的解法）× 纵向（古代/现代/未来）
  4. 学科交叉：各专业方法论（博弈/统计/医学/工程/计算机……）
  5. 四极一击创新：范式×尺度×状态×知识四维极值扫描 + 降维打击
  6. 方案评估 + 场景拓展 + 反馈闭环（用户认可度写回画像，持续进化）

无 LLM 时自动降级为本地引擎（智慧库检索 + 画像聚合 + 规则推理），保证开箱即用。
"""
import json
from collections import Counter

from twinmind.config import load_config
from twinmind.llm import LLMClient, LLMError
from twinmind.memory import store
from twinmind.profile.profiler import build_profile
from twinmind.wisdom import library as wisdom

SYSTEM_PROMPT = """你是「TwinMind 高维顾问」，一位融合了中华智慧、西方方法论与 AI 推演能力的首席顾问。

你的使命：帮用户站在更高维度解决问题。输出必须严格 JSON（不要任何其他文字）：

{
  "goal": "第一性原理：用户的真正目标是什么（剥离表面需求后的本质目标，一句话）",
  "portrait_insight": "结合用户的数字画像，指出TA遇到这类问题时的惯用思路与可能的盲区",
  "first_principles_plan": "抛开用户过去的做法，从问题本质重新推演的更优方案（可落地的具体步骤）",
  "spacetime_matrix": [
    {"source": "出处（如：孙子兵法·谋攻篇）", "culture": "文化", "era_type": "古代/现代",
     "essence": "核心思想一句话", "how_to_apply": "对这个具体问题怎么借鉴"}
  ],
  "cross_discipline": [
    {"discipline": "学科（如：博弈论/医学/计算机）", "idea": "该学科的方法", "how_to_apply": "怎么迁移到这个问题上"}
  ],
  "four_poles": {
    "macro": "极宏观视角（系统/全局/趋势层面怎么看）",
    "micro": "极微观视角（机理/单元层面怎么拆）",
    "extreme": "极端环境视角（极限工况/最坏情况怎么防）",
    "cross": "极交叉视角（最意想不到的跨界灵感）",
    "strike": "降维打击：从四极萃取的底层规律映射回常规解法的关键一击"
  },
  "evaluation": [
    {"option": "方案A：遵循旧做法", "score": 0-100, "pros": "优点", "cons": "缺点"},
    {"option": "方案B：第一性原理新方案", "score": 0-100, "pros": "优点", "cons": "缺点"},
    {"option": "方案C：借鉴智慧的组合方案", "score": 0-100, "pros": "优点", "cons": "缺点"}
  ],
  "action_plan": ["第一步", "第二步", "第三步"],
  "scenario_expansion": "这个解法还能迁移到哪些别的场景，对别人有什么借鉴价值"
}

要求：所有借鉴必须真实有据、具体可操作，禁止空话套话；最终推荐要给出明确选择。"""


def advise(question: str, cfg: dict | None = None, record: bool = True) -> dict:
    """核心入口：输入问题，输出高维建议。"""
    cfg = cfg or load_config()
    profile = store.load_profile()
    if profile is None:
        profile = build_profile(cfg)

    # 1) 画像匹配：找用户过去的相似模式
    past_patterns = _match_profile(question, profile)
    # 2) 时空矩阵检索：横向文化 × 纵向时代
    sp_items = wisdom.search(question, limit=6)
    # 3) 学科交叉
    disc_items = wisdom.search(question, limit=6)
    disc_items = _diversify_disciplines(disc_items)

    client = LLMClient(cfg)
    if client.ready:
        try:
            answer = _llm_advise(client, question, profile, past_patterns,
                                 sp_items, disc_items)
        except LLMError:
            answer = _local_advise(question, profile, past_patterns, sp_items, disc_items)
    else:
        answer = _local_advise(question, profile, past_patterns, sp_items, disc_items)

    result = {"question": question, "profile": profile, **answer,
              "engine": "llm" if client.ready else "local"}
    if record:
        store.add_advice(question, json.dumps(result, ensure_ascii=False)[:8000])
    return result


def feedback(question: str, helpful: bool, comment: str = "") -> dict:
    """用户反馈闭环：建议是否有用写回画像（进化信号）。"""
    profile = store.load_profile() or {}
    fb = profile.setdefault("feedback", [])
    fb.append({"question": question[:80], "helpful": bool(helpful),
               "comment": comment[:200], "ts": __import__("datetime").datetime.now().isoformat(timespec="seconds")})
    profile["feedback"] = fb[-200:]
    store.save_profile(profile)
    return {"status": "ok", "feedback_count": len(fb)}


# ---------------- LLM 引擎 ----------------

def _llm_advise(client, question, profile, past_patterns, sp_items, disc_items) -> dict:
    brief = {
        "question": question,
        "portrait_summary": profile.get("summary", ""),
        "portrait_principles": [p["content"] for p in profile.get("principles", [])[:6]],
        "user_past_patterns": [p.get("content", "") for p in past_patterns[:5]],
        "spacetime_wisdom": [
            {"source": f"{e.get('title')}（{e.get('source')}·{e.get('culture')}·{e.get('era_type')}）",
             "essence": e.get("essence", ""), "how_to_apply": e.get("how_to_apply", "")}
            for e in sp_items[:6]
        ],
        "cross_discipline_wisdom": [
            {"discipline": e.get("discipline", ""),
             "essence": e.get("essence", ""), "how_to_apply": e.get("how_to_apply", "")}
            for e in disc_items[:6]
        ],
    }
    msgs = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(brief, ensure_ascii=False)},
    ]
    raw = client.chat_json(msgs, temperature=0.5)
    if "_raw" in raw or not raw.get("goal"):
        raise LLMError("LLM 未返回结构化建议")
    return _normalize_answer(raw)


def _normalize_answer(raw: dict) -> dict:
    return {
        "goal": str(raw.get("goal", ""))[:300],
        "portrait_insight": str(raw.get("portrait_insight", ""))[:600],
        "first_principles_plan": str(raw.get("first_principles_plan", ""))[:1200],
        "spacetime_matrix": raw.get("spacetime_matrix", [])[:6],
        "cross_discipline": raw.get("cross_discipline", [])[:6],
        "four_poles": raw.get("four_poles", {}) if isinstance(raw.get("four_poles"), dict) else {},
        "evaluation": raw.get("evaluation", [])[:4],
        "action_plan": [str(x)[:200] for x in (raw.get("action_plan") or [])][:8],
        "scenario_expansion": str(raw.get("scenario_expansion", ""))[:600],
    }


# ---------------- 本地引擎（无 LLM 兜底） ----------------

def _local_advise(question, profile, past_patterns, sp_items, disc_items) -> dict:
    principles = [p["content"] for p in profile.get("principles", [])[:3]]
    spacetime = [
        {"source": f"{e.get('title')}（{e.get('source')}·{e.get('culture')}·{e.get('era_type')}）",
         "culture": e.get("culture", ""), "era_type": e.get("era_type", ""),
         "essence": e.get("essence", ""), "how_to_apply": e.get("how_to_apply", "")}
        for e in sp_items[:4]
    ]
    cross = [
        {"discipline": e.get("discipline", ""), "idea": e.get("essence", ""),
         "how_to_apply": e.get("how_to_apply", "")}
        for e in disc_items[:4]
    ]
    top = sp_items[0] if sp_items else None
    goal = f"从第一性原理看，问题的本质是：{_infer_goal(question)}"
    return {
        "goal": goal,
        "portrait_insight": f"你的画像显示，你遇到这类问题通常的做法是：{'；'.join(p['content'] for p in past_patterns[:2]) or '尚无类似经验记录'}。注意避免惯性思维，建议结合下方案例重新审视。",
        "first_principles_plan": _local_first_principles(question, top),
        "spacetime_matrix": spacetime,
        "cross_discipline": cross,
        "four_poles": _four_poles(question, sp_items),
        "evaluation": _local_evaluation(question, top),
        "action_plan": _local_action_plan(question, top),
        "scenario_expansion": _local_expansion(question, top),
    }


def _match_profile(question: str, profile: dict) -> list[dict]:
    """用智慧库检索逻辑匹配画像模式"""
    from twinmind.wisdom.library import _tokenize, _score
    q_tokens = set(_tokenize(question))
    items = (profile.get("patterns", []) + profile.get("principles", []))
    scored = []
    for it in items:
        s = _score({k: it.get(k, "") for k in ("title", "essence", "how_to_apply", "applicable_to", "tags")},
                   q_tokens)
        if s > 0:
            scored.append((s, it))
    scored.sort(key=lambda x: -x[0])
    return [it for _, it in scored[:5]]


def _diversify_disciplines(items: list[dict]) -> list[dict]:
    """学科去重：保证交叉借鉴来自不同学科"""
    seen, out = set(), []
    for e in items:
        d = e.get("discipline", "")
        if d in seen:
            continue
        seen.add(d)
        out.append(e)
    return out[:6]


def _infer_goal(question: str) -> str:
    # 简单启发式：去掉疑问词后取核心名词短语
    for w in ("怎么", "如何", "怎样", "为什么", "能不能", "是否应该"):
        if w in question:
            return question.replace(w, "").strip("？? ") or question
    return question[:60]


def _local_first_principles(question: str, top) -> str:
    if not top:
        return "1) 先定义清楚要达成的本质结果；2) 列出所有前提假设并逐条质疑；3) 从零开始设计最少步骤方案；4) 用最小成本验证后再放大。"
    return f"1) 重新定义问题本质：不急着动手，先问'最终要达成什么结果'；2) 质疑现有做法的每个前提；3) 借鉴「{top.get('title')}」的思路重新设计最少步骤方案；4) 小成本验证后迭代。"


def _four_poles(question: str, sp_items) -> dict:
    tags = [t for e in sp_items for t in e.get("tags", [])]
    counter = Counter(tags)
    hot = [t for t, _ in counter.most_common(5)]
    return {
        "macro": f"系统层面：把问题放到更大的系统中看，谁是关键环节、什么趋势在改变它（相关智慧：{'、'.join(hot[:3]) or '系统思维'}）。",
        "micro": "机理层面：把问题拆到最小的单元，找到真正的驱动因子，而不是处理表面现象。",
        "extreme": "极限层面：考虑最坏情况——如果资源减半、时间减半、最不利环境，方案还成立吗？提前设计失效保护。",
        "cross": "跨界层面：这个问题在别的领域（医学/金融/军事/计算机）会怎么解决？换一个完全无关的领域找灵感。",
        "strike": f"降维打击：从四极扫描中萃取核心规律——借鉴「{sp_items[0].get('title') if sp_items else '最相关智慧'}」的底层逻辑，直接映射回当前问题的关键一击。",
    }


def _local_evaluation(question: str, top) -> list[dict]:
    return [
        {"option": "方案A：沿用你过去的做法", "score": 60, "pros": "熟悉、低风险、可快速执行", "cons": "可能没解决本质问题，边际收益递减"},
        {"option": "方案B：第一性原理重推", "score": 78, "pros": "直击本质、可能大幅降本增效", "cons": "需要重新验证，短期有学习成本"},
        {"option": "方案C：借鉴智慧的组合方案", "score": 85, "pros": f"站在巨人肩上（如：{top.get('title') if top else '跨领域智慧'}），高维破局", "cons": "需要理解并适配到自己的场景"},
    ]


def _local_action_plan(question: str, top) -> list[str]:
    steps = [
        "第一步：写下一句话定义「成功是什么」，作为所有行动的标尺。",
        "第二步：列出你现在要做的每件事，逐条问'这直接服务于成功定义吗'，砍掉无关的。",
    ]
    if top:
        steps.append(f"第三步：借鉴「{top.get('title')}」的核心思想：{top.get('how_to_apply', '')[:80]}")
    steps += [
        "第四步：用最小成本跑一个试点（1天到1周），收集真实反馈。",
        "第五步：根据反馈迭代，把有效的做法固化为你的新工作流（TwinMind 会帮你记住）。",
    ]
    return steps[:6]


def _local_expansion(question: str, top) -> str:
    if top:
        return f"「{top.get('title')}」的思路不只适用于当前问题：{top.get('applicable_to', '')}——这些场景你未来都可能遇到，TwinMind 会在合适时机提醒你复用。"
    return "这个解法的核心逻辑（定义本质目标→砍冗余→最小验证→迭代固化）可迁移到学习、投资、团队管理、产品设计等几乎所有领域。"

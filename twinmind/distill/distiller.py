"""三级抽象蒸馏器 — TwinMind 的灵魂。

把一段「做过的事」蒸馏成三层：
  L1 具体做法 (fact)      —— 这次具体完成了什么
  L2 思路模式 (pattern)   —— 用了什么可复用的思路/方法
  L3 处事原则 (principle) —— 背后体现的处事原则/价值观/思维习惯

有 LLM 时用大模型蒸馏（输出结构化 JSON）；
无 LLM 时走本地启发式（关键词+句法规则），保证开箱即用。
"""
import json
import re
from typing import Optional

from twinmind.config import load_config
from twinmind.llm import LLMClient, LLMError

SYSTEM_PROMPT = """你是一位「处事智慧分析师」，擅长从人们的言行中提炼可迁移的智慧。

用户会给你一段他们做过的事（可能是与 AI 的对话、日记、工作记录）。
请做三级抽象，输出严格 JSON（不要任何其他文字）：

{
  "summary": "这段记录讲了什么（50字内）",
  "facts": [{"content": "具体做了什么", "importance": 0.0~1.0}],
  "patterns": [{"content": "可复用的思路/方法/策略（抽象、不绑定具体工具）", "tags": ["标签"], "importance": 0.0~1.0}],
  "principles": [{"content": "体现的处事原则/价值观/思维习惯（最高抽象，像格言）", "tags": ["标签"], "importance": 0.0~1.0}]
}

要求：
1. patterns 和 principles 必须「去场景化」——换一个行业、换一个领域依然适用。
2. 宁缺毋滥：没有把握的不写，每条都必须真实有据。
3. facts 记录事实，patterns 提炼方法，principles 升华原则，三层要能互相印证。
4. importance 表示这条对理解「这个人怎么做事」的价值，0.1~1.0。
5. 标签建议从：决策、信息处理、沟通、资源管理、时间管理、风险管理、创新、执行、学习、合作、情绪管理、质量观、目标规划 中选择。"""


def _build_messages(text: str) -> list[dict]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"请分析以下记录：\n\n{text}"},
    ]


def distill_text(text: str, cfg: dict | None = None) -> dict:
    """蒸馏一段文本，返回 {summary, facts, patterns, principles}"""
    client = LLMClient(cfg)
    if client.ready:
        try:
            raw = client.chat_json(_build_messages(text))
            return _normalize(raw)
        except LLMError:
            # LLM 失败自动降级为本地启发式，保证可用
            pass
    return _heuristic(text)


def distill_session_events(events: list[dict], cfg: dict | None = None,
                           max_len: int = 12000) -> dict:
    """蒸馏一段会话事件流。自动拼接并截断。"""
    parts = []
    for e in events:
        role = e.get("role", "user")
        content = (e.get("content") or "").strip()
        if not content:
            continue
        if role == "tool":
            parts.append(f"[工具执行结果] {content[:300]}")
        elif role == "assistant":
            parts.append(f"[AI 回应] {content[:800]}")
        else:
            parts.append(f"[用户] {content[:1200]}")
    text = "\n\n".join(parts)
    if len(text) > max_len:
        text = text[:max_len] + "\n...(截断)"
    if len(text.strip()) < 30:
        return {"summary": "", "facts": [], "patterns": [], "principles": []}
    return distill_text(text, cfg)


def _normalize(raw: dict) -> dict:
    summary = str(raw.get("summary", ""))[:200]
    facts = _norm_list(raw.get("facts"))
    patterns = _norm_list(raw.get("patterns"))
    principles = _norm_list(raw.get("principles"))
    return {"summary": summary, "facts": facts, "patterns": patterns, "principles": principles}


def _norm_list(items) -> list[dict]:
    out = []
    if not isinstance(items, list):
        return out
    for it in items:
        if isinstance(it, str):
            content, imp = it, 0.5
        elif isinstance(it, dict):
            content = it.get("content") or it.get("text") or ""
            imp = _to_float(it.get("importance"), 0.5)
            tags = it.get("tags") or []
        else:
            continue
        content = str(content).strip()
        if len(content) < 6:
            continue
        out.append({
            "content": content,
            "tags": [str(t)[:20] for t in tags][:5],
            "importance": max(0.1, min(1.0, imp)),
        })
    return out


def _to_float(v, default: float) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


# ---------------- 本地启发式（无 LLM 兜底） ----------------

_ACTION_WORDS = ["完成", "开发", "写了", "搭建", "实现", "创建", "修复", "搞定", "做了", "做了", "整理",
                 "搭建", "导入", "配置", "安装", "发布", "上线", "解决", "测试", "跑通"]
_PATTERN_WORDS = ["先", "再", "然后", "通过", "采用", "利用", "借助", "按照", "分", "逐步", "优先",
                  "对比", "筛选", "验证", "迭代", "拆解", "并行", "备份", "分层"]
_PRINCIPLE_WORDS = ["省", "快", "稳", "简单", "质量", "彻底", "安全", "直接", "优先", "不", "避免",
                    "复用", "自动化", "长期", "自主", "彻底完成"]


def _heuristic(text: str) -> dict:
    facts, patterns, principles = [], [], []
    for sent in re.split(r"[。\n；;]", text):
        sent = sent.strip()
        if len(sent) < 8:
            continue
        if any(w in sent for w in _ACTION_WORDS):
            facts.append({"content": sent[:120], "tags": ["事实"], "importance": 0.4})
        if any(w in sent for w in _PATTERN_WORDS):
            patterns.append({"content": sent[:120], "tags": ["思路"], "importance": 0.5})
    for sent in re.split(r"[。，,]", text):
        sent = sent.strip()
        if 4 <= len(sent) <= 30 and any(w in sent for w in _PRINCIPLE_WORDS):
            principles.append({"content": sent[:60], "tags": ["原则"], "importance": 0.5})
    # 去重
    def dedup(items):
        seen, out = set(), []
        for it in items:
            k = it["content"][:40]
            if k in seen:
                continue
            seen.add(k)
            out.append(it)
        return out
    return {"summary": text[:80], "facts": dedup(facts)[:10],
            "patterns": dedup(patterns)[:10], "principles": dedup(principles)[:8]}

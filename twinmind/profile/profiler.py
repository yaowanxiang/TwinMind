"""数字画像器 — 把散落的记忆聚合成「你是谁、你怎么做事」。

画像结构：
  domains      活跃领域（从标签/内容聚类）
  principles   L3 处事原则（去重、按重要性加权）
  patterns     L2 思路模式
  preferences  表达偏好（语言、格式、风格）
  tools        常用工具
  strengths    高价值模式（你最擅长的套路）
  summary      一段话画像（LLM 或本地拼接）
  stats        统计信息
  updated_at   更新时间
"""
import json
import re
from collections import Counter
from datetime import datetime, timezone

from twinmind.config import load_config
from twinmind.llm import LLMClient, LLMError
from twinmind.memory import store

PREF_PATTERNS = [
    (r"偏好?[：:]?\s*(.{2,40}?)[。；;]", "表达"),
    (r"(喜欢|习惯|倾向于|总是|一向)\s*(.{3,40}?)[。；;]", "习惯"),
    (r"(不喜欢|讨厌|避免)\s*(.{3,40}?)[。；;]", "规避"),
]

DOMAIN_KEYWORDS = {
    "科研": ["论文", "期刊", "实验", "数据", "学术", "文献", "课题", "NSFC", "综述", "审稿"],
    "软件开发": ["开发", "代码", "GitHub", "开源", "接口", "部署", "bug", "项目", "打包", "前端", "后端"],
    "金融投资": ["股票", "基金", "持仓", "买入", "卖出", "行情", "仓位", "收益", "投资", "风险"],
    "教学": ["课程", "学生", "教学", "课堂", "考试", "教案", "授课"],
    "写作": ["写作", "润色", "翻译", "文章", "公众号", "报告", "文档"],
    "个人管理": ["时间", "计划", "日程", "目标", "习惯", "效率", "省时"],
    "健康": ["运动", "睡眠", "饮食", "体检", "健康"],
}

def build_profile(cfg: dict | None = None, rebuild: bool = True) -> dict:
    """从 patterns 库重新构建/更新画像"""
    cfg = cfg or load_config()
    patterns = store.list_patterns(limit=500)
    facts = [p for p in patterns if p["level"] == 1]
    pats = [p for p in patterns if p["level"] == 2]
    prins = [p for p in patterns if p["level"] == 3]

    profile: dict = {
        "domains": _detect_domains(pats + prins + facts),
        "principles": _dedup_weighted(prins, top=12),
        "patterns": _dedup_weighted(pats, top=15),
        "preferences": _detect_preferences(patterns),
        "tools": _detect_tools(patterns),
        "strengths": _dedup_weighted([p for p in pats + prins if p["importance"] >= 0.7], top=8),
        "stats": {
            "pattern_count": len(patterns),
            "fact_count": len(facts),
            "pattern_count_L2": len(pats),
            "principle_count": len(prins),
            "session_count": store.stats().get("sessions", 0),
        },
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    # 尝试用 LLM 生成一段话画像
    client = LLMClient(cfg)
    if client.ready:
        try:
            profile["summary"] = _llm_summary(client, profile)
        except LLMError:
            profile["summary"] = _local_summary(profile)
    else:
        profile["summary"] = _local_summary(profile)

    store.save_profile(profile)
    return profile


def _dedup_weighted(items: list[dict], top: int) -> list[dict]:
    """按语义近似去重（前缀+首句），按 importance 加权聚合"""
    buckets: dict[str, list[dict]] = {}
    for it in items:
        key = _canonical(it.get("content", ""))
        if not key:
            continue
        buckets.setdefault(key, []).append(it)
    out = []
    for key, group in buckets.items():
        imp = sum(x.get("importance", 0.5) for x in group) / len(group)
        tags = Counter()
        for x in group:
            for t in x.get("tags", []):
                tags[t] += 1
        out.append({"content": max(group, key=lambda x: x.get("importance", 0))["content"],
                    "importance": round(imp, 2),
                    "count": len(group),
                    "tags": [t for t, _ in tags.most_common(3)]})
    out.sort(key=lambda x: (x["importance"] * min(x["count"], 5)), reverse=True)
    return out[:top]


def _canonical(content: str) -> str:
    s = content.strip()
    s = re.sub(r"[，。；、\s]+", "", s)
    return s[:24]


def _detect_domains(items: list[dict]) -> list[str]:
    text = " ".join(it.get("content", "") for it in items)
    scores = {}
    for domain, kws in DOMAIN_KEYWORDS.items():
        scores[domain] = sum(text.count(k) for k in kws)
    return [d for d, s in sorted(scores.items(), key=lambda x: -x[1]) if s >= 2]


def _detect_preferences(patterns: list[dict]) -> list[str]:
    prefs = []
    for p in patterns:
        content = p.get("content", "")
        for pat, kind in PREF_PATTERNS:
            m = re.search(pat, content)
            if m:
                prefs.append(f"{kind}: {m.group(1).strip()[:40]}")
    seen, out = set(), []
    for x in prefs:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out[:15]


def _detect_tools(patterns: list[dict]) -> list[str]:
    known = ["Python", "Hermes", "GitHub", "Excel", "Word", "PPT", "VSCode", "Obsidian",
             "Zotero", "Linux", "Windows", "macOS", "Docker", "SQLite", "FastAPI", "React",
             "Claude", "Codex", "OpenClaw", "智谱", "DeepSeek", "Kimi", "PyInstaller"]
    text = " ".join(p.get("content", "") for p in patterns)
    return [t for t in known if re.search(rf"\b{re.escape(t)}", text)][:12]


def _local_summary(profile: dict) -> str:
    domains = "、".join(profile["domains"][:3]) or "多领域"
    top = profile["principles"][:2]
    p1 = top[0]["content"] if top else "在实践中不断总结"
    return f"你是一个活跃在「{domains}」的实践者。最核心的处事原则：{p1}。已积累 {profile['stats']['pattern_count']} 条经验记忆，画像持续进化中。"


def _llm_summary(client: LLMClient, profile: dict) -> str:
    brief = {
        "domains": profile["domains"][:5],
        "principles": [p["content"] for p in profile["principles"][:5]],
        "patterns": [p["content"] for p in profile["patterns"][:5]],
        "preferences": profile["preferences"][:5],
        "tools": profile["tools"][:6],
    }
    msgs = [
        {"role": "system", "content": "你是数字画像分析师。根据一个人的行为画像数据，用150字以内的中文写一段精准、有洞察、鼓励性的「人物速写」，突出TA的处事风格与思维方式，不要罗列数据。"},
        {"role": "user", "content": json.dumps(brief, ensure_ascii=False)},
    ]
    return client.chat(msgs, max_tokens=400).strip()

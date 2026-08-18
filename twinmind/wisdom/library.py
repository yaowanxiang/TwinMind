"""智慧库加载与检索 — 零依赖，内置 67 条人类智慧（古籍/历史/跨学科/未来）。

检索维度：
  - 关键词相关度（essence + how_to_apply + tags + applicable_to 加权）
  - 文化/国家过滤（横向：中国、美国、日本、全球……）
  - 时代过滤（纵向：古代/近代/现代/未来）
  - 学科过滤（交叉：军事/金融/医学/计算机……）
"""
import json
from pathlib import Path

from twinmind.config import WISDOM_PATH


def load_library(path: str | Path | None = None) -> list[dict]:
    p = Path(path) if path else WISDOM_PATH
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data.get("entries", data) if isinstance(data, dict) else data
    except Exception:
        return []


def _tokenize(text: str) -> list[str]:
    """中文按字二元组 + 英文按词，简单而有效的检索特征"""
    text = text.lower()
    tokens = []
    for word in text.split():
        if word.isascii() and len(word) > 1:
            tokens.append(word)
    for i in range(len(text) - 1):
        ch = text[i:i + 2]
        if any('\u4e00' <= c <= '\u9fff' for c in ch):
            tokens.append(ch)
    return tokens


# 概念扩展：查询词 → 同义/近义概念（大幅提升中文检索命中质量）
CONCEPT_EXPANSION = {
    "推广": ["宣传", "传播", "营销", "发布", "影响力", "借势", "人脉", "知名度", "推广", "扩散", "推荐"],
    "开源": ["开源", "软件", "代码", "项目", "社区", "共享", "开放"],
    "效率": ["效率", "省时", "省力", "极简", "自动化", "聚焦", "精简", "优化", "快捷"],
    "时间": ["时间", "计划", "安排", "日程", "期限", "截止", "紧急"],
    "谈判": ["谈判", "说服", "沟通", "合作", "博弈", "协商", "争取"],
    "风险": ["风险", "安全", "保险", "分散", "危机", "防御", "保障", "防范"],
    "学习": ["学习", "知识", "技能", "费曼", "教学", "读书", "训练", "成长"],
    "团队": ["团队", "管理", "领导", "协作", "组织", "用人", "激励"],
    "投资": ["投资", "理财", "成本", "收益", "金融", "股票", "复利", "资产"],
    "决策": ["决策", "选择", "判断", "权衡", "取舍", "分析"],
    "创新": ["创新", "创意", "发明", "突破", "灵感", "变革"],
    "竞争": ["竞争", "对手", "博弈", "商场", "优势", "取胜"],
    "目标": ["目标", "计划", "方向", "战略", "愿景", "规划"],
    "失败": ["失败", "错误", "教训", "复盘", "挫折", "止损"],
    "沟通": ["沟通", "交流", "表达", "说服", "倾听", "汇报"],
    "执行": ["执行", "行动", "落实", "完成", "专注", "习惯", "坚持"],
    "个人": ["个人", "成长", "习惯", "自律", "修炼"],
    "赚钱": ["赚钱", "收入", "副业", "商业", "变现", "创业"],
    "创业": ["创业", "商业", "公司", "生意", "市场", "产品"],
    "管理": ["管理", "制度", "流程", "组织", "团队", "体系"],
    "压力": ["压力", "焦虑", "情绪", "心态", "放松", "韧性"],
    "信息": ["信息", "情报", "数据", "调研", "检索", "分析"],
    "创新方法": ["创新", "TRIZ", "SCAMPER", "发散", "头脑风暴"],
    "做事": ["做事", "方法", "原则", "智慧", "思路", "处世"],
    "选择": ["选择", "取舍", "决策", "权衡", "两难"],
    "合作": ["合作", "联盟", "共赢", "信任", "团队", "携手"],
    "坚持": ["坚持", "恒心", "持续", "长期", "毅力", "专注"],
    "健康": ["健康", "身体", "养生", "睡眠", "运动", "作息"],
}


def expand_query(query: str) -> set[str]:
    """查询概念扩展：返回 原始二元组 + 同义概念词"""
    tokens = set(_tokenize(query))
    for word, exts in CONCEPT_EXPANSION.items():
        if word in query:
            tokens.update(_tokenize(" ".join(exts)))
    return tokens


def _score(entry: dict, query_tokens: set[str]) -> float:
    haystack = " ".join([
        entry.get("title", ""), entry.get("essence", ""),
        entry.get("how_to_apply", ""), entry.get("applicable_to", ""),
        " ".join(entry.get("tags", [])), entry.get("contrast", ""),
    ]).lower()
    if not query_tokens:
        return 0.5
    # 直接子串命中加权
    score = 0.0
    for t in query_tokens:
        if t in haystack:
            score += 1.0
    # 二元组命中
    h_tokens = set(_tokenize(haystack))
    overlap = len(h_tokens & query_tokens)
    score += overlap * 0.5
    # 标签命中加权更高
    tag_text = " ".join(entry.get("tags", [])).lower()
    for t in query_tokens:
        if t in tag_text:
            score += 1.5
    return score


def search(query: str, limit: int = 8, culture: str | None = None,
           era_type: str | None = None, discipline: str | None = None,
           path: str | Path | None = None) -> list[dict]:
    """按相关性检索智慧库，支持时空/学科过滤"""
    entries = load_library(path)
    q_tokens = expand_query(query)
    scored = []
    for e in entries:
        if culture and e.get("culture", "") != culture:
            continue
        if era_type and e.get("era_type", "") != era_type:
            continue
        if discipline and e.get("discipline", "") != discipline:
            continue
        s = _score(e, q_tokens)
        if s > 0:
            scored.append((s, e))
    scored.sort(key=lambda x: -x[0])
    return [dict(e, _score=round(s, 2)) for s, e in scored[:limit]]


def by_culture(culture: str, limit: int = 50) -> list[dict]:
    """横向：某个国家/文化/民族的解法"""
    return [e for e in load_library() if culture in e.get("culture", "")][:limit]


def by_era(era_type: str, limit: int = 50) -> list[dict]:
    """纵向：某个时代的解法"""
    return [e for e in load_library() if e.get("era_type") == era_type][:limit]


def by_discipline(discipline: str, limit: int = 50) -> list[dict]:
    """学科交叉：某个学科的解法"""
    return [e for e in load_library() if discipline in e.get("discipline", "")][:limit]


def spacetime_view() -> dict:
    """时空矩阵总览：culture × era_type 交叉统计"""
    from collections import Counter
    lib = load_library()
    cultures = Counter(e.get("culture", "未知") for e in lib)
    eras = Counter(e.get("era_type", "未知") for e in lib)
    disciplines = Counter(e.get("discipline", "未知") for e in lib)
    matrix = {}
    for e in lib:
        key = (e.get("culture", "未知"), e.get("era_type", "未知"))
        matrix.setdefault(key, 0)
        matrix[key] += 1
    return {
        "total": len(lib),
        "cultures": dict(cultures.most_common(15)),
        "eras": dict(eras),
        "disciplines": dict(disciplines.most_common(20)),
        "matrix": {f"{c}×{e}": n for (c, e), n in sorted(matrix.items(), key=lambda x: -x[1])},
    }

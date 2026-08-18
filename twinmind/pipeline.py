"""TwinMind 全流程管道 — 六大系统闭环：摄入→画像→优化→决策→授权执行→反馈。"""
import json

from twinmind.config import load_config
from twinmind.distill.distiller import distill_session_events
from twinmind.memory import store
from twinmind.profile.profiler import build_profile


def run_pipeline(limit_sessions: int = 20, cfg: dict | None = None) -> dict:
    """把最近 N 个未蒸馏会话走完「摄入→蒸馏→画像」全流程。"""
    cfg = cfg or load_config()
    sessions = store.list_sessions(limit=limit_sessions)
    distilled, patterns_added = 0, 0
    for s in sessions:
        if store.get_kv(f"distilled.session.{s['id']}"):
            continue
        events = store.get_session_events(s["id"], limit=200)
        if not events:
            continue
        result = distill_session_events(events, cfg)
        n = _persist(result, s)
        store.set_kv(f"distilled.session.{s['id']}", "1")
        distilled += 1
        patterns_added += n
    # 画像更新
    profile = build_profile(cfg, rebuild=True)
    return {
        "sessions_processed": distilled,
        "patterns_added": patterns_added,
        "profile": profile,
        "stats": store.stats(),
    }


def _persist(result: dict, session: dict) -> int:
    n = 0
    sid = session["id"]
    for f in result.get("facts", []):
        store.add_pattern(1, f["content"], f.get("tags", []), f.get("importance", 0.5), sid, "distill")
        n += 1
    for p in result.get("patterns", []):
        store.add_pattern(2, p["content"], p.get("tags", []), p.get("importance", 0.5), sid, "distill")
        n += 1
    for pr in result.get("principles", []):
        store.add_pattern(3, pr["content"], pr.get("tags", []), pr.get("importance", 0.5), sid, "distill")
        n += 1
    return n


def distill_sessions(session_ids: list[int] | None = None, cfg: dict | None = None) -> dict:
    """蒸馏指定会话（None=全部未蒸馏）"""
    cfg = cfg or load_config()
    if session_ids:
        sessions = [store.list_sessions(limit=1000)[i] for i in session_ids if i < 1000]
        sessions = [s for s in store.list_sessions(limit=1000) if s["id"] in session_ids]
    else:
        sessions = store.list_sessions(limit=1000)
    distilled, added = 0, 0
    for s in sessions:
        if store.get_kv(f"distilled.session.{s['id']}"):
            continue
        events = store.get_session_events(s["id"], limit=200)
        if not events:
            continue
        result = distill_session_events(events, cfg)
        added += _persist(result, s)
        store.set_kv(f"distilled.session.{s['id']}", "1")
        distilled += 1
    return {"distilled": distilled, "patterns_added": added}

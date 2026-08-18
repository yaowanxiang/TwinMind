"""审计日志 — 一切动作留痕：谁、何时、做了什么、风险级、如何批准的。

原则：TwinMind 所有对外动作默认记录审计；日志只增不改。
"""
import json
from datetime import datetime, timezone

from twinmind.memory import store


def log(action: str, risk: str, params: dict, decision: str,
        mode: str, actor: str = "agent", operator: str = "user", note: str = "") -> int:
    entry = {
        "action": action,
        "risk": risk,
        "params": params,
        "decision": decision,       # allow / approve / deny / approved / denied / error
        "mode": mode,
        "actor": actor,
        "operator": operator,
        "note": note,
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    return store.add_audit(entry)


def recent(limit: int = 100) -> list[dict]:
    return store.list_audit(limit)

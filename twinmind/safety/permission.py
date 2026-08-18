"""授权管理 — 三种运行模式 + 审批队列。

模式：
  auto   全自动：R0/R1 直接执行，R2/R3 进审批队列
  semi   半自动：R0 直接执行，R1/R2/R3 进审批队列
  manual 人工主导：只有 R0 直接执行，其余全部进审批队列

审批队列持久化在 SQLite（pending_approvals 表），桌面端可逐条批准/拒绝。
"""
import json
import sqlite3
from datetime import datetime, timezone

from twinmind.memory import store
from twinmind.safety.policy import requirement_for, RISK_NAMES

MODE_KEY = "twinmind.mode"


def get_mode() -> str:
    return store.get_kv(MODE_KEY, "semi")


def set_mode(mode: str) -> None:
    if mode not in ("auto", "semi", "manual"):
        raise ValueError(f"未知模式: {mode}")
    store.set_kv(MODE_KEY, mode)


def check(action: str, risk: str, params: dict, actor: str = "agent") -> dict:
    """检查一个动作在当前模式下的处理方式。

    返回 {decision: allow|approve|deny, reason, approval_id?}
    """
    mode = get_mode()
    req = requirement_for(mode, risk)
    if req == "allow":
        return {"decision": "allow", "mode": mode, "reason": f"{RISK_NAMES.get(risk, risk)}动作，当前{mode}模式下直接执行"}
    if req == "approve":
        aid = store.add_approval(action, risk, params, actor, mode)
        return {"decision": "approve", "mode": mode, "approval_id": aid,
                "reason": f"{RISK_NAMES.get(risk, risk)}动作已进入审批队列，等待用户批准"}
    return {"decision": "deny", "mode": mode, "reason": "该动作在当前模式下被禁止"}


def decide(approval_id: int, approve: bool, operator: str = "user") -> dict:
    """处理一条审批：批准或拒绝。"""
    item = store.get_approval(approval_id)
    if not item:
        raise ValueError(f"审批不存在: {approval_id}")
    if item["status"] != "pending":
        raise ValueError(f"审批已被处理: {item['status']}")
    status = "approved" if approve else "denied"
    store.update_approval(approval_id, status, operator)
    return {"approval_id": approval_id, "status": status, "action": item["action"]}

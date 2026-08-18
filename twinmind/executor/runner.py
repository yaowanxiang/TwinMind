"""动作执行器 — 四道闸门：策略分级 → 恶意防护 → 授权检查 → 审计留痕。

execute(action, params, actor) 返回统一结果：
  {"status": "executed" | "approved" | "denied" | "error",
   "approval_id"?, "reason", "result"?}

执行规则：
  - R0 只读：直接执行
  - R1 本地：auto 直接执行；semi/manual 需批准（semi 默认 R1 批准）
  - R2/R3 对外：一律审批队列（auto 的 R2 也需批准）
  - 恶意模式命中：直接拒绝 + 审计
"""
from twinmind.safety import audit, guard, permission, policy


def execute(action: str, params: dict, actor: str = "agent") -> dict:
    spec = policy.get_spec(action)
    risk = spec.risk_level

    # 闸门1：恶意防护（命令/意图扫描）
    if action == "run_command" and params.get("command"):
        hits = guard.check_command(params["command"])
        if hits:
            audit.log(action, risk, guard.redact(params), "denied", permission.get_mode(),
                      actor=actor, note=f"危险命令模式命中: {hits}")
            return {"status": "denied", "reason": f"检测到危险命令模式，已拦截: {hits}"}
    intent_hits = guard.check_intent(json_str(params))
    if intent_hits:
        audit.log(action, risk, guard.redact(params), "denied", permission.get_mode(),
                  actor=actor, note=f"敏感意图命中: {intent_hits}")
        return {"status": "denied", "reason": f"检测到敏感意图措辞，已拦截: {intent_hits}"}

    # 闸门2：授权检查
    check = permission.check(action, risk, guard.redact(params), actor)
    if check["decision"] == "deny":
        audit.log(action, risk, guard.redact(params), "denied", check["mode"], actor=actor,
                  note=check["reason"])
        return {"status": "denied", "reason": check["reason"]}
    if check["decision"] == "approve":
        audit.log(action, risk, guard.redact(params), "approved", check["mode"], actor=actor,
                  note=f"进入审批队列 #{check['approval_id']}")
        return {"status": "approved", "approval_id": check["approval_id"], "reason": check["reason"]}

    # 闸门3：执行
    try:
        result = _run(action, params)
        audit.log(action, risk, guard.redact(params), "executed", check["mode"], actor=actor,
                  note="执行成功")
        return {"status": "executed", "reason": "执行成功", "result": result}
    except Exception as e:
        audit.log(action, risk, guard.redact(params), "error", check["mode"], actor=actor,
                  note=f"执行失败: {e}")
        return {"status": "error", "reason": f"执行失败: {e}"}


def json_str(params: dict) -> str:
    import json
    return json.dumps(params, ensure_ascii=False)


def execute_approved(approval_id: int, operator: str = "user") -> dict:
    """用户批准后真正执行动作（批准→执行→审计 闭环）。"""
    from twinmind.memory import store
    from twinmind.safety import permission as perm
    item = store.get_approval(approval_id)
    if not item:
        return {"status": "error", "reason": f"审批不存在: {approval_id}"}
    if item["status"] != "pending":
        return {"status": "error", "reason": f"审批状态不是 pending: {item['status']}"}
    perm.decide(approval_id, True, operator)
    action, risk, params = item["action"], item["risk"], item["params"]
    try:
        result = _run(action, params)
        audit.log(action, risk, guard.redact(params), "executed", item["mode"],
                  operator=operator, note=f"审批 #{approval_id} 通过后执行")
        return {"status": "executed", "approval_id": approval_id, "result": result}
    except Exception as e:
        audit.log(action, risk, guard.redact(params), "error", item["mode"],
                  operator=operator, note=f"审批 #{approval_id} 执行失败: {e}")
        return {"status": "error", "approval_id": approval_id, "reason": f"执行失败: {e}"}


def _run(action: str, params: dict):
    """实际执行。MVP 覆盖只读与本地动作；对外动作(R2/R3)需用户批准后在接线中执行。"""
    if action == "read_memory":
        from twinmind.memory import store
        q = params.get("query", "")
        patterns = store.list_patterns(limit=50)
        return {"patterns": patterns, "stats": store.stats()}
    if action == "read_file":
        from pathlib import Path
        p = Path(params["path"])
        if not p.exists():
            raise FileNotFoundError(str(p))
        return {"content": p.read_text(encoding="utf-8", errors="replace")[:20000]}
    if action == "advise":
        from twinmind.advisor.advisor import advise
        return advise(params.get("question", ""))
    if action == "write_file":
        from pathlib import Path
        p = Path(params["path"])
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(params.get("content", ""), encoding="utf-8")
        return {"path": str(p), "bytes": p.stat().st_size}
    if action == "run_command":
        import subprocess
        r = subprocess.run(params["command"], shell=True, capture_output=True, text=True, timeout=300)
        return {"exit_code": r.returncode, "stdout": r.stdout[-3000:], "stderr": r.stderr[-2000:]}
    if action == "send_email":
        raise NotImplementedError("邮件发送需用户批准后由邮件客户端执行（配置中）")
    if action == "send_message":
        raise NotImplementedError("消息发送需用户批准后由对应渠道执行（配置中）")
    raise NotImplementedError(f"动作未实现: {action}")

"""Hermes 会话导入器 — 直接从 Hermes state.db 读取会话与消息。

自动探测 Hermes 数据库位置：
  1. 环境变量 HERMES_STATE_DB
  2. Windows: %LOCALAPPDATA%/hermes/state.db
  3. macOS: ~/Library/Application Support/hermes/state.db
  4. Linux: ~/.hermes/state.db 等常见位置
"""
import json
import os
import sqlite3
from pathlib import Path

from twinmind.memory import store


def _probe_paths() -> list[Path]:
    candidates: list[Path] = []
    env = os.environ.get("HERMES_STATE_DB")
    if env:
        candidates.append(Path(env))
    home = Path.home()
    local = os.environ.get("LOCALAPPDATA")
    if local:
        candidates.append(Path(local) / "hermes" / "state.db")
        candidates.append(Path(local) / "hermes" / "profiles" / "default" / "state.db")
    candidates += [
        home / "Library" / "Application Support" / "hermes" / "state.db",
        home / ".hermes" / "state.db",
        home / ".config" / "hermes" / "state.db",
    ]
    seen, out = set(), []
    for p in candidates:
        key = str(p).lower()
        if key not in seen:
            seen.add(key)
            if p.exists():
                out.append(p)
    return out

def find_db() -> Path | None:
    for p in _probe_paths():
        if p.exists():
            return p
    return None

def import_sessions(limit: int = 30, min_messages: int = 3, db_path: str | None = None,
                    source: str = "hermes") -> dict:
    """导入最近的会话。返回 {imported: n, sessions: [...], skipped: n}"""
    path = Path(db_path) if db_path else find_db()
    if path is None:
        raise FileNotFoundError("未找到 Hermes 数据库，请设置 HERMES_STATE_DB 或传入 db_path")
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, title, started_at, model, cwd, message_count FROM sessions "
        "WHERE message_count >= ? AND hidden != 1 ORDER BY started_at DESC LIMIT ?",
        (min_messages, limit),
    ).fetchall()

    imported, skipped, details = 0, 0, []
    for row in rows:
        sid = row["id"]
        msgs = conn.execute(
            "SELECT role, content, tool_name, timestamp FROM messages "
            "WHERE session_id=? ORDER BY id", (sid,),
        ).fetchall()
        events = []
        for m in msgs:
            content = m["content"] or ""
            if not content.strip():
                continue
            role = m["role"] or "user"
            if role == "tool" and m["tool_name"]:
                # 工具调用结果太长则截断保留头尾
                content = _trim(content, 600)
            events.append({
                "role": role,
                "content": content,
                "tool_name": m["tool_name"] or "",
                "timestamp": m["timestamp"] or "",
            })
        if len(events) < min_messages:
            skipped += 1
            continue
        meta = {"model": row["model"], "cwd": row["cwd"], "hermes_session_id": sid}
        sess_id = store.add_session(source, external_id=str(sid),
                                    title=row["title"] or f"会话 {sid}",
                                    started_at=row["started_at"] or "", meta=meta)
        store.add_events_batch(sess_id, events)
        imported += 1
        details.append({"id": sess_id, "title": row["title"] or f"会话 {sid}",
                        "events": len(events), "started_at": row["started_at"] or ""})
    conn.close()
    return {"imported": imported, "skipped": skipped, "sessions": details}

def _trim(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n...[已截断，原长 {len(text)} 字符]"

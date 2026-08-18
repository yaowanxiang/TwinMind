"""TwinMind 存储层 — SQLite，零外部依赖。

核心表：
  sessions   会话（一次导入/一段日记/一个对话）
  events     原始事件流（消息、操作），供蒸馏与回放
  patterns   三级抽象结果：L1 具体做法 / L2 思路模式 / L3 处事原则
  profile    数字画像（单行 JSON）
  advices    历史建议记录
"""
import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path

from twinmind.config import DB_PATH

_lock = threading.Lock()
_conn: sqlite3.Connection | None = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,            -- hermes / jsonl / journal / manual
    external_id TEXT DEFAULT '',     -- 原始会话 id（如 hermes session_id）
    title TEXT DEFAULT '',
    started_at TEXT DEFAULT '',
    meta TEXT DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    role TEXT DEFAULT 'user',        -- user / assistant / tool / action
    content TEXT DEFAULT '',
    tool_name TEXT DEFAULT '',
    timestamp TEXT DEFAULT '',
    meta TEXT DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_events_session ON events(session_id);
CREATE TABLE IF NOT EXISTS patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level INTEGER NOT NULL,          -- 1 具体做法 / 2 思路模式 / 3 处事原则
    content TEXT NOT NULL,
    tags TEXT DEFAULT '[]',
    importance REAL DEFAULT 0.5,
    source_session INTEGER DEFAULT 0,
    source TEXT DEFAULT '',
    created_at TEXT DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_patterns_level ON patterns(level);
CREATE TABLE IF NOT EXISTS profile (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    data TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS advices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT DEFAULT '',
    answer TEXT DEFAULT '',
    created_at TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS kv (
    key TEXT PRIMARY KEY,
    value TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS pending_approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    risk TEXT NOT NULL,
    params TEXT DEFAULT '{}',
    actor TEXT DEFAULT 'agent',
    mode TEXT DEFAULT 'semi',
    status TEXT DEFAULT 'pending',   -- pending / approved / denied
    requested_at TEXT DEFAULT '',
    decided_at TEXT DEFAULT '',
    operator TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    risk TEXT DEFAULT '',
    params TEXT DEFAULT '{}',
    decision TEXT DEFAULT '',
    mode TEXT DEFAULT '',
    actor TEXT DEFAULT 'agent',
    operator TEXT DEFAULT 'user',
    note TEXT DEFAULT '',
    ts TEXT DEFAULT ''
);
"""

def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def get_conn() -> sqlite3.Connection:
    global _conn
    with _lock:
        if _conn is None:
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            _conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
            _conn.row_factory = sqlite3.Row
            _conn.executescript(SCHEMA)
            _conn.commit()
        return _conn

def add_session(source: str, external_id: str = "", title: str = "",
                started_at: str = "", meta: dict | None = None) -> int:
    c = get_conn()
    cur = c.execute(
        "INSERT INTO sessions(source, external_id, title, started_at, meta) VALUES(?,?,?,?,?)",
        (source, external_id, title, started_at, json.dumps(meta or {}, ensure_ascii=False)),
    )
    c.commit()
    return cur.lastrowid

def add_event(session_id: int, role: str, content: str, tool_name: str = "",
              timestamp: str = "", meta: dict | None = None) -> int:
    c = get_conn()
    cur = c.execute(
        "INSERT INTO events(session_id, role, content, tool_name, timestamp, meta) VALUES(?,?,?,?,?,?)",
        (session_id, role, content, tool_name, timestamp or _now(),
         json.dumps(meta or {}, ensure_ascii=False)),
    )
    c.commit()
    return cur.lastrowid

def add_events_batch(session_id: int, events: list[dict]) -> int:
    c = get_conn()
    rows = [
        (session_id, e.get("role", "user"), e.get("content", ""), e.get("tool_name", ""),
         e.get("timestamp", _now()), json.dumps(e.get("meta", {}), ensure_ascii=False))
        for e in events
    ]
    c.executemany(
        "INSERT INTO events(session_id, role, content, tool_name, timestamp, meta) VALUES(?,?,?,?,?,?)",
        rows,
    )
    c.commit()
    return len(rows)

def get_session_events(session_id: int, limit: int | None = None) -> list[dict]:
    c = get_conn()
    sql = "SELECT * FROM events WHERE session_id=? ORDER BY id"
    if limit:
        sql += f" LIMIT {int(limit)}"
    return [dict(r) for r in c.execute(sql, (session_id,)).fetchall()]

def list_sessions(limit: int = 50) -> list[dict]:
    c = get_conn()
    rows = c.execute(
        "SELECT s.*, (SELECT COUNT(*) FROM events e WHERE e.session_id=s.id) AS event_count "
        "FROM sessions s ORDER BY s.id DESC LIMIT ?", (limit,),
    ).fetchall()
    return [dict(r) for r in rows]

def add_pattern(level: int, content: str, tags: list[str] | None = None,
                importance: float = 0.5, source_session: int = 0,
                source: str = "") -> int:
    c = get_conn()
    cur = c.execute(
        "INSERT INTO patterns(level, content, tags, importance, source_session, source, created_at) "
        "VALUES(?,?,?,?,?,?,?)",
        (level, content, json.dumps(tags or [], ensure_ascii=False), importance,
         source_session, source, _now()),
    )
    c.commit()
    return cur.lastrowid

def list_patterns(level: int | None = None, limit: int = 200) -> list[dict]:
    c = get_conn()
    if level is None:
        rows = c.execute("SELECT * FROM patterns ORDER BY importance DESC, id DESC LIMIT ?", (limit,))
    else:
        rows = c.execute(
            "SELECT * FROM patterns WHERE level=? ORDER BY importance DESC, id DESC LIMIT ?",
            (level, limit),
        )
    out = []
    for r in rows.fetchall():
        d = dict(r)
        d["tags"] = json.loads(d.get("tags") or "[]")
        out.append(d)
    return out

def count_patterns() -> dict:
    c = get_conn()
    rows = c.execute("SELECT level, COUNT(*) AS n FROM patterns GROUP BY level").fetchall()
    return {f"L{r['level']}": r["n"] for r in rows}

def save_profile(data: dict) -> None:
    c = get_conn()
    c.execute(
        "INSERT INTO profile(id, data) VALUES(1, ?) "
        "ON CONFLICT(id) DO UPDATE SET data=excluded.data",
        (json.dumps(data, ensure_ascii=False, indent=2),),
    )
    c.commit()

def load_profile() -> dict | None:
    c = get_conn()
    row = c.execute("SELECT data FROM profile WHERE id=1").fetchone()
    if not row:
        return None
    try:
        return json.loads(row["data"])
    except Exception:
        return None

def add_advice(question: str, answer: str) -> int:
    c = get_conn()
    cur = c.execute("INSERT INTO advices(question, answer, created_at) VALUES(?,?,?)",
                    (question, answer, _now()))
    c.commit()
    return cur.lastrowid

def list_advices(limit: int = 30) -> list[dict]:
    c = get_conn()
    return [dict(r) for r in c.execute(
        "SELECT * FROM advices ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]

def get_kv(key: str, default: str = "") -> str:
    c = get_conn()
    row = c.execute("SELECT value FROM kv WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default

def set_kv(key: str, value: str) -> None:
    c = get_conn()
    c.execute("INSERT INTO kv(key, value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
              (key, value))
    c.commit()

def add_approval(action: str, risk: str, params: dict, actor: str, mode: str) -> int:
    c = get_conn()
    cur = c.execute(
        "INSERT INTO pending_approvals(action, risk, params, actor, mode, requested_at) "
        "VALUES(?,?,?,?,?,?)",
        (action, risk, json.dumps(params, ensure_ascii=False), actor, mode, _now()),
    )
    c.commit()
    return cur.lastrowid

def get_approval(approval_id: int) -> dict | None:
    c = get_conn()
    row = c.execute("SELECT * FROM pending_approvals WHERE id=?", (approval_id,)).fetchone()
    if not row:
        return None
    d = dict(row)
    d["params"] = json.loads(d.get("params") or "{}")
    return d

def update_approval(approval_id: int, status: str, operator: str) -> None:
    c = get_conn()
    c.execute("UPDATE pending_approvals SET status=?, decided_at=?, operator=? WHERE id=?",
              (status, _now(), operator, approval_id))
    c.commit()

def list_approvals(status: str | None = "pending", limit: int = 100) -> list[dict]:
    c = get_conn()
    if status:
        rows = c.execute("SELECT * FROM pending_approvals WHERE status=? ORDER BY id DESC LIMIT ?",
                         (status, limit))
    else:
        rows = c.execute("SELECT * FROM pending_approvals ORDER BY id DESC LIMIT ?", (limit,))
    out = []
    for r in rows.fetchall():
        d = dict(r)
        d["params"] = json.loads(d.get("params") or "{}")
        out.append(d)
    return out

def add_audit(entry: dict) -> int:
    c = get_conn()
    cur = c.execute(
        "INSERT INTO audit_log(action, risk, params, decision, mode, actor, operator, note, ts) "
        "VALUES(?,?,?,?,?,?,?,?,?)",
        (entry.get("action", ""), entry.get("risk", ""),
         json.dumps(entry.get("params", {}), ensure_ascii=False),
         entry.get("decision", ""), entry.get("mode", ""), entry.get("actor", "agent"),
         entry.get("operator", "user"), entry.get("note", ""), entry.get("ts", _now())),
    )
    c.commit()
    return cur.lastrowid

def list_audit(limit: int = 100) -> list[dict]:
    c = get_conn()
    out = []
    for r in c.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,)).fetchall():
        d = dict(r)
        d["params"] = json.loads(d.get("params") or "{}")
        out.append(d)
    return out

def stats() -> dict:
    c = get_conn()
    s = {
        "sessions": c.execute("SELECT COUNT(*) FROM sessions").fetchone()[0],
        "events": c.execute("SELECT COUNT(*) FROM events").fetchone()[0],
        "patterns": c.execute("SELECT COUNT(*) FROM patterns").fetchone()[0],
        "advices": c.execute("SELECT COUNT(*) FROM advices").fetchone()[0],
    }
    s["pattern_levels"] = count_patterns()
    return s

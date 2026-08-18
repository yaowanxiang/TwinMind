"""通用 JSONL/JSON 导入器 — 任何 AI 工具、任何格式的会话都能进 TwinMind。

支持两种输入：
  1. JSONL：每行一个 JSON，字段 {role, content, tool_name?, timestamp?, session_id?}
  2. JSON 数组：[{role, content, ...}, ...] 或 {messages: [...]} 或 {conversation: [...]}
  3. 目录：递归导入目录下所有 .jsonl / .json
"""
import json
from pathlib import Path

from twinmind.memory import store


def _parse_one(raw: dict) -> dict:
    role = raw.get("role") or raw.get("type") or raw.get("speaker") or "user"
    content = raw.get("content") or raw.get("text") or raw.get("message") or ""
    if isinstance(content, list):  # OpenAI 风格 content 数组
        parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append(item.get("text", ""))
                elif item.get("type") == "tool_result":
                    parts.append(str(item.get("content", "")))
            else:
                parts.append(str(item))
        content = "\n".join(parts)
    return {
        "role": str(role),
        "content": str(content),
        "tool_name": str(raw.get("tool_name") or raw.get("name") or ""),
        "timestamp": str(raw.get("timestamp") or raw.get("time") or ""),
        "meta": {"raw_keys": sorted(raw.keys())},
    }

def import_file(path: str | Path, source: str = "jsonl") -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"文件不存在: {p}")
    raw = p.read_text(encoding="utf-8")
    data = None
    try:
        data = json.loads(raw)          # 尝试整体解析（JSON 数组 / 对象）
    except Exception:
        # JSONL：逐行解析
        rows = []
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
        if rows:
            data = rows
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = (data.get("messages") or data.get("conversation")
                 or data.get("turns") or [data])
    else:
        raise ValueError(f"无法解析文件: {p}")

    events = [_parse_one(x) for x in items if isinstance(x, dict)]
    events = [e for e in events if e["content"].strip()]
    if not events:
        return {"imported": 0, "events": 0, "path": str(p)}

    sess_id = store.add_session(source, external_id=p.name, title=p.stem,
                                started_at=events[0]["timestamp"], meta={"path": str(p)})
    store.add_events_batch(sess_id, events)
    return {"imported": 1, "events": len(events), "path": str(p), "session_id": sess_id}

def import_dir(path: str | Path, glob: str = "*.jsonl") -> dict:
    """递归导入目录下所有匹配文件"""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"目录不存在: {p}")
    files = sorted(p.rglob(glob)) + sorted(p.rglob("*.json"))
    total_imported, total_events = 0, 0
    for f in files:
        try:
            r = import_file(f, source="jsonl")
            total_imported += r["imported"]
            total_events += r["events"]
        except Exception:
            continue
    return {"imported": total_imported, "events": total_events, "files": len(files)}

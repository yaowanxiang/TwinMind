"""日记记录器 — 普通用户入口。

不懂技术也能用：把「今天做了什么、怎么做的、为什么这样做」用大白话写下来，
TwinMind 会从中提炼你的处事方式。也支持语音转文字后直接粘贴。
"""
from datetime import datetime

from twinmind.memory import store


def add_journal(text: str, title: str = "") -> int:
    """添加一篇日记/随手记，返回 session_id"""
    text = text.strip()
    if not text:
        raise ValueError("内容不能为空")
    now = datetime.now().isoformat(timespec="seconds")
    sess_id = store.add_session("journal", title=title or f"日记 {now[:16]}", started_at=now)
    store.add_event(sess_id, "user", text, timestamp=now)
    return sess_id

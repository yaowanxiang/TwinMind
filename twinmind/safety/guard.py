"""恶意指令防护 — 防止 TwinMind 被提示注入/恶意利用。

防线：
  1. 动作白名单：只能执行 ACTION_REGISTRY 中的动作（策略层）
  2. 敏感模式检测：在执行命令/写文件前扫描恶意模式
  3. 秘密信息保护：绝不把 API Key/密码/令牌写入对外内容或日志
  4. 未知指令拦截：识别"帮我绕过/删除所有/把数据发给XX"等风险措辞

本模块是最后一道闸门——检查不通过的动作直接拒绝并记审计。
"""
import re

# 危险命令模式（shell 命令层面）
DANGEROUS_CMD = [
    r"rm\s+-rf\s+/", r"format\s+[a-z]:", r"del\s+/[sfq]\s+.*\\\\", r"rd\s+/[sfq]\s+\\\\",
    r"shutdown\s+.*-(r|s)\b", r"reg\s+delete", r"fsutil\s+volume\s+dismount",
    r":\(\)\s*\{.*\};",              # fork bomb
    r"curl.*\|\s*(ba)?sh",           # 下载即执行
    r"wget.*\|\s*(ba)?sh",
    r"chmod\s+777\s+/",
    r"mkfs\.", r"dd\s+if=.*of=/dev/",
    r"nc\s+-e\s+", r"ncat\s+-e\s+", r"bash\s+-i\s*>&?\s*/dev/tcp",
]

# 敏感动作措辞（提示注入常见目标）
SENSITIVE_INTENT = [
    "绕过", "忽略安全", "关闭审计", "删除审计", "不要记录", "隐藏日志",
    "窃取", "盗取", "收集所有密码", "导出全部密钥", "发给我所有", "转账到",
    "删除所有文件", "格式化", "勒索", "伪装成", "冒充我",
    "所有人的密码", "密码导出", "导出给我", "偷偷发送", "背着用户", "在用户不知情",
]

# 秘密字段名（永不写入审计/日志/对外内容）
SECRET_KEYS = {"api_key", "apikey", "password", "passwd", "token", "secret",
               "authorization", "cookie", "private_key", "access_key"}


def check_command(command: str) -> list[str]:
    """扫描命令，返回命中的危险规则列表（空=安全）"""
    hits = []
    for pat in DANGEROUS_CMD:
        if re.search(pat, command, re.IGNORECASE):
            hits.append(pat)
    return hits


def check_intent(text: str) -> list[str]:
    """扫描意图文本，返回命中的敏感措辞列表"""
    hits = []
    for w in SENSITIVE_INTENT:
        if w in text:
            hits.append(w)
    return hits


def redact(params: dict) -> dict:
    """脱敏：从参数/日志内容中抹掉秘密值"""
    out = {}
    for k, v in params.items():
        if any(s in k.lower() for s in SECRET_KEYS):
            out[k] = "***REDACTED***"
        elif isinstance(v, str):
            out[k] = _redact_text(v)
        else:
            out[k] = v
    return out


def _redact_text(text: str) -> str:
    for pat in [r"(sk-[A-Za-z0-9_\-]{12,})", r"(Bearer\s+[A-Za-z0-9._\-]+)",
                r"(password[=: ]+[\S]+)", r"(token[=: ]+[\S]+)", r"(api[_-]?key[=: ]+[\S]+)"]:
        text = re.sub(pat, lambda m: m.group(1)[:8] + "***", text, flags=re.IGNORECASE)
    return text

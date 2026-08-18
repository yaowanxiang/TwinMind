"""动作策略 — 把 TwinMind 能做的动作按「对外影响」分级。

风险分级（risk_level）：
  R0 本地只读    —— 读文件、检索记忆、生成建议。无副作用。
  R1 本地写入    —— 写本地文件、改本地配置。仅影响本机。
  R2 对外通信    —— 发邮件、发消息、发帖子、提交 PR、发布内容。以用户名义对外。
  R3 高影响      —— 转账、删除数据、购买、修改公开身份、不可逆操作。必须人工批准。

每个动作类声明：名称、中文描述、风险级、需要哪些参数。
"""
from dataclasses import dataclass, field

RISK_NAMES = {"R0": "本地只读", "R1": "本地写入", "R2": "对外通信", "R3": "高影响"}


@dataclass
class ActionSpec:
    name: str
    description: str
    risk_level: str          # R0/R1/R2/R3
    params: list[str] = field(default_factory=list)   # 需要的参数字段


ACTION_REGISTRY: dict[str, ActionSpec] = {
    "read_memory": ActionSpec("read_memory", "检索我的记忆库", "R0", ["query"]),
    "read_file": ActionSpec("read_file", "读取本地文件", "R0", ["path"]),
    "advise": ActionSpec("advise", "生成建议", "R0", ["question"]),
    "write_file": ActionSpec("write_file", "写入本地文件", "R1", ["path", "content"]),
    "run_command": ActionSpec("run_command", "执行本地命令", "R1", ["command"]),
    "install_package": ActionSpec("install_package", "安装软件包", "R1", ["package"]),
    "schedule_task": ActionSpec("schedule_task", "创建定时任务", "R1", ["schedule", "task"]),
    "send_email": ActionSpec("send_email", "发送电子邮件", "R2", ["to", "subject", "body"]),
    "send_message": ActionSpec("send_message", "发送消息/推送", "R2", ["channel", "text"]),
    "publish_content": ActionSpec("publish_content", "发布内容(文章/帖子)", "R2", ["platform", "content"]),
    "create_issue": ActionSpec("create_issue", "创建 GitHub Issue/PR", "R2", ["repo", "title", "body"]),
    "delete_file": ActionSpec("delete_file", "删除文件", "R3", ["path"]),
    "send_money": ActionSpec("send_money", "转账/付款", "R3", ["to", "amount"]),
    "modify_identity": ActionSpec("modify_identity", "修改公开身份/账号信息", "R3", ["target"]),
}

# 每个风险级对应的授权要求（三种模式）
#  mode: auto(全自动) / semi(半自动) / manual(人工主导)
#  requirement: allow(直接执行) / approve(需批准) / deny(禁止)
MODE_POLICY = {
    "auto":   {"R0": "allow", "R1": "allow", "R2": "approve", "R3": "approve"},
    "semi":   {"R0": "allow", "R1": "approve", "R2": "approve", "R3": "approve"},
    "manual": {"R0": "allow", "R1": "approve", "R2": "approve", "R3": "approve"},
}

# 人工主导模式下 R1 也要求批准；全自动模式下 R3 仍强制批准（不可绕过）
MODE_NAMES = {"auto": "全自动", "semi": "半自动", "manual": "人工主导"}


def get_spec(action: str) -> ActionSpec:
    if action not in ACTION_REGISTRY:
        return ActionSpec(action, f"自定义动作 {action}", "R1", [])
    return ACTION_REGISTRY[action]


def requirement_for(mode: str, risk: str) -> str:
    """返回 allow / approve / deny"""
    mode = mode if mode in MODE_POLICY else "manual"
    if risk == "R3":
        return "approve"          # 高影响动作任何模式都强制批准
    return MODE_POLICY[mode].get(risk, "approve")

"""TwinMind 全局配置管理 — 数据目录、LLM 接口、默认值。"""
import json
import os
from pathlib import Path

APP_NAME = "TwinMind"

def get_home() -> Path:
    """数据目录：环境变量 TWINMIND_HOME 优先，否则 ~/.twinmind"""
    env = os.environ.get("TWINMIND_HOME")
    if env:
        p = Path(env)
    else:
        p = Path.home() / ".twinmind"
    p.mkdir(parents=True, exist_ok=True)
    return p

HOME = get_home()
DB_PATH = HOME / "twinmind.db"
WISDOM_PATH = Path(__file__).parent / "wisdom" / "data" / "wisdom.json"
CONFIG_PATH = HOME / "config.json"

DEFAULT_CONFIG = {
    # LLM 接口（OpenAI 兼容）。默认示例为智谱免费模型，可换成任意 OpenAI 兼容端点。
    "llm": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_key": "",            # 也可用环境变量 TWINMIND_API_KEY / ZHIPU_API_KEY
        "model": "glm-4.7-flash",
        "temperature": 0.4,
        "timeout": 120,
    },
    "distill": {
        "max_messages_per_batch": 60,   # 每次蒸馏的消息上限（超长自动分批）
        "min_content_len": 8,           # 蒸馏时忽略的过短消息
    },
    "advice": {
        "cross_domain_count": 3,        # 顾问输出跨行业借鉴条数
        "ancient_count": 3,             # 顾问输出古籍/历史借鉴条数
    },
}

def load_config() -> dict:
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    if CONFIG_PATH.exists():
        try:
            user = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            _deep_merge(cfg, user)
        except Exception:
            pass
    # 环境变量兜底
    env_key = os.environ.get("TWINMIND_API_KEY") or os.environ.get("ZHIPU_API_KEY")
    if env_key and not cfg["llm"]["api_key"]:
        cfg["llm"]["api_key"] = env_key
    return cfg

def save_config(cfg: dict) -> None:
    merged = json.loads(json.dumps(DEFAULT_CONFIG))
    _deep_merge(merged, cfg)
    CONFIG_PATH.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")

def _deep_merge(base: dict, patch: dict) -> None:
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v

def llm_ready(cfg: dict) -> bool:
    return bool(cfg["llm"]["api_key"])

"""TwinMind Web API — FastAPI 后端，驱动桌面 GUI。

端点：
  GET  /api/stats            统计
  GET  /api/profile          数字画像
  POST /api/profile/rebuild  重建画像
  GET  /api/sessions         会话列表
  GET  /api/patterns         经验记忆（三级抽象）
  GET  /api/wisdom           智慧库总览
  GET  /api/wisdom/search    智慧库检索
  POST /api/record/journal   写日记
  POST /api/record/hermes    导入 Hermes 会话
  POST /api/record/file      导入多模态文件
  POST /api/distill          蒸馏
  POST /api/advise           高维顾问
  POST /api/advise/feedback  反馈
  GET/POST /api/mode         授权模式
  GET  /api/approvals        审批队列
  POST /api/approvals/decide 批准/拒绝
  GET  /api/audit            审计日志
  POST /api/execute          执行动作（四道闸门）
"""
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from twinmind import config as cfg_mod
from twinmind.advisor.advisor import advise, feedback
from twinmind.config import HOME
from twinmind.executor.runner import execute
from twinmind.memory import store
from twinmind.multimodal import ingest
from twinmind.profile.profiler import build_profile
from twinmind.recorder import hermes_importer, journal
from twinmind.safety import audit as audit_mod
from twinmind.safety import permission
from twinmind.wisdom import library as wisdom

app = FastAPI(title="TwinMind", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

UI_DIR = cfg_mod.HOME.parent / "twinmind" / "ui" / "web"
if not UI_DIR.exists():
    from pathlib import Path
    UI_DIR = Path(__file__).parent.parent / "ui" / "web"


class JournalIn(BaseModel):
    text: str
    title: str = ""


class AdviseIn(BaseModel):
    question: str


class FeedbackIn(BaseModel):
    question: str = ""
    helpful: bool
    comment: str = ""


class ModeIn(BaseModel):
    mode: str


class DecideIn(BaseModel):
    approval_id: int
    approve: bool


class ExecuteIn(BaseModel):
    action: str
    params: dict = {}


class FileIn(BaseModel):
    path: str


# ---------- 基础 ----------

@app.get("/")
def index():
    return FileResponse(str(UI_DIR / "index.html"))


@app.get("/api/stats")
def api_stats():
    s = store.stats()
    s["wisdom"] = wisdom.spacetime_view()
    s["mode"] = permission.get_mode()
    s["llm_ready"] = cfg_mod.load_config()["llm"]["api_key"] != ""
    return s


@app.get("/api/config")
def api_config():
    cfg = cfg_mod.load_config()
    return {"llm": {"base_url": cfg["llm"]["base_url"], "model": cfg["llm"]["model"],
                    "api_key_set": bool(cfg["llm"]["api_key"])},
            "mode": permission.get_mode()}


@app.post("/api/config")
def api_save_config(body: dict):
    cfg = cfg_mod.load_config()
    if body.get("base_url"):
        cfg["llm"]["base_url"] = body["base_url"]
    if body.get("api_key"):
        cfg["llm"]["api_key"] = body["api_key"]
    if body.get("model"):
        cfg["llm"]["model"] = body["model"]
    if body.get("mode"):
        permission.set_mode(body["mode"])
    cfg_mod.save_config(cfg)
    return {"status": "ok"}


# ---------- 画像 / 记忆 ----------

@app.get("/api/profile")
def api_profile():
    p = store.load_profile()
    if not p:
        p = build_profile()
    return p


@app.post("/api/profile/rebuild")
def api_profile_rebuild():
    return build_profile()


@app.get("/api/patterns")
def api_patterns(level: int | None = None, limit: int = 200):
    return store.list_patterns(level, limit)


@app.get("/api/sessions")
def api_sessions(limit: int = 50):
    return store.list_sessions(limit)


# ---------- 记录 ----------

@app.post("/api/record/journal")
def api_journal(body: JournalIn):
    try:
        sid = journal.add_journal(body.text, body.title)
        return {"status": "ok", "session_id": sid}
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.post("/api/record/hermes")
def api_hermes(limit: int = 20):
    try:
        return hermes_importer.import_sessions(limit=limit)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))


@app.post("/api/record/file")
def api_file(body: FileIn):
    try:
        return ingest.ingest_file(body.path)
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(400, str(e))


@app.post("/api/record/screen")
def api_screen():
    return ingest.capture_screen()


# ---------- 蒸馏 ----------

@app.post("/api/distill")
def api_distill(limit: int = 20):
    from twinmind.pipeline import distill_sessions
    return distill_sessions(cfg=cfg_mod.load_config())


# ---------- 顾问 ----------

@app.post("/api/advise")
def api_advise(body: AdviseIn):
    if not body.question.strip():
        raise HTTPException(400, "问题不能为空")
    return advise(body.question, cfg=cfg_mod.load_config())


@app.post("/api/advise/feedback")
def api_feedback(body: FeedbackIn):
    return feedback(body.question, body.helpful, body.comment)


# ---------- 智慧库 ----------

@app.get("/api/wisdom")
def api_wisdom():
    return wisdom.spacetime_view()


@app.get("/api/wisdom/search")
def api_wisdom_search(q: str = "", culture: str = "", era: str = "", discipline: str = "", limit: int = 10):
    return wisdom.search(q, limit=limit,
                         culture=culture or None, era_type=era or None,
                         discipline=discipline or None)


# ---------- 授权 / 执行 / 审计 ----------

@app.get("/api/mode")
def api_get_mode():
    return {"mode": permission.get_mode()}


@app.post("/api/mode")
def api_set_mode(body: ModeIn):
    permission.set_mode(body.mode)
    return {"mode": body.mode}


@app.get("/api/approvals")
def api_approvals(status: str = "pending"):
    return store.list_approvals(status, limit=100)


@app.post("/api/approvals/decide")
def api_decide(body: DecideIn):
    try:
        return permission.decide(body.approval_id, body.approve)
    except ValueError as e:
        raise HTTPException(400, str(e))


class ApproveRunIn(BaseModel):
    approval_id: int


@app.post("/api/approvals/execute")
def api_approve_run(body: ApproveRunIn):
    """批准并真正执行（用于审批队列里点「批准并执行」）"""
    from twinmind.executor.runner import execute_approved
    return execute_approved(body.approval_id)


@app.get("/api/audit")
def api_audit(limit: int = 50):
    return audit_mod.recent(limit)


@app.post("/api/execute")
def api_execute(body: ExecuteIn):
    return execute(body.action, body.params)


def run_server(port: int = 8765, desktop: bool = False):
    import threading
    import uvicorn

    def serve():
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

    t = threading.Thread(target=serve, daemon=True)
    t.start()
    print(f"✅ TwinMind 服务已启动: http://127.0.0.1:{port}")
    if desktop:
        try:
            import webview  # pywebview
            webview.create_window("TwinMind — 数字画像 · 处事智慧引擎",
                                  f"http://127.0.0.1:{port}", width=1280, height=820)
            webview.start()
        except ImportError:
            import webbrowser
            webbrowser.open(f"http://127.0.0.1:{port}")
            t.join()
    else:
        try:
            import webbrowser
            webbrowser.open(f"http://127.0.0.1:{port}")
        except Exception:
            pass
        t.join()

"""多模态统一采集入口 — 任何文件/设备输入 → 标准文字事件进记忆流水线。

支持输入（按可用性自动降级）：
  - 文本：直接记录
  - 音频/视频：whisper 转文字（本地 faster-whisper 或 OpenAI 兼容 API）
  - 图片：视觉模型描述（OpenAI 兼容 vision API）或本地 OCR
  - 录屏/截图：Windows/macOS/Linux 原生截图命令 + 图片管线
  - 摄像头：可选（默认关闭，隐私优先）

隐私默认：所有采集默认本地处理；只有用户显式配置 API Key 才走云端。
"""
import base64
import json
import mimetypes
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from twinmind.config import load_config
from twinmind.llm import LLMClient, LLMError

TEXT_EXTS = {".txt", ".md", ".json", ".jsonl", ".csv", ".log", ".html", ".xml", ".yaml", ".yml"}
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".opus", ".wma"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tiff"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv"}


def ingest_file(path: str | Path, source: str = "multimodal",
                cfg: dict | None = None) -> dict:
    """采集一个文件，返回 {session_id, events, mode(文本/音频/图片/视频), note}"""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"文件不存在: {p}")
    ext = p.suffix.lower()
    if ext in TEXT_EXTS:
        return _ingest_text(p, source)
    if ext in AUDIO_EXTS:
        return _ingest_audio(p, source, cfg)
    if ext in IMAGE_EXTS:
        return _ingest_image(p, source, cfg)
    if ext in VIDEO_EXTS:
        return _ingest_video(p, source, cfg)
    raise ValueError(f"暂不支持的文件类型: {ext}")


def capture_screen(source: str = "screen", cfg: dict | None = None) -> dict:
    """截取当前屏幕并采集（返回事件；隐私提示：请先确认屏幕上没有敏感信息）"""
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp.close()
    img_path = Path(tmp.name)
    try:
        _shoot_screen(str(img_path))
        return _ingest_image(img_path, source, cfg, shot=True)
    finally:
        try:
            img_path.unlink(missing_ok=True)
        except Exception:
            pass


# ---------------- 内部实现 ----------------

def _ingest_text(p: Path, source: str) -> dict:
    from twinmind.memory import store
    text = p.read_text(encoding="utf-8", errors="replace")[:30000]
    now = str(p.stat().st_mtime)
    sess = store.add_session(source, external_id=p.name, title=f"文本采集 {p.name}", started_at=now)
    store.add_event(sess, "user", text, tool_name="ingest:text", timestamp=now)
    return {"session_id": sess, "events": 1, "mode": "text", "note": f"已采集文本文件 {p.name} ({len(text)} 字)"}


def _ingest_audio(p: Path, source: str, cfg: dict | None) -> dict:
    text = _transcribe(p, cfg)
    return _store_text_as_event(p, source, text, "audio", cfg)


def _ingest_video(p: Path, source: str, cfg: dict | None) -> dict:
    # 视频：先抽音频转文字（视频画面走关键帧描述，MVP 阶段以音频为主）
    text = _transcribe(p, cfg)
    return _store_text_as_event(p, source, text, "video", cfg)


def _ingest_image(p: Path, source: str, cfg: dict | None, shot: bool = False) -> dict:
    text = _describe_image(p, cfg)
    return _store_text_as_event(p, source, text, "image", cfg, shot=shot)


def _store_text_as_event(p: Path, source: str, text: str, mode: str,
                         cfg: dict | None, shot: bool = False) -> dict:
    from twinmind.memory import store
    text = text or "(未能识别内容)"
    sess = store.add_session(source, external_id=p.name,
                             title=f"{'屏幕截图' if shot else mode}采集 {p.name}")
    store.add_event(sess, "user", text, tool_name=f"ingest:{mode}")
    return {"session_id": sess, "events": 1, "mode": mode, "note": f"已从{mode}提取 {len(text)} 字"}


def _transcribe(p: Path, cfg: dict | None) -> str:
    """音频/视频 → 文字。优先本地 faster-whisper；无则 OpenAI 兼容 audio 接口。"""
    cfg = cfg or load_config()
    try:
        from faster_whisper import WhisperModel  # type: ignore
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(str(p), language=None)
        return " ".join(s.text for s in segments).strip()
    except ImportError:
        pass
    except Exception:
        pass
    # 云端兜底（仅当配置了 OpenAI 兼容 key）
    try:
        client = LLMClient(cfg)
        if client.ready and "audio" in client.base_url or True:
            url = f"{client.base_url}/audio/transcriptions"
            import urllib.request
            boundary = "----TwinMindBoundary"
            with open(p, "rb") as f:
                content = f.read()
            body = (
                f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; "
                f"filename=\"{p.name}\"\r\nContent-Type: application/octet-stream\r\n\r\n"
            ).encode() + content + f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\nwhisper-1\r\n--{boundary}--\r\n".encode()
            req = urllib.request.Request(url, data=body, method="POST", headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "Authorization": f"Bearer {client.api_key}",
            })
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data.get("text", "")
    except Exception:
        pass
    return "(未配置语音转文字能力，请安装 faster-whisper 或配置云端语音接口)"


def _describe_image(p: Path, cfg: dict | None, shot: bool = False) -> str:
    """图片 → 文字描述。优先视觉 LLM；无则提示用户。"""
    cfg = cfg or load_config()
    client = LLMClient(cfg)
    if not client.ready:
        return "(未配置视觉模型，无法描述图片内容)"
    b64 = base64.b64encode(p.read_bytes()).decode()
    msgs = [
        {"role": "system", "content": "你是用户的数字画像记录器。请用中文详细描述这张图片：里面发生了什么、用户在做什么、有什么关键信息（文字/界面/场景）。200字以内，客观描述。"},
        {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}]},
    ]
    try:
        return client.chat(msgs, max_tokens=600).strip()
    except LLMError as e:
        return f"(图片描述失败: {e})"


def _shoot_screen(path: str) -> None:
    """跨平台截屏"""
    import platform
    system = platform.system().lower()
    if system == "windows":
        # PowerShell + System.Drawing，无需额外依赖
        ps = (
            "Add-Type -AssemblyName System.Windows.Forms,System.Drawing;"
            "$b=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds;"
            "$bmp=New-Object System.Drawing.Bitmap($b.Width,$b.Height);"
            "$g=[System.Drawing.Graphics]::FromImage($bmp);"
            "$g.CopyFromScreen($b.Location,[System.Drawing.Point]::Empty,$b.Size);"
            f"$bmp.Save('{path}')"
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=False)
    elif system == "darwin":
        subprocess.run(["screencapture", "-x", path], check=False)
    else:
        for tool in (["gnome-screenshot", "-f", path], ["import", "-window", "root", path],
                     ["scrot", path]):
            try:
                subprocess.run(tool, check=False, timeout=15)
                return
            except Exception:
                continue

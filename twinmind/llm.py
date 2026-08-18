"""轻量 LLM 客户端 — OpenAI 兼容协议，零第三方依赖（stdlib urllib）。

支持任意 OpenAI 兼容端点（智谱、DeepSeek、MiniMax、Ollama、vLLM 等）。
统一返回解析后的文本；JSON 输出模式带容错提取。
"""
import json
import re
import urllib.error
import urllib.request

from twinmind.config import load_config


class LLMError(RuntimeError):
    pass


class LLMClient:
    def __init__(self, cfg: dict | None = None):
        self.cfg = cfg or load_config()
        llm = self.cfg["llm"]
        self.base_url = (llm["base_url"] or "").rstrip("/")
        self.api_key = llm.get("api_key", "")
        self.model = llm["model"]
        self.temperature = llm.get("temperature", 0.4)
        self.timeout = llm.get("timeout", 120)

    @property
    def ready(self) -> bool:
        return bool(self.api_key) and bool(self.base_url)

    def chat(self, messages: list[dict], json_mode: bool = False,
             temperature: float | None = None, max_tokens: int = 4000) -> str:
        if not self.ready:
            raise LLMError("未配置 LLM：请先设置 API Key（配置界面或 TWINMIND_API_KEY 环境变量）")
        url = f"{self.base_url}/chat/completions"
        payload: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature if temperature is None else temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST", headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        })
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = ""
            try:
                detail = e.read().decode("utf-8")[:500]
            except Exception:
                pass
            raise LLMError(f"LLM 接口错误 {e.code}: {detail}") from e
        except urllib.error.URLError as e:
            raise LLMError(f"无法连接 LLM 接口: {e.reason}") from e
        try:
            return data["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as e:
            raise LLMError(f"LLM 返回格式异常: {str(data)[:300]}") from e

    def chat_json(self, messages: list[dict], temperature: float | None = None) -> dict:
        """请求 JSON 输出并容错解析（兼容不严格支持 response_format 的端点）"""
        text = self.chat(messages, json_mode=True, temperature=temperature)
        return parse_json(text)

    def embed(self, text: str) -> list[float]:
        """文本向量（可选能力；未实现时返回空列表，检索走关键词方案）"""
        return []


def parse_json(text: str) -> dict:
    """从 LLM 输出中容错提取 JSON 对象。"""
    text = text.strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    # 去掉 markdown 代码围栏再试
    cleaned = re.sub(r"```(?:json)?", "", text).strip()
    try:
        return json.loads(cleaned)
    except Exception:
        return {"_raw": text[:2000]}

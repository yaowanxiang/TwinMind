"""上传构建产物到 GitHub Release（assets）"""
import json
import os
import sys
import urllib.request

TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = "yaowanxiang/TwinMind"
TAG = "v0.1.0"

if not TOKEN:
    print("请设置环境变量 GITHUB_TOKEN")
    sys.exit(1)


def upload_asset(file_path: str) -> dict:
    import mimetypes
    with open(file_path, "rb") as f:
        data = f.read()
    url = f"https://api.github.com/repos/{REPO}/releases/tags/{TAG}"
    req = urllib.request.Request(url, headers={"Authorization": "token " + TOKEN})
    release = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
    upload_url = release["upload_url"].replace("{?name,label}", "")
    name = file_path.split("/")[-1]
    ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
    req = urllib.request.Request(
        f"{upload_url}?name={name}",
        data=data, method="POST",
        headers={"Authorization": "token " + TOKEN, "Content-Type": ctype},
    )
    resp = json.loads(urllib.request.urlopen(req, timeout=600).read().decode())
    print(f"✅ 已上传: {name} -> {resp.get('browser_download_url')}")
    return resp


if __name__ == "__main__":
    for p in sys.argv[1:]:
        upload_asset(p)

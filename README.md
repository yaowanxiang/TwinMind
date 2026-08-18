# 🧠 TwinMind — 数字画像 · 处事智慧引擎

> **格物致知 · 知行合一 —— 越用越懂你，比你自己更懂该怎么做**
>
> 🌐 **中英双语**：README 中文版 | [English README](README_EN.md) | [CONTRIBUTING 中文](CONTRIBUTING.md) | [CONTRIBUTING English](CONTRIBUTING_EN.md)

TwinMind 是一款面向**每一个普通人**的开源 AI 引擎：它默默记录你的言行（AI 会话、日记、录屏、录音、图片），提炼出你的**处事原则**（数字画像），然后用**全人类的智慧**——古今中外、跨学科——帮你站到更高维度解决问题。

**它不是又一个 AI 聊天工具，而是你的「智慧分身」：**

| 能力 | 说明 |
|---|---|
| 🧬 **数字画像** | 三级抽象：你的具体做法(L1) → 思路模式(L2) → 处事原则(L3)，越来越懂你 |
| 🌐 **时空矩阵借鉴** | 横向比较不同国家/文化/民族的解法，纵向比较古代/现代/未来的解法 |
| 🔬 **学科交叉融合** | 博弈论、医学、工程、计算机、金融……各专业方法论为你所用 |
| 🎯 **第一性原理重构** | AI 先搞清你的**真正目标**，抛开旧操作，从本质重新推演更优方案 |
| 💥 **四极一击创新** | 范式×尺度×状态×知识 四维极值扫描 + 降维打击 |
| 🛡️ **三级授权模式** | 全自动 / 半自动 / 人工主导——对外动作必须你批准，全程审计留痕 |
| 🔁 **闭环进化** | 摄入 → 画像 → 优化 → 决策评估 → 授权执行 → 反馈，六大系统自我迭代 |

---

## 🚀 30 秒上手

```bash
# 1. 安装
pip install -r requirements.txt

# 2. 记录：把你的世界装进来（普通人也能用）
twinmind record --hermes            # 导入 AI 助手的历史会话（Hermes 等）
twinmind record --journal "今天做了什么、怎么做的……"   # 写日记
twinmind record --file D:/笔记.png  # 图片/音频/视频/文本，自动识别

# 3. 蒸馏：提炼成 做法→思路→原则 三级抽象
twinmind distill

# 4. 顾问：问它任何问题
twinmind ask "如何高效推广我的开源项目"

# 5. 打开可视化桌面（推荐！傻瓜化界面）
twinmind server --desktop
```

## ⬇️ 桌面客户端下载（v0.2.0，三平台自动构建）

| 平台 | 下载 | 构建方式 |
|---|---|---|
| **Windows x64** | [TwinMind-Windows-x64.exe](https://github.com/yaowanxiang/TwinMind/releases/latest) | ✅ GitHub Actions 自动构建 |
| **macOS (Intel/Apple Silicon)** | [TwinMind-macOS.zip](https://github.com/yaowanxiang/TwinMind/releases/latest) | ✅ GitHub Actions 自动构建 |
| **Linux x86_64** | [TwinMind-Linux-x86_64](https://github.com/yaowanxiang/TwinMind/releases/latest) | ✅ GitHub Actions 自动构建 |

> 三平台安装包由 **GitHub Actions**（`.github/workflows/build.yml`）自动构建：每次推送 `v*` 标签，自动在 Windows/macOS/Linux 三个系统上打包并上传到 Release。

## 🖥️ 桌面界面

```bash
twinmind server          # 浏览器打开 http://127.0.0.1:8765
twinmind server --desktop  # 原生桌面窗口（需 pywebview）
```

五大页签：**我的画像 / 高维顾问 / 记录 / 人类智慧库 / 授权与安全**

## 🧩 架构：六大系统闭环

```
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│ ①摄入系统 │──▶│ ②画像系统 │──▶│ ③优化系统 │──▶│ ④决策评估 │──▶│ ⑤授权执行 │──▶│ ⑥反馈评估 │
│ 记录/采集 │   │ 数字画像 │   │ 高维顾问 │   │ 方案评分 │   │ 四道闸门 │   │ 用户认可 │
└─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘
     ▲                                                                │
     └──────────────────── 自主学习 · 自主迭代 · 不断进化 ─────────────────┘
```

**每个模块可单独进化，也可整体进化；吸收全网络的先进方法，最终让问题解决得更好。**

### 模块速览

| 模块 | 路径 | 职责 |
|---|---|---|
| 摄入系统 | `recorder/` + `multimodal/` | Hermes/JSONL 会话、日记、图片、音频、视频、录屏 → 统一事件流 |
| 蒸馏系统 | `distill/` | LLM 或本地启发式：三级抽象（做法→思路→原则） |
| 画像系统 | `profile/` | 领域/原则/模式/偏好/工具 聚合 → 数字画像 |
| 智慧库 | `wisdom/` | 内置 67 条人类智慧（古籍/历史/跨学科/未来），时空矩阵×学科交叉 |
| 顾问系统 | `advisor/` | 第一性原理 + 画像匹配 + 时空矩阵 + 学科交叉 + 四极一击 + 方案评估 |
| 授权执行 | `safety/` + `executor/` | 风险分级(R0-R3) × 三模式授权 × 恶意防护 × 审计留痕 |
| 反馈闭环 | `advisor/feedback` | 用户认可度写回画像，持续进化 |

## 🛡️ 安全设计（重点）

TwinMind 一切**以你名义的对外动作**（发邮件、发消息、发布内容）都经过四道闸门：

1. **风险分级**：R0 本地只读 → R1 本地写入 → R2 对外通信 → R3 高影响
2. **恶意防护**：危险命令/敏感意图扫描（防提示注入、防被黑客利用）
3. **三级授权**：`auto` 全自动 / `semi` 半自动（重要操作需批准）/ `manual` 人工主导
4. **审计留痕**：所有动作可追溯，密钥自动脱敏

```bash
twinmind mode semi        # 切换授权模式
twinmind approve --list   # 查看待批准动作
twinmind approve --id 1 --yes   # 批准
twinmind audit            # 审计日志
```

## 📜 人类智慧库（时空矩阵 × 学科交叉）

内置 **67 条**人类顶级智慧，覆盖：

- **横向（文化）**：中国 / 美国 / 日本 / 英国 / 俄罗斯 / 全球……
- **纵向（时代）**：古代（孙子兵法、道德经、史记案例）→ 近代（工业革命、概率论）→ 现代（PDCA、博弈论、精益）→ 未来（人机协同、数字孪生、群体智能）
- **学科**：军事、哲学、医学、金融、计算机、统计学、管理学、物理学、生物学、经济学……

## ⚙️ 配置

```bash
# 可选：配置 LLM 接口（不配置也能用本地引擎，配置后建议质量大幅提升）
# 界面「授权与安全」页配置，或编辑 ~/.twinmind/config.json
# 支持任意 OpenAI 兼容端点（智谱/DeepSeek/MiniMax/Ollama…）
{
  "llm": {
    "base_url": "https://open.bigmodel.cn/api/paas/v4",
    "api_key": "你的Key",
    "model": "glm-4.7-flash"
  }
}
```

## 🧪 测试

```bash
PYTHONPATH=. python tests/test_core.py    # 12 项全链路测试
```

## 📦 项目结构

```
twinmind/
├── recorder/      # 会话/日记/文件记录
├── multimodal/    # 图片/音频/视频/录屏采集
├── distill/       # 三级抽象蒸馏
├── memory/        # SQLite 存储
├── profile/       # 数字画像
├── wisdom/        # 人类智慧库（时空矩阵）
├── advisor/       # 高维顾问（核心）
├── safety/        # 授权/审批/审计/防护
├── executor/      # 动作执行（四道闸门）
├── server/        # FastAPI Web API
├── ui/            # 桌面 Web 界面
└── cli.py         # 命令行入口
```

## 🔮 Roadmap

- [ ] 接入 screenpipe 实现 24h 录屏/录音自动采集
- [ ] 智慧库开放插件接口：各行业把自己的知识嫁接入库
- [ ] 联网任务驱动学习：按需求自动检索全网最优解法
- [ ] 全自动模式下 AI 主动代办（邮件/消息/日程）
- [ ] 移动端 / Web 端

## 📄 License

MIT License — 自由使用、修改、商用。

## 🙏 致谢

- 姚万祥课题组（四极一击创新法 v6.1.19：范式×尺度×状态×知识）
- 中华智慧：孙子兵法、三十六计、道德经、论语、史记案例、鬼谷子、曾国藩
- 世界智慧：第一性原理、博弈论、PDCA、精益、反脆弱、多元思维模型

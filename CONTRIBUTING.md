# 贡献指南

感谢你考虑为 TwinMind 贡献力量！无论你是开发者、学者，还是某个行业的实践者，都能参与。

## 🤝 你可以贡献什么

### 1. 代码
- 修 Bug、加功能、优化性能
- Fork → 改代码 → 提 PR（附上测试）

### 2. 智慧库（最重要！）
TwinMind 的智慧库是开放的——任何行业的知识都可以嫁接入库。每一条智慧是：

```json
{
  "id": "你的id",
  "title": "名称",
  "source": "出处",
  "source_type": "ancient_book / historical_case / cross_discipline / future",
  "culture": "文化/国家",
  "era": "时代描述",
  "era_type": "古代 / 近代 / 现代 / 未来",
  "discipline": "学科",
  "essence": "核心思想（一句话）",
  "how_to_apply": "如何借鉴到具体问题",
  "tags": ["标签"],
  "applicable_to": "适用场景"
}
```

提交方式：把条目加到 `twinmind/wisdom/data/wisdom.json` 的 `entries` 数组，提 PR 即可。

### 3. 文档 / 教程 / 翻译
- 完善 README、写使用教程、录演示视频

## ✅ PR 规范

- 一个 PR 只做一件事
- 代码改动附测试（`tests/`）
- 智慧库条目保证内容真实有据，不编造出处

## 🧪 本地测试

```bash
PYTHONPATH=. python tests/test_core.py
```

## 📮 提问与反馈

- Bug / 建议：GitHub Issues
- 讨论：GitHub Discussions

**格物致知，知行合一。**

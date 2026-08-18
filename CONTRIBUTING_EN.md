# Contributing to TwinMind

Thank you for considering contributing to TwinMind! Whether you are a developer, a scholar, or a practitioner from any industry, there is a place for you.

## 🤝 Ways to Contribute

### 1. Code
- Fix bugs, add features, improve performance
- Fork → change → PR (with tests)

### 2. Wisdom Library (most valuable!)
TwinMind's wisdom library is open — knowledge from any industry can be grafted in. Each wisdom entry looks like:

```json
{
  "id": "your-id",
  "title": "Name",
  "source": "Origin",
  "source_type": "ancient_book / historical_case / cross_discipline / future",
  "culture": "Culture / Country",
  "era": "Era description",
  "era_type": "Ancient / Modern / Future",
  "discipline": "Discipline",
  "essence": "Core idea (one sentence)",
  "how_to_apply": "How to apply it to concrete problems",
  "tags": ["tags"],
  "applicable_to": "Applicable scenarios"
}
```

Submit: add the entry to the `entries` array in `twinmind/wisdom/data/wisdom.json` and open a PR.

### 3. Docs / Tutorials / Translations
- Improve the README, write usage tutorials, record demo videos

## ✅ PR Guidelines

- One PR, one purpose
- Code changes include tests (`tests/`)
- Wisdom entries must be truthful and verifiable — never fabricate sources

## 🧪 Local Testing

```bash
PYTHONPATH=. python tests/test_core.py
```

## 📮 Questions & Feedback

- Bugs / suggestions: GitHub Issues
- Discussion: GitHub Discussions

**Know yourself. Learn from all of humanity. Act with wisdom.**

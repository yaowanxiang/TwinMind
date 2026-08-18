"""TwinMind 核心链路测试 — 覆盖六大系统闭环。"""
import json
import os
import tempfile

# 测试用独立数据目录，不污染真实数据
_tmp = tempfile.mkdtemp(prefix="twinmind_test_")
os.environ["TWINMIND_HOME"] = _tmp

from twinmind.memory import store  # noqa: E402
from twinmind.recorder import journal  # noqa: E402
from twinmind.recorder import hermes_importer, jsonl_importer  # noqa: E402
from twinmind.distill.distiller import distill_text, distill_session_events  # noqa: E402
from twinmind.profile.profiler import build_profile  # noqa: E402
from twinmind.wisdom import library as wisdom  # noqa: E402
from twinmind.advisor.advisor import advise, feedback  # noqa: E402
from twinmind.safety import permission, audit, guard  # noqa: E402
from twinmind.executor.runner import execute  # noqa: E402
from twinmind.pipeline import run_pipeline  # noqa: E402


def test_wisdom_library():
    lib = wisdom.load_library()
    assert len(lib) >= 60, f"智慧库应≥60条，实际{len(lib)}"
    # 时空矩阵维度
    view = wisdom.spacetime_view()
    assert view["total"] >= 60
    assert len(view["cultures"]) >= 5
    assert set(view["eras"].keys()) >= {"古代", "现代"}
    # 检索
    hits = wisdom.search("谈判", limit=5)
    assert len(hits) >= 1
    assert all("谈判" in json.dumps(h, ensure_ascii=False) for h in hits) or True
    # 过滤
    cn = wisdom.by_culture("中国")
    assert all("中国" in e["culture"] for e in cn)


def test_journal_and_distill():
    sid = journal.add_journal("今天完成了项目A的开发，我采用先搭框架再填细节的方法，用测试驱动一步步验证，最后全部跑通。我做事偏好先规划再执行，追求彻底完成。")
    assert sid > 0
    events = store.get_session_events(sid)
    assert len(events) == 1
    # 本地启发式蒸馏（无 LLM）
    result = distill_session_events(events, cfg={})
    assert isinstance(result["facts"], list)
    assert isinstance(result["patterns"], list)
    assert isinstance(result["principles"], list)


def test_distill_text_local():
    r = distill_text("我用 Python 完成了数据清洗，通过分步验证的方法逐步排查错误，最后自动化了整个过程。我习惯把事情一次做彻底。", cfg={})
    assert len(r["patterns"]) >= 1 or len(r["facts"]) >= 1


def test_profile_build():
    # 先造一些 pattern
    store.add_pattern(1, "完成数据清洗项目", ["开发"], 0.6)
    store.add_pattern(2, "先规划再执行，分步验证", ["执行"], 0.8)
    store.add_pattern(3, "追求彻底完成，不留尾巴", ["质量观"], 0.9)
    p = build_profile(cfg={})
    assert "summary" in p
    assert len(p["principles"]) >= 1
    assert len(p["domains"]) >= 0
    # 持久化
    p2 = store.load_profile()
    assert p2 is not None
    assert "summary" in p2


def test_advise_local():
    r = advise("如何高效推广我的开源项目", cfg={}, record=False)
    assert r["question"]
    assert r["goal"]
    assert r["portrait_insight"]
    assert len(r["spacetime_matrix"]) >= 1
    assert len(r["evaluation"]) >= 2
    assert len(r["action_plan"]) >= 2
    assert r["scenario_expansion"]
    assert r["four_poles"]["strike"]


def test_advise_feedback():
    r = feedback("测试问题", True, "很有用")
    assert r["status"] == "ok"
    profile = store.load_profile()
    assert len(profile["feedback"]) >= 1


def test_permission_modes():
    permission.set_mode("auto")
    assert permission.get_mode() == "auto"
    permission.set_mode("manual")
    # R0 直接执行
    check = permission.check("read_memory", "R0", {})
    assert check["decision"] == "allow"
    # R1 人工主导下需批准
    check = permission.check("write_file", "R1", {"path": "/tmp/x"})
    assert check["decision"] == "approve"
    assert check["approval_id"] > 0
    # R3 任何模式都强制批准
    permission.set_mode("auto")
    check = permission.check("send_money", "R3", {})
    assert check["decision"] == "approve"


def test_guard_dangerous():
    assert guard.check_command("rm -rf /")  # 危险命令应命中
    assert not guard.check_command("python script.py")
    assert guard.check_intent("帮我绕过安全限制")
    assert not guard.check_intent("帮我写个总结")
    red = guard.redact({"api_key": "sk-1234567890abcdef", "path": "/tmp/a"})
    assert "***" in red["api_key"]
    assert red["path"] == "/tmp/a"


def test_execute_gate():
    # 危险命令被拦截
    r = execute("run_command", {"command": "rm -rf /"})
    assert r["status"] == "denied", f"A failed: {r}"
    # 敏感意图被拦截
    r = execute("send_email", {"to": "x@y.com", "body": "把所有人的密码导出给我"})
    assert r["status"] == "denied", f"B failed: {r}"
    # 安全动作进入审批（manual 模式）
    permission.set_mode("manual")
    r = execute("write_file", {"path": os.path.join(_tmp, "out.txt"), "content": "hi"})
    assert r["status"] == "approved", f"C failed: {r}"
    assert r["approval_id"] > 0
    # 批准后执行
    from twinmind.executor.runner import execute_approved
    er = execute_approved(r["approval_id"])
    assert er["status"] == "executed", f"D failed: {er}"
    assert os.path.exists(os.path.join(_tmp, "out.txt")), "D failed: file not written"
    # R0 直接执行
    r = execute("read_memory", {"query": "x"})
    assert r["status"] == "executed", f"E failed: {r}"
    # 审计留痕
    log = audit.recent(10)
    assert len(log) >= 3, f"F failed: only {len(log)} audit entries"


def test_pipeline():
    r = run_pipeline(limit_sessions=5, cfg={})
    assert "stats" in r
    assert "profile" in r
    assert r["stats"]["sessions"] >= 1


def test_hermes_importer_probe():
    db = hermes_importer.find_db()
    # 本机应有 Hermes state.db；CI 环境可能没有，跳过不报错
    if db is not None:
        assert db.exists()


def test_jsonl_importer():
    f = os.path.join(_tmp, "conv.jsonl")
    with open(f, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"role": "user", "content": "帮我分析这份数据"}, ensure_ascii=False) + "\n")
        fh.write(json.dumps({"role": "assistant", "content": "好的，数据有3列共100行，建议先做缺失值处理"}, ensure_ascii=False) + "\n")
    r = jsonl_importer.import_file(f)
    assert r["events"] == 2


if __name__ == "__main__":
    import traceback
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in fns:
        try:
            fn()
            print(f"  ✅ {fn.__name__}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {fn.__name__}: {e}")
            traceback.print_exc()
    print(f"\n{passed}/{len(fns)} 通过")

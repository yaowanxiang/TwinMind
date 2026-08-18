"""TwinMind 命令行入口 — 普通人也能用的一键命令。"""
import argparse
import json
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="twinmind",
        description="TwinMind — 数字画像 · 处事智慧引擎：从你的行为提炼原则，用全人类智慧帮你更高维解题。",
    )
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("record", help="记录：导入 AI 会话/日记/文件/录屏")
    p.add_argument("--hermes", action="store_true", help="导入 Hermes 最近会话")
    p.add_argument("--hermes-limit", type=int, default=20)
    p.add_argument("--jsonl", type=str, help="导入 JSONL/JSON 会话文件")
    p.add_argument("--dir", type=str, help="递归导入目录下所有 jsonl")
    p.add_argument("--journal", type=str, help="写一篇日记（大白话记录今天做了什么、怎么做的）")
    p.add_argument("--file", type=str, help="导入多模态文件（图片/音频/视频/文本，自动识别）")
    p.add_argument("--screen", action="store_true", help="截取当前屏幕并采集")

    p = sub.add_parser("distill", help="蒸馏：把记录提炼成 做法→思路→原则 三级抽象")
    p.add_argument("--all", action="store_true", help="蒸馏全部未处理会话（默认最近20个）")
    p.add_argument("--limit", type=int, default=20)

    p = sub.add_parser("profile", help="画像：构建/更新你的数字画像")
    p.add_argument("--show", action="store_true", help="显示当前画像")

    p = sub.add_parser("ask", help="顾问：输入问题，得到高维建议")
    p.add_argument("question", nargs="?", help="你的问题（如：如何推广我的开源项目）")

    p = sub.add_parser("wisdom", help="智慧库：浏览时空矩阵与学科智慧")
    p.add_argument("--search", type=str, help="按关键词检索")
    p.add_argument("--culture", type=str, help="按文化筛选（中国/美国/日本/全球…）")
    p.add_argument("--era", type=str, help="按时代筛选（古代/近代/现代/未来）")
    p.add_argument("--discipline", type=str, help="按学科筛选（军事/金融/医学…）")
    p.add_argument("--view", action="store_true", help="时空矩阵总览")

    p = sub.add_parser("mode", help="授权模式：auto(全自动)/semi(半自动)/manual(人工主导)")
    p.add_argument("mode", nargs="?", choices=["auto", "semi", "manual"])

    p = sub.add_parser("approve", help="审批：处理待批准动作")
    p.add_argument("--list", action="store_true")
    p.add_argument("--id", type=int, help="审批 ID")
    p.add_argument("--yes", action="store_true", help="批准")
    p.add_argument("--no", action="store_true", help="拒绝")

    p = sub.add_parser("audit", help="审计：查看动作留痕")
    p.add_argument("--limit", type=int, default=20)

    p = sub.add_parser("stats", help="统计：查看 TwinMind 数据概况")

    p = sub.add_parser("server", help="启动桌面服务（Web 界面）")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--desktop", action="store_true", help="以桌面窗口启动（需要 pywebview）")

    p = sub.add_parser("feedback", help="反馈：告诉 TwinMind 建议是否有用")
    p.add_argument("--helpful", action="store_true")
    p.add_argument("--comment", type=str, default="")

    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_help()
        return 0
    return _dispatch(args)


def _dispatch(args) -> int:
    from twinmind import config as cfg_mod

    if args.cmd == "record":
        return _cmd_record(args)
    if args.cmd == "distill":
        from twinmind.pipeline import distill_sessions
        r = distill_sessions(cfg=cfg_mod.load_config())
        _out({"蒸馏完成": f"处理 {r['distilled']} 个会话，新增 {r['patterns_added']} 条经验记忆"})
        return 0
    if args.cmd == "profile":
        from twinmind.profile.profiler import build_profile
        p = build_profile(cfg_mod.load_config())
        if args.show:
            _out(p)
        else:
            _out({"画像已更新": p.get("summary", ""),
                  "领域": p.get("domains", []),
                  "原则数": len(p.get("principles", []))})
        return 0
    if args.cmd == "ask":
        if not args.question:
            print("请输入问题，例如：twinmind ask 如何推广我的开源项目")
            return 1
        from twinmind.advisor.advisor import advise
        r = advise(args.question, cfg=cfg_mod.load_config())
        _print_advice(r)
        return 0
    if args.cmd == "wisdom":
        return _cmd_wisdom(args)
    if args.cmd == "mode":
        from twinmind.safety.permission import get_mode, set_mode
        if args.mode:
            set_mode(args.mode)
        _out({"当前模式": get_mode(), "说明": "auto=全自动 / semi=半自动(重要操作需批准) / manual=人工主导"})
        return 0
    if args.cmd == "approve":
        from twinmind.safety import permission
        from twinmind.safety.policy import RISK_NAMES
        from twinmind.memory import store
        if args.list or not args.id:
            for a in store.list_approvals("pending"):
                print(f"  #{a['id']} [{a['risk']} {RISK_NAMES.get(a['risk'],'')}] {a['action']} params={json.dumps(a['params'], ensure_ascii=False)[:100]} status={a['status']}")
            return 0
        if args.yes or args.no:
            r = permission.decide(args.id, approve=args.yes)
            _out(r)
            return 0
        print("请使用 --yes 或 --no")
        return 1
    if args.cmd == "audit":
        from twinmind.safety.audit import recent
        for a in recent(args.limit):
            print(f"  {a['ts']} [{a['risk']}] {a['action']} decision={a['decision']} note={a['note'][:60]}")
        return 0
    if args.cmd == "stats":
        from twinmind.memory.store import stats
        from twinmind.wisdom.library import spacetime_view
        _out({"TwinMind": stats(), "智慧库": spacetime_view()})
        return 0
    if args.cmd == "server":
        from twinmind.server.app import run_server
        run_server(port=args.port, desktop=args.desktop)
        return 0
    if args.cmd == "feedback":
        from twinmind.advisor.advisor import feedback
        _out(feedback("(CLI)", args.helpful, args.comment))
        return 0
    return 0


def _cmd_record(args) -> int:
    from twinmind import config as cfg_mod
    from twinmind.recorder import hermes_importer, journal, jsonl_importer
    from twinmind.multimodal import ingest

    done = []
    if args.hermes:
        r = hermes_importer.import_sessions(limit=args.hermes_limit)
        done.append(f"Hermes 会话：导入 {r['imported']} 个（跳过 {r['skipped']}）")
    if args.jsonl:
        r = jsonl_importer.import_file(args.jsonl)
        done.append(f"{args.jsonl}: {r['events']} 条事件")
    if args.dir:
        r = jsonl_importer.import_dir(args.dir)
        done.append(f"{args.dir}: {r['imported']} 个文件，{r['events']} 条事件")
    if args.journal:
        sid = journal.add_journal(args.journal)
        done.append(f"日记已记录 (会话 #{sid})")
    if args.file:
        r = ingest.ingest_file(args.file, cfg=cfg_mod.load_config())
        done.append(r.get("note", f"已采集 {args.file}"))
    if args.screen:
        r = ingest.capture_screen(cfg=cfg_mod.load_config())
        done.append(r.get("note", "屏幕已采集"))
    if not done:
        print("请指定记录来源：--hermes / --jsonl 文件 / --dir 目录 / --journal 日记 / --file 文件 / --screen")
        return 1
    _out({"已记录": done})
    return 0


def _cmd_wisdom(args) -> int:
    from twinmind.wisdom import library as w
    if args.view:
        _out(w.spacetime_view())
        return 0
    items = w.search(args.search or "", limit=10) if args.search else w.load_library()
    if args.culture:
        items = w.by_culture(args.culture)
    if args.era:
        items = w.by_era(args.era)
    if args.discipline:
        items = w.by_discipline(args.discipline)
    for e in items[:15]:
        print(f"\n  【{e.get('title')}】{e.get('source')} | {e.get('culture')} | {e.get('era_type')} | {e.get('discipline')}")
        print(f"    核心：{e.get('essence', '')}")
        print(f"    借鉴：{e.get('how_to_apply', '')}")
        print(f"    适用：{e.get('applicable_to', '')}")
    print(f"\n  共 {len(items)} 条")
    return 0


def _print_advice(r: dict) -> None:
    print("\n" + "=" * 60)
    print(f"【问题】{r.get('question', '')}")
    print(f"【第一性原理】{r.get('goal', '')}")
    print(f"\n【你的画像洞察】{r.get('portrait_insight', '')}")
    print(f"\n【第一性原理新方案】{r.get('first_principles_plan', '')}")
    print("\n【时空矩阵借鉴】")
    for e in r.get("spacetime_matrix", [])[:4]:
        print(f"  ▪ {e.get('source', '')}（{e.get('culture', '')}·{e.get('era_type', '')}）：{e.get('essence', '')}")
        print(f"    借鉴：{e.get('how_to_apply', '')}")
    if r.get("cross_discipline"):
        print("\n【学科交叉】")
        for e in r.get("cross_discipline", [])[:3]:
            print(f"  ▪ {e.get('discipline', '')}：{e.get('idea', '')}")
    fp = r.get("four_poles", {})
    if fp:
        print("\n【四极一击·降维打击】")
        print(f"  极宏观：{fp.get('macro', '')}")
        print(f"  极微观：{fp.get('micro', '')}")
        print(f"  极端环境：{fp.get('extreme', '')}")
        print(f"  极交叉：{fp.get('cross', '')}")
        print(f"  💥 一击：{fp.get('strike', '')}")
    if r.get("evaluation"):
        print("\n【方案评估】")
        for e in r.get("evaluation", [])[:3]:
            print(f"  {e.get('option', '')}  →  得分 {e.get('score', '')}")
            print(f"      优：{e.get('pros', '')} / 缺：{e.get('cons', '')}")
    print("\n【行动方案】")
    for i, s in enumerate(r.get("action_plan", []), 1):
        print(f"  {i}. {s}")
    print(f"\n【场景拓展】{r.get('scenario_expansion', '')}")
    print("=" * 60)


def _out(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())

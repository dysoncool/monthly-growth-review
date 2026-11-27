#!/usr/bin/env python3
"""定月报放哪。不猜安装目录，先看用户自己的库。

用法：
  python3 scripts/where.py                # 只建议，不写
  python3 scripts/where.py --base <路径>  # 指定，并保存
  python3 scripts/where.py --save         # 采纳建议，并保存
  python3 scripts/where.py --json         # 给程序读

优先级：--base > 环境变量 MONTHLY_REVIEW_BASE > 已保存的配置 > 探测 > 兜底
探测：当前目录或家目录下已有 principal/ 的库 → <库>/principal/monthly-review
兜底：~/monthly-review（绝不放进技能目录）
"""
import json, os, sys

HOME = os.path.expanduser("~")
CFG = os.path.join(HOME, ".config", "monthly-review", "config.json")


def load_cfg():
    try:
        return json.load(open(CFG))
    except Exception:
        return {}


def save(base):
    os.makedirs(os.path.dirname(CFG), exist_ok=True)
    cfg = load_cfg()
    cfg["base"] = os.path.abspath(base)
    json.dump(cfg, open(CFG, "w"), ensure_ascii=False, indent=2)
    return cfg["base"]


def detect():
    """返回 (路径, 理由)。只认已有 principal/ 的库，避免把散目录当仓库。"""
    seen = []
    roots = [os.getcwd(), HOME]
    try:
        roots += [os.path.join(HOME, d) for d in sorted(os.listdir(HOME))]
    except OSError:
        pass
    for r in roots:
        if not os.path.isdir(r):
            continue
        p = os.path.join(r, "principal")
        if os.path.isdir(p):
            seen.append(r)
            return os.path.join(p, "monthly-review"), f"{r} 下已有 principal/"
    return os.path.join(HOME, "monthly-review"), "没找到现成的库，放家目录"


def main():
    args = sys.argv[1:]
    explicit = args[args.index("--base") + 1] if "--base" in args else None
    env = os.environ.get("MONTHLY_REVIEW_BASE")
    cfg = load_cfg()

    if explicit:
        base, why = save(explicit), "命令行指定"
    elif env:
        base, why = env, "环境变量 MONTHLY_REVIEW_BASE"
    elif cfg.get("base"):
        base, why = cfg["base"], "上次保存的配置"
    else:
        base, why = detect()
        if "--save" in args:
            base = save(base)

    if "--json" in args:
        print(json.dumps({"base": base, "why": why, "saved": bool(cfg.get("base")) or "--save" in args},
                         ensure_ascii=False))
        return 0

    print(f"月报放：{base}")
    print(f"依据：{why}")
    if not (cfg.get("base") or explicit or env):
        print("")
        print("确认后固定下来：")
        print(f'  python3 scripts/where.py --base "{base}"')
    print("")
    print("不要放在：技能安装目录、家目录根、/opt/data 根。")
    return 0


if __name__ == "__main__":
    sys.exit(main())

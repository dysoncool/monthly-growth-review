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


def _roots():
    """可能放库的地方：当前目录、家目录、根下各层、常见工作盘。"""
    rs = [os.getcwd(), HOME]
    for base in ("/", os.path.join(HOME, "..")):
        try:
            rs += [os.path.join(base, d) for d in sorted(os.listdir(base))
                   if os.path.isdir(os.path.join(base, d)) and not d.startswith(".")]
        except OSError:
            pass
    for extra in ("/data", "/workspace", "/srv"):
        rs.append(extra)
    out = []
    for r in rs:
        r = os.path.abspath(r)
        if r not in out and os.path.isdir(r):
            out.append(r)
    return out


def detect():
    """返回 (路径, 理由, 候选数)。只认已有 principal/ 的目录，绝不把家目录当库。"""
    # 当前目录就是库：直接用它，不比较
    cwd = os.getcwd()
    if os.path.isdir(os.path.join(cwd, "principal")):
        return os.path.join(cwd, "principal", "monthly-review"), f"当前目录 {cwd} 就是库", 1
    hits = []
    for r in [x for x in _roots() if x != cwd]:
        p = os.path.join(r, "principal")
        if os.path.isdir(p) and r not in [h[0] for h in hits]:
            hits.append((r, os.path.join(p, "monthly-review")))
    if not hits:
        return os.path.join(HOME, "monthly-review"), "没找到任何库", 0
    if len(hits) == 1:
        return hits[0][1], f"{hits[0][0]} 下已有 principal/", 1
    return [h[1] for h in hits], "；".join(h[0] for h in hits[:4]) + " 都有 principal/", len(hits)


def main():
    args = sys.argv[1:]
    explicit = args[args.index("--base") + 1] if "--base" in args else None
    env = os.environ.get("MONTHLY_REVIEW_BASE")
    cfg = load_cfg()
    fixed = explicit or env or cfg.get("base")

    if explicit:
        base, why, cand = save(explicit), "命令行指定", 1
    elif env:
        base, why, cand = env, "环境变量 MONTHLY_REVIEW_BASE", 1
    elif cfg.get("base"):
        base, why, cand = cfg["base"], "上次保存的配置", 1
    else:
        base, why, cand = detect()
        if "--save" in args and not isinstance(base, list):
            base = save(base)

    if "--json" in args:
        print(json.dumps({"base": base, "why": why, "candidates": cand}, ensure_ascii=False))
        return 0

    if isinstance(base, list):
        print(f"！有 {cand} 个库都能放，别自己挑，让用户选：")
        for i, c in enumerate(base, 1):
            print(f"  {i}) {c}")
        print("")
        print("选定后：python3 scripts/where.py --base \"<选中的路径>\"")
        return 2

    print(f"月报放：{base}")
    print(f"依据：{why}")
    print("")
    print("不要放在：技能安装目录、家目录根、系统盘根。")

    if fixed:
        return 0
    if cand == 1:
        print("")
        print("这是探测到的库。出稿前让用户确认一次，然后固定：")
        print(f'  python3 scripts/where.py --base "{base}"')
        return 0
    print("")
    print("！没找到你的库。不许用这个默认路径，先问用户：月报放哪？")
    return 2


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""体检：这台机器上装了几份、各是什么版本、月报散落在哪。
用法：python3 scripts/doctor.py
只读不改，不会动你的文件。
"""
import hashlib, json, os, re, sys
from urllib.request import Request, urlopen

HOME = os.path.expanduser("~")
REPO = "dysoncool/monthly-growth-review-beta"
NAME = "monthly-growth-review-beta"
MAXD = 5


def _get(path):
    url = f"https://api.github.com/repos/{REPO}/contents/skill/{path}?ref=main"
    req = Request(url, headers={"User-Agent": "doctor", "Accept": "application/vnd.github+json"})
    import base64, json
    return base64.b64decode(json.loads(urlopen(req, timeout=8).read())["content"]).decode()


def official():
    """返回 (版本, 模板样式哈希)；连不上就是 ('?', '')。"""
    try:
        return _get("VERSION").strip(), style_hash_text(_get("templates/monthly-review-blank.html"))
    except Exception:
        return "?", ""


def roots():
    rs = {os.getcwd(), HOME}
    env = os.environ.get("AGENT_SKILLS_DIR")
    if env and os.path.isdir(env):
        rs.add(env)
    for a in sys.argv[1:]:
        if not a.startswith("-") and os.path.isdir(a):
            rs.add(a)
    return [r for r in rs if os.path.isdir(r)]


def find_skills():
    hits = []
    for root in roots():
        base = root.rstrip("/")
        for dirpath, dirnames, _ in os.walk(base):
            depth = dirpath[len(base):].count(os.sep)
            if depth > MAXD:
                dirnames[:] = []
                continue
            dirnames[:] = [d for d in dirnames if not d.startswith(".") or d == ".agents"]
            if os.path.basename(dirpath) == NAME and os.path.isfile(os.path.join(dirpath, "SKILL.md")):
                hits.append(dirpath)
    return sorted(set(hits))


def ver(d):
    try:
        return open(os.path.join(d, "VERSION")).read().strip()
    except OSError:
        return "无 VERSION"


def style_hash_text(t):
    m = re.search(r"<style>(.*?)</style>", t, re.S)
    return hashlib.sha256(m.group(1).encode()).hexdigest()[:12] if m else ""


def style_hash(path):
    try:
        return style_hash_text(open(path, encoding="utf-8").read())
    except OSError:
        return ""


def find_reports():
    out = []
    bases = {HOME}
    try:
        cfg = json.load(open(os.path.join(HOME, ".config", "monthly-review", "config.json")))
        if cfg.get("base") and os.path.isdir(cfg["base"]):
            bases.add(cfg["base"])
    except Exception:
        pass
    for base in bases:
        for dirpath, dirnames, files in os.walk(base):
            depth = dirpath[len(base):].count(os.sep)
            if depth > 3:
                dirnames[:] = []
                continue
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for f in files:
                if f.endswith(".html") and "月度成长总结" in f:
                    out.append(os.path.join(dirpath, f))
    return out


def main():
    off, off_hash = official()
    skills = find_skills()
    print(f"官方最新版本：{off}")
    print("扫描：  " + "  ".join(roots()))
    print("")
    if not skills:
        print("✘ 没找到已安装的技能，先装：")
        print(f"  curl -fsSL https://raw.githubusercontent.com/{REPO}/main/install.sh | bash")
        return 1
    print(f"装了 {len(skills)} 份：")
    for d in skills:
        v = ver(d)
        h = style_hash(os.path.join(d, "templates/monthly-review-blank.html"))
        tag = "样式一致" if h and h == off_hash else "样式不同"
        print(f"  [{v}] {d}  ({tag})")
    if len(skills) > 1:
        print("")
        print("！多份同时存在，agent 可能读到旧的那份。只保留一份，其余移走或删除。")
    bad = [d for d in skills if ver(d) != off]
    if bad:
        print("")
        print("更新（会覆盖同位置旧版）：")
        print(f"  curl -fsSL https://raw.githubusercontent.com/{REPO}/main/install.sh | bash")
    print("")
    reps = find_reports()
    if reps:
        print(f"月报 {len(reps)} 份：")
        for r in reps[:12]:
            print("  " + r)
        print("")
        print("位置对不对，跑一遍：python3 <技能目录>/scripts/where.py")
    else:
        print("还没出过月报。")
    return 0


if __name__ == "__main__":
    sys.exit(main())

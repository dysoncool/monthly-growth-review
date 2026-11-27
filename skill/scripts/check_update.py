#!/usr/bin/env python3
"""出稿前先跑：本地版本与模板是否最新、是否被改过。
用法：python3 scripts/check_update.py           # 只检查
     python3 scripts/check_update.py --quiet   # 只在有问题时输出
退出码：0 最新；3 落后；4 模板被改动；5 查不到（离线）
"""
import hashlib, json, re, sys, urllib.request

REPO = "dysoncool/monthly-growth-review-beta"
API = f"https://api.github.com/repos/{REPO}/contents/skill"
RAW = f"https://raw.githubusercontent.com/{REPO}/main/skill"
HERE = __file__.rsplit("/", 1)[0] if "/" in __file__ else "."


def fetch(path, timeout=8):
    """先走 API（不吃 CDN 缓存），失败再退 raw。"""
    import base64
    req = urllib.request.Request(f"{API}/{path}?ref=main",
                                 headers={"Accept": "application/vnd.github+json",
                                          "User-Agent": "monthly-review-check"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
        return base64.b64decode(data["content"]).decode("utf-8")
    except Exception:
        with urllib.request.urlopen(f"{RAW}/{path}", timeout=timeout) as r:
            return r.read().decode("utf-8")


def style(txt):
    m = re.search(r"<style>(.*?)</style>", txt, re.S)
    return hashlib.sha256(m.group(1).encode()).hexdigest()[:12] if m else ""


def main():
    quiet = "--quiet" in sys.argv
    try:
        local_ver = open(f"{HERE}/../VERSION").read().strip()
    except OSError:
        print("✘ 找不到 VERSION，安装不完整，请重装")
        return 3
    try:
        remote_ver = fetch("VERSION").strip()
        remote_tpl = fetch("templates/monthly-review-blank.html")
    except Exception as e:
        if not quiet:
            print(f"? 连不上 GitHub（{type(e).__name__}），跳过版本检查")
        return 5

    tpl = open(f"{HERE}/../templates/monthly-review-blank.html", encoding="utf-8").read()
    problems = []
    if local_ver != remote_ver:
        problems.append(f"版本落后：本地 {local_ver}，最新 {remote_ver}")
    if style(tpl) != style(remote_tpl):
        problems.append("模板样式与官方不一致（可能被改过，或装的是旧版）")

    if problems:
        print("！这套技能有问题，先修再出稿：")
        for p in problems:
            print("  - " + p)
        print("  更新：curl -fsSL https://raw.githubusercontent.com/"
              f"{REPO}/main/install.sh | bash")
        return 3
    if not quiet:
        print(f"✔ 版本 {local_ver}，模板样式与官方一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""冒烟自检：每个脚本都真跑一遍，只抓崩溃（NameError 之类），不判断业务结论。
用法：python3 scripts/selftest.py        退出码 0 = 全部能跑
"""
import os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "..", "templates", "monthly-review-blank.html")
PY = sys.executable or "python3"

def run(args, cwd):
    p = subprocess.run([PY] + args, cwd=cwd, capture_output=True, text=True, timeout=120)
    bad = "Traceback (most recent call last)" in (p.stdout + p.stderr)
    return bad, (p.stdout + p.stderr).strip().splitlines()[-1:] or [""]

def main():
    tmp = tempfile.mkdtemp(prefix="mr-selftest-")
    cases = [
        ("where.py", [os.path.join(HERE, "where.py")]),
        ("check_update.py", [os.path.join(HERE, "check_update.py")]),
        ("check_page.py", [os.path.join(HERE, "check_page.py"), os.path.abspath(TPL)]),
        ("check_clean.py", [os.path.join(HERE, "check_clean.py"), os.path.abspath(TPL)]),
        ("check_continuity.py", [os.path.join(HERE, "check_continuity.py"), "--base", tmp]),
        ("doctor.py", [os.path.join(HERE, "doctor.py"), tmp]),
    ]
    failed = 0
    for name, args in cases:
        try:
            bad, tail = run(args, tmp)
        except Exception as exc:
            bad, tail = True, [f"{type(exc).__name__}: {exc}"]
        print(("✘ " if bad else "✔ ") + name + ("" if not bad else "  " + tail[0]))
        failed += 1 if bad else 0
    print(f"\n通过 {len(cases) - failed} / {len(cases)}")
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())

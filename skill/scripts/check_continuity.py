#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""连续性检查：从起始月到本月，逐月看有没有成品。

用法：
    python3 check_continuity.py --base <月报目录> [--start 2026-01] [--end 2026-12]
退出码 0 = 连续；1 = 有缺口。
"""
import argparse, glob, os, re, sys
from datetime import date


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="月报所在目录")
    ap.add_argument("--start", default=None, help="最早有记录的月份，默认取现有最早一份")
    ap.add_argument("--end", default=None, help="默认到今天")
    a = ap.parse_args()

    found = {}
    for p in glob.glob(os.path.join(a.base, "*-月度成长总结*.html")):
        m = re.search(r"(\d{4})-(\d{2})-月度成长总结", os.path.basename(p))
        if m:
            found.setdefault(f"{m.group(1)}-{m.group(2)}", []).append(os.path.basename(p))
    if not found:
        print("✘ 目录里一个月报都没有：" + a.base)
        return 1

    start = a.start or sorted(found)[0]
    end = a.end or date.today().strftime("%Y-%m")

    def seq(s, e):
        y, m = map(int, s.split("-")); ey, em = map(int, e.split("-"))
        out = []
        while (y, m) <= (ey, em):
            out.append(f"{y}-{m:02d}")
            m += 1
            if m == 13:
                y, m = y + 1, 1
        return out

    months = seq(start, end)
    gaps = [x for x in months if x not in found]
    for k in sorted(found):
        print(f"✔ {k}  {len(found[k])} 个版本  {sorted(found[k])[-1]}")
    if gaps:
        print("✘ 缺口：" + "、".join(gaps))
    print(f"连续 {len(months) - len(gaps)} / {len(months)} 个月")
    return 0 if not gaps else 1


if __name__ == "__main__":
    sys.exit(main())

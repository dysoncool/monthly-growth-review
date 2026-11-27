#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""连续性检查：先找最早记录，再从那个月起逐月对账。

用法：
    python3 check_continuity.py --base <月报目录> --records <记录目录> [--records ...]
    python3 check_continuity.py --base <月报目录> --start 2026-05
退出码 0 = 连续；1 = 有缺口或还没开始；2 = 用错了。
"""
import argparse, glob, os, re, sys
from datetime import date

DATE_RE = re.compile(r"(20\d{2})[-_.]?(\d{2})[-_.]?(\d{2})?")
MD_RE = re.compile(r"(20\d{2})-(\d{2})-月度成长总结")


def scan_records(dirs, maxdepth=4):
    """扫记录目录，返回 (最早月份, 命中文件数, 最早文件)。"""
    best, cnt, best_file = None, 0, ""
    for d in dirs:
        if not os.path.isdir(d):
            continue
        base_depth = d.rstrip("/").count("/")
        for dp, dn, fn in os.walk(d):
            if dp.count("/") - base_depth >= maxdepth:
                dn[:] = []
            for f in fn:
                if not f.lower().endswith((".md", ".txt", ".html", ".json")):
                    continue
                m = DATE_RE.search(f)
                if m:
                    ym = f"{m.group(1)}-{m.group(2)}"
                    cnt += 1
                    if best is None or ym < best:
                        best, best_file = ym, os.path.join(dp, f)
    return best, cnt, best_file


COMMON = ("journal", "daily-signal", "日分析", "daily", "work-log", "日志", "日记", "records")


def guess_dirs(base):
    """没给 --records 时，自动找月报目录旁边的常见记录目录。"""
    out = []
    for parent in (os.path.dirname(os.path.abspath(base)),
                   os.path.dirname(os.path.dirname(os.path.abspath(base)))):
        if not os.path.isdir(parent):
            continue
        for name in COMMON:
            p = os.path.join(parent, name)
            if os.path.isdir(p):
                out.append(p)
    return sorted(set(out))


def scan_reports(base):
    found = {}
    for p in glob.glob(os.path.join(base, "*-月度成长总结*.html")):
        m = MD_RE.search(os.path.basename(p))
        if m:
            found.setdefault(f"{m.group(1)}-{m.group(2)}", []).append(os.path.basename(p))
    return found


def seq(s, e):
    y, m = map(int, s.split("-")); ey, em = map(int, e.split("-"))
    out = []
    while (y, m) <= (ey, em):
        out.append(f"{y}-{m:02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="月报目录")
    ap.add_argument("--records", nargs="*", default=[], help="记录目录，可给多个")
    ap.add_argument("--start", default=None, help="强制起始月 YYYY-MM")
    ap.add_argument("--end", default=None, help="默认上个月（当月不算缺）")
    a = ap.parse_args()

    records = list(a.records) or guess_dirs(a.base)
    found = scan_reports(a.base) if os.path.isdir(a.base) else {}
    earliest_rec, cnt, rec_file = scan_records(records)

    start = a.start or earliest_rec or (sorted(found)[0] if found else None)
    if not start:
        print("✘ 既没有月报，也没扫到带日期的记录。")
        print("  先告诉脚本记录在哪：--records <日记/日分析/工作日志目录>")
        return 1

    if a.end:
        end = a.end
    else:
        t = date.today()
        end = f"{t.year}-{t.month - 1:02d}" if t.month > 1 else f"{t.year - 1}-12"

    if end < start:
        print(f"最早记录 {start}，还没到能出第二期的日子。")
        return 0

    months = seq(start, end)
    gaps = [x for x in months if x not in found]

    print("=== 这套是按月连续积累的，不是单月快照 ===")
    if earliest_rec:
        print(f"最早记录：{earliest_rec}　（{cnt} 个带日期文件，例：{os.path.basename(rec_file)}）")
    else:
        print("最早记录：没扫到（没给 --records，或目录里没有带日期的文件）")
        print("  → 先问用户：日记、周报、聊天记录、工单，分别在哪？再用 --records 传进来。")
    have = sorted(found)
    print(f"应出月份：{start} 至 {end}，共 {len(months)} 期")
    print(f"已出：{'、'.join(have) if have else '无'}")
    if gaps:
        print(f"缺：{'、'.join(gaps)}")
        print(f"→ 从 {gaps[0]} 开始补，补完再出后面的。不许跳月，不许只做当月。")
    else:
        print("缺口：无")
    print(f"连续 {len(months) - len(gaps)} / {len(months)} 个月")

    if earliest_rec and start != date.today().strftime("%Y-%m") and not have:
        print("")
        print("出第一期前先跟用户说这三句：")
        print(f"  1. 这套总结是按月连续积累的，单看一个月说明不了什么。")
        print(f"  2. 你最早的记录在 {earliest_rec}，所以从那一期开始。")
        print(f"  3. 我一期一期往下补，缺的月份不会跳过。")
    return 0 if not gaps else 1


if __name__ == "__main__":
    sys.exit(main())

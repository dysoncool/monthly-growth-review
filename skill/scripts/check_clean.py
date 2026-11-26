#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""脱敏检查：成品里不许留真名占位、本机路径、联系方式、未替换占位符。

用法：python3 check_clean.py <html> [--names 张三,李四]
退出码 0 = 干净；1 = 有命中。
"""
import argparse, re, sys

RULES = {
    "本机绝对路径": r"(/Users/|C:\\Users|/home/[^/]+/|/srv/)",
    "未替换占位符": r"\{\{[^}]*\}\}",
    "手机号": r"\b1[3-9]\d{9}\b",
    "邮箱": r"[\w.+-]+@[\w-]+\.[\w.]+",
    "身份证": r"\b\d{17}[\dXx]\b",
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--names", default="", help="逗号分隔的真名清单，命中即报")
    a = ap.parse_args()
    t = open(a.path, encoding="utf-8", errors="ignore").read()
    text = re.sub(r"<[^>]+>", "", t)
    hits = []
    for name, pat in RULES.items():
        found = re.findall(pat, text)
        if found:
            hits.append(f"{name}：{len(found)} 处，例 {found[:2]}")
    for n in [x.strip() for x in a.names.split(",") if x.strip()]:
        if n in text:
            hits.append(f"真名「{n}」出现在正文")
    if hits:
        print("✘ 脱敏未过：")
        for h in hits:
            print("   - " + h)
        return 1
    print("✔ 脱敏通过：无本机路径、无占位符残留、无联系方式、无真名")
    return 0


if __name__ == "__main__":
    sys.exit(main())

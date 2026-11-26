#!/usr/bin/env bash
# 一条命令装好：
#   curl -fsSL https://raw.githubusercontent.com/dysoncool/monthly-growth-review-beta/main/install.sh | bash
# 指定目录：
#   AGENT_SKILLS_DIR=./skills bash install.sh
set -euo pipefail

REPO="dysoncool/monthly-growth-review-beta"
NAME="monthly-growth-review-beta"

# 解析技能根目录
ROOT="${AGENT_SKILLS_DIR:-}"
if [ -z "$ROOT" ]; then
  for c in "./skills" "$HOME/.agents/skills" "$HOME/skills"; do
    if [ -d "$c" ]; then ROOT="$c"; break; fi
  done
fi
[ -z "$ROOT" ] && ROOT="$HOME/.agents/skills"
DEST="$ROOT/consulting/$NAME"

if [ -d "$DEST" ] && [ "${FORCE:-0}" != "1" ]; then
  echo "! 已存在：$DEST"
  echo "  要覆盖：FORCE=1 再跑一次"
  exit 2
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
echo "→ 从 GitHub 取包…"
curl -fsSL "https://codeload.github.com/$REPO/tar.gz/refs/heads/main" | tar -xz -C "$TMP"
SRC="$(find "$TMP" -maxdepth 2 -type d -name skill | head -1)"
[ -d "$SRC" ] || { echo "✘ 包里找不到 skill 目录"; exit 1; }

mkdir -p "$(dirname "$DEST")"
rm -rf "$DEST"
cp -R "$SRC" "$DEST"
echo "✔ 已安装到：$DEST"
echo "  技能根目录：$ROOT（用 AGENT_SKILLS_DIR 可改）"
echo ""
echo "下一步："
echo "  1. mkdir -p <你的库>/monthly-review"
echo "  2. cp \"$DEST/templates/monthly-review-blank.html\" <你的库>/monthly-review/2026-01-月度成长总结.html"
echo "  3. python3 \"$DEST/scripts/check_page.py\" <成品>"

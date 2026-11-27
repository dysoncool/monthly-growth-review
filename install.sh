#!/usr/bin/env bash
# 一条命令装好：
#   curl -fsSL https://raw.githubusercontent.com/dysoncool/monthly-growth-review/main/install.sh | bash
# 指定目录：
#   AGENT_SKILLS_DIR=./skills bash install.sh
set -euo pipefail

REPO="dysoncool/monthly-growth-review"
NAME="monthly-growth-review"

# 解析技能根目录
ROOT="${AGENT_SKILLS_DIR:-}"
if [ -z "$ROOT" ]; then
  for c in "./skills" "$HOME/.agents/skills" "$HOME/skills"; do
    if [ -d "$c" ]; then ROOT="$c"; break; fi
  done
fi
[ -z "$ROOT" ] && ROOT="$HOME/.agents/skills"
DEST="$ROOT/consulting/$NAME"

OLD=""
if [ -d "$DEST" ]; then
  OLD="$(cat "$DEST/VERSION" 2>/dev/null || echo "未知版本")"
fi

if [ -n "${MR_SRC:-}" ]; then
  SRC="$MR_SRC"
  echo "→ 从本地取包：$SRC"
else
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT
  echo "→ 从 GitHub 取包…"
  curl -fsSL "https://codeload.github.com/$REPO/tar.gz/refs/heads/main" | tar -xz -C "$TMP"
  SRC="$(find "$TMP" -maxdepth 2 -type d -name skill | head -1)"
fi
[ -d "$SRC" ] || { echo "✘ 包里找不到 skill 目录"; exit 1; }

mkdir -p "$(dirname "$DEST")"
rm -rf "$DEST"
cp -R "$SRC" "$DEST"

# 改名迁移：清掉旧名字留下的目录，避免同一个技能两份并存
for old in monthly-growth-review-beta monthly-growth-review-share; do
  d="$(dirname "$DEST")/$old"
  if [ -d "$d" ]; then
    rm -rf "$d"
    echo "  已迁移旧目录：$d"
  fi
done

NEW="$(cat "$DEST/VERSION" 2>/dev/null || echo "?")"
if [ -n "$OLD" ]; then
  echo "✔ 已更新：$OLD → $NEW"
else
  echo "✔ 已安装：$NEW"
fi
echo "  位置：$DEST"
echo "  技能根目录：$ROOT（用 AGENT_SKILLS_DIR 可改）"
echo ""
echo "下一步："
echo "  1. 定存放位置（别放安装目录）：python3 \"$DEST/scripts/where.py\""
echo "  2. 复制模板出稿：cp \"$DEST/templates/monthly-review-blank.html\" <库>/2026-01-月度成长总结.html"
echo "  3. 自检：python3 \"$DEST/scripts/check_page.py\" <成品>"
echo "  4. 说明：$DEST/INSTALL.md"

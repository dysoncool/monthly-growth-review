# monthly-growth-review-beta

**A Hermes agent skill that turns a month of scattered notes into one readable review — and tells you which ability actually leveled up.**

Beta. The five-level scale and page format may still change.

![demo](docs/demo.png)

---

## What it solves

Most monthly reviews are diaries. They list what you did, not what accumulated.

This skill asks five questions and answers them with dated evidence:

1. What did you actually get done?
2. Which abilities moved up a level?
3. Which path gets easier each time?
4. Where are you leaking?
5. What would count as "standing on solid ground"?

It refuses to flatter. If nobody acted on your work, the review says so.

## Install

```bash
npx monthly-growth-review-beta
```

Installs into `~/.hermes/skills/consulting/monthly-growth-review-beta`.
Custom target:

```bash
npx monthly-growth-review-beta --target ./skills/consulting --force
```

From GitHub (before the npm release):

```bash
npx github:dysoncool/monthly-growth-review-beta
```

## First run

```bash
mkdir -p <your-vault>/monthly-review
cp ~/.hermes/skills/consulting/monthly-growth-review-beta/templates/monthly-review-blank.html \
   <your-vault>/monthly-review/2026-01-月度成长总结.html
```

Edit the content, keep the structure. Then:

```bash
python3 scripts/check_page.py <page.html>      # 19 structural checks
python3 scripts/check_clean.py <page.html>     # PII / path leak check
python3 scripts/check_continuity.py --base <your-vault>/monthly-review --start 2026-01
```

## The five levels

| Level | Meaning |
|---|---|
| 刚冒头 Emerging | First positive feedback |
| 开始积累 Accumulating | At least three times, across two weeks |
| 初有效果 Taking effect | A real change happened |
| 值得重视 Worth attention | Repeat customers, or held under pressure |
| 略有小成 Working | Systematized, methodized, easier |

Two groups: **external** (what you put out: delivery, pricing, writing) and **internal** (what you build in yourself: craft, body, records). If the internal side is thin, the report must say so and name what is missing — reading, meditation, standing practice.

## What's inside

| Path | Purpose |
|---|---|
| `skill/SKILL.md` | Method and definitions |
| `skill/INSTALL.md` | Install, first run, month-end cron |
| `skill/templates/monthly-review-blank.html` | Editable sample page |
| `skill/scripts/check_page.py` | 19 structural checks |
| `skill/scripts/check_clean.py` | PII / path leak check |
| `skill/scripts/check_continuity.py` | Month gap check |

## Month-end automation

One cron, one line of intent: run on the last day of the month at 21:00; check for missing months first; skip if this month is already out; never fail silently.

---

# 中文

**把一个月散落的记录，变成一份能读的复盘，并告诉你哪样本事真的升了一级。**

测试版。五格口径与页面样式仍可能调整。

![演示](docs/demo.png)

## 它解决什么

大多数月度总结是流水账：列了你做了什么，看不出攒下了什么。

这套东西只问五个问题，并要求每个答案带日期证据：做成了什么／哪样本事升了级／哪条路越走越省力／哪里在漏／怎样才算站住。

它不负责夸人。没人因你行动，它就直说。

## 安装

```bash
npx monthly-growth-review-beta
```

默认装到 `~/.hermes/skills/consulting/monthly-growth-review-beta`。换目录加 `--target`，覆盖加 `--force`。

npm 发布前，也可以直接从 GitHub 装：

```bash
npx github:dysoncool/monthly-growth-review-beta
```

## 第一次用

```bash
mkdir -p <你的库>/monthly-review
cp ~/.hermes/skills/consulting/monthly-growth-review-beta/templates/monthly-review-blank.html \
   <你的库>/monthly-review/2026-01-月度成长总结.html
```

改内容，不改结构；然后跑三条自检（结构 19 项／脱敏／连续性）。

## 五格档位

刚冒头（第一次获得正反馈）→ 开始积累（至少三次，横跨两周）→ 初有效果（产生重要改变）→ 值得重视（有回头客，或压力期没断）→ 略有小成（系统化、方法论、更轻松）。

分两组：**外用**（对着外面出手：交付、收费、开口、写东西、找资源）与**内修**（对自己使：手艺、身体、记录）。内修单薄必须写提醒，点名缺的读书、静坐、站桩。

## 月末自动出

一条定时任务：每月最后一天 21:00 触发；先查缺月；当月已出就跳过；失败必须吭声，不许静默。

## 边界

不含任何真实客户信息，不写死绝对路径，不允许断月出稿。

MIT License.

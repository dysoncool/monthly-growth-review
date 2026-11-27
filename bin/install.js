#!/usr/bin/env node
/** 把技能装进你的 agent 技能目录。用法：
 *   npx monthly-growth-review-beta [--target <skills 目录>] [--force]
 * 装到哪：--target 指定 > $AGENT_SKILLS_DIR > 探测（./skills、~/.agents/skills、~/skills）
 */
const fs = require('fs');
const path = require('path');
const os = require('os');

const args = process.argv.slice(2);
const get = (k) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : null; };
const force = args.includes('--force');


/** 找技能根目录：显式 --target > $AGENT_SKILLS_DIR > 探测（./skills、~/.agents/skills、~/skills） */
function resolveRoot() {
  const explicit = get('--target');
  if (explicit) return explicit;
  if (process.env.AGENT_SKILLS_DIR) return process.env.AGENT_SKILLS_DIR;
  const home = os.homedir();
  const candidates = [
    path.join(process.cwd(), 'skills'),
    path.join(home, '.agents', 'skills'),
    path.join(home, 'skills'),
  ];
  for (const c of candidates) {
    if (fs.existsSync(c)) return c;
  }
  return path.join(home, '.agents', 'skills');
}

const target = path.join(resolveRoot(), 'consulting', 'monthly-growth-review-beta');
const src = path.join(__dirname, '..', 'skill');

if (!fs.existsSync(src)) { console.error('✘ 找不到 skill 目录，包可能损坏'); process.exit(1); }
const readVer = (dir) => {
  try { return fs.readFileSync(path.join(dir, 'VERSION'), 'utf8').trim(); } catch { return '未知版本'; }
};
const oldVer = fs.existsSync(target) ? readVer(target) : '';
const isUpdate = Boolean(oldVer);
fs.mkdirSync(path.dirname(target), { recursive: true });
if (isUpdate) fs.rmSync(target, { recursive: true, force: true });
fs.cpSync(src, target, { recursive: true });
const newVer = readVer(target);
if (isUpdate) {
  console.log('✔ 已更新：' + oldVer + ' → ' + newVer);
  console.log('  （新版覆盖旧版；你的月报和数据在别处，不受影响）');
} else {
  console.log('✔ 已安装：' + newVer);
}
console.log('  位置：' + target);
console.log('  （技能根目录：' + resolveRoot() + '；换位置用 --target）');
console.log('');
console.log('下一步：');
console.log('  1. 定存放位置（别放安装目录）：python3 "' + path.join(target, 'scripts/where.py') + '"');
console.log('  2. 复制模板出稿：cp "' + path.join(target, 'templates/monthly-review-blank.html') + '" <库>/2026-01-月度成长总结.html');
console.log('  3. 自检：python3 "' + path.join(target, 'scripts/check_page.py') + '" <成品>');
console.log('  4. 详见 ' + path.join(target, 'INSTALL.md'));

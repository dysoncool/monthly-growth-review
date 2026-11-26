#!/usr/bin/env node
/** 把技能装进 Hermes 的技能目录。用法：
 *   npx monthly-growth-review-beta [--target <skills 目录>] [--force]
 * 默认目标：~/.hermes/skills/consulting/monthly-growth-review-beta
 */
const fs = require('fs');
const path = require('path');
const os = require('os');

const args = process.argv.slice(2);
const get = (k) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : null; };
const force = args.includes('--force');
const target = get('--target') || path.join(os.homedir(), '.hermes', 'skills', 'consulting', 'monthly-growth-review-beta');
const src = path.join(__dirname, '..', 'skill');

if (!fs.existsSync(src)) { console.error('✘ 找不到 skill 目录，包可能损坏'); process.exit(1); }
if (fs.existsSync(target) && !force) {
  console.log('! 目标已存在：' + target);
  console.log('  加 --force 覆盖，或先备份');
  process.exit(2);
}
fs.mkdirSync(path.dirname(target), { recursive: true });
fs.cpSync(src, target, { recursive: true });
console.log('✔ 已安装到：' + target);
console.log('');
console.log('下一步：');
console.log('  1. 建月报目录：mkdir -p <你的库>/monthly-review');
console.log('  2. 抄样板：cp "' + path.join(target, 'templates/monthly-review-blank.html') + '" <你的库>/monthly-review/2026-01-月度成长总结.html');
console.log('  3. 自检：python3 "' + path.join(target, 'scripts/check_page.py') + '" <成品>');
console.log('  4. 详见 ' + path.join(target, 'INSTALL.md'));

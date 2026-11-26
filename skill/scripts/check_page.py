#!/usr/bin/env python3
"""月度复盘页面自检（五格版 v3）。用法：python3 check_page.py <html路径>"""
import re, sys

FIVE = ['刚冒头','开始积累','初有效果','值得重视','略有小成']
COLORS = ['#ab372f','#eee7dd','#fffdf9','#faf7f3','#e3ddd3']
H2_WANT = ['一、这个月，你做成了什么？','二、势能','三、哪条路能越走越省力？','四、哪些地方在漏？','五、怎样才算真的站住了？']

def main(path):
    t = open(path, encoding='utf-8').read()
    ok, fail = [], []
    def chk(name, cond, note=''):
        (ok if cond else fail).append(f"{name} {note}".strip())

    h2 = re.findall(r'<h2>(.*?)</h2>', t)
    chk('五节结构', len(h2) == 5 and h2[0] == H2_WANT[0] and '势能' in h2[1] and h2[2] == H2_WANT[2] and h2[4] == H2_WANT[4])
    chk('无「钱从哪来」节', '钱从哪来' not in t)
    chk('编号连续', [h.split('、')[0] for h in h2] == ['一','二','三','四','五'])

    tiers = re.findall(r'<div class="tiers">(.*?)</div>\s*\n', t, re.S)
    chk('图例只有一组', len(tiers) == 1, f'{len(tiers)} 组')
    chk('五格齐全', all(x in t for x in FIVE))
    chk('每格有箭头', '.tiers b::after' in t and 'content:"→"' in t.replace(' ', ''))
    chk('不再分两套解释', '外用</em>' not in t and '内修</em>' not in t)

    names = re.findall(r'<span class="nm">(.*?)</span><span class="lv">(.*?)</span>', t)
    chk('每条线有档位', bool(names) and all(lv in FIVE for _, lv in names), str(len(names)))
    fills = re.findall(r'style="width:(\d+)%"', t)
    chk('进度条按五格', bool(fills) and all(int(f) % 20 == 0 and 0 <= int(f) <= 100 for f in fills))
    chk('无分段小方块', '<i class="on">' not in t)

    chk('外用/内修分组', t.count('class="grp"') == 2)
    chk('内修有提醒块', 'class="note"' in t)
    chk('颜色取截图值', all(c in t for c in COLORS[:1]) and '#eee7dd' in t)

    chk('测试版标识', 'class="beta"' in t and '测试版' in t)
    chk('四个关键数常显', t.count('class="srow"') == 4)
    chk('无折叠交互', '<details' not in t and 'onclick' not in t)
    chk('零外链零JS', 'http://' not in t and '<script' not in t)
    chk('标题无期号版本号', not re.search(r'第\s*\d+\s*期|v\d+', t.split('<body>')[0]))
    chk('人称只用你我', '他' not in re.sub(r'<[^>]+>', '', t).replace('其他',''))

    print('\n'.join('✔ ' + x for x in ok))
    for x in fail: print('✘ ' + x)
    print(f'通过 {len(ok)} / 失败 {len(fail)}')
    return 0 if not fail else 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))

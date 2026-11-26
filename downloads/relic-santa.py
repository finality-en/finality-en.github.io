#!/usr/bin/env python3
"""Relic crate: the Santa Hat prize shows its real name (was 'Paper') and hides the vanilla
'When on Head: +4 Max Health / Minecraft' lines. Safe to run live and to run again."""
import re, sys, shutil, time
f = sys.argv[1] + '/AdvancedCrates/Crates/relic.yml'
s = open(f, encoding='utf-8').read()
cols = ['FF3B3B', 'FF6C6C', 'FF9D9D', 'FFCECE', 'FFFFFF', 'FFCECE', 'FF9D9D', 'FF6C6C', 'FF3B3B']
name = ''.join('&x' + ''.join('&' + c for c in col) + '&l' + ch for col, ch in zip(cols, 'ꜱᴀɴᴛᴀ ʜᴀᴛ'))
blocks = re.split(r'(?m)^(?=(?:  )?[^\s#][^:\n]*:)', s)
out, hit = [], False
for b in blocks:
    if 'finalityitems:santa_hat' in b and re.match(r'  \S', b):
        hit = True
        line = f"    Name: '{name}'\n"
        if re.search(r'(?m)^    Name:', b):
            b = re.sub(r"(?m)^    Name:.*\n(?:      .*\n)*", lambda m: line, b, count=1)
        else:
            b = re.sub(r'(?m)^(    Chance:.*\n)', lambda m: m.group(1) + line, b, count=1)
        if 'minecraft:tooltip_display' not in b:
            b = b.replace('components:{', 'components:{"minecraft:tooltip_display":{hidden_components:["minecraft:attribute_modifiers"]},', 1)
    out.append(b)
if not hit:
    sys.exit('❌ Santa Hat prize not found in relic.yml')
s2 = ''.join(out)
if s2 != s:
    shutil.copy2(f, f + '.bak-santa-' + time.strftime('%Y%m%d-%H%M%S'))
    open(f, 'w', encoding='utf-8').write(s2)
    print('✅ Santa Hat prize: real name + no vanilla attribute lines')
else:
    print('= Santa Hat prize already fixed')

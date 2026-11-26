#!/usr/bin/env python3
"""Accurate damage lores. Safe to run while the SMP is up; safe to run again.

Minecraft adds the 1 damage of your fist to a weapon's attack modifier, so a Nexo item
with `amount: 11` really hits for 12. This rewrites every "+N Attack Damage" lore line on
Nexo weapons to the real total, adds the line where a weapon has none, hides the vanilla
attribute tooltip (so the lore is the only number shown), fixes the same lines in crate
previews, and sets the Hex Wand to 13 (1 more than the Astral Riftblade).
Damage itself is NOT changed for any Nexo item.
"""
import re, sys, glob, shutil, time

P = sys.argv[1]
HEX = 13
stamp = time.strftime('%Y%m%d-%H%M%S')
totals = {}

def fmt(x):
    return str(int(x)) if float(x).is_integer() else str(x)

def backup(f):
    shutil.copy2(f, f + '.bak-dmglore-' + stamp)

# 1) Nexo items
for f in sorted(glob.glob(P + '/Nexo/items/**/*.yml', recursive=True)):
    src = open(f, encoding='utf-8').read()
    parts = re.split(r'(?m)^(?=[A-Za-z0-9_\-]+:[ \t]*$)', src)
    out, changed = [], False
    for blk in parts:
        m = re.match(r'([A-Za-z0-9_\-]+):', blk)
        dm = re.search(r'attribute:\s*(?:GENERIC_)?ATTACK_DAMAGE\s*\n\s*amount:\s*([\d.]+)', blk) or \
             re.search(r'amount:\s*([\d.]+)\s*\n\s*(?:\w+:.*\n\s*)?attribute:\s*(?:GENERIC_)?ATTACK_DAMAGE', blk)
        if not m or not dm or not re.search(r'(?m)^  lore:\s*$', blk):
            out.append(blk); continue
        iid, total = m.group(1), float(dm.group(1)) + 1
        totals[iid] = total
        b = re.sub(r'(?m)^(  - [\'"]?(?:<[^>]*>)*)(?:⚔ ?)?\+?[\d.]+( Attack Damage)(?=[\'"]?\s*$)',
                   lambda x: x.group(1) + fmt(total) + x.group(2), blk)
        if not re.search(r'(?m)^  - .*(?<![%\d])[\d.]+ Attack Damage[\'"]?\s*$', b):
            col = re.search(r'#[0-9A-Fa-f]{6}', re.search(r'(?m)^  itemname:.*$', b).group(0) if re.search(r'(?m)^  itemname:.*$', b) else '')
            line = f"  - <{col.group(0) if col else 'red'}>{fmt(total)} Attack Damage\n"
            b = re.sub(r'(?m)^(  lore:\s*\n)', lambda x: x.group(1) + line, b, count=1)
        if 'tooltip_display' not in b and not re.search(r'(?m)^  hide-flags:[ \t]*\n(?:  - .*\n)*?  - ATTRIBUTES', b):
            b = re.sub(r'(?m)^(  lore:\s*\n)', lambda x: '  hide-flags:\n  - ATTRIBUTES\n' + x.group(1), b, count=1)
        if b != blk:
            changed = True
            print(f'✅ {iid}: lore now says {fmt(total)} Attack Damage')
        out.append(b)
    if changed:
        backup(f); open(f, 'w', encoding='utf-8').write(''.join(out))

# 2) Hex Wand = 13 in whichever plugin builds it right now
for f, sec in [(P + '/FinalityItems/config.yml', 'boss-weapons'), (P + '/FinalityBosses/config.yml', 'boss-items')]:
    try: s = open(f, encoding='utf-8').read()
    except FileNotFoundError: continue
    s2 = re.sub(r'(?m)(^' + sec + r':\n(?:(?:  .*)?\n)*?  hex_wand:\n(?:    .*\n)*?    damage: )[\d.]+', r'\g<1>' + str(HEX), s)
    if s2 != s:
        backup(f); open(f, 'w', encoding='utf-8').write(s2)
        print(f'✅ Hex Wand damage {HEX} ({f.split("/")[-2]})')

# 3) Crate previews
for f in glob.glob(P + '/AdvancedCrates/Crates/*.yml'):
    s = open(f, encoding='utf-8').read()
    blocks = re.split(r'(?m)^(?=  [^\s#][^:]*:[ \t]*$)', s)
    new = []
    for b in blocks:
        if re.search(r'hex_wand', b):
            b = re.sub(r'(?:⚔ ?)?\+?1[1-4](\s+Attack Damage)', str(HEX) + r'\1', b)
        else:
            for iid, t in totals.items():
                if re.search(r'n(?:exo)? give ' + re.escape(iid) + r'\b|"nexo:id":"' + re.escape(iid) + '"', b):
                    b = re.sub(r'\+[\d.]+(\s+Attack Damage)', fmt(t) + r'\1', b)
        new.append(b)
    s2 = ''.join(new)
    if s2 != s:
        backup(f); open(f, 'w', encoding='utf-8').write(s2)
        print('✅ crate previews fixed in', f.split('/')[-1])

print('= damage lores done')

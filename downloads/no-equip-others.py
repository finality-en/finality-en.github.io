#!/usr/bin/env python3
"""Stop armour/wearables being put onto OTHER players by right-clicking them (1.21.5+ 'equip_on_interact').
 - Nexo: every item with an equippable component gets  equip_on_interact: false  (Nexo leaves it to its default)
 - EliteLootbox: any saved item with equip_on_interact on (e.g. glacier_set) is switched off
Live-safe, run again any time. Then:  nexo reload items  (EliteLootbox: its reload command or a restart)."""
import re, sys, glob, shutil, time
P = sys.argv[1]
stamp = time.strftime('%Y%m%d-%H%M%S')

def save(f, old, new, what):
    if new != old:
        shutil.copy2(f, f + '.bak-equip-' + stamp)
        open(f, 'w', encoding='utf-8').write(new)
        print('✅', what)

# Nexo items
for f in glob.glob(P + '/Nexo/items/**/*.yml', recursive=True):
    s = open(f, encoding='utf-8', errors='replace').read()
    def fix(m):
        ind, body = m.group(1), m.group(2)
        if re.search(r'(?m)^\s+equip_on_interact:', body):
            body = re.sub(r'(?m)^(\s+equip_on_interact:)\s*\S+', r'\1 false', body)
            return ind + 'equippable:\n' + body
        child = re.match(r'(\s+)', body).group(1) if body else ind + '  '
        return ind + 'equippable:\n' + body + f'{child}equip_on_interact: false\n'
    s2, k = re.subn(r'(?m)^([ \t]+)equippable:[ \t]*\n((?:\1[ \t]+.*\n)*)', fix, s)
    save(f, s, s2, f'Nexo {f.split("/items/")[1]}: equip_on_interact off on {k} item(s)')

# EliteLootbox saved items (NBT / component text)
for f in glob.glob(P + '/EliteLootbox/**/*.yml', recursive=True):
    s = open(f, encoding='utf-8', errors='replace').read()
    s2 = re.sub(r'(equip_on_interact"?\s*:\s*)(1b|true)', lambda m: m.group(1) + ('0b' if m.group(2) == '1b' else 'false'), s)
    s2 = re.sub(r'(?m)^(\s+equip-on-interact:)\s*true', r'\1 false', s2)
    save(f, s, s2, f'EliteLootbox {f.split("/EliteLootbox/")[1]}: equip_on_interact switched off')
print('= done')

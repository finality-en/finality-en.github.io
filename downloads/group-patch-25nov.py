#!/usr/bin/env python3
"""Live config tweaks for the 25 Nov group update. Usage: group-patch-25nov.py <plugins dir>. Safe to re-run."""
import re, sys, os, shutil, glob, time
P = sys.argv[1]
stamp = time.strftime('%Y%m%d-%H%M%S')

def edit(path, fn, label):
    if not os.path.exists(path):
        print(f"?  {label}: {path} not found"); return
    s = open(path, encoding='utf-8').read()
    n = fn(s)
    if n == s:
        print(f"=  {label}: already done"); return
    shutil.copy2(path, f"{path}.bak-{stamp}")
    open(path, 'w', encoding='utf-8').write(n)
    print(f"✅ {label}")

cfg = f"{P}/FinalityBosses/config.yml"

def frostfang(s):
    m = re.search(r'\n(\s*)frostfang:\s*\n', s[s.find('weapon-effects:'):]) if 'weapon-effects:' in s else None
    if not m: return s
    start = s.find('weapon-effects:') + m.end()
    seg = s[start:start + 1500]
    seg2 = re.sub(r'(\n\s+chance:\s*)15\b', r'\g<1>20', seg, count=1)
    return s[:start] + seg2 + s[start + 1500:]
edit(cfg, frostfang, "Frostfang freeze chance 15 -> 20")

def floor(s):
    return re.sub(r'(floor-loot:\s*\n\s+max-items:\s*)\d+', r'\g<1>0', s, count=1)
edit(cfg, floor, "Frost King floor spill off (he has loot chests now)")

for f in glob.glob(f"{P}/Nexo/items/**/*.yml", recursive=True):
    if '15% chance to freeze' in open(f, encoding='utf-8').read():
        edit(f, lambda s: s.replace('15% chance to freeze', '20% chance to freeze').replace('15% freeze on hit', '20% freeze on hit'),
             f"Frostfang lore 20% ({os.path.basename(f)})")

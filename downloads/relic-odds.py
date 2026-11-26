#!/usr/bin/env python3
"""Relic crate: Frostfang + Elf Candy Cane become the rarest prizes (0.25% each), every other prize keeps its
current odds relative to the others, and all chances add up to exactly 100. Usage: relic-odds.py <plugins dir>"""
import re, sys, shutil, time
f = sys.argv[1].rstrip("/") + "/AdvancedCrates/Crates/relic.yml"
RARE = 0.25
lines = open(f, encoding="utf-8").readlines()
start = next(i for i, l in enumerate(lines) if l.rstrip() == "Prizes:")
blocks, i = [], start + 1
while i < len(lines) and (lines[i].startswith(" ") or not lines[i].strip()):
    if re.match(r"^  \S.*:\s*$", lines[i]):
        j = i + 1
        while j < len(lines) and (lines[j].startswith("   ") or not lines[j].strip()): j += 1
        blocks.append((i, j)); i = j
    else: i += 1
prizes = []
for a, b in blocks:
    txt = "".join(lines[a:b]); low = txt.lower()
    ci = next((k for k in range(a, b) if re.match(r"^    Chance:", lines[k])), None)
    if ci is None: continue
    ch = float(lines[ci].split(":", 1)[1].strip().strip("'\"") or 0)
    rare = "material: netherite_sword" in low and any(m in low for m in ("frostfang", "ꜰʀᴏꜱᴛꜰᴀɴɢ", "elf_candy_cane", "ᴇʟꜰ ᴄᴀɴᴅʏ ᴄᴀɴᴇ"))
    prizes.append(dict(key=lines[a].strip()[:-1], ci=ci, ch=ch, rare=rare))
rare = [p for p in prizes if p["rare"]]
if len(rare) != 2: sys.exit(f"❌ expected Frostfang + Elf Candy Cane, found {len(rare)} matching prizes - nothing changed")
rest = [p for p in prizes if not p["rare"]]
target = 100 - RARE * len(rare)
tot = sum(p["ch"] for p in rest)
for p in rest: p["new"] = round(p["ch"] / tot * target, 2)
for p in rare: p["new"] = RARE
# rounding fix: put the leftover on the most common prize
diff = round(100 - sum(p["new"] for p in prizes), 2)
max(rest, key=lambda p: p["new"])["new"] = round(max(rest, key=lambda p: p["new"])["new"] + diff, 2)
shutil.copy2(f, f + ".bak-odds-" + time.strftime("%Y%m%d-%H%M%S"))
for p in prizes:
    lines[p["ci"]] = f"    Chance: {p['new']}\n"
open(f, "w", encoding="utf-8").writelines(lines)
print(f"✅ relic.yml updated - chances now add up to {sum(p['new'] for p in prizes):.2f}")
for p in sorted(prizes, key=lambda p: -p["new"]):
    print(f"  {p['ch']/sum(x['ch'] for x in prizes)*100:6.2f}% -> {p['new']:6.2f}%   {p['key']}{'  (Frostfang/Elf Candy Cane)' if p['rare'] else ''}")

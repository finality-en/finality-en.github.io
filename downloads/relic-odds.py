#!/usr/bin/env python3
"""Relic crate: adds the Hex Wand (Blizzard Witch drop) if it's missing, makes Frostfang, Elf Candy Cane and the
Hex Wand the rarest prizes (0.4% each), every other prize keeps its current odds relative to the others, and all
chances add up to exactly 100. Usage: relic-odds.py <plugins dir>"""
import re, sys, shutil, time
f = sys.argv[1].rstrip("/") + "/AdvancedCrates/Crates/relic.yml"
RARE = 0.4
lines = open(f, encoding="utf-8").readlines()
HEX = """  hex_wand:
    Material: BLAZE_ROD
    Damage: 0
    Glow: true
    Amount: 1
    Lores:
    - '§7Still crackling with frost magic.'
    - '§f'
    - '§x§D§9§A§0§F§F+13 Attack Damage'
    - '§5☠ Hex §7- 35% chance on hit to give §fWither II §7for 4s'
    - '§d✦ Right click: Hex Bolt §7- 8 damage, Withers and Slows'
    - '§f'
    - '§8Blizzard Witch raid boss drop'
    NBTtags: '{DataVersion:4671,components:{"minecraft:item_model":"nexo:hex_wand","minecraft:custom_data":{PublicBukkitValues:{"nexo:id":"hex_wand"}}},count:1,id:"minecraft:blaze_rod"}'
    GiveConfiguratedItem: false
    LinkedRewards: []
    Commands:
    - fboss item hex_wand %player%
    Chance: 0.4
    Name: '&x&D&9&A&0&F&F&lʜ&x&C&9&8&F&F&A&lᴇ&x&B&9&7&F&F&4&lx &x&9&A&5&D&E&9&lᴡ&x&8&A&4&C&E&4&lᴀ&x&7&A&3&C&D&E&lɴ&x&6&A&2&B&D&9&lᴅ'
"""
if not any("hex_wand" in l for l in lines):
    start0 = next(i for i, l in enumerate(lines) if l.rstrip() == "Prizes:")
    lines[start0 + 1:start0 + 1] = [x + "\n" for x in HEX.rstrip("\n").split("\n")]
    # show it in the crate preview too
    for i, l in enumerate(lines):
        if re.match(r"^\s+- \S+,\S+", l) and i > start0:
            last = i
    try:
        lines[last] = lines[last].rstrip("\n").rstrip("'") + (",hex_wand'" if lines[last].rstrip().endswith("'") else ",hex_wand") + "\n"
    except NameError: pass
    print("✅ added the Hex Wand to the Relic crate")
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
    rare = rare or "hex_wand" in low
    prizes.append(dict(key=lines[a].strip()[:-1], ci=ci, ch=ch, rare=rare))
rare = [p for p in prizes if p["rare"]]
if len(rare) != 3: sys.exit(f"❌ expected Frostfang + Elf Candy Cane + Hex Wand, found {len(rare)} - nothing changed")
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
    print(f"  {p['ch']/sum(x['ch'] for x in prizes)*100:6.2f}% -> {p['new']:6.2f}%   {p['key']}{'  (rarest)' if p['rare'] else ''}")

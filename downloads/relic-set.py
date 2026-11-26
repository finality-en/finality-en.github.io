#!/usr/bin/env python3
"""Sets the Relic crate odds to a tiered layout (adds up to 100). Usage: relic-set.py <plugins dir>"""
import re, sys, shutil, time, yaml
f = sys.argv[1].rstrip("/") + "/AdvancedCrates/Crates/relic.yml"
SC = str.maketrans("ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡʏᴢ", "abcdefghijklmnopqrstuvwyz")
def clean(s):
    s = re.sub(r"[&§]x([&§][0-9a-fA-F]){6}", "", str(s)); s = re.sub(r"[&§][0-9a-fk-orA-FK-OR]", "", s)
    return re.sub(r"\s+", " ", s.translate(SC)).strip().lower()
# (match on the prize name, chance %) - checked in this order
PLAN = [
    # mythic boss weapons
    ("frostfang", 2.0), ("elf candy cane", 2.0), ("hex wand", 1.0),
    # legendary
    ("riftblade", 2.0), (r"pickaxe.*\[tier iii\]", 1.5),
    # rare
    ("demon wings", 2.5), ("hellfire", 2.5), ("astral dagger", 2.0), ("extra class", 2.0),
    ("glacier boots", 2.5), ("glacier pants", 2.5), ("glacier leggings", 2.5), ("glacier chestplate", 2.5), ("glacier helmet", 2.5),
    # uncommon
    (r"pickaxe.*\[tier ii\]", 5.0), (r"pickaxe.*\[tier i\]", 8.0), ("glacier blade", 7.0), ("starfall", 4.5), ("class upgrade", 4.0),
    # common
    ("glacial shard", 12.0), ("astral crystal", 10.0), ("astral shard", 6.0), ("class roll", 10.0), ("class reset", 6.0),
]
d = yaml.safe_load(open(f, encoding="utf-8"))
lines = open(f, encoding="utf-8").readlines()
start = next(i for i, l in enumerate(lines) if l.rstrip() == "Prizes:")
new, unmatched = {}, []
for k, v in (d.get("Prizes") or {}).items():
    name = clean(v.get("Name") or "") or clean(" ".join(map(str, v.get("Commands") or [])))
    hit = next((c for pat, c in PLAN if re.search(pat, name)), None)
    if hit is None: unmatched.append((k, name)); continue
    new[k] = (hit, name)
if unmatched:
    print("❌ these prizes didn't match the plan, nothing changed:"); [print("   ", k, "-", n) for k, n in unmatched]; sys.exit(1)
cur = None
for i in range(start + 1, len(lines)):
    m = re.match(r"^  (\S.*):\s*$", lines[i])
    if m: cur = m.group(1).strip("'\"")
    elif not lines[i].startswith(" ") and lines[i].strip(): break
    elif cur in new and re.match(r"^    Chance:", lines[i]): lines[i] = f"    Chance: {new[cur][0]}\n"
shutil.copy2(f, f + ".bak-set-" + time.strftime("%Y%m%d-%H%M%S"))
open(f, "w", encoding="utf-8").writelines(lines)
print(f"✅ Relic odds set - total {sum(c for c, _ in new.values()):.1f}%")
for k, (c, n) in sorted(new.items(), key=lambda x: -x[1][0]): print(f"  {c:5.1f}%  {n}")

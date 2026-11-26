#!/usr/bin/env python3
"""Relic crate preview: puts the Hex Wand right next to Frostfang and the Elf Candy Cane. Usage: relic-order.py <plugins dir>"""
import re, sys, shutil, time
f = sys.argv[1].rstrip("/") + "/AdvancedCrates/Crates/relic.yml"
lines = open(f, encoding="utf-8").readlines()
start = next(i for i, l in enumerate(lines) if l.rstrip() == "Prizes:")
keys, i = {}, start + 1
while i < len(lines) and (lines[i].startswith(" ") or not lines[i].strip()):
    if re.match(r"^  \S.*:\s*$", lines[i]):
        j = i + 1
        while j < len(lines) and (lines[j].startswith("   ") or not lines[j].strip()): j += 1
        low = "".join(lines[i:j]).lower(); k = lines[i].strip()[:-1]
        if "material: netherite_sword" in low and ("frostfang" in low or "ꜰʀᴏꜱᴛꜰᴀɴɢ" in low): keys["ff"] = k
        if "material: netherite_sword" in low and ("elf_candy_cane" in low or "ᴇʟꜰ ᴄᴀɴᴅʏ ᴄᴀɴᴇ" in low): keys["ec"] = k
        if "hex_wand" in low: keys["hex"] = k
        i = j
    else: i += 1
if len(keys) < 3: sys.exit(f"❌ couldn't find all three prizes ({keys}) - nothing changed")
try: cd = next(i for i, l in enumerate(lines) if l.rstrip() == "CustomDisplay:")
except StopIteration: sys.exit("❌ no CustomDisplay in relic.yml - the preview uses the prize order, nothing to change")
page = [i for i in range(cd, len(lines)) if re.match(r"^\s+- \S", lines[i])]
def items(l):
    m = re.match(r"^(\s+- )(['\"]?)(.*?)\2\s*$", l); return m.group(1), m.group(2), [x for x in m.group(3).split(",") if x]
# remove the hex wand wherever it is
for i in page:
    pre, q, it = items(lines[i])
    if keys["hex"] in it: it.remove(keys["hex"]); lines[i] = f"{pre}{q}{','.join(it)}{q}\n"
# insert it right after whichever of Frostfang / Elf Candy Cane comes last
placed = False
for i in reversed(page):
    pre, q, it = items(lines[i])
    idx = [n for n, x in enumerate(it) if x in (keys["ff"], keys["ec"])]
    if idx:
        it.insert(max(idx) + 1, keys["hex"]); lines[i] = f"{pre}{q}{','.join(it)}{q}\n"; placed = True; break
if not placed:
    pre, q, it = items(lines[page[-1]]); it.append(keys["hex"]); lines[page[-1]] = f"{pre}{q}{','.join(it)}{q}\n"
shutil.copy2(f, f + ".bak-order-" + time.strftime("%Y%m%d-%H%M%S"))
open(f, "w", encoding="utf-8").writelines(lines)
for i in page: print("  page:", lines[i].strip())
print("✅ Hex Wand is now next to Frostfang and the Elf Candy Cane")

#!/usr/bin/env python3
"""Gives the Frostfang and Elf Candy Cane prizes in AdvancedCrates crates their proper names + lore.
Usage: relic-names.py <plugins dir>   (all crates in AdvancedCrates/Crates). Backup: *.bak-names. Safe to re-run."""
import re, sys, glob, shutil

def grad(text, stops, bold=True):
    def hx(h): return [int(h[i:i+2], 16) for i in (0, 2, 4)]
    cs = [hx(s) for s in stops]; n = len(text); out = ""
    for i, ch in enumerate(text):
        t = i / max(1, n - 1) * (len(cs) - 1); k = min(int(t), len(cs) - 2); f = t - k
        c = [round(cs[k][j] + (cs[k + 1][j] - cs[k][j]) * f) for j in range(3)]
        h = "%02X%02X%02X" % tuple(c)
        out += "&x" + "".join("&" + d for d in h) + ("&l" if bold else "") + ch
    return out

ITEMS = {
    "frostfang": dict(
        match=["frostfang"],
        name=grad("ꜰʀᴏꜱᴛꜰᴀɴɢ", ["5BC8FF", "E6F7FF", "F2C14E"]),
        lore=["§x§5§B§C§8§F§F+11 Attack Damage", "§x§E§6§F§7§F§F20% chance to freeze your target", "§f",
              "§7Pried from the frozen grip", "§7of the §bFrost King§7. Cold to the touch."]),
    "elf_candy_cane": dict(
        match=["elf_candy_cane", "candy_cane", "candy cane"],
        name=grad("ᴇʟꜰ ᴄᴀɴᴅʏ ᴄᴀɴᴇ", ["FF4B5C", "FFF6F0", "FF4B5C"]),
        lore=["§x§F§F§4§B§5§C+11 Attack Damage", "§x§F§F§F§6§F§015% chance to send your target floating", "§f",
              "§7Ripped from the tiny, sticky hands", "§7of the §aEvil Elf§7. Peppermint scented."]),
}

def q(s): return "'" + s.replace("'", "''") + "'"

total = 0
for f in glob.glob(sys.argv[1].rstrip("/") + "/AdvancedCrates/Crates/*.yml"):
    lines = open(f, encoding="utf-8").readlines()
    try: start = next(i for i, l in enumerate(lines) if l.rstrip() == "Prizes:")
    except StopIteration: continue
    # prize blocks: '  key:' lines until the next top-level key
    blocks, i = [], start + 1
    while i < len(lines) and (lines[i].startswith(" ") or not lines[i].strip()):
        if re.match(r"^  \S.*:\s*$", lines[i]):
            j = i + 1
            while j < len(lines) and (lines[j].startswith("   ") or not lines[j].strip()): j += 1
            blocks.append((i, j)); i = j
        else: i += 1
    changed = False
    for a, b in reversed(blocks):
        text = "".join(lines[a:b]).lower()
        which = None
        for k, v in ITEMS.items():
            if any(m in text for m in v["match"]): which = k
        if not which or "material: netherite_sword" not in text: continue  # only the swords themselves
        blk = lines[a:b]
        # drop old Name / Lores (incl. wrapped continuation lines)
        out, k = [], 0
        while k < len(blk):
            if re.match(r"^    (Name|Lores):", blk[k]):
                k += 1
                while k < len(blk) and (blk[k].startswith("      ") or blk[k].startswith("    - ")): k += 1
                continue
            out.append(blk[k]); k += 1
        it = ITEMS[which]
        out.append(f"    Name: {q(it['name'])}\n")
        out.append("    Lores:\n" + "".join(f"    - {q(x)}\n" for x in it["lore"]))
        lines[a:b] = out
        changed = True
        total += 1
        print(f"✅ {f.split('/')[-1]}: prize '{blk[0].strip()[:-1]}' -> {which}")
    if changed:
        shutil.copy2(f, f + ".bak-names")
        open(f, "w", encoding="utf-8").writelines(lines)
if not total: print("❌ no Frostfang / Elf Candy Cane prizes found in AdvancedCrates/Crates/*.yml")

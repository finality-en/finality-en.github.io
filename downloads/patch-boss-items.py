#!/usr/bin/env python3
"""Sets the lore + enchants of the raid boss drops in FinalityBosses/config.yml (boss-items)
and the Elf Candy Cane / Frostfang enchants in Nexo/items/finality_bosses.yml. Usage: patch-boss-items.py <plugins dir>"""
import sys, os, re
P = sys.argv[1]
L = {
 "krampus_chain": (["&7Torn from the hands of Krampus.", "", "&c⛓ Chain Pull", "&7Full-strength hits have a &f20% &7chance to", "&7drag your target to you and slow them.", "&8(6 second cooldown)", "", "&8Raid boss drop"],
                   "{sharpness: 5, unbreaking: 3, fire_aspect: 2, looting: 3, sweeping_edge: 3, mending: 1}"),
 "nutcracker_sabre": (["&7The General's parade sword.", "", "&6💥 Crack", "&7Full-strength hits have a &f15% &7chance to", "&7deal &f+4 &7damage and give &fWeakness &7for 3s.", "&8(8 second cooldown)", "", "&8Raid boss drop"],
                   "{sharpness: 5, unbreaking: 3, fire_aspect: 2, looting: 3, sweeping_edge: 3, mending: 1}"),
 "yeti_hide": (["&7Thick white fur over netherite.", "", "&b❤ +2 Hearts &7while worn", "&b🛡 +15% Knockback Resistance", "&b⛨ Netherite-strength armour", "", "&8Raid boss drop"],
                   "{protection: 4, unbreaking: 3, thorns: 3, mending: 1}"),
 "hex_wand": (["&7Still crackling with frost magic.", "", "&5☠ Hex &7- hits have a &f30% &7chance to", "&7  give &fWither II &7for 3s &8(4s cooldown)", "&d✦ Right click: Hex Bolt &7- fires a bolt that", "&7  deals &f6 &7damage, Withers and Slows", "&8  (12 second cooldown)", "&7Hits as hard as a diamond sword.", "", "&8Raid boss drop"],
                   "{sharpness: 5, fire_aspect: 2, looting: 3, unbreaking: 3}"),
 "soulreaper": (["&7The Hollow King's axe.", "", "&3♥ Lifesteal", "&7Full-strength hits heal you for &f15%", "&7of the damage you deal &8(max 1.5 hearts a hit)", "", "&8Raid boss drop"],
                   "{sharpness: 5, efficiency: 5, unbreaking: 3, fortune: 3, mending: 1}"),
}
def yq(s): return "'" + s.replace("'", "''") + "'"
c = os.path.join(P, "FinalityBosses/config.yml")
lines = open(c, encoding="utf-8").read().split("\n")
out, cur, inb, done = [], None, False, set()
for ln in lines:
    if re.match(r"^boss-items:\s*$", ln): inb = True; out.append(ln); continue
    if inb and re.match(r"^\S", ln): inb = False; cur = None
    m = re.match(r"^  ([a-z0-9_]+):\s*$", ln) if inb else None
    if m: cur = m.group(1)
    if inb and cur in L and re.match(r"^    lore:", ln):
        out.append("    lore: [" + ", ".join(yq(x) for x in L[cur][0]) + "]"); done.add(cur + ".lore"); continue
    if inb and cur in L and re.match(r"^    enchants:", ln):
        out.append("    enchants: " + L[cur][1]); done.add(cur + ".enchants"); continue
    out.append(ln)
open(c, "w", encoding="utf-8").write("\n".join(out))
for k in L:
    for f in ("lore", "enchants"):
        print(("✅ " if k + "." + f in done else "❌ missing ") + k + " " + f)
# Nexo: Elf Candy Cane + Frostfang fully enchanted (keeps their damage as you set it)
n = None
for root, _, files in os.walk(os.path.join(P, "Nexo/items")):
    for f in files:
        if f.endswith(".yml") and re.search(r"(?m)^elf_candy_cane:", open(os.path.join(root, f), encoding="utf-8").read()): n = os.path.join(root, f)
if not n: print("❌ Elf Candy Cane not found in Nexo items"); sys.exit()
full = ["sharpness: 5", "unbreaking: 3", "fire_aspect: 2", "looting: 3", "sweeping_edge: 3", "mending: 1"]
lines = open(n, encoding="utf-8").read().split("\n"); out = []; cur = None; i = 0
while i < len(lines):
    ln = lines[i]; m = re.match(r"^([a-z0-9_]+):\s*$", ln)
    if m: cur = m.group(1)
    if cur in ("elf_candy_cane", "frostfang") and re.match(r"^  Enchantments:\s*$", ln):
        out.append(ln); i += 1; have = {}
        while i < len(lines) and re.match(r"^    \S", lines[i]):
            k, _, v = lines[i].strip().partition(":"); have[k] = v.strip(); i += 1
        for e in full:
            k, v = e.split(": ")
            out.append("    %s: %s" % (k, max(int(have.get(k, 0) or 0), int(v))))
        for k, v in have.items():
            if k not in [e.split(":")[0] for e in full]: out.append("    %s: %s" % (k, v))
        print("✅ " + cur + " fully enchanted"); continue
    out.append(ln); i += 1
open(n, "w", encoding="utf-8").write("\n".join(out))

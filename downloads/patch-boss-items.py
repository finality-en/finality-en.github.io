#!/usr/bin/env python3
"""Sets the lore + enchants of the raid boss drops in FinalityBosses/config.yml (boss-items)
and the Elf Candy Cane / Frostfang enchants in Nexo/items/finality_bosses.yml. Usage: patch-boss-items.py <plugins dir>"""
import sys, os, re
P = sys.argv[1]
L = {
 "yeti_hide": (["&7Thick white fur over netherite.", "", "&b❤ +2 Hearts &7while worn", "&b🛡 +15% Knockback Resistance", "&b⛨ Netherite-strength armour", "", "&8Raid boss drop"],
                   "{protection: 4, unbreaking: 3, thorns: 3, mending: 1}"),
}
WEAPONS = r"""  krampus_chain:
    nexo-id: krampus_chain
    material: NETHERITE_SWORD
    name: '&#FF3B2F&lᴋ&#F4382C&lʀ&#E8342A&lᴀ&#DD3127&lᴍ&#D12D25&lᴘ&#C62A22&lᴜ&#BB2620&lꜱ&#AF231D&l'' &#991C18&lᴄ&#8D1816&lʜ&#821513&lᴀ&#761111&lɪ&#6B0E0E&lɴ'
    # ── stats (totals, like the vanilla tooltip; Sharpness adds on top). Astral Riftblade = 12 damage, 1.6 speed
    damage: 15
    attack-speed: 1.6
    lore: ['&7Torn from the hands of Krampus.', '', '&c⛓ Chain Pull', '&7Full-strength hits have a &f{pull.chance}% &7chance to', '&7drag your target to you and slow them for &f{pull.slow-seconds}s&7.', '&8({pull.cooldown-seconds} second cooldown)', '', '&8Raid boss drop']
    enchants: {sharpness: 5, unbreaking: 3, fire_aspect: 2, looting: 3, sweeping_edge: 3, mending: 1}
    on-hit:
      pull: {chance: 25, cooldown-seconds: 5, strength: 1.0, slow-seconds: 2}
  nutcracker_sabre:
    nexo-id: nutcracker_sabre
    material: NETHERITE_SWORD
    name: '&#FF4B5C&lɴ&#FF535B&lᴜ&#FF5B5A&lᴛ&#FF6359&lᴄ&#FF6B58&lʀ&#FF7357&lᴀ&#FF7B56&lᴄ&#FF8355&lᴋ&#FF8B54&lᴇ&#FF9252&lʀ&#FF9A51&l''&#FFA250&lꜱ &#FFB24E&lꜱ&#FFBA4D&lᴀ&#FFC24C&lʙ&#FFCA4B&lʀ&#FFD24A&lᴇ'
    damage: 14
    attack-speed: 1.8
    lore: ['&7The General''s parade sword.', '', '&6💥 Crack', '&7Full-strength hits have a &f{crack.chance}% &7chance to', '&7deal &f+{crack.bonus-damage} &7damage and give &fWeakness &7for &f{crack.seconds}s&7.', '&8({crack.cooldown-seconds} second cooldown)', '', '&8Raid boss drop']
    enchants: {sharpness: 5, unbreaking: 3, fire_aspect: 2, looting: 3, sweeping_edge: 3, mending: 1}
    on-hit:
      crack: {chance: 25, cooldown-seconds: 6, bonus-damage: 6, seconds: 4}
  hex_wand:
    nexo-id: hex_wand
    material: BLAZE_ROD
    name: '&#D9A0FF&lʜ&#C98FFA&lᴇ&#B97FF4&lx &#9A5DE9&lᴡ&#8A4CE4&lᴀ&#7A3CDE&lɴ&#6A2BD9&lᴅ'
    damage: 13
    attack-speed: 1.6
    lore: ['&7Still crackling with frost magic.', '', '&5☠ Hex &7- hits have a &f{wither.chance}% &7chance to', '&7  give &fWither {wither.level} &7for &f{wither.seconds}s &8({wither.cooldown-seconds}s cooldown)', '&d✦ Right click: Hex Bolt &7- fires a bolt that', '&7  deals &f{on-use.damage} &7damage, Withers and Slows', '&8  ({on-use.cooldown-seconds} second cooldown)', '', '&8Raid boss drop']
    enchants: {sharpness: 5, fire_aspect: 2, looting: 3, unbreaking: 3}
    on-hit:
      wither: {chance: 35, cooldown-seconds: 4, seconds: 4, level: 2}
    on-use:
      type: hex-bolt
      damage: 8
      effects: 'wither:80:1,slowness:60:1'
      cooldown-seconds: 10
  soulreaper:
    nexo-id: soulreaper
    material: NETHERITE_AXE
    name: '&#D8FDFF&lꜱ&#C5F5F9&lᴏ&#B2EEF3&lᴜ&#9EE6ED&lʟ&#8BDEE7&lʀ&#78D7E1&lᴇ&#65CFDB&lᴀ&#51C7D5&lᴘ&#3EC0CF&lᴇ&#2BB8C9&lʀ'
    damage: 17
    attack-speed: 1.0
    lore: ['&7The Hollow King''s axe.', '', '&3♥ Lifesteal', '&7Full-strength hits heal you for &f{lifesteal.percent}%', '&7of the damage you deal &8(max {lifesteal.max-heal} HP a hit)', '', '&8Raid boss drop']
    enchants: {sharpness: 5, efficiency: 5, unbreaking: 3, fortune: 3, mending: 1}
    on-hit:
      lifesteal: {percent: 25, max-heal: 4, full-swing-only: true, sound: false}
"""
def yq(s): return "'" + s.replace("'", "''") + "'"
c = os.path.join(P, "FinalityBosses/config.yml")
# 1) raid weapons: replace their whole block (stats, lore, enchants, abilities)
blocks, cur = {}, None
for ln in WEAPONS.split("\n"):
    m = re.match(r"^  ([a-z_]+):\s*$", ln)
    if m: cur = m.group(1); blocks[cur] = []
    if cur: blocks[cur].append(ln)
lines = open(c, encoding="utf-8").read().split("\n"); out = []; inb = False; i = 0; replaced = set()
while i < len(lines):
    ln = lines[i]
    if re.match(r"^boss-items:\s*$", ln): inb = True; out.append(ln); i += 1; continue
    if inb and re.match(r"^\S", ln): inb = False
    m = re.match(r"^  ([a-z_]+):\s*$", ln) if inb else None
    if m and m.group(1) in blocks:
        out += blocks[m.group(1)]; replaced.add(m.group(1)); i += 1
        while i < len(lines) and (lines[i].startswith("    ") or (lines[i].strip() == "" and i + 1 < len(lines) and lines[i + 1].startswith("    "))): i += 1
        continue
    out.append(ln); i += 1
for k in blocks: print(("✅ " if k in replaced else "❌ not found: ") + k + (" - damage/speed/abilities/lore/enchants set" if k in replaced else ""))
lines = out
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

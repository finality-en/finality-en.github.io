#!/usr/bin/env python3
"""Repairs the Elf Candy Cane float ability in FinalityItems/config.yml (on-hit.elf_candy_cane).
Prints what was there, then writes a known-good block. Usage: fix-onhit.py <FinalityItems/config.yml>"""
import sys, re
p = sys.argv[1]
lines = open(p, encoding="utf-8").read().split("\n")
GOOD = """  elf_candy_cane:
    chance: 15
    effect: LEVITATION
    level: 1
    seconds: 2
    cooldown: 4
    players-only: false
    sound: {name: entity.shulker.shoot, volume: 1.0, pitch: 1.4}
    particle: false""".split("\n")
try:
    start = next(i for i, l in enumerate(lines) if re.match(r"^on-hit:\s*$", l))
except StopIteration:
    lines += ["", "on-hit:"]; start = len(lines) - 1
end = start + 1
while end < len(lines) and (lines[end].startswith(" ") or lines[end].strip() == "" or lines[end].lstrip().startswith("#") and lines[end].startswith(" ")):
    end += 1
block = lines[start + 1:end]
old, out, i = [], [], 0
while i < len(block):
    if re.match(r"^  elf_candy_cane:", block[i]):
        old.append(block[i]); i += 1
        while i < len(block) and (block[i].startswith("    ") or block[i].strip() == ""):
            if block[i].strip(): old.append(block[i])
            i += 1
        continue
    out.append(block[i]); i += 1
print("Elf Candy Cane on-hit before:\n  " + ("\n  ".join(old) if old else "(missing!)"))
while out and out[-1].strip() == "": out.pop()
new = lines[:start + 1] + out + GOOD + [""] + lines[end:]
open(p, "w", encoding="utf-8").write("\n".join(new))
print("✅ Elf Candy Cane: 15% chance to float the target for 2s (players + mobs)")

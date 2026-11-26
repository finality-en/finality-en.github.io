#!/usr/bin/env python3
"""Evil Elf coin rewards x2 (FinalityBosses), challenge reward coins x2 and streak rewards x2 (FinalityChallenges).
Usage: coins-2x.py <plugins dir>. Backups *.bak-2x-<time>. Each part only runs once (marker comment)."""
import re, sys, shutil, time
P = sys.argv[1].rstrip("/")
stamp = time.strftime("%Y%m%d-%H%M%S")

def block_end(lines, i, ind):
    j = i + 1
    while j < len(lines) and (not lines[j].strip() or lines[j].lstrip().startswith("#") or len(lines[j]) - len(lines[j].lstrip()) > ind): j += 1
    return j

def dbl_coins(l): return re.sub(r"(coins give \{player\} )(\d+)", lambda m: m.group(1) + str(int(m.group(2)) * 2), l)
def dbl_all(l):
    l = dbl_coins(l)
    return re.sub(r"((?:challenge (?:voucher )?give|ac key give) \{player\} \S+ )(\d+)", lambda m: m.group(1) + str(int(m.group(2)) * 2), l)

def edit(path, marker, fn):
    lines = open(path, encoding="utf-8").readlines()
    if any(marker in l for l in lines): print("= already done:", marker); return
    new = fn(lines)
    if new is None: print("? not found:", marker); return
    shutil.copy2(path, f"{path}.bak-2x-{stamp}")
    open(path, "w", encoding="utf-8").writelines([f"# {marker}\n"] + new)
    print("✅", marker)

# Evil Elf
def elf(lines):
    for i, l in enumerate(lines):
        m = re.match(r"^(\s*)evil_elf:\s*$", l)
        if not m: continue
        j = block_end(lines, i, len(m.group(1)))
        if not any("participation" in x for x in lines[i:j]): continue
        before = "".join(lines[i:j])
        lines[i:j] = [dbl_coins(x) for x in lines[i:j]]
        for a, b in zip(re.findall(r"coins give \{player\} (\d+)", before), re.findall(r"coins give \{player\} (\d+)", "".join(lines[i:j]))): print(f"   elf {a} -> {b}")
        return lines
    return None
edit(f"{P}/FinalityBosses/config.yml", "evil elf coins doubled", elf)

# Challenges
def chal(lines):
    found = False
    for key, fn in (("streaks", dbl_all), ("rewards", dbl_coins)):
        i = next((n for n, l in enumerate(lines) if re.match(rf"^{key}:\s*$", l)), None)
        if i is None: continue
        j = block_end(lines, i, 0)
        before = "".join(lines[i:j])
        lines[i:j] = [fn(x) for x in lines[i:j]]
        print(f"   {key}: coins", re.findall(r"coins give \{player\} (\d+)", before), "->", re.findall(r"coins give \{player\} (\d+)", "".join(lines[i:j])))
        found = True
    return lines if found else None
edit(f"{P}/FinalityChallenges/config.yml", "challenge coins + streaks doubled", chal)

#!/usr/bin/env python3
"""Relic crate: the Hex Wand prize is given ONLY by command (real boss item with its damage), never the preview copy.
Usage: relic-hex-cmd.py <plugins dir>"""
import re, sys, shutil, time
f = sys.argv[1].rstrip("/") + "/AdvancedCrates/Crates/relic.yml"
L = open(f, encoding="utf-8").read().split("\n")
start = next(i for i, l in enumerate(L) if l.rstrip() == "Prizes:")
i = start + 1; done = False
while i < len(L) and (L[i].startswith(" ") or not L[i].strip()):
    if re.match(r"^  \S.*:\s*$", L[i]):
        j = i + 1
        while j < len(L) and (L[j].startswith("   ") or not L[j].strip()): j += 1
        blk = "\n".join(L[i:j]).lower()
        if "hex_wand" in blk or "ʜᴇx ᴡᴀɴᴅ" in blk or "hex wand" in blk:
            print("=== BEFORE"); print("\n".join(x for x in L[i:j] if not x.strip().startswith(("NBTtags", "'{")) and len(x) < 200))
            out, k = [], i + 1
            while k < j:
                x = L[k]
                if re.match(r"^    (GiveConfiguratedItem|Commands):", x):
                    k += 1
                    while k < j and re.match(r"^    - ", L[k]): k += 1
                    continue
                out.append(x); k += 1
            out += ["    GiveConfiguratedItem: false", "    Commands:", "    - fboss item hex_wand %player%"]
            L[i + 1:j] = out
            shutil.copy2(f, f + ".bak-hexcmd-" + time.strftime("%Y%m%d-%H%M%S"))
            open(f, "w", encoding="utf-8").write("\n".join(L))
            print("✅ Hex Wand prize now gives the real item by command: fboss item hex_wand %player%")
            done = True
            break
        i = j
    else: i += 1
if not done: print("❌ no Hex Wand prize in relic.yml")

#!/usr/bin/env python3
"""Adds a 'NEXT WARZONE REGEN' line under the 'NEXT EVIL ELF' line in TAB, same style. Safe to run again.
Usage: tab-warzone.py <plugins/TAB folder>"""
import os, re, sys
T = sys.argv[1]
PH = re.compile(r"%finalitybosses_(next_formatted|next|boss)%")
def conv(line):
    l = line.replace("&a&lᴇᴠɪʟ ᴇʟꜰ", "&c&lᴡᴀʀᴢᴏɴᴇ ʀᴇɢᴇɴ").replace("ᴇᴠɪʟ ᴇʟꜰ", "ᴡᴀʀᴢᴏɴᴇ ʀᴇɢᴇɴ")
    return PH.sub("%finalitybosses_warzone_regen%", l)
done = 0
for root, _, files in os.walk(T):
    for f in files:
        if not f.endswith(".yml"): continue
        p = os.path.join(root, f)
        L = open(p, encoding="utf-8").read().split("\n")
        if any("finalitybosses_warzone_regen" in l for l in L):
            print(f"  already there: {p.replace(T, 'TAB')}"); done += 1; continue
        out, i, changed = [], 0, False
        while i < len(L):
            l = L[i]; out.append(l)
            if "ᴇᴠɪʟ ᴇʟꜰ" in l:
                if PH.search(l):
                    out.append(conv(l)); changed = True
                elif i + 1 < len(L) and PH.search(L[i + 1]):
                    out.append(L[i + 1]); out.append(conv(l)); out.append(conv(L[i + 1])); i += 1; changed = True
                else:
                    print(f"  ? found the EVIL ELF line in {p.replace(T, 'TAB')} line {i+1} but no %finalitybosses_...% next to it:\n      {l.strip()}")
            i += 1
        if changed:
            open(p + ".bak-warzone", "w", encoding="utf-8").write("\n".join(L))
            open(p, "w", encoding="utf-8").write("\n".join(out))
            print(f"✅ added to {p.replace(T, 'TAB')}:")
            for x in out:
                if "warzone_regen" in x or "ᴡᴀʀᴢᴏɴᴇ ʀᴇɢᴇɴ" in x: print("      " + x.strip())
            done += 1
if not done: print("❌ couldn't find the NEXT EVIL ELF line in TAB - add this placeholder by hand: %finalitybosses_warzone_regen%")

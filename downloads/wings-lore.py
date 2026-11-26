#!/usr/bin/env python3
"""Adds 'how to attach / who sees them' lines to the bottom of the Demon Wings item lore (Nexo items/*.yml). Safe to re-run."""
import glob, re, sys, shutil, time
N = sys.argv[1] + "/Nexo/items"
ADD = ["  - ''",
       "  - <gray>Click onto a chestplate to attach them -",
       "  - <gray>everyone sees them on your back, and you",
       "  - <gray>see them yourself while your offhand is empty."]
for f in glob.glob(N + "/**/*.yml", recursive=True):
    s = open(f, encoding="utf-8").read()
    m = re.search(r"(?ms)^demon_wings:\n.*?(?=^\S|\Z)", s)
    if not m: continue
    block = m.group(0)
    if "Click onto a chestplate" in block: print("= Demon Wings lore already updated"); continue
    lm = re.search(r"(?m)^  lore:\n((?:  - .*\n)+)", block)
    if not lm: print("? no lore section in", f); continue
    nb = block[:lm.end()] + "\n".join(ADD) + "\n" + block[lm.end():]
    shutil.copy2(f, f + ".bak-" + time.strftime("%Y%m%d-%H%M%S"))
    open(f, "w", encoding="utf-8").write(s[:m.start()] + nb + s[m.end():])
    print("✅ Demon Wings lore updated in", f.split("/")[-1])

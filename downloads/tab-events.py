#!/usr/bin/env python3
"""Restyles the 'NEXT ...' event lines in the TAB header into a clean EVENTS block. Usage: tab-events.py <plugins/TAB>
Keeps whatever placeholders your current lines use; adds the Frost King. Backup: *.bak-events. Safe to re-run."""
import re, sys, glob, shutil

def ph(line):
    m = re.findall(r"%[^%\s]+%", line)
    return m[0] if m else None

def build(indent, q, found):
    koth = found.get("koth", "%finalitybosses_koth%")
    elf = found.get("elf", "%finalitybosses_next%")
    regen = found.get("regen", "%finalitybosses_warzone_regen%")
    rows = [
        "&8&m                  &r  &#FFD36E&lᴇᴠᴇɴᴛꜱ  &8&m                  ",
        f"&#FFD36E⚔ ᴋᴏᴛʜ &8» &f{koth} &8ꜱᴘᴀᴡɴ",
        f"&#7DFF8A☃ ᴇᴠɪʟ ᴇʟꜰ &8» &f{elf} &8ᴡᴀʀᴢᴏɴᴇ",
        "&#8FD8FF❄ ꜰʀᴏꜱᴛ ᴋɪɴɢ &8» &f%finalitybosses_frost% &8ᴡᴀʀᴢᴏɴᴇ",
        f"&#FF7A7A⏳ ᴡᴀʀᴢᴏɴᴇ ʀᴇɢᴇɴ &8» &f{regen}",
    ]
    out = []
    for r in rows:
        if q == "'": r = r.replace("'", "''")
        out.append(f"{indent}- {q}{r}{q}\n")
    return out

done = 0
for f in glob.glob(sys.argv[1].rstrip("/") + "/**/*.yml", recursive=True):
    lines = open(f, encoding="utf-8").readlines()
    out, i, changed = [], 0, False
    while i < len(lines):
        l = lines[i]
        if "ᴇᴠᴇɴᴛꜱ" in l and "&8&m" in l:  # already restyled
            out.append(l); i += 1; continue
        if re.match(r"^\s*-\s", l) and "ɴᴇxᴛ" in l:
            run = []
            while i < len(lines) and re.match(r"^\s*-\s", lines[i]) and "ɴᴇxᴛ" in lines[i]:
                run.append(lines[i]); i += 1
            found = {}
            for r in run:
                p = ph(r)
                if not p: continue
                if "ᴋᴏᴛʜ" in r or "KOTH" in r.upper(): found["koth"] = p
                elif "ᴇʟꜰ" in r: found["elf"] = p
                elif "ʀᴇɢᴇɴ" in r: found["regen"] = p
            m = re.match(r"^(\s*)-\s*(['\"]?)", run[0])
            out += build(m.group(1), m.group(2) or "'", found)
            changed = True
            continue
        out.append(l); i += 1
    if changed:
        shutil.copy2(f, f + ".bak-events")
        open(f, "w", encoding="utf-8").writelines(out)
        print("✅ events restyled in", f.split("/TAB/")[-1]); done += 1
if not done: print("= nothing to change (already done, or no NEXT lines found)")

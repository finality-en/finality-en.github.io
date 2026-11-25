#!/usr/bin/env python3
"""Clone the 'kits' FancyNpcs NPC + FancyHolograms hologram into /perks and /store NPCs.
Run with the server STOPPED. Usage: add-npcs.py <plugins dir>"""
import re, sys, uuid, shutil, time

P = sys.argv[1]
NPCS = f"{P}/FancyNpcs/npcs.yml"
HOLO = f"{P}/FancyHolograms/holograms.yml"
TEMPLATE = "kits"
NEW = [
    # name, command, title, x, y, z, yaw, pitch
    ("perks", "perks", "&6&lPERKS", -12.47, 206.0, -3.52, -30.08, 17.06),
    ("store", "store", "&a&lSTORE", 10.46, 207.0, -10.29, -135.35, 3.48),
]
HOLO_OFFSET = 2.12  # same as your other NPCs (206 -> 208.12)


def blocks(lines, indent):
    """Yield (start, end) of each entry at the given indent under the top-level section."""
    pre = " " * indent
    starts = [i for i, l in enumerate(lines)
              if l.startswith(pre) and len(l) > indent and l[indent] not in " #" and l.rstrip().endswith(":")]
    for s in starts:
        e = s + 1
        while e < len(lines) and (lines[e].strip() == "" or lines[e].startswith(pre + " ")):
            e += 1
        yield s, e


def set_loc(block, x, y, z, yaw, pitch):
    vals = {"x": x, "y": y, "z": z, "yaw": yaw, "pitch": pitch}
    in_loc = False
    for i, l in enumerate(block):
        if re.match(r"^\s+location:\s*$", l):
            in_loc, ind = True, len(l) - len(l.lstrip()) + 2
            continue
        if in_loc:
            m = re.match(r"^(\s+)(x|y|z|yaw|pitch):", l)
            if m and len(m.group(1)) == ind:
                block[i] = f"{m.group(1)}{m.group(2)}: {vals[m.group(2)]}\n"
            elif len(l) - len(l.lstrip()) < ind:
                in_loc = False
    return block


def backup(f):
    b = f"{f}.bak-npcs-{time.strftime('%Y%m%d-%H%M%S')}"
    shutil.copy2(f, b)
    return b


# ---------- NPCs ----------
lines = open(NPCS, encoding="utf-8").readlines()
tpl = None
existing = set()
for s, e in blocks(lines, 2):
    for l in lines[s:e]:
        m = re.match(r"^    name:\s*'?([^'\n]*)'?\s*$", l)
        if m:
            existing.add(m.group(1))
            if m.group(1) == TEMPLATE:
                tpl = (s, e)
if not tpl:
    sys.exit(f"❌ template NPC '{TEMPLATE}' not found in npcs.yml")

out_npc = []
for name, cmd, title, x, y, z, yaw, pitch in NEW:
    if name in existing:
        print(f"⏭  NPC '{name}' already exists, skipped")
        continue
    b = lines[tpl[0]:tpl[1]]
    b[0] = f"  {uuid.uuid4()}:\n"
    b = [re.sub(r"^(    name:).*$", rf"\1 {name}", l) for l in b]
    set_loc(b, x, y, z, yaw, pitch)
    # player_command value -> new command (keeps leading slash style)
    pc = next((i for i, l in enumerate(b) if re.search(r"action:\s*player_command", l)), None)
    done = False
    if pc is not None:
        ind = len(b[pc]) - len(b[pc].lstrip())
        # value may be just before or after the action line within the same entry
        for j in list(range(pc + 1, len(b))) + list(range(pc - 1, -1, -1)):
            lj = b[j]
            if lj.strip() and len(lj) - len(lj.lstrip()) < ind:
                if j > pc:
                    continue
                break
            m = re.match(r"^(\s+value:\s*)(['\"]?)(/?)(.*?)\2\s*$", lj)
            if m and len(lj) - len(lj.lstrip()) == ind:
                b[j] = f"{m.group(1)}{m.group(2)}{m.group(3)}{cmd}{m.group(2)}\n"
                done = True
                break
    if not done:
        sys.exit("❌ couldn't find the kits NPC player_command value; nothing written")
    out_npc.append((name, b))

if out_npc:
    bk = backup(NPCS)
    ins = tpl[1]
    for _, b in out_npc:
        lines[ins:ins] = b
        ins += len(b)
    open(NPCS, "w", encoding="utf-8").writelines(lines)
    print(f"✅ NPCs added: {', '.join(n for n, _ in out_npc)}  (backup {bk})")

# ---------- Holograms ----------
lines = open(HOLO, encoding="utf-8").readlines()
tpl = None
existing = set()
for s, e in blocks(lines, 2):
    key = lines[s].strip()[:-1].strip("'\"")
    existing.add(key.lower())
    if key == TEMPLATE:
        tpl = (s, e)
if not tpl:
    sys.exit(f"❌ template hologram '{TEMPLATE}' not found in holograms.yml")

out_h = []
for name, cmd, title, x, y, z, yaw, pitch in NEW:
    if name in existing:
        print(f"⏭  hologram '{name}' already exists, skipped")
        continue
    b = lines[tpl[0]:tpl[1]]
    b[0] = f"  {name}:\n"
    set_loc(b, x, round(y + HOLO_OFFSET, 2), z, yaw, pitch)
    b = [re.sub(r"^(\s+linkedNpc:).*$", rf"\1 {name}", l) for l in b]
    # text: first line = title, '/kit' line = command
    t = next(i for i, l in enumerate(b) if re.match(r"^\s+text:\s*$", l))
    b[t + 1] = re.sub(r"'.*'", f"'{title}'", b[t + 1])
    for i in range(t + 1, len(b)):
        if re.search(r"'&f/", b[i]):
            b[i] = re.sub(r"'&f/[^']*'", f"'&f/{cmd}'", b[i])
            break
    out_h.append(b)

if out_h:
    bk = backup(HOLO)
    ins = tpl[1]
    for b in out_h:
        lines[ins:ins] = b
        ins += len(b)
    open(HOLO, "w", encoding="utf-8").writelines(lines)
    print(f"✅ holograms added: {len(out_h)}  (backup {bk})")

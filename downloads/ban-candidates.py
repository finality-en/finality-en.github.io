#!/usr/bin/env python3
"""
Finality - ban wave suspects from Vulcan's violations log.
Usage: python3 ban-candidates.py [days=7] [violations.txt path]
Prints a ranked list for STAFF REVIEW. Nothing is banned automatically.
Movement checks false-flag a lot on a SpearMace server (spear lunge, mace, wind charges,
riptide, elytra), so they only count when a player hits HIGH violation levels repeatedly.
"""
import re, sys, os, collections, datetime

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 7
PATH = sys.argv[2] if len(sys.argv) > 2 else "/var/lib/pterodactyl/volumes/9b618852-57d9-4326-b2ae-506798142a97/plugins/Vulcan/violations.txt"
LINE = re.compile(r"^\[(\d\d)-(\d\d)-(\d{4})\] \[(\d\d:\d\d:\d\d)\] (\S+) failed (.+?) \(Type (\w+)\) \[VL: (\d+)\].*?\[Version: ([^\]]*)\]")

# category, weight per flag, VL that counts as "strong", reliable?
CHECKS = {
    # PvP / combat - few false positives
    "KillAura": ("PvP", 6, 5, True), "Aim": ("PvP", 2, 8, True), "Reach": ("PvP", 5, 5, True),
    "Hitbox": ("PvP", 5, 4, True), "AutoClicker": ("PvP", 3, 8, True), "Criticals": ("PvP", 3, 6, True),
    "AutoBlock": ("PvP", 4, 5, True), "FastBow": ("PvP", 3, 6, True),
    # movement - lots of false flags from spears/maces/wind charges: only high VLs matter
    "Flight": ("Movement", 1, 25, False), "Speed": ("Movement", 0.5, 30, False), "Strafe": ("Movement", 1, 20, False),
    "Timer": ("Movement", 2, 15, True), "Motion": ("Movement", 1, 20, False), "Jesus": ("Movement", 2, 10, True),
    "VClip": ("Movement", 3, 5, True), "Step": ("Movement", 1, 15, False), "NoFall": ("Movement", 2, 10, True),
    "Elytra": ("Movement", 1, 15, False), "Jump": ("Movement", 0.2, 40, False), "Velocity": ("Movement", 0.5, 30, False),
    "Sprint": ("Movement", 1, 15, False), "NoSlow": ("Movement", 2, 10, True),
    # other cheats
    "Baritone": ("Exploit", 4, 3, True), "Scaffold": ("Other", 2, 8, True), "Tower": ("Other", 2, 6, True),
    "Invalid": ("Other", 0.5, 20, False), "BadPackets": ("Other", 2, 10, True), "FastPlace": ("Other", 2, 8, True),
    "GroundSpoof": ("Movement", 1, 15, False), "BoatFly": ("Movement", 2, 10, True), "EntitySpeed": ("Movement", 1, 15, False),
    "WallClimb": ("Movement", 2, 8, True), "AntiLevitation": ("Movement", 1, 10, False),
    "FastBreak": ("Other", 1, 15, False), "AirPlace": ("Other", 2, 8, True),
}

cut = datetime.datetime.now() - datetime.timedelta(days=DAYS)
stats = collections.defaultdict(lambda: collections.defaultdict(lambda: {"n": 0, "max": 0, "days": set(), "last": ""}))
clients = {}
if not os.path.exists(PATH):
    sys.exit(f"Can't find {PATH}")
with open(PATH, encoding="utf-8", errors="ignore") as f:
    for line in f:
        m = LINE.match(line)
        if not m: continue
        mo, d, y, t, name, check, typ, vl, ver = m.groups()
        check = check.replace(" ", "")
        when = datetime.datetime(int(y), int(mo), int(d), *map(int, t.split(":")))
        if when < cut: continue
        s = stats[name][check]
        s["n"] += 1; s["max"] = max(s["max"], int(vl)); s["days"].add(when.date()); s["last"] = f"{when:%d %b %H:%M} {check} {typ} VL {vl}"
        clients[name] = ver

rows = []
for name, checks in stats.items():
    score = 0.0; cats = collections.Counter(); strong = []
    for check, s in checks.items():
        cat, w, strong_vl, reliable = CHECKS.get(check, ("Other", 0.5, 20, False))
        part = min(s["n"], 200) * w
        if s["max"] >= strong_vl:
            part *= 2; strong.append(f"{check} max VL {s['max']} ({s['n']} flags, {len(s['days'])} day{'s' if len(s['days'])>1 else ''})")
        elif not reliable:
            part *= 0.25   # noisy check that never got high: mostly spear/mace false flags
        score += part; cats[cat] += part
    if score < 40: continue
    rows.append((score, name, cats.most_common(1)[0][0], strong, checks))

rows.sort(reverse=True)
print(f"Vulcan suspects - last {DAYS} days - {len(rows)} players worth reviewing\n")
print("Confidence: HIGH = strong flags on reliable checks; MEDIUM = high VLs on noisy movement checks; LOW = lots of small flags.")
print("ESP / tracers / x-ray-visuals can NOT be detected by Vulcan - those need staff spectating (/cmi vanish + watch them).\n")
for score, name, cat, strong, checks in rows[:40]:
    reliable_strong = any(CHECKS.get(c.split()[0], ("", 0, 0, False))[3] for c in strong)
    conf = "HIGH" if reliable_strong else ("MEDIUM" if strong else "LOW")
    print(f"[{conf:6}] {name:16} score {score:6.0f}  likely: {cat:8}  client: {clients.get(name,'?')}")
    for s in strong[:4]: print(f"           ! {s}")
    top = sorted(checks.items(), key=lambda kv: -kv[1]['n'])[:4]
    print("           flags: " + ", ".join(f"{c} x{v['n']} (max {v['max']})" for c, v in top))
    print()
print("Next step: spectate the HIGH ones, then queue them:  /banwave add <player> <PvP|Movement|ESP|...> <reason>")

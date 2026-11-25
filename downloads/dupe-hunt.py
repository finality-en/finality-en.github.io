#!/usr/bin/env python3
"""
Finality - who used the dripleaf dupe? Read-only.
  1. Every "SmallDripleafBlock.performBonemeal" error in every log -> bursts (when the dupe was run)
  2. CoreProtect: players who broke the SAME block at the SAME spot again and again without placing it back
     (the dupe leaves the block in place), plus who placed small dripleaf around the bursts
  3. Vulcan flags during the bursts
Usage: sudo python3 dupe-hunt.py [server folder]
"""
import gzip, os, re, sqlite3, sys, collections, datetime, glob, shutil, tempfile

V = sys.argv[1] if len(sys.argv) > 1 else "/var/lib/pterodactyl/volumes/9b618852-57d9-4326-b2ae-506798142a97"
P = os.path.join(V, "plugins")
ERR = "SmallDripleafBlock.performBonemeal"
TS = re.compile(r"^\[(\d\d):(\d\d):(\d\d)\]")

# ---------------------------------------------------------------- 1. log bursts
events = []
files = sorted(glob.glob(os.path.join(V, "logs", "*.log.gz"))) + [os.path.join(V, "logs", "latest.log")]
for f in files:
    m = re.search(r"(\d{4}-\d\d-\d\d)", os.path.basename(f))
    day = m.group(1) if m else datetime.date.fromtimestamp(os.path.getmtime(f)).isoformat()
    opener = gzip.open if f.endswith(".gz") else open
    try:
        with opener(f, "rt", encoding="utf-8", errors="ignore") as fh:
            last = None
            for line in fh:
                t = TS.match(line)
                if t: last = t.groups()
                if ERR in line and last:
                    events.append(datetime.datetime.fromisoformat(f"{day}T{last[0]}:{last[1]}:{last[2]}"))
    except Exception as e:
        print("  (couldn't read", f, e, ")")
events.sort()
bursts = []
for e in events:
    if bursts and (e - bursts[-1][1]).total_seconds() <= 120: bursts[-1][1] = e; bursts[-1][2] += 1
    else: bursts.append([e, e, 1])
print(f"== 1. Dripleaf dupe errors in the logs: {len(events)} in {len(bursts)} bursts")
for a, b, n in bursts[-40:]:
    print(f"   {a:%a %d %b %H:%M:%S} -> {b:%H:%M:%S}  ({n} errors)")
if not bursts:
    print("   none found")

# ---------------------------------------------------------------- 2. CoreProtect
print("\n== 2. CoreProtect")
db = os.path.join(P, "CoreProtect", "database.db")
cfg = os.path.join(P, "CoreProtect", "config.yml")
if os.path.exists(cfg) and re.search(r"(?m)^use-mysql:\s*true", open(cfg, encoding="utf-8", errors="ignore").read()):
    print("   CoreProtect uses MySQL - this script only reads the SQLite file. Use the in-game lookups below instead.")
    db = None
elif not os.path.exists(db):
    print("   no plugins/CoreProtect/database.db found"); db = None
if db:
    print(f"   reading {os.path.getsize(db)/1e6:.0f} MB database (read-only)...")
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    cur = con.cursor()
    users = dict(cur.execute("select id, user from co_user").fetchall())
    mats = dict(cur.execute("select id, material from co_material_map").fetchall())
    worlds = dict(cur.execute("select id, world from co_world").fetchall()) if cur.execute("select name from sqlite_master where name='co_world'").fetchone() else {}
    since = int((bursts[0][0] - datetime.timedelta(days=1)).timestamp()) if bursts else int((datetime.datetime.now() - datetime.timedelta(days=7)).timestamp())

    # blocks that regrow / get farmed - breaking them in the same spot is normal
    FARM = re.compile(r"wheat|carrot|potato|beetroot|sugar_cane|cactus|bamboo|melon|pumpkin|kelp|cocoa|nether_wart|sweet_berr|vine|leaves|grass|fern|flower|tulip|dandelion|poppy|azalea|moss|dripleaf|snow|ice|stone$|cobblestone$|deepslate$|basalt|netherrack|obsidian|fire|water|lava|torch|rail|redstone_wire|tripwire|string|scaffolding|chorus|mushroom|copper|amethyst_cluster|budding|bud$|log$|wood$|stem$|sapling|crop|farmland|dirt$|sand$|gravel|concrete_powder|tnt")
    rows = con.cursor().execute("""select user, wid, x, y, z, type, action, time from co_block
                          where time >= ? and action in (0, 1) order by rowid""", (since,))
    print(f"   checking block breaks/places since {datetime.datetime.fromtimestamp(since):%d %b %H:%M}")
    # per spot: count breaks by the same player with no place in between
    state = {}
    repeated = collections.Counter()
    detail = collections.defaultdict(list)
    for user, wid, x, y, z, typ, action, t in rows:
        key = (wid, x, y, z)
        mat = mats.get(typ, str(typ)).replace("minecraft:", "")
        if action == 1:
            state[key] = None
            continue
        prev = state.get(key)
        if prev and prev[0] == user and prev[1] == mat and t - prev[2] <= 600 and not FARM.search(mat):
            repeated[(user, mat)] += 1
            if len(detail[(user, mat)]) < 3:
                detail[(user, mat)].append(f"{worlds.get(wid, wid)} {x} {y} {z} @ {datetime.datetime.fromtimestamp(t):%d %b %H:%M}")
        state[key] = (user, mat, t)
    print("\n   Same block broken again at the same spot WITHOUT being placed back (the dupe's fingerprint):")
    if not repeated:
        print("   none found")
    by_user = collections.defaultdict(list)
    for (u, mat), n in repeated.most_common():
        by_user[u].append((n, mat))
    for u, lst in sorted(by_user.items(), key=lambda kv: -sum(n for n, _ in kv[1]))[:25]:
        total = sum(n for n, _ in lst)
        print(f"   !! {users.get(u, u):16} {total:5} repeat breaks: " + ", ".join(f"{mat} x{n}" for n, mat in sorted(lst, reverse=True)[:6]))
        for n, mat in sorted(lst, reverse=True)[:2]:
            for d in detail[(u, mat)]: print(f"        e.g. {mat} at {d}")

    print("\n   Small dripleaf placed / broken within 30 min of a dupe burst:")
    found = collections.Counter()
    for a, b, n in bursts:
        lo, hi = int((a - datetime.timedelta(minutes=30)).timestamp()), int((b + datetime.timedelta(minutes=30)).timestamp())
        for u, act, cnt in cur.execute("""select b.user, b.action, count(*) from co_block b join co_material_map m on m.id = b.type
                                          where b.time between ? and ? and m.material like '%small_dripleaf%' group by b.user, b.action""", (lo, hi)):
            found[(users.get(u, u), "placed" if act == 1 else "broke" if act == 0 else "used")] += cnt
    for (u, what), cnt in found.most_common(25):
        print(f"   {u:16} {what} small dripleaf {cnt}x")
    if not found: print("   none (if the times are off, the server clock and log times may differ - check by hand)")
    con.close()

# ---------------------------------------------------------------- 3. Vulcan during bursts
print("\n== 3. Vulcan flags during the dupe bursts (+-5 min)")
vf = os.path.join(P, "Vulcan", "violations.txt")
LINE = re.compile(r"^\[(\d\d)-(\d\d)-(\d{4})\] \[(\d\d):(\d\d):(\d\d)\] (\S+) failed (.+?) \(Type")
hits = collections.Counter()
if os.path.exists(vf) and bursts:
    windows = [(a - datetime.timedelta(minutes=5), b + datetime.timedelta(minutes=5)) for a, b, n in bursts]
    for line in open(vf, encoding="utf-8", errors="ignore"):
        m = LINE.match(line)
        if not m: continue
        mo, d, y, hh, mm, ss, name, check = m.groups()
        t = datetime.datetime(int(y), int(mo), int(d), int(hh), int(mm), int(ss))
        if any(lo <= t <= hi for lo, hi in windows): hits[(name, check)] += 1
for (n, c), k in hits.most_common(20):
    print(f"   {n:16} {c} x{k}")
if not hits: print("   none")
print("\nNext: confirm in game with  /co lookup u:<name> t:7d a:-block  (look for one valuable block broken over and over at one spot)")

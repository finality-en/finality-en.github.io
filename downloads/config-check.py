#!/usr/bin/env python3
"""
Finality - finds config problems that break things silently. Read-only.
  1. Any YAML key written twice in the same section (the server keeps the LAST one and ignores the first)
  2. YAML files that don't load at all
  3. Nexo item ids defined in more than one file
  4. Ability configs pointing at item ids that don't exist (FinalityItems on-hit, FinalityBosses weapon-effects / boss-items)
Usage: sudo python3 config-check.py [server folder]
"""
import os, sys, re, collections
try:
    import yaml
except ImportError:
    sys.exit("This needs PyYAML:  sudo apt install python3-yaml")

V = sys.argv[1] if len(sys.argv) > 1 else "/var/lib/pterodactyl/volumes/9b618852-57d9-4326-b2ae-506798142a97"
P = os.path.join(V, "plugins")
SKIP_DIRS = re.compile(r"(?i)/(userdata|playerdata|players|data|cache|logs|backups?|libs?|lang|languages|locale|translations|storage|database|stats|pack/assets)(/|$)")
MAX_SIZE = 2_000_000


class DupLoader(yaml.SafeLoader):
    pass


def construct_mapping(loader, node, deep=False):
    seen = {}
    for key_node, _ in node.value:
        try:
            k = loader.construct_object(key_node, deep=deep)
        except Exception:
            continue
        if isinstance(k, (list, dict)):
            continue
        if k in seen:
            loader.dups.append((str(k), seen[k] + 1, key_node.start_mark.line + 1))
        else:
            seen[k] = key_node.start_mark.line
    return yaml.SafeLoader.construct_mapping(loader, node, deep=deep)


DupLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)


def load(path):
    loader = DupLoader(open(path, encoding="utf-8", errors="ignore"))
    loader.dups = []
    try:
        data = loader.get_single_data()
    finally:
        loader.dispose()
    return data, loader.dups


files = []
for root, dirs, fs in os.walk(P):
    rel = root.replace(P, "")
    if SKIP_DIRS.search(rel + "/"):
        dirs[:] = []
        continue
    for f in fs:
        if f.endswith((".yml", ".yaml")):
            fp = os.path.join(root, f)
            if os.path.getsize(fp) <= MAX_SIZE:
                files.append(fp)
for f in ("bukkit.yml", "spigot.yml", "purpur.yml", "commands.yml"):
    if os.path.exists(os.path.join(V, f)): files.append(os.path.join(V, f))
for f in os.listdir(os.path.join(V, "config")) if os.path.isdir(os.path.join(V, "config")) else []:
    if f.endswith(".yml"): files.append(os.path.join(V, "config", f))

print(f"Checked {len(files)} config files\n")
dup_files, broken, loaded = [], [], {}
for fp in sorted(files):
    short = fp.replace(V + "/", "")
    try:
        data, dups = load(fp)
        loaded[fp] = data
        if dups: dup_files.append((short, dups))
    except Exception as e:
        broken.append((short, str(e).split("\n")[0][:150] + " | " + " ".join(str(e).split("\n")[1:3]).strip()[:120]))

print("== 1. Settings written twice (the FIRST copy is ignored):")
if not dup_files: print("   none 👍")
for short, dups in dup_files:
    print(f"   {short}")
    for k, a, b in dups[:12]:
        print(f"      '{k}' on line {a} and again on line {b}  -> line {b} wins")
    if len(dups) > 12: print(f"      ...and {len(dups) - 12} more")

print("\n== 2. Config files that don't load (the plugin falls back to its defaults):")
if not broken: print("   none 👍")
for short, err in broken:
    print(f"   {short}\n      {err}")

# ---------------------------------------------------------------- Nexo ids
nexo_ids = collections.defaultdict(list)
nexo_dir = os.path.join(P, "Nexo", "items")
for root, _, fs in os.walk(nexo_dir):
    for f in fs:
        if not f.endswith(".yml"): continue
        fp = os.path.join(root, f)
        try:
            data = loaded.get(fp) or load(fp)[0]
        except Exception:
            continue
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, dict): nexo_ids[k].append(fp.replace(nexo_dir + "/", ""))
print(f"\n== 3. Nexo item ids in more than one file ({len(nexo_ids)} items total):")
multi = {k: v for k, v in nexo_ids.items() if len(v) > 1}
if not multi: print("   none 👍")
for k, v in sorted(multi.items()):
    print(f"   {k}: {', '.join(v)}")


# ---------------------------------------------------------------- references
def get(path, *keys):
    d = loaded.get(os.path.join(P, path))
    if d is None and os.path.exists(os.path.join(P, path)):
        try: d = load(os.path.join(P, path))[0]
        except Exception: d = None
    for k in keys:
        d = d.get(k) if isinstance(d, dict) else None
    return d


print("\n== 4. Abilities pointing at items that don't exist in Nexo:")
problems = 0
for k in (get("FinalityItems/config.yml", "on-hit") or {}):
    if k not in nexo_ids: print(f"   FinalityItems on-hit '{k}' - no Nexo item with that id"); problems += 1
for k in (get("FinalityBosses/config.yml", "weapon-effects") or {}):
    if k not in nexo_ids: print(f"   FinalityBosses weapon-effects '{k}' - no Nexo item with that id"); problems += 1
for k, v in (get("FinalityBosses/config.yml", "boss-items") or {}).items():
    nid = v.get("nexo-id") if isinstance(v, dict) else None
    if nid and nid not in nexo_ids: print(f"   FinalityBosses boss-items '{k}' uses nexo-id '{nid}' - not found"); problems += 1
wid = get("FinalityItems/config.yml", "demon-wings", "nexo-id") or "demon_wings"
if wid not in nexo_ids: print(f"   FinalityItems demon-wings nexo-id '{wid}' - not found"); problems += 1
if not problems: print("   none 👍")

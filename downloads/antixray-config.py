#!/usr/bin/env python3
"""Paper Anti-Xray + RayTraceAntiXray set to the recommended setup (Paper docs + stonar96's recommended gist).
Only touches the anticheat.anti-xray sections and RayTraceAntiXray/config.yml. Backs everything up.
Run with the SMP stopped:  python3 antixray-config.py <server volume>"""
import re, sys, os, shutil, time

V = sys.argv[1]
stamp = time.strftime('%Y%m%d-%H%M%S')

OVERWORLD = """  anti-xray:
    enabled: true
    engine-mode: 1
    hidden-blocks:
    # engine-mode 1 swaps these for stone/deepslate when fully covered;
    # RayTraceAntiXray hides the ones exposed to air (caves) too.
    - mossy_cobblestone
    - spawner
    - chest
    - coal_ore
    - deepslate_coal_ore
    - copper_ore
    - deepslate_copper_ore
    - raw_copper_block
    - diamond_ore
    - deepslate_diamond_ore
    - emerald_ore
    - deepslate_emerald_ore
    - gold_ore
    - deepslate_gold_ore
    - iron_ore
    - deepslate_iron_ore
    - raw_iron_block
    - lapis_ore
    - deepslate_lapis_ore
    - redstone_ore
    - deepslate_redstone_ore
    # ores touching lava count as covered (otherwise lava "exposes" them to x-ray)
    lava-obscures: true
    # high enough for coal/iron/copper under hills too (diamonds, gold, lapis, redstone are all far below)
    max-block-height: 128
    # not used in engine-mode 1
    replacement-blocks: []
    update-radius: 2
    use-permission: false
"""
NETHER = """  anti-xray:
    enabled: true
    engine-mode: 1
    hidden-blocks:
    - ancient_debris
    - nether_gold_ore
    - nether_quartz_ore
    lava-obscures: true
    max-block-height: 128
    replacement-blocks: []
    update-radius: 2
    use-permission: false
"""
END = """  anti-xray:
    enabled: false
"""
RTAX = """# Finality: strict settings - x-ray / freecam can't reveal valuables the player can't actually see.
settings:
  anti-xray:
    update-ticks: 1
    ms-per-ray-trace-tick: 50
    ray-trace-threads: {THREADS}
world-settings:
  default:
    anti-xray:
      ray-trace: true
      # false = ores are only revealed from the player's real first-person eye, so F5 / freecam cameras reveal nothing
      ray-trace-third-person: false
      # maxed out: the whole view distance (server.properties view-distance x 16)
      ray-trace-distance: {DIST}
      # re-hide ores again once the player can no longer see them
      rehide-blocks: true
      rehide-distance: {REHIDE}
      max-ray-trace-block-count-per-chunk: 100
      ray-trace-blocks:
      - diamond_ore
      - deepslate_diamond_ore
      - emerald_ore
      - deepslate_emerald_ore
      - gold_ore
      - deepslate_gold_ore
      - lapis_ore
      - deepslate_lapis_ore
      - chest
      - spawner
      - mossy_cobblestone
  world_nether:
    anti-xray:
      # debris in cave walls / next to tunnels other players dug stays hidden until you can see it
      ray-trace: true
      max-ray-trace-block-count-per-chunk: 60
      ray-trace-blocks:
      - ancient_debris
  world_the_end:
    anti-xray:
      ray-trace: false
"""

vd = 10
try:
    m = re.search(r'(?m)^view-distance=(\d+)', open(V + '/server.properties', encoding='utf-8').read())
    if m: vd = max(2, int(m.group(1)))
except FileNotFoundError:
    pass
thr = max(2, min(4, (os.cpu_count() or 8) // 4))
RTAX = RTAX.replace('{THREADS}', str(thr))
RTAX = RTAX.replace('{DIST}', f'{vd * 16}.0').replace('{REHIDE}', f'{vd * 16 - 4}.0')
print(f'= {thr} ray-trace threads'); print(f'= view-distance {vd} -> ray-trace distance {vd * 16} blocks')

def backup(f):
    if os.path.exists(f):
        shutil.copy2(f, f + '.bak-antixray-' + stamp)

def set_antixray(f, block, create=False):
    if not os.path.exists(f):
        if not create:
            print('= skipped (missing):', os.path.relpath(f, V)); return
        open(f, 'w', encoding='utf-8').write('anticheat:\n' + block)
        print('✅ created', os.path.relpath(f, V)); return
    s = open(f, encoding='utf-8').read()
    lines = s.splitlines(keepends=True)
    out, i, done = [], 0, False
    while i < len(lines):
        ln = lines[i]
        if re.match(r'^anticheat:\s*$', ln):
            out.append(ln); i += 1
            sec = []
            while i < len(lines) and (lines[i].startswith(' ') or lines[i].strip() == ''):
                sec.append(lines[i]); i += 1
            # drop the existing "  anti-xray:" child (and everything indented under it), keep siblings
            kept, j = [], 0
            while j < len(sec):
                if re.match(r'^  anti-xray:\s*$', sec[j]):
                    j += 1
                    while j < len(sec) and (sec[j].startswith('   ') or sec[j].strip() == ''):
                        j += 1
                    continue
                kept.append(sec[j]); j += 1
            out.append(block); out.extend(kept); done = True
            continue
        out.append(ln); i += 1
    if not done:
        out.append(('' if s.endswith('\n') or not s else '\n') + 'anticheat:\n' + block)
    s2 = ''.join(out)
    if s2 != s:
        backup(f); open(f, 'w', encoding='utf-8').write(s2)
        print('✅ anti-xray set in', os.path.relpath(f, V))
    else:
        print('= already correct:', os.path.relpath(f, V))

set_antixray(V + '/config/paper-world-defaults.yml', OVERWORLD)
nether = next((p for p in [V + '/world_nether/paper-world.yml', V + '/world/dimensions/minecraft/the_nether/paper-world.yml'] if os.path.isdir(os.path.dirname(p))), None)
end = next((p for p in [V + '/world_the_end/paper-world.yml', V + '/world/dimensions/minecraft/the_end/paper-world.yml'] if os.path.isdir(os.path.dirname(p))), None)
if nether: set_antixray(nether, NETHER, create=True)
if end: set_antixray(end, END, create=True)
# a per-world file for the overworld must not override the defaults with an old anti-xray block
ow = V + '/world/paper-world.yml'
if os.path.exists(ow) and re.search(r'(?m)^  anti-xray:', open(ow, encoding='utf-8').read()):
    set_antixray(ow, OVERWORLD)

rt = V + '/plugins/RayTraceAntiXray/config.yml'
os.makedirs(os.path.dirname(rt), exist_ok=True)
if not os.path.exists(rt) or open(rt, encoding='utf-8').read() != RTAX:
    backup(rt); open(rt, 'w', encoding='utf-8').write(RTAX)
    print('✅ RayTraceAntiXray config set (strict)')
else:
    print('= RayTraceAntiXray config already correct')
print('= anti-xray configs done')

#!/usr/bin/env python3
"""RaycastedAntiESP: anti-freecam / ESP tuning for Finality. Safe to run again.
- players are hidden behind walls even when NOT sneaking (default here was sneak-only)
- chests/signs/spawners etc. re-hide once out of sight (default: stay visible forever once seen)
- drops the 1.21.4-only 'minecraft:potion' entity id (we're on 1.21.11)"""
import re, sys, shutil, time, os
f = sys.argv[1] + '/RaycastedAntiESP/config.yml'
if not os.path.exists(f):
    sys.exit('= RaycastedAntiESP config not created yet - start the server once, then run again')
s = open(f, encoding='utf-8').read()
o = s
# player section
s = re.sub(r'(?m)^(        only-check-sneaking:) *\S+', r'\1 false', s)
# tile-entity section: recheck visible tile entities every 2s instead of never
s = re.sub(r'(?m)(^    tile-entity:\n(?:        .*\n)*?        visible-recheck-interval-ticks:) *-?\d+[^\n]*', r'\1 40  # re-hide chests/signs once out of sight', s)
s = re.sub(r'(?m)^ *- minecraft:potion\b.*\n', '', s)
# console noise (level-3 diagnostics, harmless):
#  - AbstractChunkParser: anti-xray turned a hidden chest/spawner into stone, so its block-entity data has no block;
#    RaycastedAntiESP already drops that data (correct result) but warns every time.
#  - EntitySpawnTask / PECacheablePacketReconciliationTask: packets for an entity that spawned and despawned within
#    a tick spike (e.g. kill effects); they're dropped, nothing visible happens.
def exempt(s, key, names):
    import re as _re
    m = _re.search(r'(?m)^    ' + key + r':[^\n]*\n((?:        - .*\n)*)', s)
    if not m:
        return s
    have = set(_re.findall(r'- (\S+)', m.group(1)))
    items = [n for n in names if n not in have]
    if not items:
        return s
    block = '    ' + key + ':\n' + m.group(1) + ''.join(f'        - {n}\n' for n in items)
    return s[:m.start()] + block + s[m.end():]
s = exempt(s, 'warn-exempted-classes', ['AbstractChunkParser', 'EntitySpawnTask'])
s = exempt(s, 'error-exempted-classes', ['PECacheablePacketReconciliationTask'])
if s != o:
    shutil.copy2(f, f + '.bak-' + time.strftime('%Y%m%d-%H%M%S'))
    open(f, 'w', encoding='utf-8').write(s)
    print('✅ RaycastedAntiESP tuned (players hidden even when not sneaking, tile entities re-hide)')
else:
    print('= RaycastedAntiESP already tuned')

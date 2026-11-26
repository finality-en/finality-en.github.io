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
if s != o:
    shutil.copy2(f, f + '.bak-' + time.strftime('%Y%m%d-%H%M%S'))
    open(f, 'w', encoding='utf-8').write(s)
    print('✅ RaycastedAntiESP tuned (players hidden even when not sneaking, tile entities re-hide)')
else:
    print('= RaycastedAntiESP already tuned')

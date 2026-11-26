#!/usr/bin/env python3
"""BetterTeamGUI: the team list / leaderboard / allies menus show each team owner's head with texture "",
which makes the server ask Mojang for ~40 skins every refresh -> Mojang rate-limits us (Status: 429 spam,
Steve heads, slower skins for everyone). Swap those team icons to a banner (no Mojang lookups).
Member heads inside a team, and invite menus (online players, already cached), are left alone.
Safe to run again. Needs a server restart (BetterTeamGUI has no reload command)."""
import re, sys, glob, shutil, time
P = sys.argv[1]
stamp = time.strftime('%Y%m%d-%H%M%S')
n = 0
for f in glob.glob(P + '/BetterTeamGUI/lang/*/gui/*.yml'):
    if not re.search(r'/(list_view|leaderboard_view|allies_view)\.yml$', f):
        continue
    s = open(f, encoding='utf-8').read()
    s2, k = re.subn(r'(?m)^(\s*)item:\s*PLAYER_HEAD\s*\n(\s*)texture:\s*""\s*$', r'\1item: WHITE_BANNER\n\2texture: ""', s)
    if k:
        shutil.copy2(f, f + '.bak-heads-' + stamp)
        open(f, 'w', encoding='utf-8').write(s2)
        n += k
        print(f'✅ {f.split("/BetterTeamGUI/")[1]}: {k} team icon(s) -> banner')
print(f'= done ({n} changed)' if n else '= nothing to change (already done)')

#!/bin/bash
# Kill Trackers: only from boss loot chests, 0.5% per roll. SMP can stay online - run /fboss reload after.
V=/var/lib/pterodactyl/volumes/9b618852-57d9-4326-b2ae-506798142a97; D=$V/plugins/FinalityBosses
python3 - "$D/config.yml" "$D/loot.yml" <<'PY'
import re,sys,shutil,time
ts=time.strftime('%Y%m%d-%H%M%S')
c=open(sys.argv[1],encoding='utf-8').read()
c2,a=re.subn(r"(?m)^\s*- '(?:chance [\d.]+ )?fboss give \{player\} killtracker'\s*\n",'',c)
c2,b=re.subn(r"(?m)^\s*- \{kill-tracker: true, count: \d+, chance: [\d.]+\}\s*\n",'',c2)
if c2!=c: shutil.copy2(sys.argv[1],sys.argv[1]+'.bak-kt-'+ts); open(sys.argv[1],'w',encoding='utf-8').write(c2)
print('✅ config.yml: removed %d damage-reward tracker(s) and %d chest-spread tracker(s)'%(a,b))
l=open(sys.argv[2],encoding='utf-8').read()
l2,k=re.subn(r'\{kill-tracker: true, chance: [\d.]+\}','{kill-tracker: true, chance: 0.5}',l)
if l2!=l: shutil.copy2(sys.argv[2],sys.argv[2]+'.bak-kt-'+ts); open(sys.argv[2],'w',encoding='utf-8').write(l2)
print('✅ loot.yml: %d chest entr(y/ies) set to 0.5%%'%k)
PY
grep -n -i "kill.\?tracker" $D/config.yml $D/loot.yml
echo "Done - run /fboss reload in game or console."

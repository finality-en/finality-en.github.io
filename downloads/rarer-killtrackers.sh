#!/bin/bash
# Makes Kill Trackers rarer from bosses (FinalityBosses config.yml + loot.yml). SMP can stay online - run /fboss reload after.
V=/var/lib/pterodactyl/volumes/9b618852-57d9-4326-b2ae-506798142a97; D=$V/plugins/FinalityBosses
python3 - "$D/config.yml" "$D/loot.yml" <<'PY'
import re,sys,shutil,time
ts=time.strftime('%Y%m%d-%H%M%S')
# damage rewards: guaranteed / 50% -> 40% (1st), 20% (2nd), 10% (3rd)
c=open(sys.argv[1],encoding='utf-8').read()
lines=c.split('\n'); seen=0; out=[]
for l in lines:
    m=re.match(r"^(\s*- ')(?:chance \d+ )?(fboss give \{player\} killtracker)'\s*$",l)
    if m:
        pct=[40,20,10][seen] if seen<3 else 10; seen+=1
        l="%schance %d %s'"%(m.group(1),pct,m.group(2))
    out.append(l)
new='\n'.join(out)
new=re.sub(r'\{kill-tracker: true, count: \d+, chance: \d+\}','{kill-tracker: true, count: 1, chance: 25}',new)
if new!=c: shutil.copy2(sys.argv[1],sys.argv[1]+'.bak-kt-'+ts); open(sys.argv[1],'w',encoding='utf-8').write(new)
print('✅ config.yml: %d reward line(s) -> 40%%/20%%/10%%, chest spread -> 1 at 25%%'%seen)
# loot chests: ring 5% -> 1%, vault 20% -> 6% (already-changed values are left alone)
l=open(sys.argv[2],encoding='utf-8').read()
def f(m):
    v=int(m.group(1)); nv={5:1,20:6}.get(v,v); return '{kill-tracker: true, chance: %d}'%nv
l2,k=re.subn(r'\{kill-tracker: true, chance: (\d+)\}',f,l)
if l2!=l: shutil.copy2(sys.argv[2],sys.argv[2]+'.bak-kt-'+ts); open(sys.argv[2],'w',encoding='utf-8').write(l2)
print('✅ loot.yml: %d chest entr(y/ies) made rarer'%k)
PY
grep -n -i "kill.\?tracker" $D/config.yml $D/loot.yml
echo "Done - run /fboss reload in game or console."

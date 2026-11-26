#!/bin/bash
# Finality master update 26 Nov - run with the SMP STOPPED:  sudo bash master-26nov.sh
V=/var/lib/pterodactyl/volumes/9b618852-57d9-4326-b2ae-506798142a97; P=$V/plugins
R=https://raw.githubusercontent.com/finality-en/finality-en.github.io/main/downloads
T=$(mktemp -d); mkdir -p /root/old-jars
pgrep -f "9b618852-57d9-4326-b2ae-506798142a97" >/dev/null && { echo "⚠️  The SMP still looks like it's running - stop it first (FancyNpcs would overwrite the NPCs)."; exit 1; }
dl(){ curl -fsSL "$R/$1?$(date +%s)" -o "$T/$1" && echo "$2  $T/$1" | sha256sum -c --quiet - || { echo "❌ $1 download/checksum failed"; return 1; }; }
jar(){ dl "$1-$2.jar" "$3" && { mv $P/$1-*.jar /root/old-jars/ 2>/dev/null; cp "$T/$1-$2.jar" "$P/$1-$2.jar" && chown --reference=$P "$P/$1-$2.jar" && echo "✅ $1 $2"; }; }
py(){ dl "$1" "$2" && python3 "$T/$1" "${@:3}"; }

echo "== plugins"
jar FinalityItems 1.6.2 5e162e907590fbfe583fc6fefc20eafb082bb72c5b32cd8aaec535d2e4e89193
jar FinalityBosses 1.3.10 c4554a1f29f4291ea0f809ef26cfc9340e1fc9c5fe1a3c8fb63815ee763e8d2f

echo "== Demon Wings / items"
sed -i 's/^  mode: elytra.*/  mode: fake-offhand   # others see the 3D wings like the offhand/' $P/FinalityItems/config.yml
py wings-lore.py 6a1e7023b28c6b0f4cb42e39ba277c6840467ae13215b861d28a9ebbe7e5d1ec $P

echo "== perks: coin prices -45%"
python3 - "$P/FinalityItems/config.yml" <<'PY'
import re,shutil,time,sys
p=sys.argv[1]; s=open(p,encoding='utf-8').read()
if '# perks: coin prices cut 45%' in s: print('= already done')
else:
    a=s.index('\nperks:\n'); m=re.search(r'\n\S',s[a+1:]); b=a+1+m.start() if m else len(s)
    sec=re.sub(r'coins:\s*(\d+)',lambda m:'coins: %d'%round(int(m.group(1))*0.55),s[a:b])
    shutil.copy2(p,p+'.bak-perks-'+time.strftime('%Y%m%d-%H%M%S'))
    open(p,'w',encoding='utf-8').write(s[:a]+'\n# perks: coin prices cut 45%'+sec+s[b:]); print('✅ perks cheaper')
PY

echo "== coins x2 (Evil Elf, challenges, streaks)"
py coins-2x.py 4394d0de62d75c530b9f397cbb699f5c7bbb15367fa6bfaa423304ef4abf2f08 $P

echo "== water buckets in warzone + spawn"
python3 - "$P" <<'PY'
import yaml,re,glob,sys
V=sys.argv[1]; ids=[]
for f in glob.glob(V+'/WorldGuard/worlds/*/regions.yml'):
    ids+=[k for k in (yaml.safe_load(open(f)) or {}).get('regions',{}) if 'spawn' in k.lower()]
p=V+'/FinalityBosses/config.yml'; s=open(p,encoding='utf-8').read()
want=['warzone']+[i for i in ids if i!='warzone']
block='warzone-water-pickup:\n  enabled: true\n  regions: ['+', '.join(want)+']\n'
if re.search(r'(?m)^warzone-water-pickup:',s): s=re.sub(r'(?ms)^warzone-water-pickup:\n(?:[ \t]+.*\n?)*',block,s,count=1)
else: s=s.rstrip('\n')+'\n\n'+block
open(p,'w',encoding='utf-8').write(s); print('✅ water pickup regions:', want)
PY

echo "== Relic crate (names, Hex Wand, order, odds)"
py relic-names.py 4b2fc1f33e8c61749d949a3b664bfb4d8fd665a806521f04f37d865c27d18658 $P
py relic-odds.py 97b392b764fef86c277c59ac4a72188f6e91c249ca0a9185ca050b8505fed665 $P >/dev/null && echo "✅ Hex Wand in the Relic crate"
py relic-order.py b3bbde53e32b6fede406e6b9a61ad46fff4657a75dcc1d9805c0a1d02df127ac $P | tail -1
py relic-set.py 46c5a89bfa7371081ebcf53dbfe76eb9acdf51879da135a1149b0e6b7eb9b76b $P | head -1

echo "== TAB + NPCs"
py tab-events.py e4fe27e5d3675fb7060a2b872a8fb93de545b5d9ed21a0d159a037c416fcee87 $P/TAB
py add-npcs.py 4e86c0f5399f0d6a3551791b72ec0f96ad9fd90c04c7702fb07ae4253757b13e $P
py add-store-npc.py 1166fe5f8abccdb7361cc80c08f38225924c01db73fc54febe0a51e51f4c25eb $P

chown -R --reference=$P $P/FinalityItems $P/FinalityBosses $P/FinalityChallenges $P/AdvancedCrates $P/TAB $P/FancyNpcs $P/FancyHolograms $P/Nexo/items 2>/dev/null
echo "== done - start the SMP"

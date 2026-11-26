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
jar FinalityItems 1.7.3 416e36de2a9e84c30b087e25fd40f184d897065de8faf16042eabefde5846851
jar FinalityBosses 1.4.0 08db5fe90fcb42991c9734a49377daf23e24fc3e61e2c43baa237bcbe36835a3
jar FinalityBans 1.2.4 3529c5e1c18bf7aafa1992fdbe352eebfffd65c2825070fc03f1ce17ab59fcc6

echo "== boss weapons now live in FinalityItems (stats/lore/abilities copied over from FinalityBosses)"
python3 - "$P" <<'PY'
import re,sys,shutil,time,glob
P=sys.argv[1]
b=open(P+'/FinalityBosses/config.yml',encoding='utf-8').read()
it=P+'/FinalityItems/config.yml'; s=open(it,encoding='utf-8').read()
if re.search(r'(?m)^boss-weapons:',s): print('= boss-weapons already in FinalityItems')
else:
    m=re.search(r'(?ms)^boss-items:\n.*?(?=^\S|\Z)',b)
    if m:
        shutil.copy2(it,it+'.bak-weapons-'+time.strftime('%Y%m%d-%H%M%S'))
        open(it,'w',encoding='utf-8').write(s.rstrip('\n')+'\n\n# Boss weapons (moved from FinalityBosses boss-items)\n'+m.group(0).replace('boss-items:','boss-weapons:',1))
        print('✅ copied your boss-items (incl. your tweaks) to FinalityItems boss-weapons')
    else: print('= no boss-items in FinalityBosses config - FinalityItems defaults used')
# give commands -> FinalityItems
n=0
for f in [P+'/FinalityBosses/config.yml']+glob.glob(P+'/AdvancedCrates/Crates/*.yml'):
    t=open(f,encoding='utf-8').read()
    t2=re.sub(r'fboss item (\w+) (\{player\}|%player%)',r'fitems weapon give \2 \1',t)
    if t2!=t: open(f,'w',encoding='utf-8').write(t2); n+=t.count('fboss item ')
print(f'✅ {n} reward command(s) now use: fitems weapon give <player> <id>')
PY


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
py relic-names.py 89c474f48fdc567b15c4543cf73a686fbe4eb9498d5e8ea36603928deeee735f $P
py relic-odds.py c737a12de7903b2d2ee3caf1ec8f0fa1bb74f90229d52eb494865784a099b56d $P >/dev/null && echo "✅ Hex Wand in the Relic crate"
py relic-order.py b3bbde53e32b6fede406e6b9a61ad46fff4657a75dcc1d9805c0a1d02df127ac $P | tail -1
py relic-set.py 46c5a89bfa7371081ebcf53dbfe76eb9acdf51879da135a1149b0e6b7eb9b76b $P | head -1

echo "== AdvancedCrates: animations always use fake (packet) items, never real ones"
sed -i 's/^Max_Players_Per_Animation:.*/Max_Players_Per_Animation: 500/' $P/AdvancedCrates/config.yml && grep -n "^Max_Players_Per_Animation" $P/AdvancedCrates/config.yml

echo "== TAB + NPCs"
py tab-events.py e4fe27e5d3675fb7060a2b872a8fb93de545b5d9ed21a0d159a037c416fcee87 $P/TAB
py add-npcs.py 4e86c0f5399f0d6a3551791b72ec0f96ad9fd90c04c7702fb07ae4253757b13e $P
py add-store-npc.py 1166fe5f8abccdb7361cc80c08f38225924c01db73fc54febe0a51e51f4c25eb $P

echo "== Accurate damage lores (Hex Wand 13 = Astral Riftblade +1)"
py damage-lores.py 55582934c25f3ae7a23fde210a687c0c1dee0dec2fbe304fadc7a44ee5763024 $P

echo "== Site links (never the GitHub address)"
py site-urls.py 765041a8c2dae37b0d2928ded06b5be27432d0c215d03dce871871c6580cecc8 $P

chown -R --reference=$P $P/FinalityItems $P/FinalityBosses $P/FinalityChallenges $P/AdvancedCrates $P/TAB $P/FancyNpcs $P/FancyHolograms $P/Nexo/items $P/FinalityBans $P/SeasonAbilities 2>/dev/null
echo "== done - start the SMP"

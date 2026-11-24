#!/usr/bin/env bash
# Finality SMP - raid boss drops get their looks (Elf Candy Cane variants + Glacier-style Yeti Hide), FinalityBosses 1.3.1 (/fboss test, safer commands),
# pvpmanager reload after warzone PvP returns, CMI mob/player health bars off.
# Run as root on the game machine with the SMP STOPPED.
set -u
V=/var/lib/pterodactyl/volumes/9b618852-57d9-4326-b2ae-506798142a97; P=$V/plugins
RAW=https://raw.githubusercontent.com/finality-en/finality-en.github.io/main/downloads
BK=/root/raiddrops-backup-$(date +%F-%H%M); mkdir -p $BK; T=$(mktemp -d)
ok(){ echo "✅ $*"; }; no(){ echo "❌ $*"; }
if docker ps --format '{{.Names}}' | grep -q 9b618852-57d9-4326-b2ae-506798142a97; then echo "!! Stop the SMP in the panel first, then run this again."; exit 1; fi
OWN=$(stat -c %u:%g $P)
PNGS="krampus_chain nutcracker_sabre hex_wand soulreaper yeti_hide yeti_armor_layer_1"
FILES="finality_raid_drops.yml rename.sed"; for i in $PNGS; do FILES="$FILES $i.png"; done
for f in $FILES; do curl -fsSL "$RAW/raid-drops/$f" -o $T/$f || { no "download $f"; exit 1; }; done
curl -fsSL $RAW/FinalityBosses-1.3.1.jar -o $T/fb.jar && echo "53f1cbd0a7cc2d9ac1733c48c1bd3ee2e003b9b767fd0fbe837b6afe1016e6fd  $T/fb.jar" | sha256sum -c --quiet - || { no "jar download/checksum"; exit 1; }

echo "===== 1. FinalityBosses 1.3.1"
for j in $P/FinalityBosses-*.jar; do [ -f "$j" ] && mv "$j" $BK/ && echo "  old $(basename $j) -> backup"; done
cp $T/fb.jar $P/FinalityBosses-1.3.1.jar && chown $OWN $P/FinalityBosses-1.3.1.jar && ok "FinalityBosses-1.3.1.jar installed"

echo "===== 2. FinalityBosses config: drops linked to their models + new names, pvpmanager reload"
C=$P/FinalityBosses/config.yml; cp -p $C $BK/
for i in krampus_chain yeti_hide nutcracker_sabre hex_wand soulreaper; do
  if awk -v id="  $i:" '$0==id{f=1;next} f&&/^  [a-z]/{exit} f&&/nexo-id:/{found=1} END{exit !found}' $C; then ok "$i already linked"
  else sed -i "/^  $i:[[:space:]]*$/a\\    nexo-id: $i                 # custom look (Nexo item of the same id)" $C; grep -q "nexo-id: $i " $C && ok "$i linked" || no "$i not found in boss-items"; fi
done
sed -i -f $T/rename.sed $C && ok "drop names restyled"
grep -q "pvpmanager reload" $C && ok "pvpmanager reload already there" || { sed -i "/^  enable-commands:/ s/\]\s*$/, 'pvpmanager reload']/" $C; grep -q "pvpmanager reload" $C && ok "pvpmanager reload runs when warzone PvP comes back" || no "add pvpmanager reload to pvp-toggle.enable-commands by hand"; }

echo "===== 3. Nexo: items + textures"
NI=$(grep -rl '^elf_candy_cane:' $P/Nexo/items 2>/dev/null | head -1)
TX=$(find $P/Nexo -name 'elf_candy_cane.png' -path '*textures*' 2>/dev/null | head -1)
if [ -z "$NI" ] || [ -z "$TX" ]; then no "couldn't find the Nexo items/textures folders"; else
  cp $T/finality_raid_drops.yml "$(dirname $NI)/finality_raid_drops.yml" && ok "Nexo items -> ${NI#$P/}"
  TD=$(dirname $TX); for i in $PNGS; do cp $T/$i.png $TD/; done
  rm -rf "$(dirname $(dirname $TD))/models/finality_bosses"
  ok "6 textures -> ${TD#$P/}"
fi

echo "===== 4. CMI health bars over mobs/players off"
CM=$P/CMI/config.yml; cp -p $CM $BK/; sed -i "s/^  HpBarEnabled: true/  HpBarEnabled: false/" $CM; grep -q "^  HpBarEnabled: false" $CM && ok "CMI HP bars off" || no "check CMI HpBarEnabled"

chown -R $OWN $P/FinalityBosses $P/Nexo $P/CMI
echo; echo "DONE. Backups: $BK"
echo "Now: start the SMP, then in console:  nexo reload all"

#!/usr/bin/env bash
# Finality SMP - custom textures for the 5 raid boss drops (FinalityBosses 1.3.1 + Nexo items/textures).
# Run as root on the game machine with the SMP STOPPED.
set -u
V=/var/lib/pterodactyl/volumes/9b618852-57d9-4326-b2ae-506798142a97; P=$V/plugins
RAW=https://raw.githubusercontent.com/finality-en/finality-en.github.io/main/downloads
BK=/root/raiddrops-backup-$(date +%F-%H%M); mkdir -p $BK; T=$(mktemp -d)
ok(){ echo "✅ $*"; }; no(){ echo "❌ $*"; }
if docker ps --format '{{.Names}}' | grep -q 9b618852-57d9-4326-b2ae-506798142a97; then echo "!! Stop the SMP in the panel first, then run this again."; exit 1; fi
OWN=$(stat -c %u:%g $P)
IDS="krampus_chain yeti_hide nutcracker_sabre hex_wand soulreaper"
for f in finality_raid_drops.yml $(for i in $IDS; do echo $i.png; done); do curl -fsSL "$RAW/raid-drops/$f" -o $T/$f || { no "download $f"; exit 1; }; done
curl -fsSL $RAW/FinalityBosses-1.3.1.jar -o $T/fb.jar && echo "c926af42a26d7f5a622b5b2d11efa0c8ed9d3cd8cdb99eca4ba3fbe593fc1c48  $T/fb.jar" | sha256sum -c --quiet - || { no "jar download/checksum"; exit 1; }

echo "===== FinalityBosses 1.3.1"
for j in $P/FinalityBosses-*.jar; do [ -f "$j" ] && mv "$j" $BK/ && echo "  old $(basename $j) -> backup"; done
cp $T/fb.jar $P/FinalityBosses-1.3.1.jar && chown $OWN $P/FinalityBosses-1.3.1.jar && ok "FinalityBosses-1.3.1.jar installed"

echo "===== Link the drops to their textures (FinalityBosses config)"
C=$P/FinalityBosses/config.yml; cp -p $C $BK/
for i in $IDS; do
  if awk -v id="  $i:" '$0==id{f=1;next} f&&/^  [a-z]/{exit} f&&/nexo-id:/{found=1} END{exit !found}' $C; then ok "$i already linked"
  else sed -i "/^  $i:[[:space:]]*$/a\    nexo-id: $i                 # custom texture (Nexo item of the same id)" $C; grep -q "nexo-id: $i " $C && ok "$i linked" || no "$i not found in config.yml boss-items"; fi
done

echo "===== Nexo items + textures"
NI=$(grep -rl '^elf_candy_cane:' $P/Nexo/items 2>/dev/null | head -1)
if [ -z "$NI" ]; then no "couldn't find the Nexo items folder"; else cp $T/finality_raid_drops.yml "$(dirname $NI)/finality_raid_drops.yml" && ok "Nexo items -> ${NI%/*}/finality_raid_drops.yml"; fi
TX=$(find $P/Nexo -name 'elf_candy_cane.png' -path '*textures*' 2>/dev/null | head -1)
if [ -z "$TX" ]; then no "couldn't find the Nexo textures folder"; else for i in $IDS; do cp $T/$i.png "$(dirname $TX)/$i.png"; done; ok "5 textures -> $(dirname ${TX#$P/})"; fi
chown -R $OWN $P/FinalityBosses $P/Nexo
echo; echo "DONE. Backups: $BK"
echo "Now: start the SMP, then in console:  nexo reload all"

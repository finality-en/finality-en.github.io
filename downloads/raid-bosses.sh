#!/usr/bin/env bash
# Finality SMP - FinalityBosses 1.3.0: 5 raid bosses (manual spawn only) + their drops + /fboss menu + MSPT fixes.
# Run as root on the game machine with the SMP STOPPED (mass-update.sh runs it for you).
set -u
V=/var/lib/pterodactyl/volumes/9b618852-57d9-4326-b2ae-506798142a97; P=$V/plugins
RAW=https://raw.githubusercontent.com/finality-en/finality-en.github.io/main/downloads
BK=/root/raidbosses-backup-$(date +%F-%H%M); mkdir -p $BK; T=$(mktemp -d)
ok(){ echo "✅ $*"; }; no(){ echo "❌ $*"; }
if docker ps --format '{{.Names}}' | grep -q 9b618852-57d9-4326-b2ae-506798142a97; then echo "!! Stop the SMP in the panel first, then run this again."; exit 1; fi
OWN=$(stat -c %u:%g $P)
bak(){ [ -f "$1" ] && cp -p "$1" "$BK/$(echo ${1#$P/} | tr / _)"; }
ins_after(){ awk -v f="$3" -v a="$2" '{print} $0 ~ a && !d {while((getline l < f)>0) print l; d=1}' "$1" > $T/x && cat $T/x > "$1"; }

echo "===== 7. FinalityBosses 1.3.0 (raid bosses, admin menu, MSPT fixes)"
for f in raid_bosses_block.yml boss_items_block.yml raid_loot.yml; do curl -fsSL "$RAW/raid-bosses/$f" -o $T/$f || { no "download $f"; exit 1; }; done
curl -fsSL $RAW/FinalityBosses-1.3.0.jar -o $T/fb.jar && echo "e348bae417a5afd7941f57e2bd72a616f71442ce67a4d889a4a1d32de75b7d29  $T/fb.jar" | sha256sum -c --quiet - || { no "jar download/checksum"; exit 1; }
for j in $P/FinalityBosses-*.jar; do [ -f "$j" ] && mv "$j" $BK/ && echo "  old $(basename $j) -> backup"; done
cp $T/fb.jar $P/FinalityBosses-1.3.0.jar && chown $OWN $P/FinalityBosses-1.3.0.jar && ok "FinalityBosses-1.3.0.jar installed"

C=$P/FinalityBosses/config.yml; bak $C
if grep -q '^  krampus:' $C; then ok "raid bosses already in config.yml"; else ins_after $C '^bosses:[[:space:]]*$' $T/raid_bosses_block.yml; fi
for b in krampus yeti nutcracker blizzard_witch hollow_king; do grep -q "^  $b:" $C && ok "boss $b" || no "boss $b missing from config.yml"; done
if grep -q '^boss-items:' $C; then ok "boss-items already there"; else cat $T/boss_items_block.yml >> $C && ok "boss-items (5 raid drops) added"; fi
L=$P/FinalityBosses/loot.yml; bak $L
if grep -q '^krampus:' $L; then ok "raid loot already there"; else cat $T/raid_loot.yml >> $L && ok "raid boss loot tables added"; fi
chown -R $OWN $P/FinalityBosses
echo "  Backups: $BK"

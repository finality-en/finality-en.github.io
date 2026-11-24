#!/usr/bin/env bash
# Finality SMP - mass update. Run as root on the game machine with the SMP STOPPED.
set -u
V=/var/lib/pterodactyl/volumes/9b618852-57d9-4326-b2ae-506798142a97; P=$V/plugins
RAW=https://raw.githubusercontent.com/finality-en/finality-en.github.io/main/downloads
BK=/root/mass-update-$(date +%F-%H%M); mkdir -p $BK
ok(){ echo "✅ $*"; }; no(){ echo "❌ $*"; }
if docker ps --format '{{.Names}}' | grep -q 9b618852-57d9-4326-b2ae-506798142a97; then echo "!! Stop the SMP in the panel first, then run this again."; exit 1; fi
OWN=$(stat -c %u:%g $P)

echo "===== 1. FinalityBosses 1.2.1 (Frost King is immune to maces)"
curl -fsSL $RAW/FinalityBosses-1.2.1.jar -o /tmp/fb.jar && echo "bd69fb691ff7bb07d7b8ee27cdb35cb4ea533b1f7c8f5f9767fd77f6071a7bbd  /tmp/fb.jar" | sha256sum -c --quiet - || { no "jar download/checksum"; exit 1; }
for j in $P/FinalityBosses-*.jar; do [ -f "$j" ] && mv "$j" $BK/ && echo "  old $(basename $j) -> backup"; done
mv /tmp/fb.jar $P/FinalityBosses-1.2.1.jar && chown $OWN $P/FinalityBosses-1.2.1.jar && ok "FinalityBosses-1.2.1.jar installed"
C=$P/FinalityBosses/config.yml; cp -p $C $BK/
if ! grep -q '^    mace: ' $C; then
  awk '/^  frost_king:/{f=1} f && /^    max-damage-per-hit:/ && !d {print; print "    mace: immune                 # immune = maces do nothing to him | no-smash = capped, no fall bonus | normal"; print "    mace-max-damage: 7"; d=1; next} {print}' $C > /tmp/c.yml && cat /tmp/c.yml > $C
fi
grep -n '^    mace' $C && ok "Frost King mace setting"

echo "===== 2. Mob farms: Leaf spawn throttle off for hostile mobs"
L=$V/config/leaf-global.yml; cp -p $L $BK/
sed -i '/throttle-mob-spawning:/,/creature:/ s/spawn-chance: 25.0/spawn-chance: 100.0/' $L
grep -A4 'throttle-mob-spawning:' $L | grep -q 'spawn-chance: 100.0' && ok "monster spawn throttle off (spawn-chance 100)" || no "check leaf-global.yml throttle-mob-spawning"

echo; echo "DONE. Backups: $BK  -> start the SMP."

#!/usr/bin/env bash
# Finality SMP - mass update. Run as root on the game machine with the SMP STOPPED.
#  1. Frost King: FinalityBosses 1.2.1 + latest settings (mace immunity, Frost Nova, Frozen Armour, 2000 HP...)
#  2. Mob farms: Leaf spawn throttle off for hostile mobs (pillager farms)
#  3. FinalityBosses 1.3.0: 5 raid bosses (manual only) + drops, /fboss menu, MSPT fixes
set -u
V=/var/lib/pterodactyl/volumes/9b618852-57d9-4326-b2ae-506798142a97
RAW=https://raw.githubusercontent.com/finality-en/finality-en.github.io/main/downloads
if docker ps --format '{{.Names}}' | grep -q 9b618852-57d9-4326-b2ae-506798142a97; then echo "!! Stop the SMP in the panel first, then run this again."; exit 1; fi
curl -fsSL $RAW/frost-king.sh -o /root/frost-king.sh && bash /root/frost-king.sh || { echo "❌ Frost King part failed"; exit 1; }

echo "===== 6. Mob farms: Leaf spawn throttle off for hostile mobs"
L=$V/config/leaf-global.yml; cp -p $L /root/leaf-global.$(date +%F-%H%M).yml
sed -i '/throttle-mob-spawning:/,/creature:/ s/spawn-chance: 25.0/spawn-chance: 100.0/' $L
grep -A4 'throttle-mob-spawning:' $L | grep -q 'spawn-chance: 100.0' && echo "✅ monster spawn throttle off" || echo "❌ check leaf-global.yml throttle-mob-spawning"
curl -fsSL $RAW/raid-bosses.sh -o /root/raid-bosses.sh && bash /root/raid-bosses.sh || echo "❌ raid boss part failed"

echo; echo "ALL DONE -> start the SMP, then in console: nexo reload all"

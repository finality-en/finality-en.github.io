#!/usr/bin/env bash
# Finality SMP - everything from 24 Nov in one go. Run as root on the game machine with the SMP STOPPED.
#  1. raid-drops.sh: FinalityBosses 1.3.1 (/fboss test, safer commands), raid drop looks, pvpmanager reload, CMI HP bars off
#  2. Santa Hat: FinalityItems 1.1.0 + model/texture in the Nexo pack
#  3. Challenges count spawner mobs
#  4. Railguns: arrows from dispensers/pistons no longer vanish after 1 second
#  5. TAB: "NEXT EVIL ELF" line (red NEXT + green EVIL ELF)
set -u
V=/var/lib/pterodactyl/volumes/9b618852-57d9-4326-b2ae-506798142a97; P=$V/plugins
RAW=https://raw.githubusercontent.com/finality-en/finality-en.github.io/main/downloads
BK=/root/master24-backup-$(date +%F-%H%M); mkdir -p $BK; T=$(mktemp -d)
ok(){ echo "✅ $*"; }; no(){ echo "❌ $*"; }
if docker ps --format '{{.Names}}' | grep -q 9b618852-57d9-4326-b2ae-506798142a97; then echo "!! Stop the SMP in the panel first, then run this again."; exit 1; fi
OWN=$(stat -c %u:%g $P)

curl -fsSL $RAW/raid-drops.sh -o /root/raid-drops.sh && bash /root/raid-drops.sh || no "raid drops part failed (see above)"

echo "===== 5. Santa Hat (FinalityItems 1.1.0 + Nexo pack files)"
for f in santa_hat.png santa_hat.json santa_hat_item.json; do curl -fsSL "$RAW/santa-hat/$f" -o $T/$f || { no "download $f"; exit 1; }; done
curl -fsSL $RAW/FinalityItems-1.1.0.jar -o $T/fi.jar && echo "a1f0cc80c73deca707df7d46997f0a1844318b4bd50b284931896fd7c437f1d6  $T/fi.jar" | sha256sum -c --quiet - || { no "FinalityItems download/checksum"; exit 1; }
for j in $P/FinalityItems-*.jar; do [ -f "$j" ] && mv "$j" $BK/ && echo "  old $(basename $j) -> backup"; done
cp $T/fi.jar $P/FinalityItems-1.1.0.jar && ok "FinalityItems-1.1.0.jar installed"
A=$P/Nexo/pack/assets/finality; mkdir -p $A/items $A/models/item $A/textures/item
cp $T/santa_hat_item.json $A/items/santa_hat.json; cp $T/santa_hat.json $A/models/item/santa_hat.json; cp $T/santa_hat.png $A/textures/item/santa_hat.png
ok "Santa Hat model -> Nexo/pack/assets/finality"

echo "===== 6. Challenges: spawner mobs count"
C=$P/FinalityChallenges/config.yml; cp -p $C $BK/; sed -i "s/ignore-spawner-mobs: true/ignore-spawner-mobs: false/" $C
echo "  $(grep -c 'ignore-spawner-mobs: false' $C) mob challenges now count spawner mobs"; ok "challenges"

echo "===== 7. Railguns: dispenser/piston arrows stay"
W=$V/config/paper-world-defaults.yml; cp -p $W $BK/
sed -i "s/^    non-player-arrow-despawn-rate: '20'/    non-player-arrow-despawn-rate: default/" $W
grep -q "non-player-arrow-despawn-rate: default" $W && ok "non-player arrows now last as long as normal arrows (15s in the ground)" || no "check paper-world-defaults.yml non-player-arrow-despawn-rate"

echo "===== 8. TAB: NEXT EVIL ELF"
F=$(grep -rlE "ɴᴇxᴛ (ʙᴏꜱꜱ|ᴇᴠɪʟ ᴇʟꜰ)" $P/TAB --include=*.yml 2>/dev/null)
for f in $F; do cp -p "$f" $BK/; sed -i -E "s/ɴᴇxᴛ (\&a\&l)?(ʙᴏꜱꜱ|ᴇᴠɪʟ ᴇʟꜰ)/ɴᴇxᴛ \&a\&lᴇᴠɪʟ ᴇʟꜰ/g" "$f"; done
[ -n "$F" ] && ok "TAB line set" || echo "  (no NEXT BOSS line found in TAB - skipped)"

chown -R $OWN $P/FinalityItems-1.1.0.jar $P/Nexo $P/FinalityChallenges $P/TAB $V/config/paper-world-defaults.yml 2>/dev/null
echo; echo "ALL DONE. Backups: $BK"
echo "Now: start the SMP, then in console:  nexo reload all"

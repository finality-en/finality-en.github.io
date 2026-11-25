#!/usr/bin/env bash
# Finality SMP - everything from 25 Nov in one go. Run as root on the game machine with the SMP STOPPED.
#  0. Weapon abilities that never triggered (full-strength hit check read 0% on 1.21.11) - fixed in both plugins
#  1. FinalityItems 1.4.2: /fitems menu + tab complete + /fitems debug, Elf Candy Cane float ability repaired, /perks (7 perks, player + admin menus), Kill Tracker, rank Santa Hat once per player,
#     rename guard (no /itemname, /itemlore or anvil names that fake our items)
#  2. FinalityBosses 1.3.5: raid weapons much stronger (damage/speed/abilities all in config), /fboss warzonepvp,
#     boss items fully enchanted with lore that explains them,
#     /nexo give copies of boss items turn into the real thing
#  3. FinalityBans 1.2.0: ban waves + /banwave menu (Vulcan suspects, X-ray mining stats, queue, run wave),
#     bans 1 day -> 7 days -> permanent, announced in chat + Discord with the reason
#  4. CMI schedule: Warzone regen turns PvP off for 45s (then back on + pvpmanager reload)
#  5. ClickVillagers: claimed villagers can't be killed
#  6. InstantBrew disabled (brewing is now a perk). Set KEEP_INSTANTBREW=1 to skip this.
#  7. Ban suspects script -> /root/ban-candidates.py
set -u
V=/var/lib/pterodactyl/volumes/9b618852-57d9-4326-b2ae-506798142a97; P=$V/plugins
RAW=https://raw.githubusercontent.com/finality-en/finality-en.github.io/main/downloads
BK=/root/master25-backup-$(date +%F-%H%M); mkdir -p $BK; T=$(mktemp -d)
ok(){ echo "✅ $*"; }; no(){ echo "❌ $*"; }
if docker ps --format '{{.Names}}' | grep -q 9b618852-57d9-4326-b2ae-506798142a97; then echo "!! Stop the SMP in the panel first, then run this again."; exit 1; fi
OWN=$(stat -c %u:%g $P)

jar(){ # name version sha
  curl -fsSL "$RAW/$1-$2.jar" -o "$T/$1.jar" && echo "$3  $T/$1.jar" | sha256sum -c --quiet - || { no "$1 $2 download/checksum"; return 1; }
  for j in $P/$1-*.jar $P/$1.jar; do [ -f "$j" ] && mv "$j" $BK/ && echo "  old $(basename $j) -> backup"; done
  cp "$T/$1.jar" "$P/$1-$2.jar" && chown $OWN "$P/$1-$2.jar" && ok "$1-$2.jar installed"
}

echo "===== 1-3. Plugins"
jar FinalityItems  1.4.2 0cd491297b501fb96531e404f558a383ff07827c597e6e478a5d16e63fa9cd99
jar FinalityBosses 1.3.5 494fc15222a060a93ccacf05a76d289dcf0ccfc2d9f70111aa6a37f626f99596
jar FinalityBans   1.2.0 91876fbf652bc99e61ffcdbbca67c04fe943f9b10950b76df9b30cfb2cef4e30
FIC=$P/FinalityItems/config.yml
if [ -f $FIC ] && ! grep -q "^perks:" $FIC; then cp -p $FIC $BK/; curl -fsSL "$RAW/finality-items/perks-config.yml?$(date +%s)" >> $FIC && ok "perks + kill tracker settings added to FinalityItems/config.yml"; else ok "FinalityItems config already has perks (or is new)"; fi

echo "===== 3a. Elf Candy Cane float ability"
[ -f $FIC ] && { cp -p $FIC $BK/fitems-config-before-onhit.yml; curl -fsSL "$RAW/fix-onhit.py?$(date +%s)" -o $T/fo.py && python3 $T/fo.py $FIC || no "on-hit repair failed"; }

echo "===== 3b. Raid weapons: stronger, configurable, lore that explains them, fully enchanted"
cp -p $P/FinalityBosses/config.yml $BK/fb-config.yml; NX=$(grep -rl '^elf_candy_cane:' $P/Nexo/items | head -1); [ -n "$NX" ] && cp -p "$NX" $BK/
curl -fsSL "$RAW/patch-boss-items.py?$(date +%s)" -o $T/pbi.py && python3 $T/pbi.py $P || no "boss item patch failed (backups in $BK)"
RD=$(grep -rl '^krampus_chain:' $P/Nexo/items | head -1)
if [ -n "$RD" ]; then cp -p "$RD" $BK/; curl -fsSL "$RAW/raid-drops/finality_raid_drops.yml?$(date +%s)" -o "$RD" && ok "Nexo Raid Drops: lore + full enchants"; else no "Nexo raid drops file not found"; fi

echo "===== 3c. Lag spikes no longer kick players (packet limit 500 -> 1000)"
PG=$V/config/paper-global.yml; cp -p $PG $BK/
sed -i "/^  all-packets:/,/max-packet-rate/ s/max-packet-rate: .*/max-packet-rate: 1000.0/" $PG && ok "packet limit 1000"

echo "===== 3d. Leaf async entity tracker off (cause of the 18:58 freeze)"
LG=$V/config/leaf-global.yml; cp -p $LG $BK/
sed -i "/^  async-entity-tracker:/,/enabled:/ s/enabled: true/enabled: false/" $LG
grep -A1 "^  async-entity-tracker:" $LG | grep -q "enabled: false" && ok "async-entity-tracker off" || no "check async-entity-tracker in leaf-global.yml"

echo "===== 4. Warzone regen turns PvP off"
S=$P/CMI/Settings/Schedules.yml
if grep -q "fboss warzonepvp" $S; then ok "schedule already done"
else cp -p $S $BK/
  sed -i 's/^\(  - broadcast! .*Warzone regenerating\.\.\.\)$/\1\n  - fboss warzonepvp off 45\n  - broadcast! \&8[\&dFinality\&7] \&cPvP is off in the Warzone while it regenerates./' $S
  grep -q "fboss warzonepvp off 45" $S && ok "Warzone regen: PvP off for 45s, then on + pvpmanager reload" || no "couldn't find the 'Warzone regenerating...' line in CMI Schedules.yml"
fi

echo "===== 5. Claimed villagers can't be killed"
CV=$P/ClickVillagers/config.yml
if [ -f $CV ]; then cp -p $CV $BK/; sed -i 's/^claimed_damage: true/claimed_damage: false/' $CV; grep -q "^claimed_damage: false" $CV && ok "ClickVillagers claimed_damage: false" || no "check ClickVillagers config"; else no "no ClickVillagers config"; fi

echo "===== 6. InstantBrew"
if [ "${KEEP_INSTANTBREW:-0}" = 1 ]; then echo "  kept (KEEP_INSTANTBREW=1)"
else for j in $P/InstantBrew*.jar; do [ -f "$j" ] && mv "$j" $BK/ && ok "InstantBrew disabled (jar moved to $BK) - brewing is now normal speed unless you buy Insta Brew"; done; fi

echo "===== 7. Ban suspects script"
curl -fsSL "$RAW/ban-candidates.py?$(date +%s)" -o /root/ban-candidates.py && ok "/root/ban-candidates.py  (run: sudo python3 /root/ban-candidates.py 7)"

chown -R $OWN $P/FinalityItems $P/FinalityBosses $P/Nexo/items $P/CMI/Settings/Schedules.yml $P/ClickVillagers $V/config/paper-global.yml $V/config/leaf-global.yml 2>/dev/null
echo; echo "ALL DONE. Backups: $BK"
echo "Now start the SMP, then in console: nexo reload all"
echo "Then: FinalityBans makes its config on first start - put your Discord webhook in plugins/FinalityBans/config.yml then /banwave reload"

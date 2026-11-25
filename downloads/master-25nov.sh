#!/usr/bin/env bash
# Finality SMP - everything from 25 Nov in one go. Run as root on the game machine with the SMP STOPPED.
#  1. FinalityItems 1.2.0: /perks (Insta Smelt + Insta Brew), Kill Tracker, rank Santa Hat once per player
#  2. FinalityBosses 1.3.2: /fboss warzonepvp - PvP is off while the Warzone regenerates
#  3. FinalityBans 1.0.0: weekly ban waves -> Discord + finality-en.github.io/bans
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
jar FinalityItems  1.2.0 68738aa6336f95bb64d7e522147c92ccffa031af7e65a3cdd9a889193d9085cd
jar FinalityBosses 1.3.2 5b8133c0f0b8d254820a64b266a22e56e4d6d60cbde7699dfdcd520d2f96717b
jar FinalityBans   1.0.0 44505be1ca153866c84ea864480837014c6f72221a2ac3cd34e31cf45df61c96
FIC=$P/FinalityItems/config.yml
if [ -f $FIC ] && ! grep -q "^perks:" $FIC; then cp -p $FIC $BK/; curl -fsSL $RAW/finality-items/perks-config.yml >> $FIC && ok "perks + kill tracker settings added to FinalityItems/config.yml"; else ok "FinalityItems config already has perks (or is new)"; fi

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
curl -fsSL $RAW/ban-candidates.py -o /root/ban-candidates.py && ok "/root/ban-candidates.py  (run: sudo python3 /root/ban-candidates.py 7)"

chown -R $OWN $P/FinalityItems $P/CMI/Settings/Schedules.yml $P/ClickVillagers 2>/dev/null
echo; echo "ALL DONE. Backups: $BK"
echo "Now start the SMP. FinalityBans makes its config on first start - put your Discord webhook in plugins/FinalityBans/config.yml then /banwave reload"

#!/usr/bin/env bash
# Finality SMP - everything from 25 Nov in one go. Run as root on the game machine with the SMP STOPPED.
#  0. Weapon abilities that never triggered (full-strength hit check read 0% on 1.21.11) - fixed in both plugins
#  1. FinalityItems 1.5.4: perks take coins properly, Demon Wings attach to chestplates (pinned to the back, /fitems wings to adjust), /fitems menu + tab complete + /fitems debug, Elf Candy Cane float ability repaired, /perks (7 perks, player + admin menus), Kill Tracker, rank Santa Hat once per player,
#     rename guard (no /itemname, /itemlore or anvil names that fake our items)
#  2. FinalityBosses 1.3.6: raid weapons much stronger (damage/speed/abilities all in config), /fboss warzonepvp,
#     boss items fully enchanted with lore that explains them,
#     /nexo give copies of boss items turn into the real thing
#  2a. Leaf 1.21.11 168 -> 184: includes the fix for the dripleaf dupe ("Paper: Fix tree capture state leak", build 181+)
#  2b. finality-classes 1.22.3: Class Upgrade Token craftable with crate/shop items (only real custom items are refused, with a message)
#  3. FinalityBans 1.2.1: ban waves + /banwave menu (Vulcan suspects, X-ray mining stats, queue, run wave),
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
jar FinalityItems  1.5.4 ab7ef4d7fe18b65cd3ebe52ec758bdc3e090bea42172410ec25bb8ae8324a075 || exit 1
jar FinalityBosses 1.3.6 af7cbf1d5b57256a11cbed5fd23f5a4b1e5888a1d32d3be136b7703d0461df70 || exit 1
jar finality-classes 1.22.3 5dff997efc0c8ba0859c4bcd53583ee032308212ce01a0cbc377de63cee26ae2 || exit 1
jar FinalityBans   1.2.1 c1918e96c932e18ec781ebeaa7afcae6ce30d38a18a0236fd0baec916eb15283 || exit 1
FIC=$P/FinalityItems/config.yml
if [ -f $FIC ] && ! grep -q "^  keepxp:" $FIC; then
  cp -p $FIC $BK/
  # an earlier update may have added the first version of perks (2 perks, cheap) - take it out first
  python3 - "$FIC" <<'PY'
import sys, re
p = sys.argv[1]; out = []; skip = False
for ln in open(p, encoding="utf-8").read().split("\n"):
    if re.match(r"^(perks|perks-menu):\s*$", ln): skip = True; continue
    if skip and (ln.startswith(" ") or ln.strip() == ""): continue
    skip = False; out.append(ln)
open(p, "w", encoding="utf-8").write("\n".join(out).rstrip("\n") + "\n")
PY
  curl -fsSL "$RAW/finality-items/perks-config.yml?$(date +%s)" >> $FIC && ok "perks settings (7 perks) in FinalityItems/config.yml"
else ok "FinalityItems config already has the 7 perks (or is new)"; fi
FBC=$P/FinalityBans/config.yml
[ -f $FBC ] && { cp -p $FBC $BK/fbans-config.yml; sed -i "s/^  post-instant-bans: false/  post-instant-bans: true/" $FBC; ok "FinalityBans: single bans post to Discord too (new settings get added on start)"; }

echo "===== 2a. Leaf 1.21.11 update (dripleaf dupe fix is in build 181+)"
LJ=$(ls $V/leaf-1.21.11*.jar 2>/dev/null | head -1)
if [ -z "$LJ" ]; then no "couldn't find the leaf-1.21.11 jar in the server folder - update Leaf by hand (build 181 or newer)"
else
  URL=$(curl -fsSL https://api.github.com/repos/Winds-Studio/Leaf/releases/tags/ver-1.21.11 | grep -o '"browser_download_url": *"[^"]*leaf-1\.21\.11-[0-9]*\.jar"' | head -1 | cut -d'"' -f4)
  BUILD=$(echo "$URL" | grep -o '1\.21\.11-[0-9]*' | cut -d- -f2)
  if [ -z "$URL" ] || [ "${BUILD:-0}" -lt 181 ]; then no "couldn't find Leaf 1.21.11 build 181+ on GitHub (found: ${BUILD:-none}) - kept your current Leaf"
  elif curl -fsSL "$URL" -o $T/leaf.jar && unzip -l $T/leaf.jar >/dev/null 2>&1; then
    SUM=$(sha256sum $T/leaf.jar | cut -c1-64)
    if [ "$BUILD" = 184 ] && [ "$SUM" != 7d2684d6801519015b78f946b5845609c06a5eb258d04574e8dd05a1156d46e8 ]; then no "Leaf 184 checksum mismatch - kept your current Leaf"
    else cp -p "$LJ" $BK/; cp $T/leaf.jar "$LJ" && chown $OWN "$LJ" && ok "Leaf 1.21.11 build $BUILD installed as $(basename $LJ) (old one in $BK) - dripleaf dupe fixed"; fi
  else no "Leaf download failed - kept your current Leaf"; fi
fi

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

echo "===== 3d. Leaf: async entity tracker off (18:58 freeze) + full entity movement updates (railguns)"
LG=$V/config/leaf-global.yml; cp -p $LG $BK/
sed -i "/^  async-entity-tracker:/,/enabled:/ s/enabled: true/enabled: false/" $LG
grep -A1 "^  async-entity-tracker:" $LG | grep -q "enabled: false" && ok "async-entity-tracker off" || no "check async-entity-tracker in leaf-global.yml"
sed -i "s/^    reduce-entity-move-packets: true/    reduce-entity-move-packets: false/" $LG
grep -q "^    reduce-entity-move-packets: false" $LG && ok "entity move packets not reduced (railgun arrows moved by pistons show properly)" || no "check reduce-entity-move-packets in leaf-global.yml"

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
else for j in $P/[Ii]nstant[Bb]rew*.jar; do [ -f "$j" ] && mv "$j" $BK/ && ok "InstantBrew disabled (jar moved to $BK) - brewing is now normal speed unless you buy Insta Brew"; done; fi

echo "===== 7. Ban suspects script"
curl -fsSL "$RAW/ban-candidates.py?$(date +%s)" -o /root/ban-candidates.py && ok "/root/ban-candidates.py  (run: sudo python3 /root/ban-candidates.py 7)"

chown -R $OWN $P/FinalityItems $P/FinalityBans $P/FinalityBosses $P/Nexo/items $P/CMI/Settings/Schedules.yml $P/ClickVillagers $V/config/paper-global.yml $V/config/leaf-global.yml 2>/dev/null
echo; echo "ALL DONE. Backups: $BK"
echo "Now start the SMP, then in console: nexo reload all"
echo "Then: FinalityBans makes its config on first start - put your Discord webhook in plugins/FinalityBans/config.yml then /banwave reload"

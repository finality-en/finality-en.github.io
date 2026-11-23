#!/usr/bin/env bash
# Finality SMP - fix-all (23 Nov). Run as root on the game machine with the SMP STOPPED.
# Every file it touches is copied to /root/finality-backup-<date> first.
set -u
V=/var/lib/pterodactyl/volumes/9b618852-57d9-4326-b2ae-506798142a97
P=$V/plugins
RAW=https://raw.githubusercontent.com/finality-en/finality-en.github.io/main/downloads
BK=/root/finality-backup-$(date +%F-%H%M)
hr(){ echo; echo "==================== $* ===================="; }
bak(){ [ -f "$1" ] && mkdir -p "$BK$(dirname "${1#$V}")" && cp -p "$1" "$BK${1#$V}"; }

[ -d "$P" ] || { echo "SMP plugins folder not found at $P"; exit 1; }
if docker ps --format '{{.Names}}' | grep -q 9b618852-57d9-4326-b2ae-506798142a97; then
  echo "!! The SMP is still running. Stop it in the panel first (configs get overwritten on shutdown), then run this again."
  exit 1
fi
OWN=$(stat -c %u:%g "$P")
mkdir -p "$BK"; echo "Backups -> $BK"

plugname(){  # plugin name inside a jar
  if command -v unzip >/dev/null; then unzip -p "$1" plugin.yml paper-plugin.yml 2>/dev/null
  else python3 - "$1" <<'PY' 2>/dev/null
import sys,zipfile
z=zipfile.ZipFile(sys.argv[1])
for n in ("plugin.yml","paper-plugin.yml"):
    if n in z.namelist(): print(z.read(n).decode("utf8","ignore")); break
PY
  fi | grep -m1 '^name:' | sed "s/^name:[ ]*//; s/['\"]//g; s/\r//"
}

hr "1. PLUGIN JARS"
putjar(){ # file pluginName sha256
  f=$1; n=$2; sha=$3
  curl -fsSL "$RAW/$f" -o "/tmp/$f" || { echo "FAIL download $f"; return; }
  echo "$sha  /tmp/$f" | sha256sum -c --quiet - || { echo "FAIL checksum $f"; return; }
  for j in "$P"/*.jar; do
    [ "$(plugname "$j")" = "$n" ] && { mv "$j" "$BK/"; echo "  old: $(basename "$j") -> backup"; }
  done
  mv "/tmp/$f" "$P/$f"; chown "$OWN" "$P/$f"; echo "OK  $f"
}
putjar FinalityChallenges-1.3.0.jar FinalityChallenges 7788099e9d3e3095dc6cafbf6d22bb2da3c2c1601deacf1ddf9c892dd8a46320
putjar FinalityBosses-1.1.0.jar     FinalityBosses     1c0caafc2b4d6452bcf1ca7b6ce2406dce4a073ae59e83dee4ba509042b47509
putjar FinalityKillFeed-1.1.0.jar   FinalityKillFeed   8aeedd10876c47a5d8e0e5d21a9402d570d5386e2c1f5b798c865460c2592e1d
putjar finality-classes-1.22.1.jar  finality-classes   f545557a9ed4177a7e9826fa056c811c090bb53276b4002b708f7c72882fc6b0

hr "2. MACE DUPE (MaceLimiter craft handler off)"
F=$P/MaceLimiter/config.yml
if [ -f "$F" ]; then bak "$F"; sed -i 's/^enabled:[ ]*true/enabled: false/' "$F"; grep -n '^enabled' "$F"; else echo "MaceLimiter config not found"; fi

hr "3. TREASURE MAPS"
for F in "$V/config/paper-world-defaults.yml" "$V"/*/paper-world.yml; do
  [ -f "$F" ] || continue
  grep -q 'treasure-maps:' "$F" || continue
  bak "$F"
  sed -i '/treasure-maps:/,/enabled:/ s/enabled: false/enabled: true/' "$F"
  echo "$F:"; grep -n -A1 'treasure-maps:' "$F"
done

hr "4. CHALLENGES (relic key + /claim)"
F=$P/FinalityChallenges/config.yml
if [ -f "$F" ]; then
  bak "$F"
  sed -i "s/\([\"']\|- \)key give /\1ac key give /g; s/Rewards given\./Type \/claim to collect them!/g" "$F"
  grep -q '^  claim:' "$F" || sed -i '/^rewards-delivery:/a\  claim: true\n  remind-minutes: 5' "$F"
  echo "key commands now:"; grep -n 'key give' "$F" | head -20
  echo "rewards-delivery:"; grep -n -A6 '^rewards-delivery:' "$F"
  echo "voucher/shard ids (for nexusbagels):"; grep -n -i 'voucher\|glacial' "$F" | head -10
else echo "Challenges config not found"; fi

hr "5. EVIL ELF (relic key, warzone lockdown, pre-spawn clear)"
F=$P/FinalityBosses/config.yml
RG=$P/WorldGuard/worlds/world/regions.yml
if [ -f "$F" ]; then
  bak "$F"
  sed -i "s/\([\"']\|- \)key give /\1ac key give /g" "$F"
  # what are the warzone's normal build flags? restore to that after the fight
  WZ=$(awk '/^    warzone:/{f=1;next} f&&/^    [^ ]/{f=0} f' "$RG" 2>/dev/null)
  echo "warzone flags now: $(echo "$WZ" | grep -o 'block-[a-z]*: [a-z]*' | tr '\n' ' ')"
  BP=""; echo "$WZ" | grep -q 'block-place: allow' && BP=" allow"
  BB=""; echo "$WZ" | grep -q 'block-break: allow' && BB=" allow"
  sed -i "s/^  disable-commands:.*/  disable-commands: ['rg flag -w world warzone pvp deny', 'rg flag -w world warzone block-place deny', 'rg flag -w world warzone block-break deny']/" "$F"
  sed -i "s/^  enable-commands:.*/  enable-commands: ['rg flag -w world warzone pvp allow', 'rg flag -w world warzone block-place$BP', 'rg flag -w world warzone block-break$BB']/" "$F"
  CMIS=$P/CMI/Saves/Schedules.yml; [ -f "$CMIS" ] || CMIS=$(find "$P/CMI" -name 'Schedules.yml' | head -1)
  PRE=""
  if [ -n "$CMIS" ] && grep -q '^  WarzoneRegeneration:' "$CMIS"; then PRE="'cmi schedule WarzoneRegeneration'"
  else echo "!! No CMI schedule called WarzoneRegeneration. Schedules found:"; grep -o '^  [A-Za-z0-9_]*:' "$CMIS" 2>/dev/null; fi
  if ! grep -q '^  pre-spawn:' "$F"; then
    sed -i "/^  min-players:/a\  pre-spawn:\n    enabled: true\n    seconds: 60\n    commands: [$PRE]" "$F"
  fi
  grep -n 'able-commands\|ac key give' "$F"; grep -n -A3 '^  pre-spawn:' "$F"; grep -n -A1 '^  times:' "$F"
else echo "Bosses config not found"; fi

hr "6. KOTH TWICE A DAY (16:00 + 21:00)"
F=$P/AxKoth/schedulers.yml
if [ -f "$F" ]; then
  bak "$F"
  grep -q "0 16 \* \* \*" "$F" || sed -i "s/^\( *\)- '\?0 21 \* \* \*'\?$/\1- 0 16 * * *\n\1- 0 21 * * */" "$F"
  cat "$F"
  echo "AxKoth timezone setting:"; grep -rn -i 'timezone\|time-zone' "$P/AxKoth/config.yml" || echo "  (none - uses server clock: $(date +%Z))"
else echo "AxKoth schedulers.yml not found"; fi

hr "7. DISCORD DEATH MESSAGES"
F=$P/DiscordSRV/messages.yml
if [ -f "$F" ]; then
  bak "$F"
  awk '/^[A-Za-z]/{s=($0 ~ /^MinecraftPlayerDeathMessage:/)} s && /^  Enabled: true/{sub(/true/,"false")} {print}' "$F" > /tmp/dsrv.yml && cat /tmp/dsrv.yml > "$F"
  grep -n -A1 '^MinecraftPlayerDeathMessage:' "$F"
fi
echo "KillFeed channel: $(grep -m1 'channel-id' "$P/FinalityKillFeed/config.yml" 2>/dev/null)"
echo "DiscordSRV channels: $(grep -A4 '^Channels:' "$P/DiscordSRV/config.yml" | tr '\n' ' ' 2>/dev/null)"

hr "8. TAB: Next Boss / Next KOTH"
F=$P/TAB/config.yml
if [ -f "$F" ]; then
  bak "$F"
  if grep -q finalitybosses "$F"; then echo "already added"
  else
    awk '
      /^header-footer:/ {hf=1}
      /^[a-z]/ && !/^header-footer:/ {hf=0}
      {print}
      hf && !done && /^[ ]+footer:[ ]*$/ {
        getline nxt; ind=nxt; sub(/-.*/, "", ind)
        print ind "- \"&7Next Boss: &a%finalitybosses_next%  &8|  &7Next KOTH: &6%finalitybosses_koth%\""
        print nxt; done=1
      }' "$F" > /tmp/tab.yml && mv /tmp/tab.yml "$F" && chown "$OWN" "$F"
  fi
  awk '/^header-footer:/{f=1} f&&/^[a-z]/&&!/^header-footer:/{f=0} f' "$F" | head -40
else
  echo "No TAB on the SMP. Looking elsewhere:"; ls -d /var/lib/pterodactyl/volumes/*/plugins/[Tt][Aa][Bb]* 2>/dev/null
fi

chown -R "$OWN" "$P/FinalityChallenges" "$P/FinalityBosses" "$P/AxKoth" 2>/dev/null
hr "DONE - start the SMP now. Backups in $BK"

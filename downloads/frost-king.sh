#!/usr/bin/env bash
# Finality SMP - Frost King (PvP boss) + Frostfang + Frost King Voucher + End date -> Sat 5 Dec.
# Run as root on the game machine with the SMP STOPPED. Backups go to /root/frostking-backup-<time>.
set -u
V=/var/lib/pterodactyl/volumes/9b618852-57d9-4326-b2ae-506798142a97; P=$V/plugins
RAW=https://raw.githubusercontent.com/finality-en/finality-en.github.io/main/downloads
BK=/root/frostking-backup-$(date +%F-%H%M); mkdir -p $BK; T=$(mktemp -d)
ok(){ echo "✅ $*"; }; no(){ echo "❌ $*"; }
if docker ps --format '{{.Names}}' | grep -q 9b618852-57d9-4326-b2ae-506798142a97; then echo "!! Stop the SMP in the panel first, then run this again."; exit 1; fi
OWN=$(stat -c %u:%g $P)
bak(){ [ -f "$1" ] && cp -p "$1" "$BK/$(echo ${1#$P/} | tr / _)"; }
ins_after(){ # file anchorRegex snippetFile
  awk -v f="$3" -v a="$2" '{print} $0 ~ a && !d {while((getline l < f)>0) print l; d=1}' "$1" > $T/x && cat $T/x > "$1"; }

echo "===== 1. FinalityBosses 1.2.0"
for f in frost_king_block.yml frost_king_loot.yml frost_voucher.yml frostfang_nexo.yml weapon_effects_frostfang.yml frostfang.png; do curl -fsSL "$RAW/frost-king/$f" -o $T/$f || { no "download $f"; exit 1; }; done
curl -fsSL $RAW/FinalityBosses-1.2.0.jar -o $T/fb.jar && echo "fa74fc3484cda510bb01925db2599bdcb0aa2937b915b18b39087ddc1747f865  $T/fb.jar" | sha256sum -c --quiet - || { no "jar download/checksum"; exit 1; }
for j in $P/FinalityBosses-*.jar; do [ -f "$j" ] && mv "$j" $BK/ && echo "  old $(basename $j) -> backup"; done
cp $T/fb.jar $P/FinalityBosses-1.2.0.jar && chown $OWN $P/FinalityBosses-1.2.0.jar && ok "FinalityBosses-1.2.0.jar installed"

echo "===== 2. Frost King config"
C=$P/FinalityBosses/config.yml; bak $C
if grep -q '^  frost_king:' $C; then # replace an older Frost King block with the new one
  awk '/^  frost_king:[[:space:]]*$/{skip=1; next} skip && (/^  [A-Za-z_]/ || /^[^ #\n]/){skip=0} !skip' $C > $T/x && cat $T/x > $C; echo "  (replacing the old frost_king settings)"; fi
ins_after $C '^bosses:[[:space:]]*$' $T/frost_king_block.yml; grep -q '^  frost_king:' $C && ok "frost_king (2000 HP, new abilities) in config.yml" || no "couldn't add frost_king"
if grep -q '^  frostfang:' $C; then ok "frostfang effects already there"; else ins_after $C '^weapon-effects:[[:space:]]*$' $T/weapon_effects_frostfang.yml; grep -q '^  frostfang:' $C && ok "Frostfang swing + freeze added" || no "couldn't add weapon-effects.frostfang"; fi
L=$P/FinalityBosses/loot.yml; bak $L
grep -q '^frost_king:' $L && ok "loot already there" || { cat $T/frost_king_loot.yml >> $L && ok "Frost King floor loot added"; }

echo "===== 3. Frost King Voucher (FinalityChallenges)"
CC=$P/FinalityChallenges/config.yml; bak $CC
if grep -q '^  frost_voucher:' $CC; then ok "voucher already there"; else ins_after $CC '^vouchers:[[:space:]]*$' $T/frost_voucher.yml; grep -q '^  frost_voucher:' $CC && ok "frost_voucher added" || no "couldn't add frost_voucher"; fi

echo "===== 4. Frostfang Nexo item + texture"
NI=$(grep -rl '^elf_candy_cane:' $P/Nexo/items 2>/dev/null | head -1)
if [ -z "$NI" ]; then no "couldn't find the Nexo items file with elf_candy_cane"; else bak $NI; grep -q '^frostfang:' $NI && ok "Frostfang already in $(basename $NI)" || { cat $T/frostfang_nexo.yml >> $NI && ok "Frostfang added to Nexo/items/$(basename $NI)"; }; fi
TX=$(find $P/Nexo -name 'elf_candy_cane.png' -path '*textures*' 2>/dev/null | head -1)
if [ -z "$TX" ]; then no "couldn't find elf_candy_cane.png texture - put frostfang.png next to it by hand"; else cp $T/frostfang.png "$(dirname $TX)/frostfang.png" && ok "texture -> ${TX#$P/}"; fi

echo "===== 5. End opens Sat 5 Dec 20:00 (finality-unlocks.sk)"
SK=$(find $P/Skript/scripts -name 'finality-unlocks.sk' | head -1)
if [ -z "$SK" ]; then no "finality-unlocks.sk not found"; else bak $SK; sed -i 's/^\(\s*end-at:\s*\)[0-9]\+/\11796500800/; s/1795809600 = Fri 27 Nov 2026, 20:00/1796500800 = Sat 5 Dec 2026, 20:00/' $SK; grep -n 'end-at:' $SK; fi

chown -R $OWN $P/FinalityBosses $P/FinalityChallenges $P/Nexo $P/Skript 2>/dev/null
echo; echo "DONE. Backups: $BK"
echo "Now: start the SMP, then in console:  nexo reload all"

#!/usr/bin/env bash
# KOTH rewards -> one KOTH Reward Voucher (claim needs 9 empty slots). FinalityChallenges 1.3.2.
# Run as root on the game machine with the SMP STOPPED.
set -u
V=/var/lib/pterodactyl/volumes/9b618852-57d9-4326-b2ae-506798142a97; P=$V/plugins
RAW=https://raw.githubusercontent.com/finality-en/finality-en.github.io/main/downloads
BK=/root/kothvoucher-backup-$(date +%F-%H%M); mkdir -p $BK; T=$(mktemp -d)
ok(){ echo "✅ $*"; }; no(){ echo "❌ $*"; }
if docker ps --format '{{.Names}}' | grep -q 9b618852-57d9-4326-b2ae-506798142a97; then echo "!! Stop the SMP in the panel first, then run this again."; exit 1; fi
OWN=$(stat -c %u:%g $P)
curl -fsSL $RAW/koth_voucher.yml -o $T/kv.yml || { no "download voucher"; exit 1; }
curl -fsSL $RAW/FinalityChallenges-1.3.2.jar -o $T/fc.jar && echo "b1386a5b9400fa1f4f5cd382571d3dc56f9fa6831180c9d0946351a52d3646f4  $T/fc.jar" | sha256sum -c --quiet - || { no "jar download/checksum"; exit 1; }
for j in $P/FinalityChallenges-*.jar; do [ -f "$j" ] && mv "$j" $BK/ && echo "  old $(basename $j) -> backup"; done
cp $T/fc.jar $P/FinalityChallenges-1.3.2.jar && ok "FinalityChallenges-1.3.2.jar installed"
C=$P/FinalityChallenges/config.yml; cp -p $C $BK/
if grep -q '^  koth_rewards:' $C; then ok "voucher already in config"; else sed -i "/^vouchers:[[:space:]]*$/r $T/kv.yml" $C; grep -q '^  koth_rewards:' $C && ok "KOTH Reward Voucher added" || no "couldn't add the voucher"; fi
K=$P/AxKoth/koths/koth.yml; cp -p $K $BK/koth.yml
awk 'BEGIN{r=0} /^reward-commands:/{print; print "- challenge voucher give %player% koth_rewards 1"; r=1; next} r && /^- /{next} {r=0; print}' $K > $T/k && cat $T/k > $K
sed -n '/^reward-commands:/,/^$/p' $K; ok "KOTH now gives the voucher"
chown -R $OWN $P/FinalityChallenges $P/FinalityChallenges-1.3.2.jar $K
echo; echo "DONE. Backups: $BK  (NOT inside plugin folders)"; echo "Now: start the SMP."

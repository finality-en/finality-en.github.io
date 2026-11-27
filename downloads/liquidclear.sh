#!/bin/bash
# Installs FinalityLiquidClear (lag-free /clearblocks) and turns off the old Skript version.
# Safe with the SMP running - both changes take effect at the next restart.
V=/var/lib/pterodactyl/volumes/9b618852-57d9-4326-b2ae-506798142a97; P=$V/plugins
R=${R:-https://raw.githubusercontent.com/finality-en/finality-en.github.io/main/downloads}
J=FinalityLiquidClear-1.0.0.jar; SUM=b2f352f7826e3a727ebc72cd6e67d77f228ecb9b8c7171f8c1494a4e7e46d379
T=$(mktemp -d); curl -fsSL "$R/$J" -o "$T/$J" && echo "$SUM  $T/$J" | sha256sum -c --quiet - || { echo "❌ download/checksum failed - nothing changed"; exit 1; }
cp "$T/$J" $P/ && chown --reference=$P $P/$J && echo "✅ $J installed"
S=$P/Skript/scripts/clearliquids.sk
if [ -f "$S" ]; then mv "$S" "$P/Skript/scripts/-clearliquids.sk" && echo "✅ old clearliquids.sk disabled (renamed to -clearliquids.sk)"; else echo "ℹ️  clearliquids.sk already disabled"; fi
echo "Restart the SMP when convenient. /clearblocks then runs without lag (allow-flight=true also applies then)."

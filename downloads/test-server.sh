#!/usr/bin/env bash
# Copies the SMP's plugins + configs onto a NEW Pterodactyl server for testing weapons/bosses.
# Usage (as root, both servers stopped):  bash test-server.sh <test-server-uuid> [--with-worlds]
# Store, website, Discord and vote plugins are left out so the test server can't deliver purchases,
# overwrite website stats or post to Discord. Whitelist is turned on.
set -u
SMP=/var/lib/pterodactyl/volumes/9b618852-57d9-4326-b2ae-506798142a97
[ $# -ge 1 ] || { echo "Usage: bash test-server.sh <test-server-uuid> [--with-worlds]"; exit 1; }
TV=/var/lib/pterodactyl/volumes/$1
[ -d "$TV" ] || { echo "!! No volume $TV - copy the UUID from the test server's panel URL / Settings > Debug Information"; exit 1; }
for id in 9b618852-57d9-4326-b2ae-506798142a97 $1; do
  docker ps --format '{{.Names}}' | grep -q $id && { echo "!! Stop both servers first ($id is running)"; exit 1; }; done
OWN=$(stat -c %u:%g $TV)

EXCL=(--exclude='logs' --exclude='crash-reports' --exclude='cache' --exclude='libraries' --exclude='versions'
  --exclude='plugins/FinalityStore*' --exclude='plugins/FinalityWebStats*' --exclude='plugins/FinalityBans*'
  --exclude='plugins/DiscordSRV*' --exclude='plugins/*otifier*' --exclude='plugins/Votifier*' --exclude='plugins/FancyAnalytics*'
  --exclude='plugins/spark/tmp*' --exclude='*.lock')
if [ "${2:-}" != "--with-worlds" ]; then
  for w in $(cd $SMP && for d in */; do [ -f "$d/level.dat" ] && echo "${d%/}"; done); do EXCL+=(--exclude="/$w"); done
  echo "Worlds left out (fresh worlds will generate). Add --with-worlds to copy them too."
fi
rsync -a "${EXCL[@]}" $SMP/ $TV/ || { echo "rsync failed"; exit 1; }
sed -i -e 's/^white-list=.*/white-list=true/' -e 's/^enforce-whitelist=.*/enforce-whitelist=true/' \
       -e 's/^motd=.*/motd=\\u00a7c\\u00a7lFinality \\u00a77Test Server/' $TV/server.properties
chown -R $OWN $TV
echo "✅ Test server ready. Start it in the panel, then in ITS console:  whitelist on  and  whitelist add <name>  for each mod / Finality player."

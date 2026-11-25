#!/usr/bin/env bash
# Ticket 684: what happened around 20:55-21:15 (everyone timed out / "server freeze").
# Usage: sudo bash lag-diag.sh            (checks the last 6 log files + latest.log)
L=/var/lib/pterodactyl/volumes/9b618852-57d9-4326-b2ae-506798142a97/logs
cd $L || exit 1
for f in $(ls -t *.log.gz 2>/dev/null | head -6 | tac) latest.log; do
  M=$(zcat -f "$f" | awk -F'[][:]' '($2==20 && $3>=50) || ($2==21 && $3<=20)')
  echo "$M" | grep -qiE "Oppossite|Penguin|BigManMao|Fentzi|yozin" || continue
  echo "################ $f"
  echo "$M" | grep -iE "keep up|timed out|lost connection|watchdog|thread dump|disconnect|kick|exception|error|warn|save|Oppossite|Penguin|BigManMao|Fentzi|yozin|regen|boss|koth|clearblocks|restart" | cut -c1-260 | head -150
  echo "--- 'Can't keep up' in this window: $(echo "$M" | grep -c "keep up")"
done

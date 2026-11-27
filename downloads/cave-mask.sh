#!/bin/bash
# Finality cave mask v2 (RayTraceAntiXray 1.16.3-pe6) - run with the SMP STOPPED:  sudo bash cave-mask.sh
V=/var/lib/pterodactyl/volumes/9b618852-57d9-4326-b2ae-506798142a97; P=$V/plugins
R=${R:-https://raw.githubusercontent.com/finality-en/finality-en.github.io/main/downloads}
T=$(mktemp -d); mkdir -p /root/old-jars
pgrep -f "9b618852-57d9-4326-b2ae-506798142a97" >/dev/null && { echo "⚠️  The SMP still looks like it's running - stop it first."; exit 1; }
J=RayTraceAntiXray-1.16.3-pe6.jar; SUM=40eb30136837e6aa72337e2635a3eba23e9d7922097589dcb0497e66a8e1e220
curl -fsSL "$R/$J" -o "$T/$J" && echo "$SUM  $T/$J" | sha256sum -c --quiet - || { echo "❌ download/checksum failed - nothing changed"; exit 1; }
for f in $P/raytraceantixray-*.jar $P/RayTraceAntiXray-*.jar $P/.paper-remapped/raytraceantixray-*.jar $P/.paper-remapped/RayTraceAntiXray-*.jar; do [ -f "$f" ] && mv "$f" /root/old-jars/; done
cp "$T/$J" $P/ && chown --reference=$P $P/$J && echo "✅ RayTraceAntiXray 1.16.3-pe6 (cave mask v2)"

HIDE=${HIDE:-60}; DEPTH=${DEPTH:-5}; RADIUS=${RADIUS:-3}; BAND=${BAND:-1}
python3 - "$P/RayTraceAntiXray/config.yml" "$HIDE" "$DEPTH" "$RADIUS" "$BAND" <<'PY'
import re,sys,shutil,time
p=sys.argv[1]; H,D,RA,B=map(int,sys.argv[2:6]); s=open(p,encoding='utf-8').read()
shutil.copy2(p,p+'.bak-cavemask-'+time.strftime('%Y%m%d-%H%M%S'))
s=re.sub(r'(?m)^    cave-mask:[^\n]*\n(?:(?:      [^\n]*)?\n)*','',s)
block=('    cave-mask:\n'
       '      # everything more than surface-depth blocks under the natural ground (and below hide-below-y) is sent as solid\n'
       '      # stone/deepslate. Underground, only the player\'s own height band within reveal-radius-chunks is real.\n'
       '      enabled: true\n      hide-below-y: %d\n      surface-depth: %d\n      reveal-radius-chunks: %d\n      reveal-vertical-sections: %d\n'%(H,D,RA,B))
m=re.search(r'(?m)^  world:[^\n]*\n',s)
if m: s=s[:m.end()]+block+s[m.end():]
else:
    m=re.search(r'(?m)^world-settings:\s*\n',s)
    if not m: sys.exit('❌ no world-settings: in RayTraceAntiXray config - not changed')
    s=s[:m.end()]+'  world:\n'+block+s[m.end():]
if 'check-interval-ticks' not in s: s=s.replace('settings:\n  anti-xray:\n','settings:\n  cave-mask:\n    check-interval-ticks: 10\n    max-resends-per-check: 24\n  anti-xray:\n',1)
open(p,'w',encoding='utf-8').write(s)
print('✅ cave mask v2 in "world": hidden more than %d blocks under the ground (below Y %d); underground you see %d chunks around you, +/-%d section(s)'%(D,H,RA,B))
PY
echo "Done - start the SMP. Staff who need to see real caves: raytraceantixray.cavemask.bypass"

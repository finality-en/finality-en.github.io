#!/bin/bash
# Finality cave mask (RayTraceAntiXray 1.16.3-pe5) - run with the SMP STOPPED:  sudo bash cave-mask.sh
V=/var/lib/pterodactyl/volumes/9b618852-57d9-4326-b2ae-506798142a97; P=$V/plugins
R=${R:-https://raw.githubusercontent.com/finality-en/finality-en.github.io/main/downloads}
T=$(mktemp -d); mkdir -p /root/old-jars
pgrep -f "9b618852-57d9-4326-b2ae-506798142a97" >/dev/null && { echo "⚠️  The SMP still looks like it's running - stop it first."; exit 1; }
J=RayTraceAntiXray-1.16.3-pe5.jar; SUM=f4920830492ccf239391b757d82957e18bcc2162361b84e2651072167afabb41
curl -fsSL "$R/$J" -o "$T/$J" && echo "$SUM  $T/$J" | sha256sum -c --quiet - || { echo "❌ download/checksum failed - nothing changed"; exit 1; }
for f in $P/raytraceantixray-*.jar $P/RayTraceAntiXray-*.jar $P/.paper-remapped/raytraceantixray-*.jar $P/.paper-remapped/RayTraceAntiXray-*.jar; do [ -f "$f" ] && mv "$f" /root/old-jars/; done
cp "$T/$J" $P/ && chown --reference=$P $P/$J && echo "✅ RayTraceAntiXray 1.16.3-pe5 (cave mask)"

HIDE=${HIDE:-16}; REVEAL=${REVEAL:-40}
python3 - "$P/RayTraceAntiXray/config.yml" "$HIDE" "$REVEAL" <<'PY'
import re,sys,shutil,time
p=sys.argv[1]; H=int(sys.argv[2])>>4<<4; RV=int(sys.argv[3]); s=open(p,encoding='utf-8').read()
if re.search(r'(?m)^    cave-mask:',s):
    s2=re.sub(r'(?m)^(      hide-below-y:) *-?\d+',r'\g<1> %d'%H,s); s2=re.sub(r'(?m)^(      reveal-when-below-y:) *-?\d+',r'\g<1> %d'%RV,s2)
    if s2!=s: shutil.copy2(p,p+'.bak-cavemask-'+time.strftime('%Y%m%d-%H%M%S')); open(p,'w',encoding='utf-8').write(s2)
    print('✅ cave mask: hidden below Y %d, revealed once below Y %d'%(H,RV)); sys.exit()
block=('    cave-mask:\n'
       '      # below hide-below-y everything is sent as solid deepslate (caves, trial chambers, ancient cities,\n'
       '      # mineshafts, underground bases, chests/spawners) until the player is below reveal-when-below-y,\n'
       '      # then the real terrain within reveal-radius-chunks around them is sent\n'
       '      enabled: true\n      hide-below-y: %d\n      reveal-when-below-y: %d\n      reveal-radius-chunks: 3\n'%(H,RV))
shutil.copy2(p,p+'.bak-cavemask-'+time.strftime('%Y%m%d-%H%M%S'))
m=re.search(r'(?m)^  world:\s*\n',s)
if m: s=s[:m.end()]+block+s[m.end():]
else:
    m=re.search(r'(?m)^world-settings:\s*\n',s)
    if not m: sys.exit('❌ no world-settings: in RayTraceAntiXray config - not changed')
    s=s[:m.end()]+'  world:\n'+block+s[m.end():]
s=s.replace('settings:\n  anti-xray:\n','settings:\n  cave-mask:\n    check-interval-ticks: 10\n    max-resends-per-check: 24\n  anti-xray:\n',1) if 'check-interval-ticks' not in s else s
open(p,'w',encoding='utf-8').write(s); print('✅ cave mask on in "world": hidden below Y %d, revealed within 3 chunks once below Y %d'%(H,RV))
PY
echo "Done - start the SMP. Staff who need to see real caves from the surface: raytraceantixray.cavemask.bypass"

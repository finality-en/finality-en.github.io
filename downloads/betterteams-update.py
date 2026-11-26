#!/usr/bin/env python3
"""BetterTeams: update to the latest SpigotMC release (via the Spiget mirror) and turn off its
Minecraft-team nametags (useTeams) - 5.1.2 added players to scoreboard teams from a background thread,
which corrupted the scoreboard and froze the server (26 Nov 17:46).
Only installs a jar that really is BetterTeams >= 5.1.9; otherwise keeps the current one.
Run with the SMP stopped:  python3 betterteams-update.py <plugins folder>"""
import sys, os, re, glob, io, json, shutil, time, zipfile, urllib.request

P = sys.argv[1]
UA = {"User-Agent": "finality-smp-master/1.0"}
MIN = (5, 1, 9)

def ver(s):
    return tuple(int(x) for x in re.findall(r'\d+', s)[:3])

# 1) config: useTeams false
cfg = P + '/BetterTeams/config.yml'
if os.path.exists(cfg):
    s = open(cfg, encoding='utf-8').read()
    s2 = re.sub(r'(?m)^useTeams:\s*true\b', 'useTeams: false', s)
    if s2 != s:
        shutil.copy2(cfg, cfg + '.bak-useteams-' + time.strftime('%Y%m%d-%H%M%S'))
        open(cfg, 'w', encoding='utf-8').write(s2)
        print('✅ BetterTeams useTeams: false (no more async scoreboard writes)')
    else:
        print('= BetterTeams useTeams already off')

# 2) jar
cur = [f for f in glob.glob(P + '/BetterTeams-*.jar')]
try:
    meta = json.load(urllib.request.urlopen(urllib.request.Request(
        'https://api.spiget.org/v2/resources/17129/versions/latest', headers=UA), timeout=30))
    data = urllib.request.urlopen(urllib.request.Request(
        'https://api.spiget.org/v2/resources/17129/download', headers=UA), timeout=120).read()
    z = zipfile.ZipFile(io.BytesIO(data))
    pyml = z.read('plugin.yml').decode('utf-8', 'replace')
    name = re.search(r'(?m)^name:\s*(\S+)', pyml).group(1)
    v = re.search(r'(?m)^version:\s*[\'"]?([^\'"\s]+)', pyml).group(1)
    if name != 'BetterTeams' or ver(v) < MIN:
        sys.exit(f'❌ download was {name} {v} (need BetterTeams >= 5.1.9) - kept the current jar')
    if any(os.path.basename(f) == f'BetterTeams-{v}.jar' for f in cur):
        print(f'= BetterTeams {v} already installed')
    else:
        os.makedirs('/root/old-jars', exist_ok=True)
        for f in cur + glob.glob(P + '/.paper-remapped/BetterTeams-*.jar'):
            shutil.move(f, '/root/old-jars/' + os.path.basename(f))
        out = P + f'/BetterTeams-{v}.jar'
        open(out, 'wb').write(data)
        st = os.stat(P); os.chown(out, st.st_uid, st.st_gid)
        print(f'✅ BetterTeams {v} installed (Spigot latest: {meta.get("name")}); old jar in /root/old-jars')
except SystemExit:
    raise
except Exception as e:
    print(f'❌ BetterTeams download failed ({e}) - kept the current jar; useTeams is still off so the freeze can\'t happen')

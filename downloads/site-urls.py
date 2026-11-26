#!/usr/bin/env python3
"""Players never see the GitHub address: ban list -> guide.finalitymc.org/bans, /guide -> guide.finalitymc.org.
Leaves repo: settings (where the plugins upload to) alone. Safe to run live and to run again."""
import re, sys, glob, shutil, time
P = sys.argv[1]
stamp = time.strftime('%Y%m%d-%H%M%S')
for f in glob.glob(P + '/*/config.yml') + glob.glob(P + '/*/messages.yml'):
    try: s = open(f, encoding='utf-8').read()
    except Exception: continue
    out = []
    for line in s.splitlines(keepends=True):
        if not re.match(r'\s*repo:', line):
            line = re.sub(r'https?://finality-en\.github\.io/bans/?', 'https://guide.finalitymc.org/bans', line)
            line = line.replace('finality-en.github.io/bans', 'guide.finalitymc.org/bans')
            if f.endswith('SeasonAbilities/config.yml'):
                line = re.sub(r'^(\s*url:\s*)"https?://finality-en\.github\.io/?"', r'\1"https://guide.finalitymc.org/"', line)
        out.append(line)
    s2 = ''.join(out)
    if f.endswith('FinalityBans/config.yml') and not re.search(r'(?m)^  footer:', s2):
        s2 = re.sub(r'(?m)^(  description: .*\n)', r'\1  footer: "guide.finalitymc.org/bans"\n', s2, count=1)
    if s2 != s:
        shutil.copy2(f, f + '.bak-urls-' + stamp)
        open(f, 'w', encoding='utf-8').write(s2)
        print('✅ links fixed in', f.split('/')[-2])
print('= site links done')

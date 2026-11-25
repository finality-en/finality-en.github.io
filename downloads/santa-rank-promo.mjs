// One-off: makes "ranks come with a Santa Hat" easy to see.
//  1. MVP / Finality ranks + the 3 upgrades: the Santa Hat line moves to the TOP of the description
//  2. Santa Hat: says it's free with MVP or higher
//  3. MVP + Finality cards get a "🎅 + Santa Hat" badge
// Run on the VPS with the store stopped:
//   systemctl stop finality-store
//   cd /opt/finality/store-server && sudo -u finality node scripts/santa-rank-promo.mjs
//   systemctl start finality-store
// Safe to run again.
import { db } from '../src/db.js';
import { getPackage } from '../src/catalog.js';
import { writeLocal } from '../src/publisher.js';

const LINE = '> 🎅 **Comes with a free Santa Hat!** One per player, so upgrading again won\'t give you a second one.';
const OLD = /\n*🎅 \*\*Comes with a Santa Hat\*\*[^\n]*/g;

for (const id of ['mvp-rank', 'finality-rank', 'vip-mvp', 'mvp-finality', 'vip-finality']) {
  const p = getPackage(id);
  if (!p) { console.log(`  (no package ${id})`); continue; }
  let d = (p.description || '').replace(OLD, '').replace(LINE, '').replace(/^\n+/, '').replace(/\n+$/, '');
  p.description = LINE + '\n\n' + d;
  console.log(`  ${p.name}: Santa Hat line at the top`);
}

const hat = getPackage('santa-hat');
if (hat) {
  const FREE = '> 🎅 **Free with MVP rank or higher** (one per player)';
  if (!hat.description.includes(FREE)) {
    const d = hat.description.split('\n');
    const at = d[0].startsWith('## ') ? 1 : 0;   // straight under the heading
    d.splice(at, 0, FREE, '');
    hat.description = d.join('\n');
  }
  console.log('  Santa Hat: says it is free with MVP+');
}

for (const id of ['mvp-rank', 'finality-rank']) {
  const p = getPackage(id);
  if (!p) continue;
  if (p.badge && p.badge !== '🎅 + Santa Hat') console.log(`  ${p.name}: badge "${p.badge}" -> "🎅 + Santa Hat"`);
  p.badge = '🎅 + Santa Hat';
}

writeLocal();
db.flushSync();
console.log('Done. Start the store: systemctl start finality-store (it publishes to the website within a minute)');

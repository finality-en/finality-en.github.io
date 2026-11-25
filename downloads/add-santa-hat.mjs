// One-off: adds the Santa Hat cosmetic at a fixed $6.50, shown at the top of the store home page.
// Fixed price = never in the store-wide sale, and discount codes can't be used on an order with it.
// Run on the VPS with the store stopped:
//   systemctl stop finality-store
//   cd /opt/finality/store-server && sudo -u finality node scripts/add-santa-hat.mjs
//   systemctl start finality-store
// Also makes MVP, Finality and the MVP/Finality upgrades come with one Santa Hat (only ever once per player:
// `fitems santahat grant` remembers who already got one, so upgrading again doesn't give a second).
// Safe to run again.
import { db } from '../src/db.js';
import { upsertCategory, upsertPackage, syncPackageToStripe, getPackage } from '../src/catalog.js';
import { writeLocal } from '../src/publisher.js';

const live = db.d.servers.filter(s => !s.revoked);
const smp = live.filter(s => !/ffa/i.test(s.name));
const servers = smp.length === 1 && live.length > 1 ? [smp[0].id] : ['any'];

const found = db.d.categories.find(c => /^cosmetics?$/i.test(c.name) || c.id === 'cosmetics');
const cat = upsertCategory({
  id: found?.id, name: 'Cosmetics', order: found?.order ?? 6,
  description: 'Look the part. Seasonal cosmetics for Finality.',
  image: 'assets/img/item-santa-hat.webp', guiIcon: 'RED_WOOL', hidden: false,
});

const existing = getPackage('santa-hat') || db.d.packages.find(p => !p.archived && p.name === 'Santa Hat');
const pkg = upsertPackage({
  id: existing?.id, name: 'Santa Hat', categoryId: cat.id, kind: 'standard', enabled: true, giftable: true,
  price: '6.50', compareAtPrice: '', monthlyPrice: '', badge: 'Christmas', image: 'assets/img/item-santa-hat.webp', guiIcon: 'RED_WOOL',
  description: "## Get festive\nA proper 3D **Santa Hat** with a big fluffy bobble.\n\n- **+2 hearts** while you wear it\n- **Attach it to your helmet:** hold the hat on your cursor and click your helmet. You keep all your armour, enchants and durability, and everyone sees the Santa Hat instead\n- **Right-click** the helmet to take the hat back off whenever you like\n> Fixed price. Sales and discount codes don't apply.",
  contentsTitle: '', contents: [], upgradeFrom: null, servers,
  commands: [
    { when: 'purchase', cmd: 'fitems santahat give {player} 1', requireOnline: true, servers: null },
    { when: 'purchase', cmd: '@message {player} &c&lSANTA HAT &7is in your inventory! Click it onto your helmet to wear it over your armour.', requireOnline: true, servers: null },
  ],
});
pkg.fixedPrice = true;  // never discounted (sale.js / checkout.js)
pkg.featured = true;    // shown at the top of the home page
await syncPackageToStripe(pkg);
console.log(`${existing ? 'Updated' : 'Added'} ${pkg.name}: $${(pkg.price / 100).toFixed(2)} fixed -> ${pkg.stripe.onceLinkUrl ? 'synced to Stripe' : 'NOT synced'}`);

// Rank perk: MVP and above get one free Santa Hat (FinalityItems 1.2.0+ "grant" = once per player ever)
const GRANT = 'fitems santahat grant {player}';
for (const id of ['mvp-rank', 'finality-rank', 'vip-mvp', 'mvp-finality', 'vip-finality']) {
  const p = getPackage(id);
  if (!p) { console.log(`  (no package ${id}, skipped)`); continue; }
  p.commands = p.commands || [];
  if (!p.commands.some(c => c.cmd === GRANT)) {
    p.commands.push({ when: 'purchase', cmd: GRANT, requireOnline: true, servers: null });
    if (!/Santa Hat/.test(p.description || '')) p.description = (p.description || '') + '\n\n🎅 **Comes with a Santa Hat** (one per player, upgrading again won\'t give a second one)';
    console.log(`  ${p.name}: now includes a Santa Hat`);
  } else console.log(`  ${p.name}: already includes the Santa Hat`);
}

writeLocal();
db.flushSync();
console.log('Done. Start the store again: systemctl start finality-store');

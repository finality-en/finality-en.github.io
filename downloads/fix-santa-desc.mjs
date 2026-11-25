// Santa Hat store text: taking the hat off is now just right-click (FinalityItems 1.5.6). Run with the store stopped.
import { db } from '../src/db.js';
import { getPackage } from '../src/catalog.js';
import { writeLocal } from '../src/publisher.js';
const p = getPackage('santa-hat') || db.d.packages.find(x => !x.archived && x.name === 'Santa Hat');
if (!p) { console.log('No Santa Hat package found.'); process.exit(0); }
const before = p.description || '';
p.description = before.replace(/\*\*Shift \+ right-click\*\*/g, '**Right-click**').replace(/Shift \+ right-click/g, 'Right-click');
console.log(before === p.description ? 'Already up to date.' : 'Santa Hat description updated.');
writeLocal();
db.flushSync();

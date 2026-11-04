# Finality

Website for the Finality Minecraft server, hosted with GitHub Pages.

- `/` — Finality SMP guide with the **winter redesign**: top players, player stat search, snow, mouse parallax
- `/classes/` — Finality Classes player guide
- `/killeffects/` — Kill effects showcase
- `/backup/2026-11-04/` — the site exactly as it was before the winter redesign

## Winter redesign
All of it lives in two files shared by every page, so the page content itself is untouched:
- `assets/winter.css` — the three themes (**Frost**, **Aurora**, **Ember**), glass cards, hero, top players, player card, login
- `assets/winter.js` — snow, mouse parallax and glow, theme switcher, top players + search, player cards, admin login

Visitors switch themes from the **Theme** button in the top bar; their choice is remembered on their device.
Link straight to a player with `#player/<name>`, e.g. `/#player/Pairyma`.

## Player stats
`data/players.json` is a snapshot made from the server's pvpstats (`plugins/pvpstats/pvpstats.yml`)
and BetterTeams team files. Fields: `n` name, `u` uuid, `k` kills, `d` deaths, `bs` best streak,
`cs` current streak, `ls` last PvP (unix seconds), `t` team, `r` team rank; `updated` is when the snapshot was taken.
Refresh it by regenerating that file from the server's current data.

## Admin login
The **Login** button opens a staff login that shows the admin panel. The site is static and public,
so this is a convenience, not real security: only a SHA-256 hash of `user:password` is stored in
`assets/winter.js`, never the password itself. Don't put anything private behind it.

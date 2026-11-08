/* ==================================================================
   Finality FFA — ELO leaderboard + player cards.
   Data: data/ffa.json, written by the FinalityFFA plugin
   ({updated, worlds:[{id,name,color,players:[{n,u,e,k,d,s,bs}]}]}, players sorted by ELO).
   On the home page it only fills the FFA button's mini top 3.
   ================================================================== */
(function () {
  "use strict";
  var base = (document.currentScript && document.currentScript.getAttribute("data-base")) || "";
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  function $(s, e) { return (e || document).querySelector(s); }
  function $$(s, e) { return Array.prototype.slice.call((e || document).querySelectorAll(s)); }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function fmt(n) { return Number(n).toLocaleString("en-GB"); }
  var head = function (n, s) { return "https://mc-heads.net/avatar/" + encodeURIComponent(n) + "/" + (s || 64); };
  var body = function (n, s) { return "https://mc-heads.net/body/" + encodeURIComponent(n) + "/" + (s || 240); };
  function kd(p) { return p.d ? p.k / p.d : p.k; }
  function kdS(p) { return kd(p).toFixed(2); }

  var promo = $("[data-ffa-top]");
  var page = $("#ffa-board");
  if (!promo && !page) return;

  fetch(base + "data/ffa.json", { cache: "no-cache" }).then(function (r) { return r.json(); }).then(function (data) {
    if (promo) fillPromo(data);
    if (page) Board(data);
  }).catch(function () {
    if (promo) promo.innerHTML = '<span class="empty">Live ELO leaderboard inside →</span>';
    if (page) $(".fz-rows", page).innerHTML = '<p style="color:var(--faint)">Couldn\'t load FFA stats right now.</p>';
  });

  /* ---------------- Home page button ---------------- */
  function fillPromo(data) {
    var w = data.worlds && data.worlds[0];
    var list = w ? w.players.slice(0, 3) : [];
    promo.innerHTML = list.length ? list.map(function (p, i) {
      return '<span class="r"><span class="p">#' + (i + 1) + '</span><img alt="" src="' + head(p.n, 32) + '"><span class="n">' + esc(p.n) +
        '</span><span class="e">' + fmt(p.e) + "<small>ELO</small></span></span>";
    }).join("") : '<span class="empty">Nobody ranked yet — be the first #1.</span>';
  }

  /* ---------------- /ffa/ page ---------------- */
  function Board(data) {
    var worlds = data.worlds || [];
    var worldIdx = 0, sortKey = "elo";
    var SORTS = {
      elo: { fn: function (a, b) { return b.e - a.e || b.k - a.k; } },
      kills: { fn: function (a, b) { return b.k - a.k || b.e - a.e; } },
      kd: { fn: function (a, b) { return kd(b) - kd(a) || b.k - a.k; }, min: 5 },
      streak: { fn: function (a, b) { return b.bs - a.bs || b.e - a.e; } }
    };
    function world() { return worlds[worldIdx] || { players: [], name: "FFA" }; }
    function eloRank(p, w) { return (w || world()).players.indexOf(p) + 1; }
    function ranked() {
      var s = SORTS[sortKey];
      return world().players.filter(function (p) { return p.k >= (s.min || 0); }).slice().sort(s.fn);
    }
    function find(name, w) {
      name = String(name).toLowerCase();
      var list = (w || world()).players;
      for (var i = 0; i < list.length; i++) if (list[i].n.toLowerCase() === name) return list[i];
      return null;
    }

    // World + sort buttons
    var segW = $("[data-ffa-worlds]", page);
    segW.innerHTML = worlds.map(function (w, i) { return '<button type="button" data-w="' + i + '"' + (i === 0 ? ' class="on"' : "") + ">" + esc(w.name) + "</button>"; }).join("");
    segW.addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b) return;
      worldIdx = +b.dataset.w; $$("button", segW).forEach(function (x) { x.classList.toggle("on", x === b); }); render();
    });
    var segS = $("[data-ffa-sort]", page);
    segS.addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b) return;
      sortKey = b.dataset.sort; $$("button", segS).forEach(function (x) { x.classList.toggle("on", x === b); }); render();
    });

    function mainStat(p) {
      if (sortKey === "kills") return { v: fmt(p.k), l: "Kills" };
      if (sortKey === "kd") return { v: kdS(p), l: "K/D" };
      if (sortKey === "streak") return { v: p.bs, l: "Best streak" };
      return { v: fmt(p.e), l: "ELO" };
    }

    function render() {
      var list = ranked(), pod = $(".fz-podium", page), rows = $(".fz-rows", page);
      if (!list.length) {
        pod.innerHTML = "";
        rows.innerHTML = '<p style="color:var(--faint);text-align:center;padding:30px 0">Nobody is ranked in ' + esc(world().name) + " yet. Get a kill to claim #1!</p>";
        $("[data-ffa-all]", page).style.display = "none";
        return;
      }
      $("[data-ffa-all]", page).style.display = "";
      pod.innerHTML = [1, 0, 2].map(function (i) {
        var p = list[i]; if (!p) return "<div></div>";
        var m = mainStat(p);
        return '<div class="fz-pod fz-glow p' + (i + 1) + '" data-ffa-name="' + esc(p.n) + '" tabindex="0" role="button" aria-label="' + esc(p.n) + ' stats">' +
          '<span class="rank">#' + (i + 1) + "</span>" +
          '<img class="body" loading="lazy" alt="" src="' + body(p.n, i === 0 ? 220 : 180) + '">' +
          '<div class="name">' + esc(p.n) + '</div><div class="team elo">' + fmt(p.e) + " ELO</div>" +
          '<div class="nums"><div><b>' + m.v + "</b><small>" + m.l + "</small></div>" +
          "<div><b>" + (sortKey === "kills" ? fmt(p.e) : fmt(p.k)) + "</b><small>" + (sortKey === "kills" ? "ELO" : "Kills") + "</small></div>" +
          "<div><b>" + kdS(p) + "</b><small>K/D</small></div></div></div>";
      }).join("");
      var maxV = Math.max.apply(null, list.slice(0, 10).map(val)) || 1;
      rows.innerHTML = list.slice(3, 10).map(function (p, n) { return rowHtml(p, n + 4, maxV); }).join("");
      setTimeout(function () { $$(".fz-bar i", page).forEach(function (b) { b.style.width = b.dataset.w; }); }, 60);
    }
    function val(p) { return sortKey === "kills" ? p.k : sortKey === "kd" ? kd(p) : sortKey === "streak" ? p.bs : p.e; }
    function rowHtml(p, pos, maxV) {
      return '<div class="fz-row fz-glow" data-ffa-name="' + esc(p.n) + '" tabindex="0" role="button">' +
        '<span class="pos">' + pos + '</span><img loading="lazy" alt="" src="' + head(p.n, 64) + '">' +
        '<div class="who"><b>' + esc(p.n) + "</b><span>" + (p.s >= 3 ? "🔥 " + p.s + " kill streak" : "Best streak " + p.bs) + '</span><div class="fz-bar"><i data-w="' + Math.max(4, val(p) / maxV * 100) + '%"></i></div></div>' +
        '<div class="num elo"><b>' + fmt(p.e) + '</b><small>ELO</small></div><div class="num hide-sm"><b>' + fmt(p.k) + '</b><small>Kills</small></div>' +
        '<div class="num"><b>' + kdS(p) + '</b><small>K/D</small></div><span class="go">›</span></div>';
    }

    // Hero numbers
    function heroStats() {
      var all = {}, kills = 0, topElo = 0;
      worlds.forEach(function (w) { w.players.forEach(function (p) { all[p.n.toLowerCase()] = 1; kills += p.k; topElo = Math.max(topElo, p.e); }); });
      var set = function (k, v) { var n = $('[data-ffa="' + k + '"]'); if (n) countUp(n, v); };
      set("players", Object.keys(all).length); set("kills", kills); set("topelo", topElo); set("arenas", worlds.length);
      var best = worlds[0] && worlds[0].players[0], w = $("[data-ffa-best]");
      if (w) {
        if (best) {
          w.setAttribute("data-ffa-name", best.n);
          w.innerHTML = '<img alt="" src="' + head(best.n, 64) + '"><div><span>👑 #1 in ' + esc(worlds[0].name) + '</span><b style="font-size:24px">' + esc(best.n) + "</b><span>" + fmt(best.e) + " ELO · " + fmt(best.k) + " kills</span></div>";
        } else w.innerHTML = "<span>No one holds #1 yet — go take it.</span>";
      }
      var up = $("[data-ffa-updated]");
      if (up) up.textContent = new Date(data.updated * 1000).toLocaleString("en-GB", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
    }
    function countUp(node, to) {
      if (reduce) { node.textContent = fmt(to); return; }
      var t0 = performance.now();
      (function step(t) { var k = Math.min(1, (t - t0) / 1100); node.textContent = fmt(Math.round(to * (1 - Math.pow(1 - k, 3)))); if (k < 1) requestAnimationFrame(step); })(t0);
    }

    // Modal
    var modal = document.createElement("div");
    modal.className = "fz-modal";
    modal.innerHTML = '<div class="fz-card" role="dialog" aria-modal="true"></div>';
    (document.getElementById("fc-guide") || document.body).appendChild(modal);
    var card = modal.firstChild, lastFocus;
    function openModal(html, wide) {
      lastFocus = document.activeElement;
      card.className = "fz-card" + (wide ? " wide" : "");
      card.style.width = wide ? "min(860px, 100%)" : "";
      card.innerHTML = '<button class="fz-card-x" type="button" aria-label="Close">✕</button>' + html;
      $(".fz-card-x", card).addEventListener("click", closeModal);
      modal.classList.add("open"); document.body.style.overflow = "hidden";
    }
    function closeModal() {
      modal.classList.remove("open"); document.body.style.overflow = "";
      if (/^#player\//.test(location.hash)) history.replaceState(null, "", location.pathname + location.search);
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    }
    modal.addEventListener("mousedown", function (e) { if (e.target === modal) closeModal(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && modal.classList.contains("open")) closeModal(); });

    function openPlayer(name) {
      var p = find(name), w = world();
      if (!p) { for (var i = 0; i < worlds.length; i++) { p = find(name, worlds[i]); if (p) { w = worlds[i]; break; } } }
      if (!p) return;
      var r = eloRank(p, w), total = p.k + p.d, pct = total ? Math.round(p.k / total * 100) : 0;
      var badges = [];
      if (r <= 3) badges.push('<span class="fz-badge gold">#' + r + " in " + esc(w.name) + "</span>");
      else badges.push('<span class="fz-badge ice">Rank #' + r + " of " + w.players.length + "</span>");
      if (r <= 20) badges.push('<span class="fz-badge">🏷 #' + r + " tag above their head</span>");
      if (p.s >= 3) badges.push('<span class="fz-badge ice">🔥 On a ' + p.s + " kill streak</span>");
      var other = worlds.filter(function (x) { return x !== w; }).map(function (x) {
        var o = find(p.n, x); return o ? '<span class="fz-badge">' + esc(x.name) + ": " + fmt(o.e) + " ELO · #" + eloRank(o, x) + "</span>" : "";
      }).join("");
      openModal('<div class="fz-card-grid"><div class="fz-card-side"><img alt="' + esc(p.n) + '" src="' + body(p.n, 260) + '"></div>' +
        '<div class="fz-card-main"><h3>' + esc(p.n) + '</h3><div class="ffa-elo-big">' + fmt(p.e) + "<small>ELO</small></div>" +
        '<div class="fz-badges">' + badges.join("") + other + "</div>" +
        '<div class="fz-kv">' +
        "<div><b>" + fmt(p.k) + "</b><small>Kills</small></div>" +
        "<div><b>" + fmt(p.d) + "</b><small>Deaths</small></div>" +
        "<div><b>" + kdS(p) + "</b><small>K/D ratio</small></div>" +
        "<div><b>" + p.s + "</b><small>Current streak</small></div>" +
        "<div><b>" + p.bs + "</b><small>Best streak</small></div>" +
        "<div><b>" + esc(w.name) + "</b><small>Arena</small></div></div>" +
        '<div class="fz-meter"><div class="lbl"><span>Fights won</span><span>' + pct + '%</span></div><div class="track"><i></i></div></div>' +
        '<div class="fz-card-links"><a class="fc-btn" href="https://namemc.com/profile/' + encodeURIComponent(p.n) + '" target="_blank" rel="noopener">NameMC ↗</a>' +
        '<button class="fc-btn" type="button" data-copy="' + esc(location.origin + location.pathname + "#player/" + p.n) + '">🔗 Copy link</button></div>' +
        "</div></div>");
      setTimeout(function () { var i = $(".fz-meter i", card); if (i) i.style.width = pct + "%"; }, 50);
      var cp = $("[data-copy]", card);
      cp.addEventListener("click", function () {
        var t = cp.dataset.copy;
        (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject()).then(function () { cp.textContent = "Copied!"; }, function () { cp.textContent = t; });
      });
      if (location.hash !== "#player/" + p.n) history.replaceState(null, "", "#player/" + encodeURIComponent(p.n));
    }

    function openAll(q) {
      var list = world().players;
      openModal('<div class="fz-all"><h3>⚔ ' + esc(world().name) + ' — all ranked players</h3><div class="fz-search" style="margin-bottom:12px"><input type="search" placeholder="Filter by name…" autocomplete="off"></div><div class="fz-rows"></div></div>', true);
      var input = $("input", card), rows = $(".fz-rows", card), maxE = list.length ? list[0].e : 1;
      var saved = sortKey;
      function draw() {
        var f = input.value.trim().toLowerCase();
        sortKey = "elo";
        rows.innerHTML = list.filter(function (p) { return !f || p.n.toLowerCase().indexOf(f) >= 0; }).slice(0, 400)
          .map(function (p) { return rowHtml(p, eloRank(p), maxE); }).join("") || '<p style="color:var(--faint);text-align:center">No players match.</p>';
        sortKey = saved;
        $$(".fz-bar i", rows).forEach(function (b) { b.style.width = b.dataset.w; });
      }
      input.value = q || ""; input.addEventListener("input", draw); draw();
      setTimeout(function () { input.focus(); }, 50);
    }
    $("[data-ffa-all]", page).addEventListener("click", function () { openAll(""); });

    // Search box
    var input = $(".fz-search input", page), box = $(".fz-suggest", page), res = [];
    function suggest() {
      var q = input.value.trim().toLowerCase();
      if (!q) { box.classList.remove("open"); return; }
      var seen = {}; res = [];
      worlds.forEach(function (w) { w.players.forEach(function (p) { if (p.n.toLowerCase().indexOf(q) >= 0 && !seen[p.n]) { seen[p.n] = 1; res.push(p); } }); });
      res = res.slice(0, 8);
      box.innerHTML = res.length ? res.map(function (p) {
        return '<li data-ffa-name="' + esc(p.n) + '"><img alt="" src="' + head(p.n, 32) + '"><span>' + esc(p.n) + '</span><span class="meta">' + fmt(p.e) + " ELO · " + kdS(p) + " K/D</span></li>";
      }).join("") : '<li style="cursor:default;color:var(--faint)">No player found</li>';
      box.classList.add("open");
    }
    input.addEventListener("input", suggest);
    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter") { e.preventDefault(); if (res[0]) { openPlayer(res[0].n); box.classList.remove("open"); } else if (input.value.trim()) openAll(input.value.trim()); }
      if (e.key === "Escape") box.classList.remove("open");
    });
    box.addEventListener("mousedown", function (e) { var li = e.target.closest("li[data-ffa-name]"); if (li) { e.preventDefault(); openPlayer(li.dataset.ffaName); box.classList.remove("open"); } });
    document.addEventListener("click", function (e) { if (!box.contains(e.target) && e.target !== input) box.classList.remove("open"); });

    // Clicking any player
    document.addEventListener("click", function (e) {
      var t = e.target.closest && e.target.closest("[data-ffa-name]");
      if (t && !box.contains(t)) openPlayer(t.getAttribute("data-ffa-name"));
    });
    document.addEventListener("keydown", function (e) {
      var t = document.activeElement;
      if (e.key === "Enter" && t && t.hasAttribute && t.hasAttribute("data-ffa-name") && t.tagName !== "LI") openPlayer(t.getAttribute("data-ffa-name"));
    });

    render(); heroStats();
    var m = location.hash.match(/^#player\/(.+)$/);
    if (m) openPlayer(decodeURIComponent(m[1]));
    window.addEventListener("hashchange", function () { var h = location.hash.match(/^#player\/(.+)$/); if (h) openPlayer(decodeURIComponent(h[1])); });
  }
})();

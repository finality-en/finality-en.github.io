/* ==================================================================
   Finality SMP — winter redesign
   Snow, mouse parallax, theme switcher, top players + player search,
   player cards and the admin login. Works on every page that loads it;
   parts that need an element simply skip when it isn't there.
   ================================================================== */
(function () {
  "use strict";
  var doc = document.documentElement;
  var root = document.getElementById("fc-guide") || document.body;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var base = (document.currentScript && document.currentScript.getAttribute("data-base")) || "";

  function $(sel, el) { return (el || document).querySelector(sel); }
  function $$(sel, el) { return Array.prototype.slice.call((el || document).querySelectorAll(sel)); }
  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  function fmt(n) { return Number(n).toLocaleString("en-GB"); }

  /* ---------------- Themes ---------------- */
  var SKINS = [
    { id: "frost", name: "Frost", sub: "Midnight ice & Finality gold" },
    { id: "aurora", name: "Aurora", sub: "Northern lights" },
    { id: "ember", name: "Ember", sub: "Warm cabin glow" }
  ];
  function setSkin(id, quiet) {
    if (!SKINS.some(function (s) { return s.id === id; })) id = "frost";
    doc.setAttribute("data-skin", id);
    root.setAttribute("data-theme", "dark");
    store("fz-skin", id);
    $$(".fz-skin-menu button").forEach(function (b) { b.classList.toggle("on", b.dataset.skin === id); });
    var sw = $(".fz-skin-btn .fz-swatch"); if (sw) sw.className = "fz-swatch " + id;
    if (!quiet) toast("Theme: " + SKINS.filter(function (s) { return s.id === id; })[0].name);
  }
  setSkin(store("fz-skin") || "frost", true);

  /* ---------------- Background layers ---------------- */
  var sky = el("div", "fz-sky", '<div class="stars"></div><div class="orb a"></div><div class="orb b"></div><div class="orb c"></div>');
  var canvas = el("canvas"); canvas.id = "fz-snow"; canvas.setAttribute("aria-hidden", "true");
  root.insertBefore(sky, root.firstChild);
  root.appendChild(canvas);

  /* ---------------- Toast ---------------- */
  var toastEl = el("div", "fz-toast"); root.appendChild(toastEl);
  var toastT;
  function toast(msg) { toastEl.textContent = msg; toastEl.classList.add("show"); clearTimeout(toastT); toastT = setTimeout(function () { toastEl.classList.remove("show"); }, 1800); }

  /* ---------------- Top bar: theme picker + login ---------------- */
  var actions = $(".fc-top-actions");
  if (actions) {
    var picker = el("div", "fz-skin");
    picker.innerHTML = '<button class="fc-btn fz-skin-btn" type="button" aria-haspopup="true" title="Change theme"><span class="fz-swatch ' + doc.getAttribute("data-skin") + '"></span><span class="lbl">Theme</span></button>' +
      '<div class="fz-skin-menu" role="menu">' + SKINS.map(function (s) {
        return '<button type="button" role="menuitem" data-skin="' + s.id + '"><span class="fz-swatch ' + s.id + '"></span><span>' + s.name + '<small>' + s.sub + "</small></span></button>";
      }).join("") + "</div>";
    actions.appendChild(picker);
    picker.querySelector(".fz-skin-btn").addEventListener("click", function (e) { e.stopPropagation(); picker.classList.toggle("open"); });
    picker.querySelectorAll(".fz-skin-menu button").forEach(function (b) {
      b.addEventListener("click", function () { setSkin(b.dataset.skin); picker.classList.remove("open"); });
    });
    document.addEventListener("click", function () { picker.classList.remove("open"); });
    setSkin(doc.getAttribute("data-skin"), true);

    var loginBtn = el("button", "fc-btn fz-loginbtn", '🔐 <span class="lbl">Login</span>');
    loginBtn.type = "button"; loginBtn.title = "Admin login";
    actions.appendChild(loginBtn);
    loginBtn.addEventListener("click", function () { isAdmin() ? showAdmin(true, true) : openLogin(); });
  }

  /* ---------------- Mouse: the whole page drifts with it ----------------
     Layers move by different amounts so the page has depth: the sky moves most,
     the page content a little the other way, and the hero tilts. Mouse only. */
  var mx = 0.5, my = 0.5, tx = 0.5, ty = 0.5, px = 0, pvx = 0;
  var orbs = $$(".fz-sky .orb"), stars = $(".fz-sky .stars");
  var hero = $(".fz-hero-inner"), crystals = $$(".fz-crystal");
  var page = $$(".fc-guide > .fc-wrap");
  var finePointer = window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  page.forEach(function (w) { w.classList.add("fz-drift"); });
  window.addEventListener("mousemove", function (e) {
    tx = e.clientX / window.innerWidth; ty = e.clientY / window.innerHeight;
    pvx = e.clientX - px; px = e.clientX;
  }, { passive: true });
  document.addEventListener("mouseleave", function () { tx = 0.5; ty = 0.5; });
  function frame() {
    mx += (tx - mx) * 0.05; my += (ty - my) * 0.05;
    var dx = mx - 0.5, dy = my - 0.5;
    if (!reduce && finePointer) {
      page.forEach(function (w) { w.style.transform = "translate3d(" + (-dx * 14).toFixed(2) + "px," + (-dy * 9).toFixed(2) + "px,0)"; });
      orbs.forEach(function (o, i) { var k = (i + 1) * 18; o.style.transform = "translate3d(" + (-dx * k) + "px," + (-dy * k) + "px,0)"; });
      if (stars) stars.style.transform = "translate3d(" + (dx * 14) + "px," + (dy * 14) + "px,0)";
      if (hero && heroVisible) hero.style.transform = "rotateY(" + (dx * 6) + "deg) rotateX(" + (-dy * 5) + "deg)";
      crystals.forEach(function (c, i) { var k = 20 + i * 14; c.style.transform = "translate3d(" + (dx * k) + "px," + (dy * k) + "px,0) rotate(" + (dx * 30) + "deg)"; });
    }
    requestAnimationFrame(frame);
  }
  var heroVisible = true;
  if (hero && "IntersectionObserver" in window) {
    new IntersectionObserver(function (es) { heroVisible = es[0].isIntersecting; }).observe(hero);
  }
  requestAnimationFrame(frame);

  // Cards that tilt towards the cursor
  function tilt(card, amount) {
    if (reduce) return;
    card.addEventListener("mousemove", function (e) {
      var r = card.getBoundingClientRect();
      var x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
      card.style.transform = "perspective(800px) rotateY(" + (x * amount) + "deg) rotateX(" + (-y * amount) + "deg) translateY(-4px)";
    });
    card.addEventListener("mouseleave", function () { card.style.transform = ""; });
  }

  // Glow + reveal on the guide's existing cards and sections
  function enhance(scope) {
    $$(".fc-card, .fc-note, .fc-faq details, details.fc-crate, .fz-stat, .fz-pod, .fz-row", scope).forEach(function (c) {
      // .fc-step and special class cards already use ::before/::after for their numbers and glow
      if (!c.matches(".fc-step, .is-special")) c.classList.add("fz-glow");
    });
  }
  enhance(document);
  var revealIO = "IntersectionObserver" in window && !reduce ? new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); revealIO.unobserve(e.target); } });
  }, { rootMargin: "0px 0px -8% 0px" }) : null;
  function reveal(nodes) {
    nodes.forEach(function (n) { if (!revealIO) return; n.classList.add("fz-reveal"); revealIO.observe(n); });
  }
  reveal($$("main .fc-section, .fz-top, .fc-items > *, .fc-recipes > *, .fc-grid > *"));

  /* ---------------- Snow ---------------- */
  (function snow() {
    var ctx = canvas.getContext("2d"), W, H, dpr, flakes = [], mouse = { x: -999, y: -999 };
    var on = store("fz-snow") !== "off";
    function size() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = window.innerWidth; H = window.innerHeight;
      canvas.width = W * dpr; canvas.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      var want = Math.round(Math.min(160, W * H / 11000) * (reduce ? 0.35 : 1));
      while (flakes.length < want) flakes.push(make(true));
      flakes.length = want;
    }
    function make(anywhere) {
      var depth = Math.random();
      return { x: Math.random() * W, y: anywhere ? Math.random() * H : -10, r: 0.6 + depth * 2.2, d: depth,
        vy: 0.25 + depth * 0.9, sway: Math.random() * Math.PI * 2, sw: 0.004 + Math.random() * 0.01, a: 0.25 + depth * 0.5 };
    }
    window.addEventListener("resize", size);
    window.addEventListener("mousemove", function (e) { mouse.x = e.clientX; mouse.y = e.clientY; }, { passive: true });
    window.addEventListener("mouseout", function () { mouse.x = mouse.y = -999; });
    var wind = 0;
    function tick() {
      ctx.clearRect(0, 0, W, H);
      if (on && !document.hidden) {
        wind += (pvx * 0.02 - wind) * 0.05; pvx *= 0.9;
        for (var i = 0; i < flakes.length; i++) {
          var f = flakes[i];
          f.sway += f.sw;
          f.x += Math.sin(f.sway) * 0.35 * (0.4 + f.d) + wind * (0.3 + f.d);
          f.y += f.vy;
          // Flakes drift away from the cursor
          var ddx = f.x - mouse.x, ddy = f.y - mouse.y, dist = ddx * ddx + ddy * ddy;
          if (dist < 9000) { var push = (1 - dist / 9000) * 1.6; f.x += ddx / 60 * push; f.y += ddy / 90 * push; }
          if (f.y > H + 6) { flakes[i] = make(false); continue; }
          if (f.x > W + 6) f.x = -6; else if (f.x < -6) f.x = W + 6;
          ctx.beginPath(); ctx.arc(f.x, f.y, f.r, 0, 6.283);
          ctx.fillStyle = "rgba(255,255,255," + f.a + ")"; ctx.fill();
        }
      }
      requestAnimationFrame(tick);
    }
    size(); requestAnimationFrame(tick);
    window.fzSnow = function (state) { on = state; store("fz-snow", state ? "on" : "off"); };
    window.fzSnowOn = function () { return on; };
  })();

  /* ---------------- Modal helper ---------------- */
  var modal = el("div", "fz-modal", '<div class="fz-card" role="dialog" aria-modal="true"></div>');
  root.appendChild(modal);
  var card = modal.firstChild, lastFocus;

  // Skin images: try a second skin service, then fall back to a plain Steve head
  var STEVE = "data:image/svg+xml," + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8" shape-rendering="crispEdges"><rect width="8" height="8" fill="#6b4a2f"/><rect y="2" width="8" height="6" fill="#c69c6d"/><rect x="1" y="4" width="2" height="1" fill="#fff"/><rect x="2" y="4" width="1" height="1" fill="#3b2a73"/><rect x="5" y="4" width="2" height="1" fill="#fff"/><rect x="5" y="4" width="1" height="1" fill="#3b2a73"/><rect x="3" y="6" width="2" height="1" fill="#7a4a3a"/></svg>');
  root.addEventListener("error", function (e) {
    var img = e.target;
    if (!img || img.tagName !== "IMG" || !/mc-heads\.net|minotar\.net/.test(img.src)) return;
    var m = img.src.match(/\/(avatar|body)\/([^/]+)/);
    if (/mc-heads/.test(img.src) && m) img.src = "https://minotar.net/" + (m[1] === "body" ? "armor/body" : "helm") + "/" + m[2] + "/" + (m[1] === "body" ? 180 : 64) + ".png";
    else { img.src = STEVE; img.style.imageRendering = "pixelated"; }
  }, true);
  function openModal(html, cls) {
    lastFocus = document.activeElement;
    card.className = "fz-card" + (cls ? " " + cls : "");
    card.innerHTML = '<button class="fz-card-x" type="button" aria-label="Close">✕</button>' + html;
    card.querySelector(".fz-card-x").addEventListener("click", closeModal);
    modal.classList.add("open");
    document.body.style.overflow = "hidden";
  }
  function closeModal() {
    modal.classList.remove("open"); document.body.style.overflow = "";
    if (/^#player\//.test(location.hash)) history.replaceState(null, "", location.pathname + location.search);
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  modal.addEventListener("mousedown", function (e) { if (e.target === modal) closeModal(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && modal.classList.contains("open")) closeModal(); });

  /* ---------------- Players ---------------- */
  var DATA = null, byName = {};
  var top = $("#fz-top");
  var head = function (n, s) { return "https://mc-heads.net/avatar/" + encodeURIComponent(n) + "/" + (s || 64); };
  var body = function (n, s) { return "https://mc-heads.net/body/" + encodeURIComponent(n) + "/" + (s || 240); };
  function kd(p) { return p.d ? p.k / p.d : p.k; }
  function kdS(p) { return kd(p).toFixed(2); }
  var SORTS = {
    kills: { label: "Kills", fn: function (a, b) { return b.k - a.k || kd(b) - kd(a); } },
    kd: { label: "K/D", fn: function (a, b) { return kd(b) - kd(a) || b.k - a.k; }, min: 10 },
    streak: { label: "Best streak", fn: function (a, b) { return b.bs - a.bs || b.k - a.k; } }
  };
  var sortKey = "kills";
  function ranked(key) {
    var s = SORTS[key || sortKey];
    return DATA.players.filter(function (p) { return p.k >= (s.min || 1); }).slice().sort(s.fn);
  }
  function rankOf(p) { var r = ranked("kills"); return r.indexOf(p) + 1; }
  function ago(sec) {
    if (!sec) return "—";
    var d = Math.max(0, Date.now() / 1000 - sec), u = [[31536000, "year"], [2592000, "month"], [86400, "day"], [3600, "hour"], [60, "minute"]];
    for (var i = 0; i < u.length; i++) if (d >= u[i][0]) { var n = Math.floor(d / u[i][0]); return n + " " + u[i][1] + (n > 1 ? "s" : "") + " ago"; }
    return "just now";
  }
  function countUp(node, to, dec) {
    if (reduce) { node.textContent = dec ? to.toFixed(dec) : fmt(to); return; }
    var t0 = performance.now(), dur = 1200;
    (function step(t) {
      var k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 3), v = to * e;
      node.textContent = dec ? v.toFixed(dec) : fmt(Math.round(v));
      if (k < 1) requestAnimationFrame(step);
    })(t0);
  }

  function statValue(p, key) {
    if (key === "kd") return { v: kdS(p), l: "K/D" };
    if (key === "streak") return { v: p.bs, l: "Streak" };
    return { v: fmt(p.k), l: "Kills" };
  }

  function renderTop() {
    if (!top || !DATA) return;
    var list = ranked();
    var pod = $(".fz-podium", top), rows = $(".fz-rows", top);
    var order = [1, 0, 2];
    pod.innerHTML = order.map(function (i) {
      var p = list[i]; if (!p) return "<div></div>";
      var main = statValue(p, sortKey);
      return '<div class="fz-pod p' + (i + 1) + '" data-name="' + esc(p.n) + '" tabindex="0" role="button" aria-label="' + esc(p.n) + ' stats">' +
        '<span class="rank">#' + (i + 1) + "</span>" +
        '<img class="body" loading="lazy" alt="" src="' + body(p.n, i === 0 ? 220 : 180) + '">' +
        '<div class="name">' + esc(p.n) + '</div><div class="team">' + (p.t ? "🛡 " + esc(p.t) : "&nbsp;") + "</div>" +
        '<div class="nums"><div><b>' + main.v + "</b><small>" + main.l + "</small></div>" +
        (sortKey !== "kills" ? "<div><b>" + fmt(p.k) + "</b><small>Kills</small></div>" : "<div><b>" + p.d + "</b><small>Deaths</small></div>") +
        "<div><b>" + (sortKey === "kd" ? p.bs : kdS(p)) + "</b><small>" + (sortKey === "kd" ? "Streak" : "K/D") + "</small></div></div></div>";
    }).join("");
    var maxK = Math.max.apply(null, list.slice(0, 10).map(function (p) { return sortKey === "kd" ? kd(p) : sortKey === "streak" ? p.bs : p.k; })) || 1;
    rows.innerHTML = list.slice(3, 10).map(function (p, n) { return rowHtml(p, n + 4, maxK); }).join("");
    enhance(top);
    $$(".fz-pod", top).forEach(function (c) { tilt(c, 10); });
    setTimeout(function () { $$(".fz-bar i", rows).forEach(function (b) { b.style.width = b.dataset.w; }); }, 60);
  }
  function rowHtml(p, pos, maxV) {
    var v = sortKey === "kd" ? kd(p) : sortKey === "streak" ? p.bs : p.k;
    return '<div class="fz-row" data-name="' + esc(p.n) + '" tabindex="0" role="button">' +
      '<span class="pos">' + pos + '</span><img loading="lazy" alt="" src="' + head(p.n, 64) + '">' +
      '<div class="who"><b>' + esc(p.n) + "</b><span>" + (p.t ? "🛡 " + esc(p.t) : "No team") + '</span><div class="fz-bar"><i data-w="' + Math.max(4, v / maxV * 100) + '%"></i></div></div>' +
      '<div class="num"><b>' + fmt(p.k) + '</b><small>Kills</small></div><div class="num hide-sm"><b>' + fmt(p.d) + '</b><small>Deaths</small></div>' +
      '<div class="num"><b>' + kdS(p) + '</b><small>K/D</small></div><span class="go">›</span></div>';
  }

  function openPlayer(name) {
    var p = byName[String(name).toLowerCase()];
    if (!p) { toast("No player called " + name); return; }
    var r = rankOf(p), total = p.k + p.d, pct = total ? Math.round(p.k / total * 100) : 0;
    var badges = [];
    if (r > 0 && r <= 3) badges.push('<span class="fz-badge gold">#' + r + " on the leaderboard</span>");
    else if (r > 0) badges.push('<span class="fz-badge ice">Rank #' + r + " of " + ranked("kills").length + "</span>");
    if (p.t) badges.push('<span class="fz-badge">🛡 ' + esc(p.t) + (p.r ? " · " + esc(p.r) : "") + "</span>");
    if (p.cs >= 3) badges.push('<span class="fz-badge ice">🔥 On a ' + p.cs + " kill streak</span>");
    if (kd(p) >= 2 && p.k >= 10) badges.push('<span class="fz-badge ice">⚔ Sharpshooter</span>');
    openModal('<div class="fz-card-grid"><div class="fz-card-side"><img alt="' + esc(p.n) + '" src="' + body(p.n, 260) + '"></div>' +
      '<div class="fz-card-main"><h3>' + esc(p.n) + "</h3>" +
      '<div class="fz-badges">' + badges.join("") + "</div>" +
      '<div class="fz-kv">' +
      "<div><b data-c=\"" + p.k + "\">0</b><small>Kills</small></div>" +
      "<div><b data-c=\"" + p.d + "\">0</b><small>Deaths</small></div>" +
      "<div><b data-c=\"" + kd(p) + "\" data-dec=\"2\">0</b><small>K/D ratio</small></div>" +
      "<div><b data-c=\"" + p.bs + "\">0</b><small>Best streak</small></div>" +
      "<div><b data-c=\"" + p.cs + "\">0</b><small>Current streak</small></div>" +
      "<div><b style=\"font-size:17px;line-height:1.5\">" + ago(p.ls) + "</b><small>Last PvP</small></div></div>" +
      '<div class="fz-meter"><div class="lbl"><span>Fights won</span><span>' + pct + "%</span></div><div class=\"track\"><i></i></div></div>" +
      '<div class="fz-card-links"><a class="fc-btn" href="https://namemc.com/profile/' + encodeURIComponent(p.n) + '" target="_blank" rel="noopener">NameMC ↗</a>' +
      '<button class="fc-btn" type="button" data-copy="' + esc(location.origin + location.pathname + "#player/" + p.n) + '">🔗 Copy link</button></div>' +
      "</div></div>");
    $$("[data-c]", card).forEach(function (b) { countUp(b, parseFloat(b.dataset.c), b.dataset.dec ? 2 : 0); });
    setTimeout(function () { var i = $(".fz-meter i", card); if (i) i.style.width = pct + "%"; }, 50);
    var cp = $("[data-copy]", card);
    if (cp) cp.addEventListener("click", function () {
      var t = cp.dataset.copy;
      (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject()).then(function () { toast("Link copied"); }, function () { toast(t); });
    });
    if (location.hash !== "#player/" + p.n) history.replaceState(null, "", "#player/" + encodeURIComponent(p.n));
  }

  function openAll(query) {
    var list = ranked("kills");
    openModal('<div class="fz-all"><h3>🏆 All players</h3><div class="fz-search" style="margin-bottom:12px"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><input type="search" placeholder="Filter by name or team…" autocomplete="off"></div><div class="fz-rows"></div></div>', "wide");
    card.style.width = "min(860px, 100%)";
    var input = $("input", card), rows = $(".fz-rows", card);
    var maxK = list.length ? list[0].k : 1;
    function draw() {
      var q = input.value.trim().toLowerCase();
      var shown = list.filter(function (p) { return !q || p.n.toLowerCase().indexOf(q) >= 0 || (p.t || "").toLowerCase().indexOf(q) >= 0; });
      var saved = sortKey; sortKey = "kills";
      rows.innerHTML = shown.slice(0, 300).map(function (p) { return rowHtml(p, list.indexOf(p) + 1, maxK); }).join("") ||
        '<p style="color:var(--faint);text-align:center">No players match.</p>';
      sortKey = saved;
      $$(".fz-bar i", rows).forEach(function (b) { b.style.width = b.dataset.w; });
    }
    input.value = query || ""; input.addEventListener("input", draw); draw();
    setTimeout(function () { input.focus(); }, 50);
  }

  function setupSearch(input, box) {
    var res = [], on = 0;
    function draw() {
      var q = input.value.trim().toLowerCase();
      if (!q || !DATA) { box.classList.remove("open"); return; }
      res = DATA.players.filter(function (p) { return p.n.toLowerCase().indexOf(q) >= 0; })
        .sort(function (a, b) { var ai = a.n.toLowerCase().indexOf(q), bi = b.n.toLowerCase().indexOf(q); return ai - bi || b.k - a.k; }).slice(0, 8);
      on = 0;
      box.innerHTML = res.length ? res.map(function (p, i) {
        var n = esc(p.n).replace(new RegExp("(" + q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "i"), "<mark>$1</mark>");
        return '<li class="' + (i === 0 ? "on" : "") + '" data-name="' + esc(p.n) + '"><img alt="" src="' + head(p.n, 32) + '"><span>' + n + '</span><span class="meta">' + fmt(p.k) + " kills · " + kdS(p) + " K/D</span></li>";
      }).join("") : '<li style="cursor:default;color:var(--faint)">No player found</li>';
      box.classList.add("open");
    }
    function setOn(n) { var li = $$("li[data-name]", box); if (!li.length) return; on = (n + li.length) % li.length; li.forEach(function (l, i) { l.classList.toggle("on", i === on); }); }
    input.addEventListener("input", draw);
    input.addEventListener("focus", draw);
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { e.preventDefault(); setOn(on + 1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); setOn(on - 1); }
      else if (e.key === "Enter") { e.preventDefault(); if (res[on]) { openPlayer(res[on].n); box.classList.remove("open"); } else if (input.value.trim()) openAll(input.value.trim()); }
      else if (e.key === "Escape") box.classList.remove("open");
    });
    box.addEventListener("mousedown", function (e) { var li = e.target.closest("li[data-name]"); if (li) { e.preventDefault(); openPlayer(li.dataset.name); box.classList.remove("open"); input.blur(); } });
    document.addEventListener("click", function (e) { if (!box.contains(e.target) && e.target !== input) box.classList.remove("open"); });
  }

  // Click / Enter on any player card or row
  document.addEventListener("click", function (e) {
    var t = e.target.closest && e.target.closest("[data-name].fz-pod, [data-name].fz-row, .fz-stat.wide[data-name]");
    if (t) openPlayer(t.dataset.name);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Enter") return;
    var t = document.activeElement;
    if (t && t.matches && t.matches("[data-name].fz-pod, [data-name].fz-row")) openPlayer(t.dataset.name);
  });

  function heroStats() {
    var p = DATA.players, kills = 0, teams = {};
    p.forEach(function (x) { kills += x.k; if (x.t) teams[x.t] = 1; });
    var set = function (k, v, dec) { var n = $('[data-fz="' + k + '"]'); if (n) countUp(n, v, dec); };
    set("players", p.length); set("kills", kills); set("teams", Object.keys(teams).length);
    var best = ranked("kills")[0], w = $(".fz-stat.wide");
    if (best && w) {
      w.dataset.name = best.n;
      w.innerHTML = '<img alt="" src="' + head(best.n, 64) + '"><div><span>Top killer</span><b style="font-size:24px">' + esc(best.n) + '</b><span>' + fmt(best.k) + " kills · " + kdS(best) + " K/D</span></div>";
    }
    var up = $("[data-fz-updated]");
    if (up) up.textContent = new Date(DATA.updated * 1000).toLocaleString("en-GB", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" });
  }

  if (top) {
    $$(".fz-seg button", top).forEach(function (b) {
      b.addEventListener("click", function () {
        sortKey = b.dataset.sort;
        $$(".fz-seg button", top).forEach(function (x) { x.classList.toggle("on", x === b); });
        renderTop();
      });
    });
    var allBtn = $("[data-fz-all]", top); if (allBtn) allBtn.addEventListener("click", function () { openAll(""); });
    setupSearch($(".fz-search input", top), $(".fz-suggest", top));
  }

  function loadPlayers() {
    if (!top && !$('[data-fz="players"]')) return;
    fetch(base + "data/players.json", { cache: "no-cache" }).then(function (r) { return r.json(); }).then(function (d) {
      DATA = d; byName = {};
      d.players.forEach(function (p) { byName[p.n.toLowerCase()] = p; });
      renderTop(); heroStats(); adminStats();
      var m = location.hash.match(/^#player\/(.+)$/);
      if (m) openPlayer(decodeURIComponent(m[1]));
    }).catch(function () {
      if (top) $(".fz-rows", top).innerHTML = '<p style="color:var(--faint)">Couldn\'t load player stats right now.</p>';
    });
  }
  window.addEventListener("hashchange", function () {
    var m = location.hash.match(/^#player\/(.+)$/);
    if (m && DATA) openPlayer(decodeURIComponent(m[1]));
  });
  window.fzOpenPlayer = openPlayer;

  /* ---------------- Admin login ----------------
     The site is static and public, so this only gates the admin panel on this page.
     The password itself is never stored — only a SHA-256 hash of "user:password". */
  var HASH = "5fbbbf3d2096b028f06e8ea823403c9ed5caf9b9dbbf23e25bcf6552315ff5ab";
  function isAdmin() { try { return sessionStorage.getItem("fz-admin") === HASH; } catch (e) { return false; } }
  function sha256(text) {
    return crypto.subtle.digest("SHA-256", new TextEncoder().encode(text)).then(function (buf) {
      return Array.prototype.map.call(new Uint8Array(buf), function (b) { return ("0" + b.toString(16)).slice(-2); }).join("");
    });
  }
  function openLogin() {
    openModal('<form class="fz-login" autocomplete="on"><h3>🔐 Admin login</h3><p>Staff only.</p>' +
      '<label for="fz-u">Username</label><input id="fz-u" name="username" autocomplete="username" required>' +
      '<label for="fz-p">Password</label><input id="fz-p" name="password" type="password" autocomplete="current-password" required>' +
      '<div class="err"></div><button class="fc-btn primary" type="submit">Log in</button></form>');
    card.style.width = "min(440px, 100%)";
    var f = $("form", card);
    setTimeout(function () { $("#fz-u", card).focus(); }, 60);
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!window.crypto || !crypto.subtle) { $(".err", f).textContent = "Your browser can't log in here (needs HTTPS)."; return; }
      sha256($("#fz-u", f).value.trim() + ":" + $("#fz-p", f).value).then(function (h) {
        if (h === HASH) {
          try { sessionStorage.setItem("fz-admin", HASH); } catch (x) {}
          closeModal(); showAdmin(true, true); toast("Welcome back, admin");
        } else {
          $(".err", f).textContent = "Wrong username or password.";
          card.classList.remove("fz-shake"); void card.offsetWidth; card.classList.add("fz-shake");
          $("#fz-p", f).value = "";
        }
      });
    });
  }
  var adminBox = $("#fz-admin");
  function adminStats() {
    if (!adminBox || !DATA) return;
    var k = 0, d = 0, teams = {};
    DATA.players.forEach(function (p) { k += p.k; d += p.d; if (p.t) teams[p.t] = 1; });
    var g = $(".grid", adminBox);
    if (g) g.innerHTML = "<div><b>" + fmt(DATA.players.length) + "</b><small>Players tracked</small></div><div><b>" + fmt(k) + "</b><small>Total kills</small></div>" +
      "<div><b>" + fmt(d) + "</b><small>Total deaths</small></div><div><b>" + Object.keys(teams).length + "</b><small>Teams with players</small></div>" +
      "<div><b>" + new Date(DATA.updated * 1000).toLocaleDateString("en-GB", { day: "numeric", month: "short" }) + "</b><small>Stats snapshot</small></div>";
  }
  function showAdmin(on, scroll) {
    var btn = $(".fz-loginbtn");
    if (btn) { btn.classList.toggle("on", on); btn.innerHTML = on ? '🛡 <span class="lbl">Admin</span>' : '🔐 <span class="lbl">Login</span>'; }
    if (!adminBox) return;
    adminBox.classList.toggle("on", on);
    if (on) { adminStats(); var sb = $("[data-fz-snow]", adminBox); if (sb) sb.textContent = window.fzSnowOn && window.fzSnowOn() ? "❄ Snow: on" : "❄ Snow: off"; }
    if (on && scroll) adminBox.scrollIntoView({ behavior: "smooth", block: "center" });
  }
  if (adminBox) {
    adminBox.addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b) return;
      if (b.hasAttribute("data-fz-logout")) { try { sessionStorage.removeItem("fz-admin"); } catch (x) {} showAdmin(false); toast("Logged out"); }
      if (b.hasAttribute("data-fz-snow")) { var s = !window.fzSnowOn(); window.fzSnow(s); b.textContent = s ? "❄ Snow: on" : "❄ Snow: off"; }
      if (b.dataset.fzSkin) setSkin(b.dataset.fzSkin);
    });
  }
  if (isAdmin()) showAdmin(true, false);

  loadPlayers();
})();

/**
 * toolbar.js — shared travel navigation bar
 *
 * ⚠️ HOME: Travel Website/assets/toolbar.js — site-wide shared asset.
 * The shared scripts/styles (toolbar.js, footnote.js, weather.js,
 * guide_v3.css, mobile.css, climate.json) all live in assets/. Every page
 * loads them from assets/ at its own relative depth below the site root:
 *   · index.html (depth 0):                       src="assets/toolbar.js"
 *   · depth-1 pages (Guides/guides_index.html,
 *     Trip Essentials/*.html):                    src="../assets/toolbar.js"
 *   · depth-2 pages (Guides/City/*.html,
 *     Trip Essentials/Maps|Plug Adapter/*.html):  src="../../assets/toolbar.js"
 *
 * Each page needs:
 *   <div id="toolbar-mount" data-depth="N" data-maxwidth="W"></div>
 *   <script src="PATH-TO-assets/toolbar.js"></script>   ← before </body>
 *
 *   data-depth    = directory levels below the site root  (0, 1 or 2)
 *                   (depth describes the PAGE's location, not the script's)
 *   data-maxwidth = inner max-width px  (760 for Trip Essentials, 940 for Guides)
 *
 * To update the toolbar for every page: edit ONLY this file.
 */

/* ── Pre-hide body immediately — prevents the page-background flash that occurs
   while the browser waits for this script to finish downloading. Injecting a
   <style> rule into <head> takes effect before the next paint; the inline
   body.style.opacity below is a belt-and-suspenders fallback.
   A safety setTimeout removes the rule after 2 s if something goes wrong. */
(function () {
  try {
    var _s = document.createElement('style');
    _s.id = '_tbhide';
    _s.textContent = 'body{opacity:0!important;transition:none!important}';
    (document.head || document.documentElement).appendChild(_s);
    setTimeout(function () {
      var el = document.getElementById('_tbhide');
      if (el) { el.parentNode.removeChild(el); document.body.style.opacity = '1'; }
    }, 2000);
  } catch (e) {}
})();

/* ── PWA wiring — inject the web-app manifest + Apple home-screen tags and
   register the offline service worker. One edit wires the whole site; paths use
   the page's data-depth (same base the nav uses). No-ops on file:// and never
   double-injects. Full notes: Brain/Reference/Toolbar.html § PWA. */
(function () {
  try {
    var d = document, head = d.head || d.getElementsByTagName('head')[0];
    if (!head) return;
    var m = d.getElementById('toolbar-mount');
    var dep = m ? parseInt(m.dataset.depth || '1', 10) : 1;
    var b = new Array(dep + 1).join('../');
    function link(rel, href, attrs) {
      if (d.querySelector('link[rel="' + rel + '"]')) return;
      var l = d.createElement('link'); l.rel = rel; l.href = href;
      if (attrs) for (var k in attrs) l.setAttribute(k, attrs[k]);
      head.appendChild(l);
    }
    function meta(name, content) {
      if (d.querySelector('meta[name="' + name + '"]')) return;
      var el = d.createElement('meta'); el.name = name; el.content = content; head.appendChild(el);
    }
    link('manifest', b + 'manifest.webmanifest');
    link('apple-touch-icon', b + 'assets/icons/apple-touch-icon.png');
    link('icon', b + 'assets/icons/favicon-32.png', { sizes: '32x32', type: 'image/png' });
    meta('theme-color', '#b85c2a');
    meta('apple-mobile-web-app-capable', 'yes');
    meta('mobile-web-app-capable', 'yes');
    meta('apple-mobile-web-app-status-bar-style', 'default');
    meta('apple-mobile-web-app-title', 'Travel');
    if ('serviceWorker' in navigator &&
        (location.protocol === 'https:' || location.hostname === 'localhost')) {
      window.addEventListener('load', function () {
        navigator.serviceWorker.register(b + 'sw.js', { scope: b || './' })['catch'](function () {});
      });
    }
  } catch (e) {}
})();

(function () {
  'use strict';

  /* ── Hide page immediately so the toolbar insertion doesn't cause a visible
     layout shift (flicker). Revealed below once the bar is in the DOM.      */
  document.body.style.opacity = '0';

  var mount      = document.getElementById('toolbar-mount');
  var depth      = mount ? parseInt(mount.dataset.depth    || '1',   10) : 1;
  // maxWidth (data-maxwidth) is retained for backward-compat but NO LONGER caps the
  // bar. The button row is width:max-content + margin:0 auto, so it self-centers on
  // the viewport axis (same axis the page content centers on) regardless of this
  // value. Do NOT reinstate a width cap from this — capping is exactly what broke
  // centering twice (left-pack-with-right-gap, then hidden Trips). See Toolbar.html
  // § 7 Centering; brain_check.py check_toolbar_centering enforces it.
  var maxWidth   = mount ? parseInt(mount.dataset.maxwidth || '760', 10) : 760;
  var base       = new Array(depth + 1).join('../');   // e.g. depth=2 → '../../'
  var noFootnote = mount ? !!mount.dataset.noFootnote : false;  // read BEFORE mount is removed
  var curr     = location.pathname.split('/').pop() || '';
  var prevHref = mount ? (mount.dataset.prev || '') : '';
  var nextHref = mount ? (mount.dataset.next || '') : '';

  /* ── Links ─────────────────────────────────────────────────────────────── */
  var ITEMS = [
    // Row 1 — trip planning
    { href: base + 'Trip%20Essentials/Trips.html',                                  text: '📆 Trips' },
    { href: base + 'Guides/guides_index.html',                                      text: '🌐 Guides', guides: true },
    { href: base + 'Trip%20Essentials/Travel%20Packing.html',                       text: '👕 Packing' },
    { href: base + 'Trip%20Essentials/Lounges%20US.html',                           text: '💻 US Lounges' },
    { href: base + 'Trip%20Essentials/Maps/Lounges%20Europe.html',                  text: '💻 EU Lounges' },
    // Row 2 — transport & logistics
    // Delta Routes (Full) + SEA Hub moved into Resources → Flights (2026-06-14).
    // European Train Guide moved into Resources → Trains (2026-06-14).
    { href: base + 'Trip%20Essentials/Maps/Europe%20Map.html',                      text: '🗺️ Maps' },
    { href: base + 'Trip%20Essentials/Plug%20Adapter/Plug%20Adapter%20Guide.html',  text: '🔌 Plugs' },
    { href: base + 'Trip%20Essentials/Currency%20Guide.html',                       text: '💰 Currency' },
    { href: base + 'Trip%20Essentials/Climate%20Finder.html',                       text: '🌡️ Climate' },
    { href: base + 'Trip%20Essentials/Resources.html',                              text: '⚙️ Resources' },
  ];

  /* ── Styles ─────────────────────────────────────────────────────────────── */
  var pageBg  = window.getComputedStyle(document.body).backgroundColor;
  // isGuide: only fires when data-toolbar-theme="guide" is explicitly set (guides_index).
  // Guide pages now share the #f5f4f0 warm background with essentials — colour detection
  // retired 2026-05-31 when the guide palette was reskinned to match essentials.
  var isGuide = (mount && mount.dataset.toolbarTheme === 'guide');
  var accent  = isGuide ? '#6b6860'               : '#8a6c1a';
  var acLt    = isGuide ? 'rgba(107,104,96,.06)'  : 'rgba(138,108,26,.06)';
  var acMd    = isGuide ? 'rgba(107,104,96,.10)'  : 'rgba(138,108,26,.10)';

  var styleEl = document.createElement('style');
  styleEl.textContent =
    /* Toolbar outer — static, sits at top of page */
    '.tb{padding:10px 0;position:relative;top:auto;z-index:auto;margin-bottom:0;' +
      'background:rgba(245,244,240,.96);' +
      'border-bottom:none;box-shadow:none}' +
    /* Scroll container */
    '.tb-inner{overflow-x:auto;scrollbar-width:none}' +
    '.tb-inner::-webkit-scrollbar{display:none}' +
    /* Flex row — centered, width:max-content so it never left-packs */
    '.tb-links{display:flex;flex-wrap:nowrap;' +
      'gap:5px;align-items:center;padding:0 24px;' +
      'width:-webkit-max-content;width:max-content;margin:0 auto}' +
    /* Desktop nav links — no rectangle border, just subtle background */
    '.tb a{font-size:11.5px;color:#3d3a32;text-decoration:none;padding:4px 9px;' +
      'border:none;border-radius:4px;background:transparent;white-space:nowrap;flex-shrink:0;' +
      'transition:color .15s,background .15s}' +
    '.tb a:hover{color:' + accent + ';background:' + acLt + '}' +
    '.tb a.tb-active{color:' + accent + ';background:' + acMd + ';font-weight:500}' +
    /* Separator */
    '.tb-sep{width:1px;height:18px;background:#d8d5ce;margin:0 4px;flex-shrink:0}' +
    /* Scroll progress bar */
    '.tb-progress{position:fixed;top:0;left:0;height:2px;width:0%;' +
      'background:' + accent + ';z-index:200;pointer-events:none;' +
      'transition:width .08s linear}' +
    /* Mobile: single-row, horizontally-scrollable strip of rounded chips.
       Wrapping 12 links stacked into a ~146px-tall block; one scrolling row
       is ~42px and reads as a clean nav strip (same model as desktop). */
    '@media(max-width:600px){' +
      '.tb{padding:7px 0}' +
      '.tb-links{flex-wrap:nowrap;gap:6px;padding:0 12px}' +   /* keeps desktop max-content + scroll */
      '.tb-sep{display:none}' +
      '.tb a{padding:6px 11px;font-size:12px;line-height:1;white-space:nowrap;' +
        'border:1px solid #d8d5ce;border-radius:999px;background:#fff;font-weight:500;color:#5a5650}' +
      '.tb a.tb-active{color:' + accent + ';border-color:' + accent + ';background:' + acLt + '}' +
      '.tb a:hover{color:' + accent + ';background:#fff}' +
      '.tb-scroll-wrap{right:8px!important;gap:6px!important}' +
      '.tb-scroll-wrap button{width:40px!important;height:40px!important}' +
    '}'
    ;
  document.head.appendChild(styleEl);

  /* ── Scroll progress bar ────────────────────────────────────────────────── */
  var progress = document.createElement('div');
  progress.className = 'tb-progress';
  document.body.appendChild(progress);
  window.addEventListener('scroll', function () {
    var total = document.documentElement.scrollHeight - window.innerHeight;
    progress.style.width = (total > 0 ? (window.scrollY / total * 100) : 0) + '%';
  }, { passive: true });

  /* ── Build toolbar ──────────────────────────────────────────────────────── */
  /* scroller = full-width overflow container; inner = centered flex row inside it */
  var scroller = document.createElement('div');
  scroller.className = 'tb-inner';

  var inner = document.createElement('div');
  inner.className = 'tb-links';

  ITEMS.forEach(function (item) {
    if (item === null) {
      var sep = document.createElement('span');
      sep.className = 'tb-sep';
      inner.appendChild(sep);
      return;
    }
    var a = document.createElement('a');
    a.href = item.href;
    a.textContent = item.text;
    var cls = [];
    if (item.guides) cls.push('tb-guides');
    if (item.href.split('/').pop() === curr) cls.push('tb-active');
    if (cls.length) a.className = cls.join(' ');
    inner.appendChild(a);
  });

  scroller.appendChild(inner);

  var bar = document.createElement('div');
  bar.className = 'tb';
  bar.appendChild(scroller);


  /* ── Prev / Next sticky nav-bar — sits just below toolbar, sticks to top ── */
  var isRealGuide = /\/Guides\//.test(location.pathname) && location.pathname.indexOf('guides_index') < 0;

  function guideNameFromHref(href) {
    if (!href) return '';
    var parts = href.split('/');
    var folder = parts[parts.length - 2];
    return (folder && folder !== '..') ? decodeURIComponent(folder) : '';
  }

  /* ── Prev / Next — arrows flanking the .overview-title ───────────────────── */
  var btnStyle = 'display:inline-flex;align-items:center;justify-content:center;' +
    'width:44px;height:44px;border-radius:6px;border:1.5px solid #c4b896;' +
    'background:#fdf8f0;color:#6b6860;font-size:26px;line-height:1;' +
    'padding:0;text-decoration:none;flex-shrink:0;';

  /* ── Insert toolbar ──────────────────────────────────────────────────────── */
  if (mount) {
    var hoistTarget = mount;
    while (hoistTarget.parentNode && hoistTarget.parentNode !== document.body) {
      hoistTarget = hoistTarget.parentNode;
    }
    document.body.insertBefore(bar, hoistTarget);
    mount.parentNode.removeChild(mount);
  } else {
    document.body.insertBefore(bar, document.body.firstChild);
  }

  /* ── Arrows inside .overview-title: [‹] · title · [›] — real guides only ─── */
  /* Deferred to DOMContentLoaded: script runs at the top of <body>, before
     .overview-title exists in the DOM. querySelector would return null if run
     synchronously here.                                                       */
  if (isRealGuide && (prevHref || nextHref)) {
    function injectOverviewArrows() {
      var overviewTitle = document.querySelector('.overview-title');
      if (!overviewTitle) return;

      /* Wrap existing title text in a centred span */
      var titleSpan = document.createElement('span');
      titleSpan.style.cssText = 'flex:1;text-align:center;';
      while (overviewTitle.firstChild) titleSpan.appendChild(overviewTitle.firstChild);

      overviewTitle.style.display       = 'flex';
      overviewTitle.style.alignItems    = 'center';
      overviewTitle.style.paddingBottom = '8px';

      if (prevHref) {
        var btnPrev = document.createElement('a');
        btnPrev.href = prevHref;
        btnPrev.textContent = '‹';
        btnPrev.setAttribute('aria-label', 'Previous');
        btnPrev.style.cssText = btnStyle;
        overviewTitle.appendChild(btnPrev);
      } else {
        var sL = document.createElement('span'); sL.style.cssText = 'width:36px;flex-shrink:0;'; overviewTitle.appendChild(sL);
      }

      overviewTitle.appendChild(titleSpan);

      if (nextHref) {
        var btnNext = document.createElement('a');
        btnNext.href = nextHref;
        btnNext.textContent = '›';
        btnNext.setAttribute('aria-label', 'Next');
        btnNext.style.cssText = btnStyle;
        overviewTitle.appendChild(btnNext);
      } else {
        var sR = document.createElement('span'); sR.style.cssText = 'width:36px;flex-shrink:0;'; overviewTitle.appendChild(sR);
      }
    }

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', injectOverviewArrows);
    } else {
      injectOverviewArrows();
    }
  }

  /* ── Scroll up / down fixed buttons (right side, all pages) ─────────────── */
  var scrollWrap = document.createElement('div');
  scrollWrap.className = 'tb-scroll-wrap';
  scrollWrap.style.cssText =
    'position:fixed;right:16px;top:50%;transform:translateY(-50%);' +
    'display:flex;flex-direction:column;align-items:center;gap:8px;z-index:150;';

  var scrollBtnBase =
    'display:flex;align-items:center;justify-content:center;' +
    'width:44px;height:44px;border-radius:6px;border:1.5px solid #c4b896;' +
    'background:#fdf8f0;cursor:pointer;padding:0;' +
    'box-shadow:0 1px 4px rgba(0,0,0,.10);' +
    'transition:background .15s,border-color .15s;';

  function makeScrollBtn(dir) {
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.style.cssText = scrollBtnBase;
    btn.setAttribute('aria-label', dir === 'up' ? 'Scroll to top' : 'Scroll to bottom');
    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '14');
    svg.setAttribute('height', '9');
    svg.setAttribute('viewBox', '0 0 14 9');
    svg.setAttribute('fill', 'none');
    var poly = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    poly.setAttribute('points', dir === 'up' ? '1,8 7,2 13,8' : '1,1 7,7 13,1');
    poly.setAttribute('stroke', '#6b6860');
    poly.setAttribute('stroke-width', '1.8');
    poly.setAttribute('stroke-linecap', 'round');
    poly.setAttribute('stroke-linejoin', 'round');
    svg.appendChild(poly);
    btn.appendChild(svg);
    btn.addEventListener('click', function () {
      window.scrollTo({ top: dir === 'up' ? 0 : document.documentElement.scrollHeight, behavior: 'smooth' });
    });
    btn.addEventListener('mouseenter', function () {
      btn.style.background = acLt;
      btn.style.borderColor = accent;
      poly.setAttribute('stroke', accent);
    });
    btn.addEventListener('mouseleave', function () {
      btn.style.background = '#fdf8f0';
      btn.style.borderColor = '#c4b896';
      poly.setAttribute('stroke', '#6b6860');
    });
    return btn;
  }

  var btnUp   = makeScrollBtn('up');
  var btnDown = makeScrollBtn('down');
  scrollWrap.appendChild(btnUp);
  scrollWrap.appendChild(btnDown);
  document.body.appendChild(scrollWrap);

  /* Hide entirely on non-scrollable pages (e.g. maps); dim individual buttons at limits */
  function updateScrollBtns() {
    var scrollY   = window.scrollY;
    var maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    var canScroll = maxScroll > 1;
    scrollWrap.style.display = canScroll ? 'flex' : 'none';
    if (canScroll) {
      var atTop    = scrollY <= 0;
      var atBottom = scrollY >= maxScroll - 1;
      btnUp.style.opacity        = atTop    ? '0.3' : '1';
      btnUp.style.pointerEvents  = atTop    ? 'none' : '';
      btnDown.style.opacity      = atBottom ? '0.3' : '1';
      btnDown.style.pointerEvents = atBottom ? 'none' : '';
    }
  }
  window.addEventListener('scroll', updateScrollBtns, { passive: true });
  window.addEventListener('resize', updateScrollBtns, { passive: true });
  requestAnimationFrame(function () { requestAnimationFrame(updateScrollBtns); });

  /* ── Reveal page — toolbar is now in the DOM, no layout shift visible ───── */
  requestAnimationFrame(function () {
    var hide = document.getElementById('_tbhide');
    if (hide) hide.parentNode.removeChild(hide);
    document.body.style.transition = 'opacity .12s';
    document.body.style.opacity    = '1';
  });

  /* ── Scroll active item into view — horizontal only, no window scroll ───── */
  var activeLink = inner.querySelector('.tb-active');
  if (activeLink) {
    setTimeout(function () {
      var offset = activeLink.offsetLeft - (scroller.offsetWidth - activeLink.offsetWidth) / 2;
      scroller.scrollLeft = Math.max(0, offset);
    }, 50);
  }

  /* ── Footnote toolbar — RETIRED 2026-06-06 (Dani) ─────────────────────────
     The footer sharing link (footnote.js) is retired for now and must not be
     used in the guides. toolbar.js no longer auto-loads footnote.js on any
     page. The loader below is kept (guarded off) so the feature can be
     re-enabled later by flipping FOOTNOTE_RETIRED to false.
     Validator: TB-9/TB-11 now enforce the retirement (no footnote.js load,
     no inline footer). Rule: Brain/Reference/Toolbar.html § 6. */
  var FOOTNOTE_RETIRED = true;   // retired 2026-06-06 — do not load footnote.js
  if (!FOOTNOTE_RETIRED && !noFootnote) {
    var _fn = document.createElement('script');
    /* footnote.js lives next to toolbar.js inside assets/ — permanent home.
       base resolves to the site root, so prefix with assets/. */
    _fn.src = base + 'assets/footnote.js';
    document.head.appendChild(_fn);
  }

  /* ── Weather widget — loaded on the Guides index ONLY ─────────────────────
     weather.js lives in assets/ (permanent home). On the index it adds the
     🌡 Weather control in the title banner (city picker + monthly high/low
     panel) and per-guide hover weather on the cards. Deliberately NOT loaded
     on individual guide pages. Bump the ?v= below whenever weather.js changes
     so the browser refreshes it (it has no version tag on the page itself). */
  if (curr === 'guides_index.html') {
    var _wx = document.createElement('script');
    _wx.src = base + 'assets/weather.js?v=3';
    document.head.appendChild(_wx);
  }
}());

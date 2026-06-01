/**
 * toolbar.js — shared travel navigation bar
 *
 * Each page needs:
 *   <div id="toolbar-mount" data-depth="N" data-maxwidth="W"></div>
 *   <script src="PATH/toolbar.js"></script>   ← before </body>
 *
 *   data-depth    = directory levels below Travel/ root  (1 or 2)
 *   data-maxwidth = inner max-width px  (760 for Trip Essentials, 940 for Guides)
 *
 * To update the toolbar for every page: edit ONLY this file.
 */
(function () {
  'use strict';

  var mount    = document.getElementById('toolbar-mount');
  var depth    = mount ? parseInt(mount.dataset.depth    || '1',   10) : 1;
  var maxWidth = mount ? parseInt(mount.dataset.maxwidth || '760', 10) : 760;
  var base     = new Array(depth + 1).join('../');   // e.g. depth=2 → '../../'
  var curr     = location.pathname.split('/').pop() || '';
  var prevHref = mount ? (mount.dataset.prev || '') : '';
  var nextHref = mount ? (mount.dataset.next || '') : '';

  /* ── Links ─────────────────────────────────────────────────────────────── */
  var ITEMS = [
    { href: base + 'Trip%20Essentials/Trips.html',                                  text: '📆 Trips' },
    { href: base + 'Trip%20Essentials/Travel%20Packing.html',                       text: '👕 Packing' },
    { href: base + 'Trip%20Essentials/Plug%20Adapter/Plug%20Adapter%20Guide.html',  text: '🔌 Plugs' },
    { href: base + 'Trip%20Essentials/Lounges%20US.html',                           text: '💻 Lounges US' },
    { href: base + 'Trip%20Essentials/Lounges%20Europe.html',                       text: '💻 Lounges EU' },
    { href: base + 'Trip%20Essentials/Delta%20Routes%20Full.html',                  text: '✈️ Routes' },
    { href: base + 'Trip%20Essentials/Delta%20Routes%20SEA.html',                   text: '✈️ SEA Hub' },
    { href: base + 'Trip%20Essentials/European%20Train%20Guide.html',               text: '🚂 EU Trains' },
    null, // separator before Guides
    { href: base + 'Guides/guides_index.html',                                      text: '🌎 Guides', guides: true },
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
    /* Toolbar outer — solid background band so scrolling content doesn't bleed through */
    '.tb{padding:22px 0 8px;position:sticky;top:0;z-index:100;margin-bottom:16px;background:' + pageBg + '}' +
    /* Inner row — no background; pills carry their own */
    '.tb-inner{margin:0 auto;padding:0 24px;display:flex;flex-wrap:nowrap;justify-content:center;' +
      'gap:5px;align-items:center;overflow-x:auto;scrollbar-width:none}' +
    '.tb-inner::-webkit-scrollbar{display:none}' +
    /* Nav links — each pill has its own background so it stays readable over scrolling content */
    '.tb a{font-size:11.5px;color:#6b6860;text-decoration:none;padding:4px 9px;' +
      'border:1px solid #d8d5ce;border-radius:4px;background:' + pageBg + ';white-space:nowrap;flex-shrink:0;' +
      'transition:color .15s,border-color .15s,background .15s}' +
    '.tb a:hover{color:' + accent + ';border-color:' + accent + ';background:' + acLt + '}' +
    '.tb a.tb-active{border-color:' + accent + ';color:' + accent + ';background:' + acMd + ';font-weight:500}' +
    /* Separator */
    '.tb-sep{width:1px;height:18px;background:#d8d5ce;margin:0 4px;flex-shrink:0}' +
    /* Scroll progress bar */
    '.tb-progress{position:fixed;top:0;left:0;height:2px;width:0%;' +
      'background:' + accent + ';z-index:200;pointer-events:none;' +
      'transition:width .08s linear}' +
    /* (side banners removed) */
    /* Mobile: wrap pills instead of horizontal scroll */
    '@media(max-width:600px){' +
      '.tb-inner{flex-wrap:wrap;overflow-x:visible;justify-content:center;padding:0 12px}' +
      '.tb-sep{display:none}' +
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
  var inner = document.createElement('div');
  inner.className = 'tb-inner';
  inner.style.maxWidth = maxWidth + 'px';

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

  var bar = document.createElement('div');
  bar.className = 'tb';
  bar.appendChild(inner);


  /* ── Shared button style ────────────────────────────────────────────────── */
  var isRealGuide = /\/Guides\//.test(location.pathname) && location.pathname.indexOf('guides_index') < 0;
  var cssTitleBg  = getComputedStyle(document.documentElement).getPropertyValue('--c-title-bg').trim();
  var btnColor    = '#fdf8f0';
  var fabBase  = 'position:fixed;width:44px;height:44px;border-radius:50%;' +
    'background:' + btnColor + ';color:#6b4a0a;border:1.5px solid #c4a870;font-size:18px;' +
    'cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,0.22);z-index:999;' +
    'display:flex;align-items:center;justify-content:center;' +
    'text-decoration:none;transition:opacity .25s,transform .25s;';

  /* ── Auto-hide helpers — fade out while scrolling, reappear when idle ──── */
  var scrollTimer;
  var fabsVisible = true;
  var allFabs = [];
  function hideFabs() {
    if (!fabsVisible) return;
    fabsVisible = false;
    allFabs.forEach(function (el) { el.style.opacity = '0'; el.style.pointerEvents = 'none'; });
  }
  function showFabs() {
    fabsVisible = true;
    allFabs.forEach(function (el) {
      el.style.pointerEvents = '';
      /* scroll-to-top only shows once past threshold */
      if (el === fab) {
        el.style.opacity = (window.scrollY > 300) ? '1' : '0';
        el.style.pointerEvents = (window.scrollY > 300) ? '' : 'none';
      } else {
        el.style.opacity = '1';
      }
    });
  }
  window.addEventListener('scroll', function () {
    hideFabs();
    clearTimeout(scrollTimer);
    scrollTimer = setTimeout(showFabs, 800);
  }, { passive: true });

  /* ── ↑ scroll-to-top — bottom-right, appears after 300px scroll ─────────── */
  var fab = document.createElement('button');
  fab.textContent = '↑';
  fab.setAttribute('aria-label', 'Back to top');
  fab.style.cssText = fabBase + 'right:20px;bottom:24px;opacity:0;pointer-events:none;';
  fab.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
  document.body.appendChild(fab);
  allFabs.push(fab);

  /* ── ← Prev / Next → — bottom corners, thumb-friendly ──────────────────── */
  if (prevHref) {
    var btnPrev = document.createElement('a');
    btnPrev.href = prevHref;
    btnPrev.textContent = '←';
    btnPrev.setAttribute('aria-label', 'Previous');
    btnPrev.style.cssText = fabBase + 'left:20px;bottom:24px;';
    document.body.appendChild(btnPrev);
    allFabs.push(btnPrev);
  }
  if (nextHref) {
    var btnNext = document.createElement('a');
    btnNext.href = nextHref;
    btnNext.textContent = '→';
    btnNext.setAttribute('aria-label', 'Next');
    /* if scroll-to-top is also present, offset next button left so they don't overlap */
    var nextRight = (prevHref ? 72 : 20);
    btnNext.style.cssText = fabBase + 'right:' + nextRight + 'px;bottom:24px;';
    document.body.appendChild(btnNext);
    allFabs.push(btnNext);
  }

  /* ── Insert — hoist to direct child of <body> so sticky spans full width ──
     Guide pages place the mount inside .container (760 px). Inserting there
     constrains the toolbar to container width and clips the Guides link.
     Walk up to the first child of <body> and insert before it instead.      */
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

  /* ── Scroll active item into view so it's never clipped ────────────────── */
  var activeLink = inner.querySelector('.tb-active');
  if (activeLink) {
    setTimeout(function () { activeLink.scrollIntoView({ inline: 'nearest', block: 'nearest' }); }, 50);
  }

  /* ── Shared footnote (sharing link) ──────────────────────────────────────
     One definition for every page. When the page is served over the web the
     footnote links to its OWN live URL (location), so it is always correct no
     matter what the GitHub repo is named or how the folders are arranged —
     and it survives future repo renames with no edits. Only a local file://
     preview falls back to a constructed URL.
     If the published site ever moves, update SITE_BASE below — nothing else. */
  var SITE_BASE = 'https://dbellinello.github.io/Travel/';
  var decodedPath = decodeURIComponent(location.pathname);
  if (decodedPath.indexOf('.html') > -1 || decodedPath.charAt(decodedPath.length - 1) === '/') {
    var shareUrl, shareText;
    if (location.protocol === 'http:' || location.protocol === 'https:') {
      shareUrl  = location.origin + location.pathname;
      shareText = (location.host + decodeURIComponent(location.pathname)).replace(/^www\./, '');
    } else {
      var fm  = decodedPath.match(/\/(?:travel|travel_guides|Travel)\/(.+)$/);
      var sub = fm ? fm[1] : (decodedPath.split('/').pop() || '');
      shareUrl  = SITE_BASE + sub.split('/').map(encodeURIComponent).join('/');
      shareText = SITE_BASE.replace(/^https?:\/\//, '') + sub;
    }
    var foot = document.createElement('div');
    foot.className = 'tb-footnote';
    foot.style.cssText = 'text-align:center;margin:32px 0 0;padding:0 16px 24px;font-size:11px';
    var fa = document.createElement('a');
    fa.href = shareUrl;
    fa.target = '_blank';
    fa.style.cssText = 'color:#9a9890;text-decoration:none;font-weight:normal';
    fa.textContent = shareText;
    foot.appendChild(fa);
    // Guides wrap content in .container (which carries bottom padding); drop the
    // footnote INSIDE it so it sits right under the content at the same 32px
    // distance as on Trip Essentials. Those pages have no .container, so they
    // fall back to <body> — the placement that already looks right there.
    // Defer to DOMContentLoaded: this script can run near the top of <body>,
    // so appending immediately would land the footnote above the content.
    function placeFootnote() {
      (document.querySelector('.container') || document.body).appendChild(foot);
    }
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', placeFootnote);
    } else {
      placeFootnote();
    }
  }
}());

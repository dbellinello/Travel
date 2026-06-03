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

  /* ── Hide page immediately so the toolbar insertion doesn't cause a visible
     layout shift (flicker). Revealed below once the bar is in the DOM.      */
  document.body.style.opacity = '0';

  var mount      = document.getElementById('toolbar-mount');
  var depth      = mount ? parseInt(mount.dataset.depth    || '1',   10) : 1;
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
    { href: base + 'Trip%20Essentials/Resources.html',                              text: '⚙️ Resources' },
    { href: base + 'Trip%20Essentials/Lounges%20US.html',                           text: '💻 Lounges US' },
    { href: base + 'Trip%20Essentials/Maps/Lounges%20Europe.html',                  text: '💻 Lounges EU' },
    // Row 2 — transport & logistics
    { href: base + 'Trip%20Essentials/Delta%20Routes%20Full.html',                  text: '✈️ Routes' },
    { href: base + 'Trip%20Essentials/Delta%20Routes%20SEA.html',                   text: '✈️ SEA Hub' },
    { href: base + 'Trip%20Essentials/European%20Train%20Guide.html',               text: '🚆 EU Trains' },
    { href: base + 'Trip%20Essentials/Maps/Europe%20Map.html',                      text: '🗺️ Maps' },
    { href: base + 'Trip%20Essentials/Plug%20Adapter/Plug%20Adapter%20Guide.html',  text: '🔌 Plugs' },
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
    /* Toolbar outer — scrolls with page */
    '.tb{padding:10px 0;position:relative;margin-bottom:0;background:#e8e4db;border-bottom:1px solid #ccc8be;box-shadow:0 2px 8px rgba(0,0,0,.07)}' +
    /* Scroll container — full width, hides scrollbar; no flex/justify-content here
       (justify-content:center + overflow-x:auto clips the left side of overflowing content) */
    '.tb-inner{overflow-x:auto;scrollbar-width:none}' +
    '.tb-inner::-webkit-scrollbar{display:none}' +
    /* Flex row — width:fit-content + margin:auto centers items when they fit;
       when they overflow the scroll container handles it cleanly from the left */
    '.tb-links{display:flex;flex-wrap:nowrap;justify-content:flex-start;' +
      'gap:5px;align-items:center;padding:0 24px;' +
      'width:-webkit-fit-content;width:fit-content;margin:0 auto}' +
    /* Nav links */
    '.tb a{font-size:11.5px;color:#3d3a32;text-decoration:none;padding:4px 9px;' +
      'border:1px solid #b8b3a8;border-radius:4px;background:#f0ece4;white-space:nowrap;flex-shrink:0;' +
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
    /* Mobile: 4-per-row grid with proper touch targets */
    '@media(max-width:600px){' +
      '.tb{padding:6px 0}' +
      '.tb-links{flex-wrap:wrap;justify-content:flex-start;padding:0 10px;gap:4px;width:100%;margin:0}' +
      '.tb-sep{display:none}' +
      '.tb a{flex:0 0 calc(25% - 3px);min-width:0;min-height:36px;overflow:hidden;text-overflow:ellipsis;' +
        'display:flex;align-items:center;justify-content:center;text-align:center;' +
        'box-sizing:border-box;padding:6px 2px;font-size:10.5px;line-height:1.2}' +
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

  /* ── Prev / Next — arrows flanking the .glance-title ───────────────────── */
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

  /* ── Arrows inside .glance-title: [‹] · title · [›] — real guides only ─── */
  /* Deferred to DOMContentLoaded: script runs at the top of <body>, before
     .glance-title exists in the DOM. querySelector would return null if run
     synchronously here.                                                       */
  if (isRealGuide && (prevHref || nextHref)) {
    function injectGlanceArrows() {
      var glanceTitle = document.querySelector('.glance-title');
      if (!glanceTitle) return;

      /* Wrap existing title text in a centred span */
      var titleSpan = document.createElement('span');
      titleSpan.style.cssText = 'flex:1;text-align:center;';
      while (glanceTitle.firstChild) titleSpan.appendChild(glanceTitle.firstChild);

      glanceTitle.style.display       = 'flex';
      glanceTitle.style.alignItems    = 'center';
      glanceTitle.style.paddingBottom = '8px';

      if (prevHref) {
        var btnPrev = document.createElement('a');
        btnPrev.href = prevHref;
        btnPrev.textContent = '‹';
        btnPrev.setAttribute('aria-label', 'Previous');
        btnPrev.style.cssText = btnStyle;
        glanceTitle.appendChild(btnPrev);
      } else {
        var sL = document.createElement('span'); sL.style.cssText = 'width:36px;flex-shrink:0;'; glanceTitle.appendChild(sL);
      }

      glanceTitle.appendChild(titleSpan);

      if (nextHref) {
        var btnNext = document.createElement('a');
        btnNext.href = nextHref;
        btnNext.textContent = '›';
        btnNext.setAttribute('aria-label', 'Next');
        btnNext.style.cssText = btnStyle;
        glanceTitle.appendChild(btnNext);
      } else {
        var sR = document.createElement('span'); sR.style.cssText = 'width:36px;flex-shrink:0;'; glanceTitle.appendChild(sR);
      }
    }

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', injectGlanceArrows);
    } else {
      injectGlanceArrows();
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

  /* ── Footnote toolbar — loaded as a separate script (footnote.js) ─────────
     toolbar.js handles navigation only; footnote.js handles the sharing link.
     noFootnote is read from data-no-footnote BEFORE the mount div is removed,
     so the flag is still available here even though the mount is gone. */
  if (!noFootnote) {
    var _fn = document.createElement('script');
    _fn.src = base + 'footnote.js';
    document.head.appendChild(_fn);
  }
}());

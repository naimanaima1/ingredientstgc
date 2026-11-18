/* JARA nudge: a small, dismissible card that slides in from the bottom corner.
   Gentle by design: never covers the page, never on first paint, at most once
   every 14 days per browser, never after someone has clicked through to JARA,
   and never on test or noindex pages. The wording matches the page:
     plan pages        → schedule this plan in JARA
     ingredient pages  → track how your hair responds to <ingredient>
     everything else   → the free printable tracker
   Every link carries utm_medium=popup so visits show up separately in analytics. */
(function () {
  var KEY = 'tgc_nudge';            // stores the time it was last shown or dismissed
  var CLICKED = 'tgc_nudge_clicked'; // set once someone clicks through; we stop showing
  var QUIET_DAYS = 14;
  var DELAY_MS = 25000;             // or 45% scroll, whichever comes first

  function get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  if (document.querySelector('meta[name="robots"][content*="noindex"]')) return;
  if (get(CLICKED)) return;
  var last = +get(KEY) || 0;
  if (Date.now() - last < QUIET_DAYS * 864e5) return;
  if (/utm_source=jara/.test(location.search)) return; // came from JARA already

  var parts = location.pathname.split('/').filter(Boolean);
  var SECTIONS = /^(products|plans|groups|properties|ingredients|about|label-check|test-program|programs|home-test|previous-home|data|assets)$/;
  var h1 = document.querySelector('main h1');
  var title = h1 ? h1.textContent.trim() : '';
  var kind = 'general', slug = parts.join('-') || 'home';
  if (parts[0] === 'plans' && parts.length === 2) kind = 'plan';
  else if (parts.length === 1 && !SECTIONS.test(parts[0]) && document.querySelector('.first .name h1')) kind = 'ingredient';

  function link(url, content) {
    return url + (url.indexOf('?') > -1 ? '&' : '?') +
      'utm_source=library&utm_medium=popup&utm_campaign=jara_beta&utm_content=' + encodeURIComponent(kind + '_' + content);
  }

  var COPY = {
    plan: {
      eyebrow: 'Make it stick',
      head: 'Schedule <em>this plan</em> in JARA',
      text: 'Get a reminder for each step, log wash days in seconds, and see if it is working by week 4.',
      cta: 'Start 14 days free', url: 'https://itsjara.com/beta',
      alt: 'Or grab the free printable tracker', altUrl: 'https://itsjara.com/free-hair-tracker'
    },
    ingredient: {
      eyebrow: 'Curious if it works for you?',
      head: 'Track how your hair responds to <em>' + esc(title || 'this ingredient') + '</em>',
      text: 'JARA links each product to your wash-day ratings, so you can see which ingredients your hair actually likes.',
      cta: 'Try JARA free', url: 'https://itsjara.com/beta',
      alt: 'Prefer paper? Get the free printable', altUrl: 'https://itsjara.com/free-hair-tracker'
    },
    general: {
      eyebrow: 'Free printable',
      head: 'Stop growing your hair <em>on memory</em>',
      text: 'A free wash log, length chart and trim tracker. Print it, pin it up, and see what works.',
      cta: 'Get the free tracker', url: 'https://itsjara.com/free-hair-tracker',
      alt: 'Or try the JARA app free for 14 days', altUrl: 'https://itsjara.com/beta'
    }
  }[kind];

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  var shown = false, card;
  function inlineJaraVisible() {
    var els = document.querySelectorAll('.jara');
    for (var i = 0; i < els.length; i++) {
      var r = els[i].getBoundingClientRect();
      if (r.top < innerHeight && r.bottom > 0) return true;
    }
    return false;
  }

  function show() {
    if (shown) return;
    if (inlineJaraVisible()) return; // try again on the next scroll
    shown = true;
    cleanup();
    set(KEY, Date.now());
    card = document.createElement('aside');
    card.className = 'nudge';
    card.setAttribute('role', 'dialog');
    card.setAttribute('aria-label', 'JARA hair tracker');
    card.innerHTML =
      '<button class="nudge-x" type="button" aria-label="Close">\u00d7</button>' +
      '<span class="eyebrow"><span class="little-dot"></span>' + COPY.eyebrow + '</span>' +
      '<h2>' + COPY.head + '</h2>' +
      '<p>' + COPY.text + '</p>' +
      '<a class="btn nudge-go" href="' + link(COPY.url, 'primary') + '">' + COPY.cta + '</a>' +
      '<a class="nudge-alt" href="' + link(COPY.altUrl, 'secondary') + '">' + COPY.alt + ' \u2192</a>';
    document.body.appendChild(card);
    requestAnimationFrame(function () { card.classList.add('in'); });
    card.querySelector('.nudge-x').onclick = close;
    card.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () { set(CLICKED, '1'); });
    });
    document.addEventListener('keydown', onKey);
  }

  function close() {
    set(KEY, Date.now());
    card.classList.remove('in');
    document.removeEventListener('keydown', onKey);
    setTimeout(function () { card.remove(); }, 300);
  }
  function onKey(e) { if (e.key === 'Escape') close(); }

  function onScroll() {
    var doc = document.documentElement;
    var depth = (scrollY + innerHeight) / doc.scrollHeight;
    if (depth > 0.45) show();
  }
  var timer = setTimeout(function () {
    show();
    if (!shown) addEventListener('scroll', onScroll, { passive: true });
  }, DELAY_MS);
  addEventListener('scroll', onScroll, { passive: true });
  function cleanup() { clearTimeout(timer); removeEventListener('scroll', onScroll); }
})();

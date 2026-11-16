/* Hover (or keyboard-focus) preview for any link that points at an ingredient page.
   Works anywhere without the page generators knowing about it: the slug is read
   off the href and looked up in data/tips.json, which is fetched once, lazily,
   the first time someone hovers something that might be an ingredient. */
(function () {
  if (!window.matchMedia || !matchMedia('(hover: hover)').matches) return;

  var me = document.currentScript || document.querySelector('script[src$="assets/tips.js"]');
  var ROOT = (me && me.dataset.root) || '';
  var tips = null, pending = null, box = null, current = null, timer = null;

  function load() {
    return pending || (pending = fetch(ROOT + 'data/tips.json')
      .then(function (r) { return r.json(); })
      .then(function (j) { return (tips = j); })
      .catch(function () { return (tips = {}); }));
  }

  function slugOf(a) {
    var href = a.getAttribute('href') || '';
    if (/^(https?:|mailto:|#)/.test(href) && href.indexOf(location.host) === -1) return null;
    var parts = href.replace(/[?#].*$/, '').split('/').filter(Boolean);
    var last = parts[parts.length - 1];
    if (!last || last.indexOf('.') > -1) return null;
    // ingredient pages sit at the root, so a link into a known section is not one
    if (/^(products|plans|groups|properties|ingredients|about|home-test|previous-home|test-program|programs|data|assets)$/.test(parts[parts.length - 2] || '')) return null;
    return last;
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function make() {
    box = document.createElement('div');
    box.className = 'tip';
    box.setAttribute('role', 'tooltip');
    box.hidden = true;
    document.body.appendChild(box);
    return box;
  }

  function show(a, rec) {
    var el = box || make();
    var tags = (rec[3] || []).map(function (t) { return '<span>' + esc(t) + '</span>'; }).join('');
    el.innerHTML = '<b>' + esc(rec[0]) + '</b>'
      + (rec[1] ? '<span class="tip-cat">' + esc(rec[1]) + '</span>' : '')
      + (rec[2] ? '<p>' + esc(rec[2]) + '</p>' : '')
      + (tags ? '<div class="tip-tags">' + tags + '</div>' : '');
    el.hidden = false;

    var r = a.getBoundingClientRect(), b = el.getBoundingClientRect();
    var left = Math.min(Math.max(8, r.left + r.width / 2 - b.width / 2), innerWidth - b.width - 8);
    var above = r.top > b.height + 14;
    el.classList.toggle('is-below', !above);
    el.style.left = (left + scrollX) + 'px';
    el.style.top = ((above ? r.top - b.height - 10 : r.bottom + 10) + scrollY) + 'px';
    current = a;
  }

  function hide() {
    clearTimeout(timer);
    current = null;
    if (box) { box.hidden = true; }
  }

  function enter(a) {
    if (a === current) return;
    var slug = slugOf(a);
    if (!slug) return hide();
    clearTimeout(timer);
    timer = setTimeout(function () {
      load().then(function (t) {
        var rec = t[slug];
        if (rec && document.body.contains(a) && a.matches(':hover, :focus-visible')) show(a, rec);
      });
    }, 220);
  }

  document.addEventListener('mouseover', function (ev) {
    var a = ev.target.closest && ev.target.closest('a[href]');
    if (a) enter(a); else if (current && !ev.target.closest('.tip')) hide();
  });
  document.addEventListener('focusin', function (ev) {
    var a = ev.target.closest && ev.target.closest('a[href]');
    if (a) enter(a); else hide();
  });
  document.addEventListener('mouseout', function (ev) {
    if (current && ev.target === current) hide();
  });
  document.addEventListener('focusout', hide);
  addEventListener('scroll', hide, { passive: true });
  document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') hide(); });
}());

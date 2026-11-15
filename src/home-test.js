(function () {
  var L = window.TLIB, KEYS = L.keys, CHECKS = L.checks, ROOT = L.root || '';
  var norm = function (s) { return s.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim(); };
  var esc = function (s) {
    return s.replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  };

  function split(text) {
    return text.replace(/’/g, "'")
      .replace(/(\d)\s*,\s*(\d)/g, '$1,$2')
      .split(/[;,](?!\d)/)
      .map(function (s) { return s.replace(/\*+/g, '').replace(/\s+/g, ' ').trim(); })
      .filter(function (s) { return s && s.length > 1; });
  }

  function lookup(t) {
    var n = norm(t);
    if (KEYS[n]) return KEYS[n];
    var m = n.match(/^(organic|certified organic|deionized|purified|distilled)\s+(.*)$/);
    if (m && KEYS[m[2]]) return KEYS[m[2]];
    var parts = n.split(/\s*\/\s*/);
    for (var i = 0; i < parts.length; i++) if (KEYS[parts[i]]) return KEYS[parts[i]];
    var br = t.match(/\(([^)]+)\)/);
    if (br && KEYS[norm(br[1])]) return KEYS[norm(br[1])];
    var out = norm(t.replace(/\([^)]*\)/g, ''));
    return KEYS[out] || null;
  }

  function byName(t) {
    var n = norm(t);
    if (/(cone|conol|siloxane|silane)$/.test(n) || n.indexOf('siloxane') > -1 || n.indexOf('methicone') > -1) return 'silicone';
    if (n.indexOf('sulfate') > -1 && n.indexOf('methosulfate') === -1 && n.indexOf('sulfosuccinate') === -1
        && /(lauryl|laureth|coco|myreth|coceth|decyl)/.test(n)) return 'sulfate';
    return null;
  }

  var answers = document.getElementById('t-answers'),
      note = document.getElementById('t-note'),
      more = document.getElementById('t-more'),
      inci = document.getElementById('t-inci'),
      foot = document.getElementById('t-foot'),
      fIn = document.getElementById('tf'),
      fList = document.getElementById('tf-list');

  var asked = new Set();
  document.querySelectorAll('.t-chip').forEach(function (c) {
    c.addEventListener('click', function () {
      var g = c.dataset.g, on = asked.has(g);
      on ? asked.delete(g) : asked.add(g);
      c.setAttribute('aria-pressed', String(!on));
      answers.querySelectorAll('.t-row').forEach(function (r) {
        r.classList.toggle('is-asked', asked.has(r.dataset.g));
      });
      sort();
    });
  });

  // a ticked group floats to the top; otherwise the four keep their order
  function sort() {
    var rows = [].slice.call(answers.querySelectorAll('.t-row'));
    rows.sort(function (a, b) {
      var ka = asked.has(a.dataset.g) ? 0 : 1, kb = asked.has(b.dataset.g) ? 0 : 1;
      if (ka !== kb) return ka - kb;
      return CHECKS.findIndex(function (c) { return c[0] === a.dataset.g; })
           - CHECKS.findIndex(function (c) { return c[0] === b.dataset.g; });
    });
    rows.forEach(function (r) { answers.appendChild(r); });
  }

  function read(items, product) {
    var found = items.map(function (t) { return [t, lookup(t)]; });
    var hits = {}, known = 0;
    found.forEach(function (pair) {
      var t = pair[0], h = pair[1];
      if (h) known++;
      var gs = h ? h[2] : (byName(t) ? [byName(t)] : []);
      gs.forEach(function (g) {
        hits[g] = hits[g] || [];
        var html = h ? '<a href="' + ROOT + h[0] + '/">' + esc(h[1]) + '</a>' : esc(t);
        if (hits[g].indexOf(html) === -1) hits[g].push(html);
      });
    });

    answers.classList.add('is-read');
    CHECKS.forEach(function (c) {
      var k = c[0], row = answers.querySelector('.t-row[data-g="' + k + '"]');
      var got = hits[k] || [];
      row.classList.toggle('is-yes', got.length > 0);
      row.classList.toggle('is-no', got.length === 0);
      row.querySelector('.t-ans').textContent = got.length ? 'Yes' : 'No';
      row.querySelector('.t-detail').innerHTML = got.length ? got.join(', ') : esc(c[2]);
    });
    sort();

    var miss = items.length - known;
    note.innerHTML = 'We read ' + items.length + ' ingredients'
      + (product ? ' on the label for <b>' + esc(product.n) + '</b>' : ' from what you pasted')
      + '. ' + (miss
        ? miss + ' of them are not in our library yet, so a "no" means we did not find one, not that there is none.'
        : 'All of them are in our library.');

    inci.innerHTML = found.map(function (pair) {
      var t = pair[0], h = pair[1];
      return h ? '<a href="' + ROOT + h[0] + '/">' + esc(t) + '</a>' : esc(t);
    }).join(', ') + '.';
    foot.textContent = known + ' of ' + items.length + ' have their own page.';
    more.hidden = false;
  }

  var all = null, loading = null, pick = -1, hits = [];
  function load() {
    return loading || (loading = fetch(ROOT + 'data/find.json').then(function (r) { return r.json(); })
      .then(function (j) { return (all = j); }));
  }
  function close() { fList.hidden = true; fList.innerHTML = ''; fIn.setAttribute('aria-expanded', 'false'); pick = -1; }
  function choose(p) { close(); fIn.value = p.n; read(p.i, p); }

  fIn.addEventListener('focus', load);
  fIn.addEventListener('input', function () {
    load().then(function () {
      var q = norm(fIn.value);
      if (q.length < 2) return close();
      hits = all.filter(function (p) { return norm(p.n + ' ' + p.b).indexOf(q) > -1; }).slice(0, 6);
      if (!hits.length) {
        fList.innerHTML = '<li class="t-miss">Not in our library yet — paste its ingredient list below.</li>';
      } else {
        fList.innerHTML = hits.map(function (p, n) {
          return '<li role="option" id="tf-o' + n + '" data-n="' + n + '"><b>' + esc(p.n) + '</b><span>' + esc(p.b) + '</span></li>';
        }).join('');
        fList.querySelectorAll('li[data-n]').forEach(function (li) {
          li.addEventListener('click', function () { choose(hits[+li.dataset.n]); });
        });
      }
      fList.hidden = false; fIn.setAttribute('aria-expanded', 'true'); pick = -1;
    });
  });
  fIn.addEventListener('keydown', function (ev) {
    var opts = fList.querySelectorAll('li[data-n]');
    if (!opts.length) return;
    if (ev.key === 'ArrowDown' || ev.key === 'ArrowUp') {
      ev.preventDefault();
      pick = (pick + (ev.key === 'ArrowDown' ? 1 : opts.length - 1)) % opts.length;
      opts.forEach(function (o, i) { o.classList.toggle('on', i === pick); });
      fIn.setAttribute('aria-activedescendant', 'tf-o' + pick);
    } else if (ev.key === 'Enter') {
      ev.preventDefault(); choose(hits[pick < 0 ? 0 : pick]);
    } else if (ev.key === 'Escape') { close(); }
  });
  document.addEventListener('click', function (ev) {
    if (!fIn.contains(ev.target) && !fList.contains(ev.target)) close();
  });

  document.getElementById('t-form').addEventListener('submit', function (ev) {
    ev.preventDefault();
    var items = split(document.getElementById('tt').value);
    if (items.length) read(items, null);
  });
}());

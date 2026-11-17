// Homepage: guided walk-through of the example label, and decoding a pasted label.
// Matching follows scripts/build.py (lookup and split_label).
(function () {
  const K = LIB.keys, G = LIB.groups, GN = Object.fromEntries(G.map(g => [g[0], g]));
  const norm = s => s.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  const PREFIX = /^(organic|certified organic|deionized|distilled|purified|pure|raw|natural|unrefined)\s+/i;
  const esc = s => s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  function lookup(t) {
    t = t.trim().replace(/^\*+|\*+$/g, '').trim();
    let tries = [t, t.replace(/\(.*?\)/g, ''), t.replace(/\s*\(.*?\)\s*/g, ' ')];
    const m = t.match(/\((.*?)\)/); if (m) tries.push(m[1]);
    tries.slice().forEach(x => { if (x.includes('/')) tries = tries.concat(x.split('/')); });
    tries.slice().forEach(x => tries.push(x.trim().replace(PREFIX, '')));
    for (const x of tries) { const hit = K[norm(x)]; if (hit) return hit; }
    return null;
  }
  function split(L) {
    L = L.replace(/(^|[^\w-])(\d),\s+(\d)-/g, '$1$2,$3-').replace(/^\s*(ingredients?|inci)\s*:\s*/i, '');
    const out = []; let depth = 0, cur = '';
    for (let i = 0; i < L.length; i++) {
      const c = L[i];
      if (c === '(') depth++; if (c === ')') depth = Math.max(0, depth - 1);
      if ((c === ',' || c === ';' || c === '\n') && depth === 0 && !/\d/.test(L[i + 1] || '')) { out.push(cur); cur = ''; } else cur += c;
    }
    out.push(cur);
    return out.map(t => t.replace(/\*.*$/, '').trim().replace(/\.$/, '').replace(/^(and|or)\s+/i, '')).filter(Boolean);
  }

  const chk = document.getElementById('chk');
  function byName(t) {
    const n = norm(t);
    if (/(cone|conol|siloxane|silane)$/.test(n) || n.includes('siloxane') || n.includes('methicone')) return 'silicone';
    if (n.includes('sulfate') && !n.includes('methosulfate') && !n.includes('sulfosuccinate') && /(lauryl|laureth|coco|myreth|coceth|decyl)/.test(n)) return 'sulfate';
    return null;
  }
  function namesOf(t) {
    const n = norm(t), out = [], g = byName(t);
    if (g) out.push(g);
    (LIB.watch || []).forEach(([k, src]) => { if (!out.includes(k) && new RegExp(src).test(n)) out.push(k); });
    return out;
  }
  function strip(found) {
    const cells = LIB.checks.map(([k, label, desc]) => {
      const hits = found[k] || [];
      return hits.length
        ? `<div class="chk-item is-yes" data-g="${k}"><b>${esc(label)}</b><span class="chk-state">Yes, ${hits.length}</span><p>${hits.join(', ')}</p><button type="button" class="chk-lite" data-g="${k}" aria-pressed="false">Show these</button></div>`
        : `<div class="chk-item is-no" data-g="${k}"><b>${esc(label)}</b><span class="chk-state">None found</span><p>${esc(desc)}</p></div>`;
    }).join('');
    return `<div class="chk">${cells}</div>`;
  }

  function wireLite() {
    chk.querySelectorAll('.chk-lite').forEach(btn => btn.addEventListener('click', () => {
      const on = btn.getAttribute('aria-pressed') === 'true';
      chk.querySelectorAll('.chk-lite').forEach(b => { b.setAttribute('aria-pressed', 'false'); b.textContent = 'Show these'; });
      wordsEl.querySelectorAll('.lit').forEach(w => w.classList.remove('lit'));
      if (on) return;
      btn.setAttribute('aria-pressed', 'true');
      btn.textContent = 'Hide';
      wordsEl.querySelectorAll('[data-c]').forEach(w => {
        if (w.dataset.c.split(' ').indexOf(btn.dataset.g) > -1) w.classList.add('lit');
      });
    }));
  }

  wireLite();

  const card = document.getElementById('card'), cap = document.getElementById('cap'), dotsBox = document.getElementById('dots');
  const wordsEl = document.getElementById('words'), groupsEl = document.getElementById('groups'), foot = document.getElementById('foot');
  const nameEl = document.getElementById('btl-name'), reset = document.getElementById('reset'), ta = document.getElementById('t');
  const example = { words: wordsEl.innerHTML, groups: groupsEl.innerHTML, foot: foot.innerHTML, name: nameEl.innerHTML, dots: dotsBox.innerHTML, chk: chk.innerHTML };
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let timer = null, idx = 0, keys = [];

  function setStep(i) {
    idx = (i + keys.length) % keys.length; const k = keys[idx], g = GN[k];
    wordsEl.querySelectorAll('a').forEach(a => a.classList.toggle('on', (a.dataset.g || '').split(' ').includes(k)));
    groupsEl.querySelectorAll('li').forEach(li => li.classList.toggle('on', li.dataset.k === k));
    dotsBox.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', b.dataset.k === k));
    cap.innerHTML = `<small>${idx + 1} of ${keys.length} · ${esc(g[1])}</small><b>${esc(g[2])}</b><p>${esc(g[3])}</p>`;
  }
  function play() { stop(); if (!reduce) timer = setInterval(() => setStep(idx + 1), 3800); }
  function stop() { if (timer) clearInterval(timer); timer = null; }
  function guided() {
    keys = [...dotsBox.querySelectorAll('button')].map(b => b.dataset.k);
    dotsBox.querySelectorAll('button').forEach((b, i) => b.addEventListener('click', () => { stop(); setStep(i); }));
    if (keys.length) { setStep(0); play(); }
  }
  card.addEventListener('mouseenter', stop); card.addEventListener('focusin', stop);
  card.addEventListener('mouseleave', () => { if (keys.length && !card.classList.contains('mine')) play(); });

  // what the reader ticked at the top of the page
  const asked = new Set();
  document.querySelectorAll('.ask-chip').forEach(c => c.addEventListener('click', () => {
    const g = c.dataset.g, on = asked.has(g);
    on ? asked.delete(g) : asked.add(g);
    c.setAttribute('aria-pressed', String(!on));
    paint();
  }));
  function paint() {
    chk.querySelectorAll('.chk-item').forEach(el => el.classList.toggle('is-asked', asked.has(el.dataset.g)));
    const first = [...asked][0];
    const btn = first && chk.querySelector(`.chk-lite[data-g="${first}"]`);
    if (btn && btn.getAttribute('aria-pressed') !== 'true') btn.click();
  }

  function render(items, source) {
    stop(); card.classList.add('mine');
    nameEl.innerHTML = source ? `<a href="${LIB.root}products/${source.s}/">${esc(source.n)}</a>` : 'Your label';
    const found = items.map(t => [t, lookup(t)]);
    wordsEl.innerHTML = found.map(([t, h]) => h ? `<a href="${LIB.root}${h[0]}/" data-g="${h[2].join(" ")}"${h[3].length ? ` data-c="${h[3].join(' ')}"` : ''}>${esc(t)}</a>` : `<span${namesOf(t).length ? ` data-c="${namesOf(t).join(' ')}"` : ''}>${esc(t)}</span>`).join(', ') + '.';
    const seen = new Set(found.filter(f => f[1]).map(f => f[1][0]));
    const rows = G.map(g => { const m = []; found.forEach(([t, h]) => { if (h && h[2].includes(g[0]) && !m.some(x => x[0] === h[0])) m.push(h); });
      return m.length ? [g[0], m] : null; }).filter(Boolean);
    groupsEl.innerHTML = rows.map(([k, m]) => `<li data-k="${k}"><b>${esc(GN[k][1])}</b><span>${m.map(h => `<a href="${LIB.root}${h[0]}/">${esc(h[1])}</a>`).join(', ')}</span></li>`).join('');
    foot.innerHTML = `<b>${seen.size} of ${items.length}</b> in our library · grey words aren't in it yet`;
    const checks = {};
    found.forEach(([t, h]) => {
      const gs = h ? h[3] : namesOf(t);
      gs.forEach(g => {
        checks[g] = checks[g] || [];
        const txt = h ? `<a href="${LIB.root}${h[0]}/">${esc(h[1])}</a>` : esc(t);
        if (!checks[g].includes(txt)) checks[g].push(txt);
      });
    });
    let note = source
      ? `Based on the ${items.length} ingredients on this label, as we read it.`
      : `Based on the ${items.length} ingredients you pasted.`;
    const miss = items.length - seen.size;
    if (miss) note += ` ${miss} of them are not in our library yet, so we cannot say for certain about those.`;
    chk.innerHTML = `<h3 class="chk-h">Does it have…</h3>${strip(checks)}<p class="chk-note">${note}</p>`;
    wireLite();
    paint();
    card.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }

  const fIn = document.getElementById('f'), fList = document.getElementById('f-list'), fNote = document.getElementById('f-note');
  if (fIn) {
    let all = null, loading = null, pick = -1;
    const load = () => loading = loading || fetch(LIB.root + 'data/find.json').then(r => r.json()).then(j => (all = j));
    fIn.addEventListener('focus', load);
    const close = () => { fList.hidden = true; fList.innerHTML = ''; fIn.setAttribute('aria-expanded', 'false'); pick = -1; };
    const choose = p => { close(); fIn.value = p.n; render(p.i, p); };
    const show = () => {
      const q = norm(fIn.value);
      if (!all || q.length < 2) return close();
      const hits = all.filter(p => norm(p.n + ' ' + p.b).includes(q)).slice(0, 7);
      if (!hits.length) {
        fList.innerHTML = '<li class="f-miss">We have not read that label yet. Paste the ingredient list below and we will explain it.</li>';
        fList.hidden = false; fIn.setAttribute('aria-expanded', 'true');
        return;
      }
      fList.innerHTML = hits.map((p, n) => `<li role="option" id="f-o${n}" tabindex="-1" data-n="${n}"><b>${esc(p.n)}</b><span>${esc(p.b)} · ${p.i.length} ingredients</span></li>`).join('');
      fList.querySelectorAll('li[data-n]').forEach(li => li.addEventListener('click', () => choose(hits[+li.dataset.n])));
      fList.hidden = false; fIn.setAttribute('aria-expanded', 'true'); pick = -1;
      fList._hits = hits;
    };
    fIn.addEventListener('input', () => { load().then(show); });
    fIn.addEventListener('keydown', ev => {
      const opts = fList.querySelectorAll('li[data-n]');
      if (!opts.length) return;
      if (ev.key === 'ArrowDown' || ev.key === 'ArrowUp') {
        ev.preventDefault();
        pick = (pick + (ev.key === 'ArrowDown' ? 1 : opts.length - 1)) % opts.length;
        opts.forEach((o, i) => o.classList.toggle('on', i === pick));
        fIn.setAttribute('aria-activedescendant', 'f-o' + pick);
      } else if (ev.key === 'Enter') {
        ev.preventDefault();
        choose(fList._hits[pick < 0 ? 0 : pick]);
      } else if (ev.key === 'Escape') { close(); }
    });
    document.addEventListener('click', ev => { if (!fIn.contains(ev.target) && !fList.contains(ev.target)) close(); });
  }

  document.getElementById('paste').addEventListener('submit', ev => {
    ev.preventDefault();
    const items = split(ta.value);
    if (!items.length) { ta.focus(); return; }
    render(items, null);
    nameEl.textContent = 'Your label';
    dotsBox.innerHTML = rows.map(([k]) => `<button type="button" class="dot2" data-k="${k}" aria-label="${esc(GN[k][1])}"></button>`).join('');
    cap.innerHTML = `<small>Your label</small><b>${seen.size} of ${items.length} ingredients explained</b><p>Tap a group below, or a dotted word, to read more. We add ingredients every week.</p>`;
    keys = rows.map(r => r[0]);
    dotsBox.querySelectorAll('button').forEach((b, i) => b.addEventListener('click', () => setStep(i)));
    reset.hidden = false; card.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'nearest' });
  });
  reset.addEventListener('click', () => {
    card.classList.remove('mine'); ta.value = '';
    wordsEl.innerHTML = example.words; groupsEl.innerHTML = example.groups; foot.innerHTML = example.foot; nameEl.innerHTML = example.name; dotsBox.innerHTML = example.dots; chk.innerHTML = example.chk; wireLite();
    reset.hidden = true; guided();
  });
  guided();
})();

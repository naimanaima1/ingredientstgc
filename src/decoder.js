// The full Label Decoder (/label-decoder/): one label broken down, or two or three compared.
// Also the engine for the homepage's mini decoder (src/mini.js); the page sets window.DX_ROOT.
// window.DX (written by scripts/decoder.py): keys, rows [slug, title, what, cats, inci], cats, fams, rules, quick.
(function () {
  const D = window.DX;
  const ROOT = window.DX_ROOT || '';
  const norm = s => s.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const PREFIX = /^(organic|certified organic|deionized|distilled|purified|pure|raw|natural|unrefined)\s+/i;
  const CAT = {}; D.cats.forEach((c, i) => { CAT[c[0]] = { k: c[0], n: c[1], f: c[2], d: c[3], i }; });
  const FAM = {}; D.fams.forEach(f => { FAM[f[0]] = { k: f[0], n: f[1], d: f[2] }; });
  const RULES = D.rules.map(([c, p, u]) => [c, new RegExp(p), u ? new RegExp(u) : null]);
  // A broad category is dropped when a finer one of the same kind was found.
  const GENERIC = { cond: ['quat', 'fatty', 'silicone'], cleanser: ['sulfate', 'strong', 'mild', 'cosurf'], oil: ['butter', 'wax', 'ester', 'mineral'] };
  const FLAGS = new Set(['peg', 'coconut', 'gluten', 'ethanolamine']);

  function lookup(t) {
    t = t.trim().replace(/^\*+|\*+$/g, '').trim();
    let tries = [t, t.replace(/\(.*?\)/g, ''), t.replace(/\s*\(.*?\)\s*/g, ' ')];
    const m = t.match(/\((.*?)\)/); if (m) tries.push(m[1]);
    tries.slice().forEach(x => { if (x.includes('/')) tries = tries.concat(x.split('/')); });
    tries.slice().forEach(x => tries.push(x.trim().replace(PREFIX, '')));
    for (const x of tries) { const hit = D.keys[norm(x)]; if (hit !== undefined) return D.rows[hit]; }
    return null;
  }
  function split(L) {
    L = L.replace(/(^|[^\w-])(\d),\s+(\d)-/g, '$1$2,$3-').replace(/^\s*(ingredients?|inci)\s*:\s*/i, '');
    const out = []; let depth = 0, cur = '';
    for (let i = 0; i < L.length; i++) {
      const c = L[i];
      if (c === '(' || c === '[') depth++; if (c === ')' || c === ']') depth = Math.max(0, depth - 1);
      if ((c === ',' || c === ';' || c === '\n' || c === '•') && depth === 0 && !/\d/.test(L[i + 1] || '')) { out.push(cur); cur = ''; } else cur += c;
    }
    out.push(cur);
    return out.map(t => t.replace(/\*.*$/, '').replace(/\s+/g, ' ').trim().replace(/\.$/, '').replace(/^(and|or)\s+/i, '')).filter(t => t.length > 1);
  }
  function classify(t) {
    const r = lookup(t);
    const names = [norm(t), norm(t.replace(/\(.*?\)/g, ''))];
    const m = t.match(/\((.*?)\)/); if (m) names.push(norm(m[1]));
    t.split('/').forEach(x => names.push(norm(x)));
    if (r) names.push(norm(r[4]), norm(r[1]));
    const set = new Set(r ? r[3] : []);
    for (const [c, re, un] of RULES) {
      for (const n of names) { if (n && re.test(n) && !(un && un.test(n))) { set.add(c); break; } }
    }
    if (['sil-water', 'sil-light', 'sil-amino'].some(c => set.has(c))) set.add('silicone');
    if (['paraben', 'formaldehyde', 'isothiazolinone'].some(c => set.has(c))) set.add('preserv');
    if (set.has('essential')) set.delete('oil'); // rosemary oil reads as scent, not a softening oil
    for (const g in GENERIC) if (set.has(g) && GENERIC[g].some(x => set.has(x))) set.delete(g);
    const cats = [...set].filter(c => CAT[c]).sort((a, b) => CAT[a].i - CAT[b].i);
    const main = cats.find(c => !FLAGS.has(c)) || cats[0];
    return { t, r, cats, fam: main ? CAT[main].f : null };
  }
  const read = items => items.map((t, n) => Object.assign(classify(t), { n: n + 1 }));

  function note(x) {
    const bits = [];
    const nm = norm(x.t);
    if (x.cats.includes('paraben')) {
      const kind = /(isopropyl|isobutyl|phenyl|benzyl|pentyl) ?paraben/.test(nm) ? 'banned' : /(propyl|butyl) ?paraben/.test(nm) ? 'capped' : /(methyl|ethyl) ?paraben/.test(nm) ? 'ok' : null;
      if (kind) bits.push(D.paraben[kind]);
    }
    if (x.cats.includes('phthalate')) bits.push(/(dibutyl|diethylhexyl|benzyl butyl|diisobutyl) phthalate/.test(nm) ? 'Banned in cosmetics in the EU.' : 'Some phthalates are banned in cosmetics in the EU; rules differ for each one.');
    ['formaldehyde', 'isothiazolinone', 'allergen', 'drying', 'strong', 'sulfate'].forEach(c => { if (x.cats.includes(c) && x.r) bits.push(CAT[c].d); });
    return bits;
  }
  const label = x => x.r ? `<a href="${ROOT}${x.r[0]}/">${esc(x.t)}</a>` : esc(x.t);
  const chips = x => x.cats.length ? x.cats.map(c => `<span class="dx-chip f-${CAT[c].f}">${esc(CAT[c].n)}</span>`).join('') : '<span class="dx-chip dx-unsorted">Not sorted yet</span>';

  // ---------- one label ----------
  const $ = id => document.getElementById(id);
  let out, ta;
  let current = null; // {name, slug, items}

  function focus(cat, fam) {
    const words = $('dx-words');
    words.classList.toggle('dx-focus', !!(cat || fam));
    words.querySelectorAll('li').forEach(li => {
      const cs = li.dataset.c.split(' ');
      li.classList.toggle('lit', !!(cat ? cs.includes(cat) : fam && li.dataset.f === fam));
    });
    document.querySelectorAll('[data-hl]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.hl === cat)));
    document.querySelectorAll('.dx-fam').forEach(b => b.setAttribute('aria-pressed', String(!cat && b.dataset.f === fam)));
  }

  function breakdown(items, src) {
    const xs = read(items);
    current = { name: src ? src.n : null, slug: src ? src.s : null, items };
    const lib = xs.filter(x => x.r).length, sorted = xs.filter(x => x.cats.length).length;
    $('dx-sum').innerHTML = `<b>${src ? esc(src.n) : 'Your label'}</b><span>${xs.length} ingredients · ${lib} with a library page · ${sorted} sorted${xs.length - sorted ? ` · ${xs.length - sorted} not sorted yet` : ''}</span>`;
    const by = {};
    xs.forEach(x => x.cats.forEach(c => { (by[c] = by[c] || []).push(x); }));
    $('dx-quick').innerHTML = D.quick.map(c => {
      const hits = by[c] || [];
      return hits.length
        ? `<button type="button" class="dx-q is-yes" data-hl="${c}" aria-pressed="false"><b>${esc(CAT[c].n)}</b><span class="dx-state">Yes, ${hits.length}</span><small>${hits.map(x => esc(x.t)).join(', ')}</small></button>`
        : `<div class="dx-q is-no"><b>${esc(CAT[c].n)}</b><span class="dx-state">None found</span></div>`;
    }).join('');
    $('dx-words').innerHTML = xs.map(x => `<li data-c="${x.cats.join(' ')}" data-f="${x.fam || ''}" class="${x.fam ? 'f-' + x.fam : 'dx-none'}"><a href="#dx-r${x.n}" title="${esc(x.cats.map(c => CAT[c].n).join(', ') || 'Not sorted yet')}"><i>${x.n}</i>${esc(x.t)}</a></li>`).join('');
    $('dx-fams').innerHTML = D.fams.map(([f]) => {
      const cs = D.cats.filter(c => c[2] === f && by[c[0]]).map(c => c[0]);
      if (!cs.length) return '';
      return `<div class="dx-fcard"><h3><i class="dx-sw f-${f}"></i>${esc(FAM[f].n)}</h3><p class="dx-fd">${esc(FAM[f].d)}</p><ul>${cs.map(c => `<li><button type="button" class="dx-cat" data-hl="${c}" aria-pressed="false"><b>${esc(CAT[c].n)}</b> <span>${by[c].length}</span></button><p>${by[c].map(x => `${label(x)} <small>#${x.n}</small>`).join(', ')}</p></li>`).join('')}</ul></div>`;
    }).join('');
    $('dx-rows').innerHTML = xs.map(x => {
      const what = x.r && x.r[2] ? x.r[2] : x.cats.length ? CAT[x.cats.find(c => !FLAGS.has(c)) || x.cats[0]].d : 'Not in our library yet, and we could not sort it by its name.';
      const extra = note(x).map(b => `<span class="dx-note">${esc(b)}</span>`).join('');
      return `<tr id="dx-r${x.n}"><td class="dx-n">${x.n}</td><th scope="row">${label(x)}</th><td>${chips(x)}</td><td>${esc(what)}${extra}</td></tr>`;
    }).join('');
    out.hidden = false;
    $('dx-clear').hidden = false;
    out.querySelectorAll('[data-hl]').forEach(b => b.addEventListener('click', () => focus(b.getAttribute('aria-pressed') === 'true' ? null : b.dataset.hl, null)));
    focus(null, null);
    out.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
    window.tgcTrack && tgcTrack('decoder_breakdown', { ingredients: xs.length, product: src ? src.n : '' });
  }

  // ---------- products we have read ----------
  let all = null, loading = null;
  const load = () => loading = loading || fetch(ROOT + 'data/find.json').then(r => r.json()).then(j => (all = j)).catch(() => (all = []));
  function finder(input, list, onPick) {
    let pick = -1, hits = [];
    const close = () => { list.hidden = true; list.innerHTML = ''; input.setAttribute('aria-expanded', 'false'); pick = -1; };
    const choose = p => { close(); input.value = p.n; onPick(p); };
    const show = () => {
      const q = norm(input.value);
      if (!all || q.length < 2) return close();
      hits = all.filter(p => norm(p.n + ' ' + p.b).includes(q)).slice(0, 7);
      list.innerHTML = hits.length
        ? hits.map((p, n) => `<li role="option" id="${list.id}-o${n}" data-n="${n}"><b>${esc(p.n)}</b><span>${esc(p.b)} · ${p.i.length} ingredients</span></li>`).join('')
        : '<li class="f-miss">We have not read that label yet. Paste its ingredient list instead.</li>';
      list.querySelectorAll('li[data-n]').forEach(li => li.addEventListener('click', () => choose(hits[+li.dataset.n])));
      list.hidden = false; input.setAttribute('aria-expanded', 'true'); pick = -1;
    };
    input.addEventListener('focus', load);
    input.addEventListener('input', () => load().then(show));
    input.addEventListener('keydown', ev => {
      const opts = list.querySelectorAll('li[data-n]');
      if (ev.key === 'Escape') return close();
      if (!opts.length) return;
      if (ev.key === 'ArrowDown' || ev.key === 'ArrowUp') {
        ev.preventDefault();
        pick = (pick + (ev.key === 'ArrowDown' ? 1 : opts.length - 1)) % opts.length;
        opts.forEach((o, i) => o.classList.toggle('on', i === pick));
        input.setAttribute('aria-activedescendant', `${list.id}-o${pick}`);
      } else if (ev.key === 'Enter') { ev.preventDefault(); choose(hits[pick < 0 ? 0 : pick]); }
    });
    document.addEventListener('click', ev => { if (!input.contains(ev.target) && !list.contains(ev.target)) close(); });
  }

  // ---------- compare ----------
  const METRICS = [
    ['Water binders', ['humectant']],
    ['Protein', ['protein', 'amino', 'peptide']],
    ['Ceramides and lipids', ['lipid']],
    ['Bond builders', ['bond']],
    ['Oils', ['oil']],
    ['Butters', ['butter']],
    ['Light emollients (esters)', ['ester']],
    ['Waxes, mineral oil and petrolatum', ['wax', 'mineral']],
    ['Slip and conditioning', ['quat', 'fatty', 'silicone', 'cond']],
    ['Silicones', ['silicone']],
    ['Hold', ['film']],
    ['Scalp ingredients', ['scalp']],
    ['Drying alcohols', ['drying']],
    ['Fragrance, allergens and essential oils', ['fragrance', 'allergen', 'essential']],
    ['Preservatives', ['preserv']],
  ];
  const CLEAN = [['sulfate', 'Sulfate'], ['strong', 'Strong non-sulfate'], ['mild', 'Mild'], ['cleanser', 'Cleanser'], ['cosurf', 'Co-cleansers only']];
  const slots = [];
  const NAMES = ['A', 'B', 'C'];

  function addSlot(init) {
    if (slots.length >= 3) return;
    const k = slots.length, box = document.createElement('div');
    box.className = 'dx-slot';
    box.innerHTML = `<h3>Label ${NAMES[k]}</h3>
      <div class="finder"><label for="cs-f${k}">Pick a product</label><input id="cs-f${k}" type="text" autocomplete="off" role="combobox" aria-expanded="false" aria-controls="cs-l${k}" placeholder="Start typing"><ul class="f-list" id="cs-l${k}" role="listbox" hidden></ul></div>
      <label for="cs-t${k}">Or paste the ingredient list</label><textarea id="cs-t${k}" rows="4" placeholder="Water, Glycerin, …"></textarea>
      <button type="button" class="link-btn dx-slot-clear">Clear this label</button>`;
    $('dx-slots').appendChild(box);
    const s = { name: '', slug: '', input: box.querySelector('input'), ta: box.querySelector('textarea') };
    finder(s.input, box.querySelector('ul'), p => { s.name = p.n; s.slug = p.s; s.ta.value = p.i.join(', '); });
    s.ta.addEventListener('input', () => { if (s.slug) { s.slug = ''; s.name = ''; s.input.value = ''; } });
    s.clear = () => { s.ta.value = ''; s.input.value = ''; s.name = ''; s.slug = ''; };
    box.querySelector('.dx-slot-clear').addEventListener('click', () => { s.clear(); s.input.focus(); });
    if (init) { s.ta.value = init.t || ''; s.name = init.n || ''; s.slug = init.s || ''; s.input.value = init.n || ''; }
    slots.push(s);
    $('dx-add').hidden = slots.length >= 3;
  }

  function stat(xs, cs) {
    const hit = xs.filter(x => x.cats.some(c => cs.includes(c)));
    return { count: hit.length, first: hit.length ? hit[0].n : null, hit };
  }
  function cleanser(xs) {
    for (let i = 0; i < CLEAN.length; i++) {
      const hit = xs.filter(x => x.cats.includes(CLEAN[i][0]));
      if (hit.length) return { rank: CLEAN.length - i, label: CLEAN[i][1], hit };
    }
    return { rank: 0, label: 'None', hit: [] };
  }
  function lineFor(name, st, labels) {
    const counts = st.map(s => s.count);
    if (counts.every(c => c === 0)) return labels.length === 2 ? 'Neither has any.' : 'None of them has any.';
    const max = Math.max(...counts), top = st.map((s, i) => i).filter(i => counts[i] === max);
    if (top.length === 1) {
      const rest = st.map((s, i) => i !== top[0] ? `${s.count}` : null).filter(Boolean).join(' and ');
      return `${labels[top[0]]} has more (${max} vs ${rest}).`;
    }
    const firsts = top.map(i => st[i].first || 999), best = Math.min(...firsts), lead = top.filter(i => (st[i].first || 999) === best);
    return lead.length === 1 ? `Same count; ${labels[lead[0]]}'s first one sits higher up the list (#${best}).` : 'About the same.';
  }

  function compare() {
    const used = slots.map((s, i) => ({ s, i, items: split(s.ta.value) })).filter(u => u.items.length);
    if (used.length < 2) { (slots.find(s => !split(s.ta.value).length) || slots[0]).input.focus(); return; }
    const labels = used.map(u => u.s.name || `Label ${NAMES[u.i]}`);
    const reads = used.map(u => read(u.items));
    const head = `<thead><tr><th scope="col"></th>${labels.map(l => `<th scope="col">${esc(l)}</th>`).join('')}</tr></thead>`;
    const cell = (s, more) => `<td class="${more ? 'dx-more' : ''}"><b>${s.count}</b>${s.first ? `<small>first at #${s.first}</small>` : ''}${s.hit.length ? `<p>${s.hit.map(x => esc(x.t)).join(', ')}</p>` : ''}</td>`;
    let rows = `<tr><th scope="row">Ingredients</th>${reads.map(xs => `<td><b>${xs.length}</b><small>${xs.filter(x => x.cats.length).length} sorted</small></td>`).join('')}</tr>`;
    const cl = reads.map(cleanser), maxRank = Math.max(...cl.map(c => c.rank));
    const clLine = maxRank === 0 ? (labels.length === 2 ? 'Neither has a cleanser.' : 'None of them has a cleanser.') : cl.filter(c => c.rank === maxRank).length === 1 ? `${labels[cl.findIndex(c => c.rank === maxRank)]} has the stronger cleanser.` : 'Their strongest cleansers are the same kind.';
    rows += `<tr><th scope="row">Strongest cleanser<span class="dx-line">${esc(clLine)}</span></th>${cl.map(c => `<td class="${c.rank === maxRank && maxRank && cl.filter(x => x.rank === maxRank).length === 1 ? 'dx-more' : ''}"><b>${esc(c.label)}</b>${c.hit.length ? `<small>first at #${c.hit[0].n}</small><p>${c.hit.map(x => esc(x.t)).join(', ')}</p>` : ''}</td>`).join('')}</tr>`;
    METRICS.forEach(([name, cs]) => {
      const st = reads.map(xs => stat(xs, cs));
      const max = Math.max(...st.map(s => s.count)), sole = st.filter(s => s.count === max).length === 1;
      rows += `<tr><th scope="row">${esc(name)}<span class="dx-line">${esc(lineFor(name, st, labels))}</span></th>${st.map(s => cell(s, sole && s.count === max && max > 0)).join('')}</tr>`;
    });
    $('dx-ctable').innerHTML = head + `<tbody>${rows}</tbody>`;
    $('dx-cmp-out').hidden = false;
    $('dx-cmp-out').scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
    history.replaceState(null, '', '#compare=' + used.map(u => encodeURIComponent(u.s.slug ? 'p:' + u.s.slug : 't:' + u.items.join(', '))).join('~'));
    window.tgcTrack && tgcTrack('decoder_compare', { labels: used.length });
  }

  // ---------- page wiring ----------
  function tab(which) {
    const one = which === 'one';
    $('tab-one').setAttribute('aria-selected', String(one)); $('tab-cmp').setAttribute('aria-selected', String(!one));
    $('dx-one').hidden = !one; $('dx-cmp').hidden = one;
  }

  function init() {
    out = $('dx-out'); ta = $('dx-t');
    $('tab-one').addEventListener('click', () => tab('one'));
    $('tab-cmp').addEventListener('click', () => tab('cmp'));
    $('dx-form').addEventListener('submit', ev => {
      ev.preventDefault();
      const items = split(ta.value);
      if (!items.length) return ta.focus();
      breakdown(items, null);
      history.replaceState(null, '', '#t=' + encodeURIComponent(items.join(', ')));
    });
    $('dx-ex').addEventListener('click', () => { ta.value = window.DX_EXAMPLE; $('dx-form').requestSubmit(); });
    finder($('dx-f'), $('dx-fl'), p => { ta.value = p.i.join(', '); breakdown(p.i, p); history.replaceState(null, '', '#p=' + encodeURIComponent(p.s)); });
    document.querySelectorAll('.dx-fam').forEach(b => b.addEventListener('click', () => focus(null, b.getAttribute('aria-pressed') === 'true' ? null : b.dataset.f)));
    $('dx-copy').addEventListener('click', () => navigator.clipboard.writeText(location.href).then(() => { $('dx-copy').textContent = 'Link copied'; }));
    $('dx-add').addEventListener('click', () => addSlot());
    $('dx-cmp-go').addEventListener('click', compare);
    $('dx-clear').addEventListener('click', () => {
      ta.value = ''; $('dx-f').value = ''; out.hidden = true; $('dx-clear').hidden = true; current = null;
      history.replaceState(null, '', location.pathname); ta.focus();
      window.scrollTo({ top: 0, behavior: 'auto' });
    });
    $('dx-cmp-clear').addEventListener('click', () => {
      while (slots.length > 2) { slots.pop(); $('dx-slots').lastElementChild.remove(); }
      slots.forEach(s => s.clear());
      $('dx-add').hidden = false; $('dx-cmp-out').hidden = true;
      history.replaceState(null, '', location.pathname + '#compare'); slots[0].input.focus();
    });

    // Links in: #t=<list>, #p=<product>, #compare=p:slug~t:list
    const h = location.hash.slice(1), [key, val] = [h.split('=')[0], decodeURIComponent(h.slice(h.indexOf('=') + 1))];
    if (key === 'compare') {
      tab('cmp');
      load().then(() => {
        h.slice(8).split('~').filter(Boolean).forEach(part => {
          const v = decodeURIComponent(part), p = v.startsWith('p:') && all.find(x => x.s === v.slice(2));
          addSlot(p ? { t: p.i.join(', '), n: p.n, s: p.s } : { t: v.replace(/^t:/, '') });
        });
        const any = slots.length;
        while (slots.length < 2) addSlot();
        if (any) compare();
      });
    } else {
      addSlot(); addSlot();
      if (key === 't' && val) { ta.value = val; breakdown(split(val), null); }
      if (key === 'p' && val) load().then(() => { const p = all.find(x => x.s === val); if (p) { ta.value = p.i.join(', '); $('dx-f').value = p.n; breakdown(p.i, p); } });
    }
  }

  window.DX_CORE = { split, classify, read, cleanser, stat, finder, CAT, FAM };
  if (typeof document !== 'undefined' && document.getElementById('dx-form')) init();
})();

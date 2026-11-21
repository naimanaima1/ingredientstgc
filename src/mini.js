// Homepage mini decoder: the same engine as /label-decoder/ (assets/decoder.js, window.DX_CORE),
// on a smaller scale. Opens on a real example; six quick checks highlight words on the label;
// links carry the label into the full breakdown and compare.
(function () {
  const C = window.DX_CORE, ROOT = window.DX_ROOT || '';
  if (!C) return;
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const $ = id => document.getElementById(id);
  const CHECKS = [
    ['Water binders', ['humectant']],
    ['Oils and butters', ['oil', 'butter']],
    ['Protein', ['protein', 'amino', 'peptide']],
    ['Silicones', ['silicone']],
    ['Cleanser', null],
    ['Fragrance', ['fragrance', 'allergen', 'essential']],
  ];
  let xs = [];

  function light(i) {
    const words = $('mini-words'), on = i !== null;
    words.classList.toggle('on', on);
    const cs = on ? CHECKS[i][1] : null;
    words.querySelectorAll('.mini-w').forEach(w => {
      const c = w.dataset.c.split(' ');
      w.classList.toggle('lit', on && (cs ? cs.some(x => c.includes(x)) : ['sulfate', 'strong', 'mild', 'cosurf', 'cleanser'].some(x => c.includes(x))));
    });
    $('mini-q').querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(+b.dataset.i === i)));
  }

  function render(items, src, example) {
    xs = C.read(items);
    $('mini-tag').textContent = example ? 'Example' : src ? 'Product' : 'Pasted list';
    $('btl-name').innerHTML = src ? `<a href="${ROOT}products/${src.s}/">${esc(src.n)}</a>` : 'Your label';
    $('mini-q').innerHTML = CHECKS.map(([name, cs], i) => {
      let yes, val;
      if (!cs) { const c = C.cleanser(xs); yes = c.rank > 0; val = c.label; }
      else { const s = C.stat(xs, cs); yes = s.count > 0; val = yes ? `Yes · ${s.count}` : 'No'; }
      return yes
        ? `<button type="button" class="mini-chip is-yes" data-i="${i}" aria-pressed="false"><b>${esc(name)}</b><span>${esc(val)}</span></button>`
        : `<span class="mini-chip is-no"><b>${esc(name)}</b><span>${esc(val === 'None' ? 'None' : 'No')}</span></span>`;
    }).join('');
    $('mini-words').innerHTML = xs.map(x => `<span class="mini-w ${x.fam ? 'f-' + x.fam : 'dx-none'}" data-c="${x.cats.join(' ')}" title="${esc(x.cats.map(c => C.CAT[c].n).join(', ') || 'Not sorted yet')}">${esc(x.t)}</span>`).join(' ');
    const sorted = xs.filter(x => x.cats.length).length;
    $('mini-foot').textContent = `${sorted} of ${xs.length} ingredients sorted. Tap a check to see them on the label.`;
    const key = src ? 'p:' + src.s : 't:' + items.join(', ');
    $('mini-full').href = ROOT + 'label-decoder/' + (src ? '#p=' + encodeURIComponent(src.s) : '#t=' + encodeURIComponent(items.join(', ')));
    $('mini-cmp').href = ROOT + 'label-decoder/#compare=' + encodeURIComponent(key);
    $('mini-q').querySelectorAll('button').forEach(b => b.addEventListener('click', () => light(b.getAttribute('aria-pressed') === 'true' ? null : +b.dataset.i)));
    light(null);
  }

  // tabs: find a product, or paste a list
  const tabs = [['mt-find', 'mp-find'], ['mt-paste', 't-form']];
  tabs.forEach(([t]) => $(t).addEventListener('click', () => {
    tabs.forEach(([t2, p2]) => { $(t2).setAttribute('aria-selected', String(t2 === t)); $(p2).hidden = t2 !== t; });
    (t === 'mt-find' ? $('tf') : $('tt')).focus();
  }));

  C.finder($('tf'), $('tf-list'), p => {
    render(p.i, p, false);
    window.tgcTrack && tgcTrack('label_lookup', { product: p.n, brand: p.b });
    if (matchMedia('(max-width: 760px)').matches) $('card').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
  $('t-form').addEventListener('submit', ev => {
    ev.preventDefault();
    const items = C.split($('tt').value);
    if (!items.length) return $('tt').focus();
    render(items, null, false);
    window.tgcTrack && tgcTrack('label_pasted', { ingredients: items.length });
    if (matchMedia('(max-width: 760px)').matches) $('card').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  const ex = window.MINI_EXAMPLE;
  if (ex) render(ex.i, ex, true);
})();

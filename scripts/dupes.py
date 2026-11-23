"""Dupe pages: one page per much-searched product, at /dupes/<slug>/, listing the catalog products whose
labels come closest to it. Built every night from the catalog, like the rest of the site.

Two lists on each page:
  Closest wash     same cleanser strength, then the most shared cleansers, weighted toward the top of
                   both labels (the cleanser decides how a shampoo washes).
  Closest overall  the most of the five Similar labels checks the same (scripts/similar.py).

To add a page, add a line to PAGES: the words that find the product (brand and name, any case) and
the address. A product that isn't in the catalog, or has no label yet, gets no page.
"""
import build as B
import similar as SIM

e = B.e

PAGES = [
    {'find': 'cecred hydrating shampoo', 'slug': 'cecred-hydrating-shampoo'},
]
SHOW = 3

CLEAN = {'sulfate', 'strong', 'mild', 'cosurf', 'cleanser'}


def _find(prods, words):
    want = B.norm(words.replace('é', 'e'))
    for p in prods:
        have = B.norm(B.product_full_name(p).replace('é', 'e').replace('É', 'E'))
        if want in have:
            return p
    return None


def _cleansers(prof):
    """[(position, word)] for every cleanser on the label, in order."""
    return [(i + 1, t) for i, (t, c) in enumerate(prof['read']) if c & CLEAN]


def _wash_score(a, b):
    wa = {B.norm(SIM.short(t)): 1 / pos for pos, t in _cleansers(a)}
    wb = {B.norm(SIM.short(t)): 1 / pos for pos, t in _cleansers(b)}
    score = sum(min(wa[k], wb[k]) for k in wa.keys() & wb.keys())
    if a['kind'] and a['kind'] == b['kind']:
        score += 1
    return score


def _shared_cleansers(a, b):
    nb = {B.norm(SIM.short(t)) for _, t in _cleansers(b)}
    return [t for _, t in _cleansers(a) if B.norm(SIM.short(t)) in nb]


def _lineup(prof):
    cl = _cleansers(prof)
    return ', '.join(f'{SIM.short(t)} (#{pos})' for pos, t in cl[:4]) + (' and more' if len(cl) > 4 else '') if cl else 'no cleanser'


def _built_on(prof):
    """Plain lines on what the target's label is built on."""
    lines = []
    for key, thing, cats in SIM.DIMS['cleanse'][1:]:
        bd, pos, words = SIM.band(prof, cats)
        if bd == 'none':
            lines.append(f"<b>{e(thing.capitalize())}:</b> none.")
        else:
            where = 'near the top' if bd == 'lead' else 'lower down'
            lines.append(f"<b>{e(thing.capitalize())}:</b> {e(SIM._names(words))}, {where} (from #{pos}).")
    return lines


def _card(target, prof, q, rows, extra, r, badge=None):
    lis = ''.join(f'<li class="{"same" if s else "diff"}"><span class="sim-mark">{"Same" if s else "Different"}</span>{e(line)}</li>'
                  for s, line, _ in sorted(rows, key=lambda x: not x[0]))
    n = sum(1 for s, _, _ in rows if s)
    return f'''<li class="sim">
        <div class="sim-head"><a class="sim-name" href="{r}products/{q['_slug']}/"><b>{e(q.get('name', '').strip())}</b><span>{e(q.get('brand', '').strip())}</span></a><span class="sim-count">{e(badge or f'Same on {n} of {len(rows)}')}</span></div>
        {extra}
        <ul class="sim-why">{lis}</ul>
        <a class="sim-cmp" href="{r}label-decoder/#compare=p:{target['_slug']}~p:{q['_slug']}">Compare the two labels side by side <span aria-hidden="true">&#8594;</span></a>
      </li>'''


def build(prods, step_of, items_of):
    """Writes the pages; returns {product id: page path} for the pages written."""
    made = {}
    for spec in PAGES:
        target = _find(prods, spec['find'])
        if not target or len(items_of(target)) < SIM.MIN_ITEMS:
            print(f"Dupe page skipped: {spec['find']} (not in the catalog or no label yet)")
            continue
        step = step_of(target)
        a = SIM.profile(target, items_of(target))
        cands = []
        for q in prods:
            its = items_of(q)
            if q is target or step_of(q) != step or len(its) < SIM.MIN_ITEMS:
                continue
            b = SIM.profile(q, its)
            rows = SIM.compare(a, b, step)
            if step == 'cleanse' and not rows[0][0]:
                continue  # a different cleanser strength is never a dupe for a shampoo
            n = sum(1 for s, _, _ in rows if s)
            cands.append({'q': q, 'b': b, 'rows': rows, 'n': n, 'wash': _wash_score(a, b), 'close': SIM._closeness(a, b)})
        if not cands:
            print(f"Dupe page skipped: {spec['find']} (nothing close enough yet)")
            continue
        r = '../../'
        wash = sorted(cands, key=lambda c: (-c['wash'], -c['n'], c['q'].get('name', '').lower()))[:SHOW]
        overall = sorted(cands, key=lambda c: (-c['n'], -c['close'], c['q'].get('name', '').lower()))[:SHOW]
        wash_cards = ''.join(_card(target, a, c['q'], c['rows'],
                                   f'<p class="dupe-line"><span>Cleansers on this label</span>{e(_lineup(c["b"]))}</p>', r,
                                   badge=(lambda k: f"{k} cleanser{'s' if k != 1 else ''} in common")(len(_shared_cleansers(a, c['b'])))) for c in wash)
        overall_cards = ''.join(_card(target, a, c['q'], c['rows'], '', r) for c in overall)
        name = B.product_full_name(target)
        short_name = target.get('name', '').strip()
        built = ''.join(f'<li>{line}</li>' for line in _built_on(a))
        body = f'''  <a class="crumb" href="{r}products/{target['_slug']}/">← {e(name)}</a>
  <section class="page-head">
    <span class="eyebrow"><span class="little-dot"></span>Similar labels</span>
    <h1>Looking for a {e(target.get('brand', '').strip())} {e(short_name)} dupe?</h1>
    <p>These {e(SIM.STEP_WORD.get(step, ('products', ''))[0])} in our catalog have labels built most like it, compared ingredient by ingredient. A similar label tells you what is in the bottle, not how it will feel on your hair, and no formula is an exact copy.</p>
  </section>
  <section class="section">
    <div class="intro"><span class="eyebrow">The original</span><h2>What its label is built on</h2><p>Cleansers set how a shampoo washes. Everything else shapes how hair feels after.</p></div>
    <ul class="dupe-built"><li><b>Cleansers:</b> {e(a['level'][1])}: {e(_lineup(a))}.</li>{built}</ul>
  </section>
  <section class="section" id="closest-wash">
    <div class="intro"><span class="eyebrow">Closest wash</span><h2>Washes most like it</h2><p>The same cleanser strength, then the most cleansers in common, counting most where they sit near the top of both labels.</p></div>
    <ul class="sim-list">{wash_cards}</ul>
  </section>
  <section class="section" id="closest-overall">
    <div class="intro"><span class="eyebrow">Closest overall</span><h2>Built most like it overall</h2><p>The same cleanser strength, then the most of five checks the same: cleanser, conditioning agents, water binders, protein and oils, each at about the same place on the label.</p></div>
    <ul class="sim-list">{overall_cards}</ul>
  </section>
  <p class="source"><span>Built from The Good Coil catalog and updated as we add labels. Brands change formulas, so check the label on your bottle. Prices aren't compared.</span><a href="{r}label-decoder/">Compare any two labels</a><a href="{r}about/">How we write these</a></p>'''
        path = f"dupes/{spec['slug']}/"
        desc = f"Products with labels built like {name}: closest wash and closest overall, compared ingredient by ingredient."
        B.write(path + 'index.html', B.shell(r, f"{name} dupes: similar labels compared · The Good Coil", desc, body, path, 'products'))
        made[target['id']] = path
    return made

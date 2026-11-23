"""Dupe pages: one page per much-searched product, at /dupes/<slug>/, comparing its label with the catalog.
Built every night from the catalog, like the rest of the site.

  Quick answer      the closest wash and the closest overall, up top
  Side by side      a table: each close match against the original on the five checks
  Closest wash      same cleanser strength, then the most cleansers in common, weighted toward the top
  Closest overall   the most of the five Similar labels checks the same (scripts/similar.py)
  Seen elsewhere    products other dupe lists name, checked here, with the reason when they don't match

Products not in the catalog yet can be added to a page by hand under 'extra' (brand, name, the label as
printed, where it came from). They are compared exactly like catalog products and marked as not in the
catalog yet. Add a page with a line in PAGES. A product with no label gets no page.
"""
import build as B
import similar as SIM

e = B.e

PAGES = [
    {
        'find': 'cecred hydrating shampoo',
        'slug': 'cecred-hydrating-shampoo',
        # The founder's note, in her words. Plain text; blank lines start new paragraphs. Leave '' for none.
        'note': (
            "I haven't tried Cécred myself, and I've been looking for a dupe too.\n\n"
            "Most dupe lists just name products. I wanted to see the labels side by side: which cleanser "
            "does the washing, what adds slip, where the moisture comes from. So that's what this page does.\n\n"
            "A close label is a good place to start. Your hair still gets the final say, so try one "
            "and keep notes on how your wash days go."
        ),
        'note_by': 'Founder, The Good Coil',
        'extra': [
            {'brand': 'Pacifica', 'name': 'Pineapple Curls Curl Defining Shampoo', 'source': 'pacificabeauty.com',
             'label': "Aqua (Eau), Sodium Lauroyl Methyl Isethionate, Cocamidopropyl Betaine, Sodium Cocoyl Isethionate, "
                      "Sodium Methyl Oleoyl Taurate, Cocamidopropyl Hydroxysultaine, Guar Hydroxypropyltrimonium Chloride, "
                      "Cocamide MIPA, Allantoin, Glycol Distearate, Argania Spinosa Kernel Oil, Olea Europaea (Olive) Fruit Oil, "
                      "Sodium Citrate, Citric Acid, Hydrolyzed Quinoa, Hydrolyzed Rice Protein, Carica Papaya (Fruit) Extract, "
                      "Ananas Sativus (Pineapple) Fruit Extract, Sodium Hyaluronate, Brassica Campestris/Aleurites Fordi Oil Copolymer, "
                      "Phenoxyethanol, Ethylhexylglycerin, Parfum"},
            {'brand': 'Pravana', 'name': 'Clear Cleanse Shampoo', 'source': 'pravana.com',
             'label': "Aqua (Water, Eau), Sodium C14-16 Olefin Sulfonate, Decyl Glucoside, Cocamidopropyl Betaine, "
                      "Dimethyl Lauramide/Myristamide, Phenoxyethanol, Sodium Benzoate, Parfum (Fragrance), Lactic Acid, Citric Acid, "
                      "Polyquaternium-10, Glycol Distearate, Polyquaternium-7, Laureth-4, Sodium Gluconate, Triolein, "
                      "Cetrimonium Chloride, Sodium Hydroxide, Coconut Acid, Sodium Chloride, Cocamidopropyl Dimethylamine, "
                      "Sodium Glycolate, Benzoic Acid, Sodium Hyaluronate, Tocopherol, Olus Oil (Vegetable Oil, Huile Végétale), "
                      "Linalool, Hexyl Cinnamal, Geraniol, CI 60730 (Ext. Violet 2), CI 42090 (Blue 1)"},
            {'brand': 'SEEN', 'name': 'Shampoo, Fragrance Free', 'source': 'helloseen.com',
             'label': "Water/Aqua/Eau, Sodium Lauroyl Methyl Isethionate, Cocamidopropylamine Oxide, Glycerin, Acrylates Copolymer, "
                      "C13-15 Alkane, Glycol Distearate, Aminomethyl Propanol, Guar Hydroxypropyltrimonium Chloride, Polyquaternium-7, "
                      "Tocopherol, Bisabolol, Trisodium Ethylenediamine Disuccinate, Citric Acid, Sodium Hydroxide, Phenoxyethanol, "
                      "Ethylhexylglycerin, Sodium Benzoate, Disodium EDTA"},
        ],
    },
]
SHOW = 3

CLEAN = {'sulfate', 'strong', 'mild', 'cosurf', 'cleanser'}
CHECK_SHORT = {'clean': 'Cleanser', 'cond': 'Conditioning', 'moist': 'Water binders', 'protein': 'Protein', 'oils': 'Oils'}


def _find(prods, words):
    want = B.norm(words.replace('é', 'e'))
    for p in prods:
        if want in B.norm(B.product_full_name(p).replace('é', 'e').replace('É', 'E')):
            return p
    return None


def _split(label):
    """Split a pasted label on commas that are not inside brackets."""
    out, depth, cur = [], 0, ''
    for ch in label:
        if ch in '([':
            depth += 1
        elif ch in ')]':
            depth = max(0, depth - 1)
        if ch == ',' and depth == 0:
            out.append(cur.strip())
            cur = ''
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip().rstrip('.'))
    return [t for t in out if t]


def _cleansers(prof):
    return [(i + 1, t) for i, (t, c) in enumerate(prof['read']) if c & CLEAN]


def _shared_cleansers(a, b):
    nb = {B.norm(SIM.short(t)) for _, t in _cleansers(b)}
    return [t for _, t in _cleansers(a) if B.norm(SIM.short(t)) in nb]


def _wash_score(a, b):
    wa = {B.norm(SIM.short(t)): 1 / pos for pos, t in _cleansers(a)}
    wb = {B.norm(SIM.short(t)): 1 / pos for pos, t in _cleansers(b)}
    score = sum(min(wa[k], wb[k]) for k in wa.keys() & wb.keys())
    if a['kind'] and a['kind'] == b['kind']:
        score += 1
    return score


def _lineup(prof, n=4):
    cl = _cleansers(prof)
    return ', '.join(f'{SIM.short(t)} (#{pos})' for pos, t in cl[:n]) + (' and more' if len(cl) > n else '') if cl else 'no cleanser'


def _name_html(c, r):
    q = c['q']
    name, brand = e(q.get('name', '').strip()), e(q.get('brand', '').strip())
    if c['extra']:
        return f'<span class="dupe-pname"><b>{name}</b><span>{brand} · not in our catalog yet</span></span>'
    return f'<a class="dupe-pname" href="{r}products/{q["_slug"]}/"><b>{name}</b><span>{brand}</span></a>'


def _why_lis(rows):
    return ''.join(f'<li class="{"same" if s else "diff"}"><span class="sim-mark">{"Same" if s else "Different"}</span>{e(line)}</li>'
                   for s, line, _ in sorted(rows, key=lambda x: not x[0]))


def _card(target, a, c, r, badge, lineup=False):
    q, b, rows = c['q'], c['b'], c['rows']
    note = SIM.cleanser_note(b)
    line = ''
    if lineup:
        line = f'<p class="dupe-line"><span>Cleansers on its label</span>{e(_lineup(b))}{(" " + e(note)) if note else ""}</p>'
    elif note:
        line = f'<p class="dupe-line"><span>About its cleanser</span>{e(note)}</p>'
    if c['extra']:
        foot = f'<p class="dupe-src">Label as listed on {e(c["extra"]["source"])}. We\'ll add it to the catalog after we check it against the packaging.</p>'
    else:
        foot = f'<a class="sim-cmp" href="{r}label-decoder/#compare=p:{target["_slug"]}~p:{q["_slug"]}">Compare the two labels side by side <span aria-hidden="true">&#8594;</span></a>'
    return f'''<li class="sim">
        <div class="sim-head">{_name_html(c, r)}<span class="sim-count">{e(badge)}</span></div>
        {line}
        <ul class="sim-why">{_why_lis(rows)}</ul>
        {foot}
      </li>'''


def _table(a, target, picks, r):
    """The side-by-side grid: one row per product, one column per check, words not just marks."""
    keys = [k for k, _, _ in SIM.DIMS['cleanse']]
    head = ''.join(f'<th scope="col">{e(CHECK_SHORT[k])}</th>' for k in keys)
    cats_of = {kk: cc for kk, _, cc in SIM.DIMS['cleanse']}

    def cell_ref(k):
        if k == 'clean':
            lvl = a['level'][1]
            return e((lvl[2:] if lvl.startswith('a ') else lvl).capitalize())
        bd, pos, _ = SIM.band(a, cats_of[k])
        return 'None' if bd == 'none' else f'From #{pos}'

    ref = ''.join(f'<td>{cell_ref(k)}</td>' for k in keys)
    rows = [f'<tr class="dupe-ref"><th scope="row"><b>{e(target.get("name", "").strip())}</b><span>{e(target.get("brand", "").strip())} · the original</span></th>{ref}</tr>']
    for c in picks:
        by = {k: s for s, _, k in c['rows']}
        cells = ''.join(f'<td class="{"same" if by.get(k) else "diff"}">{"Same" if by.get(k) else "Different"}</td>' for k in keys)
        q = c['q']
        nm = e(q.get('name', '').strip())
        link = nm if c['extra'] else f'<a href="{r}products/{q["_slug"]}/">{nm}</a>'
        rows.append(f'<tr><th scope="row"><b>{link}</b><span>{e(q.get("brand", "").strip())}</span></th>{cells}</tr>')
    return f'''<div class="dupe-table-wrap" role="region" aria-label="Side-by-side comparison" tabindex="0">
      <table class="dupe-table"><thead><tr><th scope="col">Shampoo</th>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table>
    </div>'''


def _else_why(a, c, orig):
    """One plain explanation of why a product named elsewhere washes differently."""
    ours = f"{orig} is built on {a['level'][1]}" + (f" ({SIM.short(a['main'])})" if a['main'] else '') + '.'
    note = SIM.cleanser_note(c['b'])
    who = SIM.label_name(c['q'])
    if note and note[0].isupper() and c['b']['level'][0] >= 2:
        return f"{ours} {who} is built on {note[0].lower()}{note[1:]}"
    theirs = f"{who} is built on {c['b']['level'][1]}" + (f" ({SIM.short(c['b']['main'])})" if c['b']['main'] else '') + '.'
    return f"{ours} {theirs}"


def _note(spec):
    text = (spec.get('note') or '').strip()
    if not text:
        return ''
    paras = ''.join(f'<p>{e(p.strip())}</p>' for p in text.split('\n\n') if p.strip())
    return f'''<aside class="dupe-note" aria-label="A note from our founder">
      <span class="eyebrow">A note from me</span>
      {paras}
      <p class="dupe-note-by">{e(spec.get('note_by', ''))}</p>
    </aside>'''


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
        pool = [(q, items_of(q), None) for q in prods if q is not target and step_of(q) == step]
        for x in spec.get('extra', []):
            q = {'id': 'X-' + B.norm(x['brand'] + ' ' + x['name']).replace(' ', '-'), 'brand': x['brand'], 'name': x['name']}
            pool.append((q, _split(x['label']), x))
        cands, elsewhere = [], []
        for q, its, extra in pool:
            if len(its) < SIM.MIN_ITEMS:
                continue
            b = SIM.profile(q, its)
            rows = SIM.compare(a, b, step)
            c = {'q': q, 'b': b, 'rows': rows, 'extra': extra, 'n': sum(1 for s, _, _ in rows if s),
                 'wash': _wash_score(a, b), 'close': SIM._closeness(a, b)}
            if step == 'cleanse' and not rows[0][0]:
                if extra:
                    elsewhere.append(c)   # named on other dupe lists, but built on a different cleanser
                continue
            cands.append(c)
        if not cands:
            print(f"Dupe page skipped: {spec['find']} (nothing close enough yet)")
            continue

        r = '../../'
        wash = sorted(cands, key=lambda c: (-c['wash'], -c['n'], c['q'].get('name', '').lower()))[:SHOW]
        overall = sorted(cands, key=lambda c: (-c['n'], -c['close'], c['q'].get('name', '').lower()))[:SHOW]
        picks = list({id(c): c for c in overall + wash}.values())
        orig = SIM.label_name(target)
        name = B.product_full_name(target)
        short_name = target.get('name', '').strip()
        brand = target.get('brand', '').strip()

        w0, o0 = wash[0], overall[0]
        shared = _shared_cleansers(a, w0['b'])
        same_first = B.norm(SIM.short(a['first'] or '')) == B.norm(SIM.short(w0['b']['first'] or ''))
        w_why = (f"Same main cleanser ({SIM.short(a['first'])})" if same_first
                 else f"Same kind of cleanser ({a['kind']})" if a['kind'] and a['kind'] == w0['b']['kind'] else 'Same cleanser strength')
        w_why += f", and {len(shared)} cleanser{'s' if len(shared) != 1 else ''} in common."
        o_diff = [line for s, line, _ in o0['rows'] if not s]
        o_why = f"The same as {orig} on {o0['n']} of {len(o0['rows'])} checks." + (f" The difference: {o_diff[0][0].lower() + o_diff[0][1:]}" if o_diff else '')

        def tile(label, c, why):
            q = c['q']
            title = e(q.get('name', '').strip())
            t = title if c['extra'] else f'<a href="{r}products/{q["_slug"]}/">{title}</a>'
            return f'''<div class="dupe-pick"><span class="dupe-pick-label">{e(label)}</span>
          <p class="dupe-pick-name">{t}</p><p class="dupe-pick-brand">{e(q.get('brand', '').strip())}{' · not in our catalog yet' if c['extra'] else ''}</p>
          <p class="dupe-pick-why">{e(why)}</p></div>'''

        if o0 is w0:
            # One product wins both: say so once, and give the second tile to the next closest.
            rest = [c for c in overall if c is not w0] + [c for c in wash if c is not w0]
            nxt = rest[0] if rest else None
            first = tile('Closest wash and closest overall', w0, f"{w_why} {o_why}")
            if nxt:
                d = [line for s_, line, _ in nxt['rows'] if not s_]
                why2 = f"The same as {orig} on {nxt['n']} of {len(nxt['rows'])} checks." + (f" The difference: {d[0][0].lower() + d[0][1:]}" if d else '')
                quick = first + tile('Next closest', nxt, why2)
            else:
                quick = first
        else:
            quick = tile('Closest wash', w0, w_why) + tile('Closest overall', o0, o_why)
        built = []
        for key, thing, cats in SIM.DIMS['cleanse'][1:]:
            bd, pos, words = SIM.band(a, cats)
            built.append(f"<li><b>{e(thing.capitalize())}</b>" + ('None' if bd == 'none' else
                         f"{e(SIM._names(words))}, {'near the top' if bd == 'lead' else 'lower down'} (from #{pos})") + '</li>')
        cnote = SIM.cleanser_note(a)
        built.insert(0, f"<li><b>Cleansers</b>{e(a['level'][1].capitalize())}: {e(_lineup(a))}.{(' ' + e(cnote)) if cnote else ''}</li>")

        def in_common(c):
            k = len(_shared_cleansers(a, c['b']))
            return f"{k} cleanser{'s' if k != 1 else ''} in common"

        wash_cards = ''.join(_card(target, a, c, r, in_common(c), lineup=True) for c in wash)
        overall_cards = ''.join(_card(target, a, c, r, f"Same on {c['n']} of {len(c['rows'])}") for c in overall)
        else_items = ''.join(f'''<li class="sim">
        <div class="sim-head">{_name_html(c, r)}<span class="sim-count sim-count-off">Different cleanser</span></div>
        <p class="dupe-else-why">{e(_else_why(a, c, orig))}</p>
        <p class="dupe-src">Label as listed on {e(c['extra']['source'])}.</p>
      </li>''' for c in elsewhere)
        else_sec = f'''<section class="section" id="seen-elsewhere">
    <div class="intro"><span class="eyebrow">Seen on other dupe lists</span><h2>Named elsewhere, built differently</h2><p>Other lists call these {e(brand)} dupes. We checked their labels the same way. They share ingredients with {e(orig)}, but the cleanser doing the washing is a different strength, so they're likely to wash differently.</p></div>
    <ul class="sim-list">{else_items}</ul>
  </section>''' if elsewhere else ''

        body = f'''  <div class="dupe-page">
  <a class="crumb" href="{r}products/{target['_slug']}/">← {e(name)}</a>
  <section class="page-head dupe-head">
    <span class="eyebrow"><span class="little-dot"></span>Dupe check</span>
    <h1>{e(brand)} {e(short_name)} dupes, checked against the label</h1>
    <p>We compared its ingredient list, cleanser first, with every shampoo in our catalog and the ones other dupe lists keep naming. Here's what comes closest, and what isn't the same.</p>
    <div class="dupe-quick">{quick}</div>
    <p class="dupe-quick-foot">No formula is an exact copy. A close label tells you what's in the bottle, not how it will feel on your hair.</p>
  </section>
  {_note(spec)}
  <section class="section" id="side-by-side">
    <div class="intro"><span class="eyebrow">Side by side</span><h2>How the closest ones compare</h2><p>Five checks, each against {e(orig)}. "Same" means both labels have it at about the same place: near the top, lower down, or not at all.</p></div>
    {_table(a, target, picks, r)}
  </section>
  <section class="section">
    <div class="intro"><span class="eyebrow">The original</span><h2>What {e(orig)}'s label is built on</h2><p>The cleanser sets how a shampoo washes. Everything after it shapes how your hair feels once you rinse.</p></div>
    <ul class="dupe-built">{''.join(built)}</ul>
  </section>
  <section class="section" id="closest-wash">
    <div class="intro"><span class="eyebrow">Closest wash</span><h2>Washes most like it</h2><p>Same cleanser strength first. Then the most cleansers in common, counting most where they sit near the top of both labels.</p></div>
    <ul class="sim-list">{wash_cards}</ul>
  </section>
  <section class="section" id="closest-overall">
    <div class="intro"><span class="eyebrow">Closest overall</span><h2>Built most like it overall</h2><p>Same cleanser strength first. Then the most of the five checks the same: cleanser, conditioning agents, water binders, protein and oils.</p></div>
    <ul class="sim-list">{overall_cards}</ul>
  </section>
  {else_sec}
  <section class="section dupe-cta">
    <div class="intro"><span class="eyebrow">Your turn</span><h2>Holding a different bottle?</h2><p>Paste any shampoo's ingredient list into the Label Decoder. It sorts every ingredient the same way this page does, and can put two labels side by side.</p></div>
    <p><a class="btn-cta" href="{r}label-decoder/">Open the Label Decoder <span aria-hidden="true">&#8594;</span></a></p>
  </section>
  <p class="source"><span>Built from The Good Coil catalog and updated as we add labels. Brands change formulas, so check the label on your bottle. Prices aren't compared.</span><a href="{r}about/">How we write these</a></p>
  </div>'''
        path = f"dupes/{spec['slug']}/"
        desc = f"{name} dupes, checked against the label: the closest wash, the closest overall, and why some popular picks wash differently."
        B.write(path + 'index.html', B.shell(r, f"{name} dupes, checked against the label · The Good Coil", desc, body, path, 'products'))
        made[target['id']] = path
    return made

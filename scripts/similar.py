"""Similar labels: for each product, the catalog products whose labels are built the same way.

Products are compared only with others at the same step (shampoo with shampoo), and only when both
labels have been read. Shampoos must also share the strength of their main cleanser. Each pair is compared on the five things that matter most for that step:

    cleanse:  main cleanser (how strong, which kind), conditioning agents, water binders, protein, oils
    others:   slip and conditioning, water binders, protein, oils and butters, silicones

Each one is either the same (both have it, or neither does; for the cleanser, the same strength) or
different. Matches are listed with the plain reasons, the differences included, never as a score out
of 100 and never as a verdict. Words are sorted with the Label Decoder's own categories (decoder.py:
sheet rows first, then RULES), so the decoder and this section always agree.

Prices are not used: catalog prices are not published (README).
"""
import re
import build as B
import decoder as DX

e = B.e

_RX = [(c, re.compile(p), re.compile(u) if u else None) for c, p, u in DX.RULES]
_GENERIC = {'cond': ['quat', 'fatty', 'silicone'], 'cleanser': ['sulfate', 'strong', 'mild', 'cosurf'],
            'oil': ['butter', 'wax', 'ester', 'mineral']}

MIN_ITEMS = 5          # a label shorter than this is too thin to compare
SHOW = 3               # matches shown on a product page
MIN_SAME = 3           # of 5: anything below is not "similar"


def classify(t):
    """The decoder's categories for one label word (mirrors classify() in src/decoder.js)."""
    r = B.lookup(t)
    names = [B.norm(t), B.norm(re.sub(r'\(.*?\)', '', t))]
    m = re.search(r'\((.*?)\)', t)
    if m:
        names.append(B.norm(m.group(1)))
    names += [B.norm(x) for x in t.split('/')]
    if r:
        names += [B.norm(r['inci_name']), B.norm(r['_title'])]
    cats = set(DX.lib_cats(r)) if r else set()
    for c, rx, un in _RX:
        for n in names:
            if n and rx.search(n) and not (un and un.search(n)):
                cats.add(c)
                break
    if cats & {'sil-water', 'sil-light', 'sil-amino'}:
        cats.add('silicone')
    if 'essential' in cats:
        cats.discard('oil')
    for g, fine in _GENERIC.items():
        if g in cats and cats & set(fine):
            cats.discard(g)
    return cats


# The kind of cleanser, for "the same kind" (more specific than the strength).
_KINDS = [('isethionate', 'isethionates'), ('taurate', 'taurates'), ('glucoside', 'glucosides'),
          ('sarcosinate', 'sarcosinates'), ('sulfosuccinate', 'sulfosuccinates'), ('ampho', 'amphoterics'),
          ('glutamate', 'glutamates'), ('glycinate', 'glycinates'), ('olefin sulfonate', 'olefin sulfonates'),
          ('sulfate', 'sulfates'), ('betaine', 'betaines'), ('sultaine', 'sultaines')]
_LEVEL = {'sulfate': (3, 'a sulfate'), 'strong': (2, 'a strong non-sulfate cleanser'), 'mild': (1, 'a mild cleanser'),
          'cosurf': (1, 'a mild cleanser')}


def kind_of(t):
    n = B.norm(t)
    for k, label in _KINDS:
        if k in n:
            return label
    return None


def short(t):
    """A label word without its bracketed translation: 'Butyrospermum Parkii (Shea) Butter' stays readable."""
    t = re.sub(r'\s*\((aqua|water|eau)\)\s*', ' ', t, flags=re.I)
    return re.sub(r'\s+', ' ', t).strip()


# Each dimension: key, the thing in plain words, categories that count.
DIMS = {
    'cleanse': [('clean', 'cleanser', None),
                ('cond', 'conditioning agents', {'quat', 'cond'}),
                ('moist', 'water binders', {'humectant'}),
                ('protein', 'protein', {'protein', 'peptide'}),
                ('oils', 'oils', {'oil', 'butter', 'ester', 'mineral', 'wax'})],
    'other': [('slip', 'slip and conditioning agents', {'quat', 'cond', 'fatty'}),
              ('moist', 'water binders', {'humectant'}),
              ('protein', 'protein', {'protein', 'peptide'}),
              ('oils', 'oils or butters', {'oil', 'butter', 'ester', 'mineral', 'wax'}),
              ('sil', 'silicones', {'silicone', 'sil-water', 'sil-light', 'sil-amino'})],
}


def profile(p, items):
    read = [(t, classify(t)) for t in items]
    main, level = None, (0, 'no cleanser')
    for want in ('sulfate', 'strong', 'mild', 'cosurf'):
        hit = next((t for t, c in read if want in c), None)
        if hit:
            main, level = hit, _LEVEL[want]
            break
    # The first cleanser on the label is the one there is most of; strength comes from the strongest.
    first = next((t for t, c in read if c & {'sulfate', 'strong', 'mild', 'cosurf', 'cleanser'}), None)
    return {'p': p, 'read': read, 'level': level, 'main': main, 'first': first,
            'kind': kind_of(first) if first else None}


def has(prof, cats):
    return [t for t, c in prof['read'] if c & cats]


def _names(ts):
    return ', '.join(short(t) for t in ts[:2]) + (' and more' if len(ts) > 2 else '')


def compare(a, b, step):
    """[(same, line)] for each dimension, written from page a's point of view ('this one' vs b's name)."""
    other = B.product_full_name(b['p'])
    out = []
    for key, thing, cats in DIMS['cleanse' if step == 'cleanse' else 'other']:
        if key == 'clean':
            la, lb = a['level'], b['level']
            same = la[0] == lb[0]
            if same and a['kind'] and a['kind'] == b['kind']:
                line = f"Same kind of main cleanser: both lead with {a['kind']} ({short(a['first'])} / {short(b['first'])})."
            elif same:
                line = f"Both are built on {la[1]} ({short(a['main'] or '')} / {short(b['main'] or '')})." if la[0] else 'Neither has a cleanser.'
            else:
                ma = f" ({short(a['main'])})" if a['main'] else ''
                mb = f" ({short(b['main'])})" if b['main'] else ''
                line = f"Different cleanser strength: this one is built on {la[1]}{ma}, {other} on {lb[1]}{mb}."
            out.append((same, line, key))
            continue
        ha, hb = has(a, cats), has(b, cats)
        if ha and hb:
            shared = [t for t in ha if B.norm(short(t)) in {B.norm(short(x)) for x in hb}]
            line = (f"Both have {thing}, including {_names(shared)}." if shared
                    else f"Both have {thing}, but different ones.")
            out.append((True, line, key))
        elif not ha and not hb:
            out.append((True, f"Neither has {thing}.", key))
        elif ha:
            out.append((False, f"Only this one has {thing} ({_names(ha)}).", key))
        else:
            out.append((False, f"Only {other} has {thing} ({_names(hb)}).", key))
    return out


def _closeness(a, b):
    """Tie-break inside the same count: shared ingredients, weighted toward the top of both labels."""
    wa = {B.norm(short(t)): 1 / (i + 1) for i, (t, _) in enumerate(a['read'])}
    wb = {B.norm(short(t)): 1 / (i + 1) for i, (t, _) in enumerate(b['read'])}
    score = sum(min(wa[k], wb[k]) for k in wa.keys() & wb.keys())
    if a['kind'] and a['kind'] == b['kind']:
        score += 1
    return score


def build_index(prods, step_of, items_of):
    """{product id: [(other product, [(same, line, key)], n_same, n_dims)]}, best first."""
    profs = {}
    for p in prods:
        st = step_of(p)
        its = items_of(p)
        if st and st != 'tool' and len(its) >= MIN_ITEMS:
            profs[p['id']] = (st, profile(p, its))
    out = {}
    for pid, (st, a) in profs.items():
        cands = []
        for qid, (st2, b) in profs.items():
            if qid == pid or st2 != st:
                continue
            rows = compare(a, b, st)
            n = sum(1 for s, _, _ in rows if s)
            # For a shampoo the cleanser decides the most: a different strength is never "similar".
            if st == 'cleanse' and not rows[0][0]:
                continue
            if n >= MIN_SAME:
                cands.append((n, _closeness(a, b), b['p'], rows))
        cands.sort(key=lambda c: (-c[0], -c[1], c[2].get('name', '').lower()))
        out[pid] = [(q, rows, n, len(rows)) for n, _, q, rows in cands[:SHOW]]
    return out


# (plural, singular) for the intro line.
STEP_WORD = {'cleanse': ('shampoos and cleansers', 'shampoo'), 'condition': ('conditioners', 'conditioner'),
             'treatment': ('treatments', 'treatment'), 'leave-in': ('leave-ins', 'leave-in'),
             'style': ('stylers', 'styler'), 'seal': ('oils and sealants', 'oil or sealant')}


def section(p, matches, step, r):
    """The 'Similar labels' section for one product page, or '' when nothing is close enough."""
    if not matches:
        return ''
    cards = []
    for q, rows, n, total in matches:
        lis = ''.join(f'<li class="{"same" if s else "diff"}"><span class="sim-mark">{"Same" if s else "Different"}</span>{e(line)}</li>'
                      for s, line, _ in sorted(rows, key=lambda x: not x[0]))
        cmp_href = f"{r}label-decoder/#compare=p:{p['_slug']}~p:{q['_slug']}"
        cards.append(f'''<li class="sim">
        <div class="sim-head"><a class="sim-name" href="{r}products/{q['_slug']}/"><b>{e(q.get('name', '').strip())}</b><span>{e(q.get('brand', '').strip())}</span></a><span class="sim-count">Same on {n} of {total}</span></div>
        <ul class="sim-why">{lis}</ul>
        <a class="sim-cmp" href="{cmp_href}">Compare the two labels side by side <span aria-hidden="true">&#8594;</span></a>
      </li>''')
    many, one = STEP_WORD.get(step, ('products', 'product'))
    return f'''<section class="section" id="similar">
    <div class="intro"><span class="eyebrow">Similar labels</span><h2>Built like this one</h2><p>Looking for a dupe? These {e(many)} in our catalog have labels built the same way, checked on the five things that matter most for a {e(one)}. A similar label says what is in the bottle, not how it will feel on your hair.</p></div>
    <ul class="sim-list">{''.join(cards)}</ul>
  </section>'''

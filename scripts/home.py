"""Homepage: a working label decoder with a guided walk-through of one real label, then three doors
(ingredients, products, hair plans). The example label and its groups are rendered in the HTML, so
the page reads fine without JavaScript; assets/library.js adds the walk-through and decoding.
"""
import json, re
import build as B

e = B.e

# Friendly groups, in the order a label is read. key, name, one-line explanation.
GROUPS = [
    ('base', 'The base', 'Water comes first', 'Most conditioners and leave-ins are mostly water. Everything else is dissolved or mixed into it.'),
    ('clean', 'Cleansers', 'Surfactants', 'They lift oil and buildup so it rinses away.'),
    ('slip', 'Slip', 'Conditioners and fatty alcohols', 'They coat the strand so it slides instead of snagging. Fatty alcohols are not drying alcohols.'),
    ('water', 'Water binders', 'Humectants', 'They draw water in and hold on to it, which is why they sit high on moisture-focused labels.'),
    ('soft', 'Softness', 'Oils and butters', 'They soften and coat the outside of the hair.'),
    ('strength', 'Strength and repair', 'Proteins, ceramides and bond builders', 'They work on the hair fibre itself.'),
    ('hold', 'Hold', 'Film-formers', 'They leave a flexible film as hair dries, for definition and hold.'),
    ('ph', 'pH and minerals', 'Acids and chelators', 'Acids set the product\'s pH; chelators bind minerals from hard water.'),
    ('scalp', 'Scalp care', 'Scalp ingredients', 'Ingredients made for the scalp, often found in serums.'),
    ('safe', 'Keeps it safe', 'Preservatives', 'Anything made with water needs them, usually under 1% and near the end of the list.'),
    ('scent', 'Scent', 'Fragrance and its allergens', 'Listed last; allergens are named one by one so sensitive scalps can spot them.'),
    ('help', 'Helpers', 'Stabilisers and antioxidants', 'They keep the formula stable in the bottle.'),
]
GNAME = {k: n for k, n, _, _ in GROUPS}

def groups_of(i):
    tags, cat, g = set(i['_tags']), (i.get('category') or '').lower(), []
    if 'solvent' in cat or 'base' in cat: g.append('base')
    if 'surfactant' in cat or 'cleanser' in cat: g.append('clean')
    if 'slip/detangler' in tags: g.append('slip')
    if 'humectant' in tags: g.append('water')
    if 'butter/oil' in tags: g.append('soft')
    if tags & {'protein', 'bond repair', 'ceramides'}: g.append('strength')
    if 'film-former' in tags: g.append('hold')
    if 'chelating' in tags: g.append('ph')
    if 'scalp active' in tags: g.append('scalp')
    if 'preserv' in cat: g.append('safe')
    if 'fragrance' in cat: g.append('scent')
    return g or ['help']

def pick_example():
    by_id = {p['id']: (p, items) for p, items in B.labels}
    if 'TGC-134' in by_id:
        return by_id['TGC-134']
    return max(B.labels, key=lambda pi: (sum(1 for t in pi[1] if B.lookup(t)) / len(pi[1]), len(pi[1])))

# The homepage. Built twice: the live one at / with the quiet answer card, and
# the first version at /previous-home/ with the full label card, for comparison.


def library_js(R=''):
    keys = {k: [v['_slug'], v['_title'], groups_of(v), [g for g, _, _ in B.CHECK_GROUPS if g in v['_tags']]] for k, v in B.keys.items()}
    data = {'root': R, 'keys': keys, 'groups': [[k, n, h, c] for k, n, h, c in GROUPS], 'checks': [[k, n, d] for k, n, d in B.CHECK_GROUPS]}
    js = 'window.LIB=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n' + open(B.os.path.join(B.ROOT, 'src', 'library.js'), encoding='utf-8').read()
    B.write('assets/library.js', js)

def find_json():
    out = []
    for p, items in B.labels:
        out.append({'s': p['_slug'], 'n': B.product_full_name(p), 'b': (p.get('brand') or '').strip(), 'i': items})
    out.sort(key=lambda x: x['n'].lower())
    B.write('data/find.json', json.dumps(out, ensure_ascii=False, separators=(',', ':')))
    return len(out)


def build(out='', root='', quiet=True):
    OUT_PATH, R = out, root
    library_js(root)
    n_found = find_json()
    p, items = pick_example()
    found = [(t, B.lookup(t)) for t in items]
    def c(t, i):
        g = B.groups_for(t, i)
        return f' data-c="{" ".join(g)}"' if g else ''
    words = ', '.join(
        (f'<a href="{i["_slug"]}/" data-g="{" ".join(groups_of(i))}"{c(t, i)}>{e(t)}</a>'
         if i else f'<span{c(t, None)}>{e(t)}</span>') for t, i in found)
    present = []
    for k, *_ in GROUPS:
        members = []
        for t, i in found:
            if i and k in groups_of(i) and i not in members:
                members.append(i)
        if members:
            present.append((k, members))
    first = next((g for g in GROUPS if g[0] == present[0][0]), GROUPS[0]) if present else GROUPS[0]
    def links(m):
        return ', '.join(f'<a href="{i["_slug"]}/">{e(i["_title"])}</a>' for i in m)
    group_rows = ''.join(f'<li data-k="{k}"><b>{e(GNAME[k])}</b><span>{links(m)}</span></li>' for k, m in present)
    dots = ''.join(f'<button type="button" class="dot2" data-k="{k}" aria-label="{e(GNAME[k])}"></button>' for k, _ in present)
    known = len({id(i) for _, i in found if i})
    name = B.product_full_name(p)

    # doors: most common label ingredients, products with labels, plans
    freq = {}
    for _, its in B.labels:
        for i in {id(x): x for x in (B.lookup(t) for t in its) if x}.values():
            freq[i['id']] = (freq.get(i['id'], (i, 0))[0], freq.get(i['id'], (i, 0))[1] + 1)
    ranked = [i for i, n in sorted(freq.values(), key=lambda v: (-v[1], v[0]['_title']))]
    BASIC = {'base', 'safe', 'scent', 'help', 'ph', 'clean'}
    # The basics: the everyday ingredients on almost every label.
    basics = [i for i in ranked if set(groups_of(i)) & BASIC][:8]
    # Featured: the owner's picks (a "featured" column set to yes), otherwise one standout per job.
    featured = [i for i in B.ing if (B.col(i, 'featured') or '').strip().lower() in ('yes', 'y', 'true', 'x', '1')][:6]
    if not featured:
        seen = set()
        everyday = {'Glycerin', 'Cetearyl Alcohol', 'Cetyl Alcohol', 'Water', 'Aqua'}
        def claimy(i):
            return B.CLAIM_WORDS.search(' '.join(i.get(c, '') for c in ('what_it_does', 'buildup_sensitivity_notes', 'category')))
        for k in ['strength', 'water', 'slip', 'soft', 'hold', 'scalp', 'strength', 'water']:
            if len(featured) >= 6:
                break
            pool = [i for i in ranked if k in groups_of(i) and not set(groups_of(i)) & BASIC and i['id'] not in seen and i['_title'] not in everyday]
            pool += [i for i in B.ing if k in groups_of(i) and not set(groups_of(i)) & BASIC and i['id'] not in seen and i['_title'] not in everyday and i not in pool]
            pool = [i for i in pool if not claimy(i)]
            if pool:
                featured.append(pool[0]); seen.add(pool[0]['id'])
    def job(i):
        g = [x for x in groups_of(i) if x not in BASIC]
        return GNAME[g[0]] if g else ''
    labelled = [pp for pp, _ in B.labels][:4]
    n_products = len([x for x in B.products if (x.get('kind') or 'product') == 'product'])
    import glob
    plans = [json.load(open(f, encoding='utf-8')) for f in sorted(glob.glob(B.os.path.join(B.ROOT, 'content', 'guide-*.json')))]
    plans.sort(key=lambda g: g.get('order', 99))

    if quiet:
        lead = ('Name a product you use and we will tell you what is in it. '
                'No scores, no verdicts.')
        controls = f'''<div class="finder">
        <label for="tf">Your product</label>
        <input id="tf" type="text" autocomplete="off" role="combobox" aria-expanded="false" aria-controls="tf-list" placeholder="Start typing, e.g. Quench or Aunt Jackie's">
        <ul class="f-list t-list" id="tf-list" role="listbox" hidden></ul>
        <p class="f-note">{n_found} labels read so far.</p>
      </div>
      <details class="paste t-paste" >
        <summary>Our library does not have your product yet?</summary>
        <form id="t-form">
          <label for="tt">Paste the ingredient list from the bottle</label>
          <textarea id="tt" rows="3" placeholder="Water, Glycerin, Cetearyl Alcohol, …"></textarea>
          <button class="go" type="submit">Read this label</button>
        </form>
      </details>'''
    else:
        lead = ('Paste the ingredient list from a bottle or a product page. Every ingredient in '
                'our library is explained by what it does. No scores, no verdicts.')
        controls = '''<form class="paste" id="paste">
        <label for="t">Ingredient list</label>
        <textarea id="t" rows="4" placeholder="Water, Glycerin, Cetearyl Alcohol, …"></textarea>
        <div class="paste-row"><button class="go" type="submit">Explain this label</button><button class="link-btn" type="button" id="reset" hidden>Back to the example</button></div>
      </form>'''
    if quiet:
        rows = ''.join(
            f'''<li class="t-row" data-g="{k}"><span class="t-name">{e(n)}</span>'''
            f'''<span class="t-ans">?</span><span class="t-detail"></span></li>'''
            for k, n, _ in B.CHECK_GROUPS)
        card = f'''<figure class="btl btl-quiet" id="card">
      <div class="btl-top"><span>Does it have…</span><b id="btl-name"></b></div>
      <ol class="t-answers" id="t-answers" aria-live="polite">{rows}</ol>
      <p class="t-note" id="t-note">Pick a product and we will read its label.</p>
      <details class="t-more" id="t-more" hidden>
        <summary>See the full ingredient list</summary>
        <p class="inci" id="t-inci"></p>
        <p class="t-foot" id="t-foot"></p>
      </details>
    </figure>'''
        script = f'<script src="{R}assets/home-test.js" defer></script>'
    else:
        card = f'''<figure class="btl" id="card" aria-labelledby="btl-name">
      <div class="cap" id="cap" aria-live="polite"><small>{e(first[1])}</small><b>{e(first[2])}</b><p>{e(first[3])}</p></div>
      <div class="dots2" id="dots" role="group" aria-label="Step through the groups">{dots}</div>
      <div class="btl-top"><span>Ingredients · as printed</span><b id="btl-name"><a href="{R}products/{p['_slug']}/">{e(name)}</a></b></div>
      <p class="btl-words" id="words">{words}.</p>
      <div class="btl-foot" id="foot"><b>{known} of {len(items)}</b> in our library · grey words aren't in it yet</div>
      <div class="chk-wrap" id="chk"><h3 class="chk-h">Does it have…</h3>{B.check_strip(items, js=False)}</div>
      <ul class="btl-groups" id="groups">{group_rows}</ul>
    </figure>'''
        script = f'<script src="{R}assets/library.js" defer></script>'
    body = f'''<section class="band">
  <div class="band-in">
    <div class="band-copy">
      <span class="eyebrow"><span class="little-dot"></span>The Good Coil Library</span>
      <h1>Read any hair-care label</h1>
      <p class="band-lead">{lead}</p>
      {controls}
    </div>
    {card}
  </div>
</section>

<div class="wrap home-rest"><section class="doors2" aria-label="Browse the library">
  <a class="door" href="{R}ingredients/"><span class="door-n">{len(B.ing)}</span><h2>Ingredients</h2><p>Every ingredient by what it is and what it does, from proteins to plant gels.</p>
    <ul class="door-feat">{''.join(f'<li><b>{e(i["_title"])}</b><span>{e(job(i))}</span></li>' for i in featured)}</ul><span class="door-go">All ingredients →</span></a>
  <a class="door" href="{R}products/"><span class="door-n">{n_products}</span><h2>Products</h2><p>{len(B.labels)} labels read so far, each decoded ingredient by ingredient.</p>
    <ul>{''.join(f'<li>{e(B.product_full_name(x))}</li>' for x in labelled)}</ul><span class="door-go">All products →</span></a>
  <a class="door door-photo" href="{R}plans/"><span class="door-n">{len(plans)}</span><h2>Hair plans</h2><p>What is going on, what to do each week, and what to look for on a label.</p>
    <img src="{R}assets/img/ends.jpg" alt="A woman with long dark curls holds the ends of a curl between her fingers." width="799" height="1344" loading="lazy">
    <span class="door-go">See the plans →</span></a>
</section>
</div>
{script}'''
    desc = ('Name a hair-care product and see whether it has protein, ceramides, silicones, '
            'sulfates or peptides in it, with every ingredient explained by what it does.' if quiet
            else 'Paste a hair-care ingredient list and see every ingredient explained by what it does.')
    html = B.shell(R, 'The Good Coil Library: read any hair-care label', desc, body, OUT_PATH, 'home')
    if not quiet:
        html = html.replace('</head>', '<meta name="robots" content="noindex">\n</head>')
    html = html.replace('<main id="main" class="wrap">', '<main id="main" class="home">', 1)
    B.write(OUT_PATH + 'index.html', html)

"""Build ingredients.thegoodcoil.com from the sheet exports in data/.

    python3 scripts/build.py            -> writes the site to _site/

Inputs (exported from the owner's Google Sheets; the sheets are the master copies):
    data/ingredients.csv   ingredient database (one row per ingredient)
    data/catalog.csv       product catalog (labels are read from "full ingredient list")
    data/programs.csv      signature hair programs (stored, not used yet)

Only the Python standard library is used, so it runs anywhere without installs.
Columns are read by name, so new columns in the sheets never break the build;
optional columns it understands: slug, source.
"""
import csv, html, json, os, re, shutil, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
OUT = os.path.join(ROOT, '_site')
SITE = 'https://ingredients.thegoodcoil.com'
e = html.escape

# ---------- data ----------
def read_csv(name):
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        return []
    with open(path, newline='', encoding='utf-8-sig') as fh:
        rows = list(csv.DictReader(fh))
    return [{(k or '').strip(): (v or '').strip() for k, v in r.items()} for r in rows if any((v or '').strip() for v in r.values())]

def col(row, *names):
    for n in names:
        if row.get(n):
            return row[n]
    return ''

norm = lambda s: re.sub(r'[^a-z0-9]+', ' ', s.lower()).strip()
slugify = lambda s: re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
split_names = lambda s: [a.strip() for a in re.split(r',(?!\d)', s or '') if a.strip()]

_a, _b = read_csv('ingredients.csv'), read_csv('catalog.csv')
# Tell the two sheets apart by their columns, so swapped links still build the right site.
if _a and 'inci_name' not in _a[0] and _b and 'inci_name' in _b[0]:
    print('Note: the ingredient and catalog links are swapped; using each sheet by its columns.')
    _a, _b = _b, _a
for name, rows in (('ingredients', _a), ('catalog', _b)):
    print(f'{name}: {len(rows)} rows; columns: {", ".join(list(rows[0])[:12]) if rows else "none"}')
ing = [r for r in _a if r.get('id') and r.get('inci_name')]
cat = _b

for i in ing:
    i['_short'] = re.sub(r'\s*\(.*?\)', '', i.get('common_name') or i['inci_name']).strip()
    i['_title'] = i['_short'] if len(i['inci_name']) > 28 else i['inci_name']
    # A slug column in the sheet freezes the address; otherwise it comes from the page title.
    i['_slug'] = col(i, 'slug') or slugify(i['_title'])
    i['_tags'] = [t.strip() for t in (i.get('property_tag') or '').split(',') if t.strip() and t.strip().lower() != 'none']
    i['_aliases'] = [a for a in split_names(i.get('aliases_also_listed_as')) if norm(a) != norm(i['inci_name'])]
    i['_source'] = col(i, 'source') or 'The Good Coil research'

dupes = [i['_short'] for i in ing]
for i in ing:
    if dupes.count(i['_short']) > 1 and len(i['inci_name']) > 28:
        i['_title'] = i['_short'] = (i.get('common_name') or i['inci_name']).strip()
        i['_slug'] = col(i, 'slug') or slugify(i['_title'])

seen = {}
for i in ing:
    if i['_slug'] in seen:
        i['_slug'] += '-' + i['id'].lower()
    seen[i['_slug']] = i

keys = {}
for i in ing:
    names = [i['inci_name'], (i.get('common_name') or '').split('(')[0]] + split_names(i.get('aliases_also_listed_as'))
    m = re.match(r'(.*?)\((.*?)\)', i['inci_name'])
    if m:
        names += [m.group(1), m.group(2)]
    for n in names:
        if norm(n):
            keys.setdefault(norm(n), i)

def lookup(t):
    return keys.get(norm(t)) or keys.get(norm(re.sub(r'\(.*?\)', '', t)))

def split_label(L):
    L = re.sub(r'(?<![\w-])(\d),\s+(\d)-', r'\1,\2-', L)  # "1, 2-Hexanediol" typed with a space
    items = [re.sub(r'\*.*$', '', t).strip().rstrip('.') for t in re.split(r',(?![^()]*\))(?!\d)', L)]
    return [t for t in items if t]

labels = [(p, split_label(p['full ingredient list'])) for p in cat
          if p.get('full ingredient list') and (p.get('kind') or 'product') == 'product']

STEPS = [('cleanse', 'Cleanse'), ('condition', 'Condition'), ('treatment', 'Treat'), ('leave-in', 'Leave-in'), ('style', 'Style'), ('seal', 'Seal')]
STEP = dict(STEPS)

# Short, neutral descriptions of each property. Edit freely; unknown tags still get a page.
PROPS = {
    'humectant': 'Draws water toward itself and holds on to it. In hair products, humectants help strands take up water and keep it.',
    'butter/oil': 'Oils, butters and other fatty ingredients that coat the hair surface, soften it and cut down friction between strands.',
    'protein': 'Proteins and amino acids, often broken into small pieces (hydrolyzed), that attach to the hair surface.',
    'film-former': 'Leaves a thin, flexible film on hair as it dries. Gels and stylers use film-formers for hold and definition.',
    'ceramides': 'Lipids like the ones found naturally between the cells of the hair\'s outer layer.',
    'slip/detangler': 'Makes wet hair slippery, so strands slide apart instead of catching on each other.',
    'scalp active': 'Ingredients used in products made for the scalp, such as serums and tonics.',
    'bond repair': 'Ingredients designed to work on the bonds inside the hair fibre, the ones colour, relaxers and heat can break.',
    'chelating': 'Binds to metals and minerals, like the ones in hard water, so they rinse away. Acids in this group also set a product\'s pH.',
    'silicone': 'Silicones form a smooth, slippery coating on hair that adds shine and reduces friction.',
    'sulfate': 'Strong cleansing agents that lift oil and buildup and make a rich lather.',
    'heat protectant': 'Ingredients used in products meant to go on before heat styling.',
}
prop_slug = lambda t: slugify(t)

# Wording that can read as a drug or hair-growth claim in the US. Reported at build time, never changed.
CLAIM_WORDS = re.compile(r'\b(grow(th|s)?|follicle\w*|shedding|density|thicker|stimulat\w*|regrow\w*|hair loss|1,?000x)\b', re.I)

# ---------- page parts ----------
def ordinal(n):
    return {1: '1st', 2: '2nd', 3: '3rd'}.get(n, f'{n}th')

ICON = '<svg width="15" height="15" viewBox="0 0 16 16" aria-hidden="true"><circle cx="7" cy="7" r="5" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M11 11l3.5 3.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>'

def shell(r, title, desc, body, path, current=''):
    """r = relative path to the site root, e.g. '../'."""
    cur = lambda k: ' aria-current="page"' if current == k else ''
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}/{path}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website">
<link rel="icon" href="{r}favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}assets/site.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <a href="{r}" class="wordmark" aria-label="The Good Coil Ingredients home"><span class="brand-symbol" aria-hidden="true">◎</span> the<span class="brand-amp">good</span>coil<span class="wordmark-sub">Ingredients</span></a>
  <nav class="nav" aria-label="Main">
    <a class="search" href="{r}#find">{ICON} Look up an ingredient</a>
    <a class="search-sm" href="{r}#find">{ICON} Search</a>
    <a href="{r}plans/" class="hide-sm"{cur('plans')}>Hair plans</a>
    <a href="{r}properties/" class="hide-sm hide-md"{cur('props')}>By property</a>
    <a href="{r}" class="hide-sm hide-md"{cur('home')}>All ingredients</a>
  </nav>
</header>
<main id="main" class="wrap">
{body}
</main>
<footer class="site-footer">
  <div><a href="{r}" class="wordmark"><span class="brand-symbol" aria-hidden="true">◎</span> the<span class="brand-amp">good</span>coil</a><p>Good knowledge. Happy hair.<br>A journey that's yours.</p></div>
  <nav class="footer-links" aria-label="Footer"><a href="{r}">All ingredients</a><a href="{r}plans/">Hair plans</a><a href="{r}properties/">By property</a><a href="{r}about/">How we write</a><a href="{r}about/#affiliate">Affiliate disclosure</a><a href="https://thegoodcoil.com">The Good Coil</a><a href="https://itsjara.com">JARA hair journal</a></nav>
  <div class="footer-bottom"><span>© {datetime.date.today().year} The Good Coil</span><span>Descriptions, not verdicts: every head of hair is different.</span><span>Educational guidance, not medical advice.</span></div>
</footer>
</body>
</html>
'''

def write(path, text):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as fh:
        fh.write(text)

# ---------- ingredient pages ----------
def hits_for(g):
    hits = []
    for p, items in labels:
        for n, t in enumerate(items, 1):
            if lookup(t) is g:
                hits.append((p, items, n))
                break
    hits.sort(key=lambda h: (h[2], -sum(1 for t in h[1] if lookup(t))))
    return hits

def ingredient_page(g):
    r = '../'
    hits = hits_for(g)
    title = g['_title']
    tags = ''.join(f'<a class="tag" href="{r}properties/{prop_slug(t)}/">{e(t)}</a>' for t in g['_tags'])

    if hits:
        p, items, n = hits[0]
        def word(t):
            i = lookup(t)
            if i is g:
                return f'<mark class="hit">{e(t)}</mark>'
            if i:
                return f'<a href="{r}{i["_slug"]}/">{e(t)}</a>'
            return e(t)
        cut = max(10, n + 4)
        head = ', '.join(word(t) for t in items[:cut])
        rest = ', '.join(word(t) for t in items[cut:])
        more = f'<span class="rest">, {rest}</span>.<button class="more-btn" type="button" hidden>Show all {len(items)} ingredients</button>' if rest else '.'
        after = 'right after water' if n == 2 and norm(items[0]).startswith(('aqua', 'water', 'eau')) else f'{ordinal(n)} of {len(items)}'
        name = f"{p.get('brand', '').strip()} {p.get('name', '').strip()}".strip()
        hero = f'''<figure class="label" aria-labelledby="lbl">
      <div class="sticker" aria-hidden="true"><em>#{n}</em><small>of {len(items)}</small></div>
      <div class="label-top"><span>Ingredients · as printed</span><b id="lbl">{e(name)}</b></div>
      <p class="inci">{head}{more}</p>
      <figcaption class="label-foot"><span><b>{e(title)} is {ordinal(n)}</b>, {after}.</span><span>Dotted words have their own page.</span></figcaption>
    </figure>'''
    else:
        spell = ''.join(f'<li>{e(a)}</li>' for a in [g['inci_name']] + g['_aliases'])
        hero = f'''<figure class="label label-empty" aria-labelledby="lbl">
      <div class="label-top"><span>How it's written</span><b id="lbl">On a label, look for</b></div>
      <ul class="spell">{spell}</ul>
      <figcaption class="label-foot"><span>We haven't read a label with it yet.</span><span>We've read {len(labels)} so far.</span></figcaption>
    </figure>'''

    sections = []
    if g.get('buildup_sensitivity_notes'):
        sections.append(f'''<section class="section" id="good">
    <div class="intro"><span class="eyebrow">Good to know</span></div>
    <p class="note">{e(g['buildup_sensitivity_notes'])}</p>
  </section>''')
    hair = col(g, 'hair_type_notes', 'hair_type_porosity_fit')
    if hair:
        sections.append(f'''<section class="section" id="hair">
    <div class="intro"><span class="eyebrow">Hair types</span><h2>Notes for different hair</h2></div>
    <div class="hair"><p>{e(hair)}</p><small>General patterns from our research, not rules. Hair of the same type can respond differently, so your own results count most.</small></div>
  </section>''')

    if hits:
        x = lambda n: round(2.5 + (min(n, 40) - 1) / 39 * 95, 1)
        stack, dots = {}, ''
        for k, (p, items, n) in enumerate(hits):
            h = stack.get(n, 0); stack[n] = h + 1
            name = f"{p.get('brand', '').strip()} {p.get('name', '').strip()}".strip()
            dots += f'<a class="dot" href="#p{k}" style="left:{x(n)}%;bottom:{58 + h * 24}px;animation-delay:{1.3 + k * .06:.2f}s" aria-label="{e(name)}: {ordinal(n)} of {len(items)}"></a>'
        ticks = ''.join(f'<span class="tick" style="left:{x(n)}%">{ordinal(n)}</span>' for n in (1, 10, 20, 30, 40))
        steps = ' · '.join(f'<span>{lbl} <b>{sum(1 for h in hits if h[0].get("step") == s)}</b></span>' for s, lbl in STEPS
                           if s != 'treatment' or any(h[0].get('step') == s for h in hits))
        top = sum(1 for h in hits if h[2] <= 3)
        heading = f"On {len(hits)} of the {len(labels)} labels we've read" + (', usually near the top' if top * 2 >= len(hits) and len(hits) > 1 else '')
        rows = ''.join(f'''<li id="p{k}"><span class="pos">{n}<small>of {len(items)}</small></span><div><span class="step">{e(STEP.get(p.get('step', ''), p.get('step', '').capitalize()))}</span><b>{e(p.get('brand', '').strip())}</b> {e(p.get('name', '').strip())}</div></li>''' for k, (p, items, n) in enumerate(hits))
        sections.append(f'''<section class="across" id="across">
    <div class="intro">
      <span class="eyebrow">Across labels</span>
      <h2>{heading}</h2>
      <p>Labels list ingredients from most to least, down to about 1%. Below that, the order is free.</p>
      <p class="steps">{steps}</p>
    </div>
    <div>
      <div class="strip" role="img" aria-label="Where {e(title)} sits on each label">{dots}<div class="axis"></div>{ticks}</div>
      <ol class="labels">{rows}</ol>
      <p class="fine">These are labels we've read by hand from brand sites and packaging, not a list of recommendations. We add more as we go.</p>
    </div>
  </section>''')

    mytags = set(g['_tags'])
    related = [i for i in ing if i is not g and (set(i['_tags']) & mytags if mytags else i.get('category') == g.get('category'))]
    if related:
        label = f"Also {g['_tags'][0]}" if g['_tags'] else e(g.get('category', ''))
        rel = ''.join(f'<a href="{r}{i["_slug"]}/">{e(i["_short"])}</a>' for i in related)
        sections.append(f'''<section class="section">
    <div class="intro"><span class="eyebrow">{e(label)}</span><h2>Other ingredients like it</h2></div>
    <nav class="related" aria-label="Related ingredients">{rel}</nav>
  </section>''')

    links = ''.join([
        '<a href="#good">Good to know</a>' if g.get('buildup_sensitivity_notes') else '',
        '<a href="#hair">Hair types</a>' if hair else '',
        f'<a href="#across">On {len(hits)} of {len(labels)} labels we\'ve read</a>' if hits else '',
    ])
    body = f'''  <a class="crumb" href="{r}">← All ingredients</a>
  <section class="first">
    <div class="name">
      <span class="eyebrow"><span class="little-dot"></span>{e(g.get('category', ''))}</span>
      <h1>{e(title)}</h1>
      <p class="aka"><em>also on labels as</em> {' · '.join(e(a) for a in g['_aliases']) or e(g['inci_name'])}</p>
      <p class="lead">{e(g.get('what_it_does', ''))}</p>
      <div class="meta">{tags}{links}</div>
    </div>
    {hero}
  </section>
  {''.join(sections)}
  <p class="source"><span>Source: {e(g['_source'])} · Ref {e(g['id'])}</span><a href="{r}data/ingredients.json">Get this as data (JSON)</a><a href="{r}about/">How we write these</a></p>
<script>if(matchMedia('(max-width:760px)').matches)document.querySelectorAll('.inci').forEach(p=>{{const b=p.querySelector('.more-btn');if(!b)return;p.classList.add('clamped');b.hidden=false;b.onclick=()=>{{p.classList.remove('clamped');b.remove()}}}})</script>'''
    desc = f"{title} ({g['inci_name']}) in hair products: what it is, what it does, how it's written on labels, and notes for different hair."
    write(f"{g['_slug']}/index.html", shell(r, f"{title} in hair products: what it is and what it does · The Good Coil Ingredients", desc, body, f"{g['_slug']}/"))
    return len(hits)

# ---------- index ----------
def index_page(counts):
    tags = sorted({t for i in ing for t in i['_tags']}, key=lambda t: (-sum(t in i['_tags'] for i in ing), t))
    chips = '<button class="chip" type="button" aria-pressed="true" data-tag="">All</button>' + ''.join(
        f'<button class="chip" type="button" aria-pressed="false" data-tag="{e(t)}">{e(t)}</button>' for t in tags)
    items = ''.join(
        f'''<li data-tags="{e('|'.join(i['_tags']))}" data-q="{e(norm(' '.join([i['inci_name'], i.get('common_name', '')] + i['_aliases'])))}"><a href="{i['_slug']}/"><b>{e(i['_title'])}</b><span>{e(', '.join(i['_tags']) or i.get('category', ''))}</span>{f'<i>{counts[i["id"]]} label{"s" if counts[i["id"]] != 1 else ""}</i>' if counts[i['id']] else ''}</a></li>'''
        for i in sorted(ing, key=lambda i: i['_title'].lower()))
    body = f'''  <section class="home-head">
    <div><span class="eyebrow"><span class="little-dot"></span>Ingredient library</span>
    <h1>What's on <em>the label,</em> explained</h1></div>
    <p>Every ingredient described by what it is and what it does, with notes for different hair. No scores and no verdicts: you decide what works for you.</p>
  </section>
  <section class="finder" id="find" aria-label="Find an ingredient">
    <label for="q">Look up an ingredient, by its label name or its everyday name</label>
    <input id="q" type="search" placeholder="Try glycerin, BTAC or shea" autocomplete="off">
    <div class="chips" role="group" aria-label="Filter by property">{chips}</div>
  </section>
  <p class="count-line" id="count" aria-live="polite">{len(ing)} ingredients · {len(labels)} labels read so far</p>
  <ul class="ing-list" id="list">{items}</ul>
  <p class="empty-msg" id="none" hidden>Nothing matches yet. The library grows every week, so check the spelling or try the everyday name.</p>
<script>
(()=>{{const q=document.getElementById('q'),list=[...document.querySelectorAll('#list li')],chips=[...document.querySelectorAll('.chip')],count=document.getElementById('count'),none=document.getElementById('none');let tag='';
const n=s=>s.toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
function run(){{const v=n(q.value);let k=0;list.forEach(li=>{{const ok=(!v||li.dataset.q.includes(v))&&(!tag||li.dataset.tags.split('|').includes(tag));li.hidden=!ok;if(ok)k++}});count.textContent=k+' of {len(ing)} ingredients';none.hidden=k>0}}
q.addEventListener('input',run);chips.forEach(c=>c.addEventListener('click',()=>{{tag=c.dataset.tag;chips.forEach(x=>x.setAttribute('aria-pressed',x===c));run()}}));
if(location.hash==='#find')q.focus();}})();
</script>'''
    write('index.html', shell('', 'The Good Coil Ingredients: hair-care ingredients, explained', 'A library of hair-care ingredients, each described by what it is and what it does, with notes for different hair. No scores, no verdicts.', body, '', 'home'))

# ---------- properties ----------
def property_pages():
    tags = sorted({t for i in ing for t in i['_tags']}, key=lambda t: (-sum(t in i['_tags'] for i in ing), t))
    rows = ''.join(f'''<li><a href="{prop_slug(t)}/"><h2>{e(t)}</h2><p>{e(PROPS.get(t, ''))}</p><span>{sum(t in i['_tags'] for i in ing)}</span></a></li>''' for t in tags)
    body = f'''  <a class="crumb" href="../">← All ingredients</a>
  <section class="page-head"><span class="eyebrow"><span class="little-dot"></span>By property</span><h1>What ingredients do</h1>
  <p>Properties group ingredients by the job they do in a product. Many ingredients do more than one job, so they show up in more than one group.</p></section>
  <ul class="prop-list">{rows}</ul>'''
    write('properties/index.html', shell('../', 'Ingredients by property · The Good Coil Ingredients', 'Hair-care ingredients grouped by what they do: humectants, oils and butters, proteins, film-formers and more.', body, 'properties/', 'props'))
    for t in tags:
        members = sorted([i for i in ing if t in i['_tags']], key=lambda i: i['_title'].lower())
        items = ''.join(f'''<li><a href="../../{i['_slug']}/"><b>{e(i['_title'])}</b><span>{e(i.get('category', ''))}</span></a></li>''' for i in members)
        body = f'''  <a class="crumb" href="../">← All properties</a>
  <section class="page-head"><span class="eyebrow"><span class="little-dot"></span>Property</span><h1>{e(t.capitalize())}</h1><p>{e(PROPS.get(t, ''))}</p></section>
  <p class="count-line">{len(members)} ingredients</p>
  <ul class="ing-list">{items}</ul>'''
        write(f'properties/{prop_slug(t)}/index.html', shell('../../', f'{t.capitalize()} ingredients in hair care · The Good Coil Ingredients', PROPS.get(t, f'{t} ingredients'), body, f'properties/{prop_slug(t)}/', 'props'))
    return tags

# ---------- about ----------
def about_page():
    body = f'''  <a class="crumb" href="../">← All ingredients</a>
  <section class="page-head"><span class="eyebrow"><span class="little-dot"></span>About</span><h1>How we write these</h1>
  <p>This library explains what's on a hair-care label. It is part of The Good Coil and is updated as our research grows.</p></section>
  <div class="prose">
    <h2>Descriptions, not verdicts</h2>
    <p>Each ingredient is described by what it is and what it does in a product. We don't score ingredients or call them good or bad for a hair type: the same ingredient can behave differently depending on the formula, the amount, your water, the weather and your hair. The notes for different hair are general patterns, not rules.</p>
    <h2>Labels we've read</h2>
    <p>Ingredient positions come from labels we've read by hand from brand websites and packaging. Labels list ingredients from most to least down to about 1%; below that, the order is free. A product appearing here is not a recommendation.</p>
    <h2>Sources</h2>
    <p>Ingredient descriptions are The Good Coil's own research unless a page says otherwise. If we use data from Open Beauty Facts, that page names it as the source; Open Beauty Facts data is shared under the Open Database Licence (share-alike).</p>
    <h2 id="affiliate">Affiliate disclosure</h2>
    <p>Ingredient pages have no shop links. Elsewhere on The Good Coil, some product links are affiliate links: we may earn a small commission at no extra cost to you. Commissions never change what we write about an ingredient.</p>
    <h2>Not medical advice</h2>
    <p>This is educational information about cosmetic ingredients. For hair loss, scalp conditions or allergies, talk to a dermatologist or doctor.</p>
    <h2>Use the data</h2>
    <p>The whole library is available as <a href="../data/ingredients.json">ingredients.json</a>, rebuilt every night from our working sheet. Last built {datetime.date.today().strftime('%B %-d, %Y')}.</p>
  </div>'''
    write('about/index.html', shell('../', 'How we write these · The Good Coil Ingredients', 'How The Good Coil describes hair-care ingredients: descriptions, not verdicts; sources; affiliate disclosure.', body, 'about/'))

# ---------- data + extras ----------
def data_files(counts):
    out = {
        'generated': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source': 'The Good Coil ingredient database',
        'labels_read': len(labels),
        'ingredients': [{
            'id': i['id'], 'slug': i['_slug'], 'url': f"{SITE}/{i['_slug']}/",
            'inci_name': i['inci_name'], 'common_name': i.get('common_name', ''), 'category': i.get('category', ''),
            'properties': i['_tags'], 'aliases': i['_aliases'],
            'what_it_does': i.get('what_it_does', ''), 'hair_type_notes': col(i, 'hair_type_notes', 'hair_type_porosity_fit'),
            'good_to_know': i.get('buildup_sensitivity_notes', ''), 'source': i['_source'], 'labels_seen_on': counts[i['id']],
        } for i in ing],
    }
    write('data/ingredients.json', json.dumps(out, ensure_ascii=False, indent=1))

def extras(tags, plan_urls=()):
    write('CNAME', 'ingredients.thegoodcoil.com\n')
    write('.nojekyll', '')
    write('robots.txt', f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
    urls = [''] + [f"{i['_slug']}/" for i in ing] + ['properties/'] + [f'properties/{prop_slug(t)}/' for t in tags] + ['about/', 'plans/'] + list(plan_urls)
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
          ''.join(f'  <url><loc>{SITE}/{u}</loc></url>\n' for u in urls) + '</urlset>\n')
    write('favicon.svg', '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="#DCF473"/><circle cx="16" cy="16" r="10" fill="none" stroke="#432731" stroke-width="3"/><circle cx="16" cy="16" r="4" fill="#432731"/></svg>')
    body = '''  <section class="page-head"><span class="eyebrow"><span class="little-dot"></span>Not found</span><h1>That page isn't here</h1>
  <p>The ingredient may have a different name, or it isn't in the library yet. <a class="crumb" href="/">Search all ingredients</a></p></section>'''
    write('404.html', shell('/', 'Page not found · The Good Coil Ingredients', 'Page not found.', body, '404.html'))

def checks(counts):
    notes = []
    for i in ing:
        text = ' '.join(i.get(k, '') for k in ('common_name', 'category', 'what_it_does', 'hair_type_porosity_fit', 'hair_type_notes', 'buildup_sensitivity_notes'))
        found = sorted({m.group(0).lower() for m in CLAIM_WORDS.finditer(text)})
        if found:
            notes.append(f"- {i['id']} {i['_title']}: may read as a growth or drug claim ({', '.join(found)})")
    unknown = {}
    for p, items in labels:
        for t in items:
            if not lookup(t):
                k = norm(re.sub(r'\(.*?\)', '', t)) or norm(t)
                unknown[k] = unknown.get(k, 0) + 1
    recognised = sum(1 for _, items in labels for t in items if lookup(t))
    total = sum(len(items) for _, items in labels)
    report = ['## Build report', f'{len(ing)} ingredients, {len(labels)} labels, {recognised} of {total} label entries recognised.', '',
              '### Wording to review (not changed)'] + (notes or ['- none']) + ['', '### Most common label words without an ingredient row'] + \
             [f'- {k} ({n})' for k, n in sorted(unknown.items(), key=lambda kv: -kv[1])[:25]]
    text = '\n'.join(report) + '\n'
    print(text)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as fh:
            fh.write(text)

def main():
    if not ing:
        sys.exit('No ingredients found in data/ingredients.csv: refusing to publish an empty site.')
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(os.path.join(OUT, 'assets'))
    shutil.copy(os.path.join(ROOT, 'src', 'site.css'), os.path.join(OUT, 'assets', 'site.css'))
    counts = {i['id']: ingredient_page(i) for i in ing}
    index_page(counts)
    tags = property_pages()
    about_page()
    data_files(counts)
    sys.modules.setdefault('build', sys.modules[__name__])
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import plans
    plan_urls, plan_notes = plans.build()
    extras(tags, plan_urls)
    checks(counts)
    text = '### Hair plans\n' + (f'{len(plan_urls)} plans built.\n' + '\n'.join(plan_notes) if plan_urls else 'No programs found.') + '\n'
    print(text)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as fh:
            fh.write(text)

if __name__ == '__main__':
    main()

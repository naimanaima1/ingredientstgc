"""Build library.thegoodcoil.com from the sheet exports in data/.

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
SITE = 'https://library.thegoodcoil.com'
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
    if col(i, 'display_name'):  # the name people actually use, set in the sheet
        i['_title'] = i['_short'] = col(i, 'display_name')
    # A slug column in the sheet freezes the address; otherwise it comes from the page title.
    i['_slug'] = col(i, 'slug') or slugify(i['_title'])
    i['_tags'] = [t.strip() for t in (i.get('property_tag') or '').split(',') if t.strip() and t.strip().lower() != 'none']
    i['_aliases'] = [a for a in split_names(i.get('aliases_also_listed_as')) if norm(a) != norm(i['inci_name'])]
    i['_source'] = col(i, 'source') or 'The Good Coil research'

dupes = [i['_short'] for i in ing]
for i in ing:
    if dupes.count(i['_short']) > 1 and len(i['inci_name']) > 28 and not col(i, 'display_name'):
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

PREFIX = re.compile(r'^(organic|certified organic|deionized|distilled|purified|pure|raw|natural|unrefined)\s+', re.I)

def lookup(t):
    t = t.strip().strip('*').strip()
    tries = [t, re.sub(r'\(.*?\)', '', t), re.sub(r'\s*\(.*?\)\s*', ' ', t)]
    m = re.search(r'\((.*?)\)', t)
    if m:
        tries.append(m.group(1))
    for x in list(tries):
        if '/' in x:  # "Water/Aqua/Eau", "Persea Gratissima Oil / Avocado Oil"
            tries += x.split('/')
    for x in list(tries):
        tries.append(PREFIX.sub('', x.strip()))
    for x in tries:
        hit = keys.get(norm(x))
        if hit:
            return hit
    return None

def split_label(L):
    L = re.sub(r'(?<![\w-])(\d),\s+(\d)-', r'\1,\2-', L)  # "1, 2-Hexanediol" typed with a space
    items = [re.sub(r'\*.*$', '', t).strip().rstrip('.') for t in re.split(r'[;,](?![^()]*\))(?!\d)', L)]
    items = [re.sub(r'^(and|or)\s+', '', t, flags=re.I) for t in items]
    return [t for t in items if t]

def product_full_name(p):
    b, n = (p.get('brand') or '').strip(), (p.get('name') or '').strip()
    return n if n.lower().startswith(b.lower()) else f'{b} {n}'.strip()

products = [p for p in cat if p.get('id') and p.get('name') and (p.get('kind') or 'product') in ('product', 'tool')]
_pseen = {}
for p in products:
    sl = col(p, 'slug') or slugify(product_full_name(p).replace("'", '').replace('’', ''))
    if sl in _pseen:
        sl += '-' + p['id'].lower()
    _pseen[sl] = p
    p['_slug'] = sl

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
    'peptide': 'Short chains of amino acids. They are built as messengers rather than as patches for the hair surface, so they are not the same thing as a hydrolysed protein.',
    'bond repair': 'Ingredients designed to work on the bonds inside the hair fibre, the ones colour, relaxers and heat can break.',
    'chelating': 'Binds to metals and minerals, like the ones in hard water, so they rinse away. Acids in this group also set a product\'s pH.',
    'silicone': 'Silicones form a smooth, slippery coating on hair that adds shine and reduces friction.',
    'sulfate': 'Strong cleansing agents that lift oil and buildup and make a rich lather.',
    'heat protectant': 'Ingredients used in products meant to go on before heat styling.',
}
prop_slug = lambda t: slugify(t)

# The quick check on product pages and in the label decoder.
CHECK_GROUPS = [
    ('protein', 'Protein', 'Proteins broken into pieces small enough to cling to the hair surface.'),
    ('ceramides', 'Ceramides', "Lipids like the ones between the cells of the hair's outer layer."),
    ('silicone', 'Silicones', 'Coating ingredients that add slip and shine.'),
    ('sulfate', 'Sulfates', 'Strong cleansing agents, the kind that make a shampoo lather hard.'),
    ('peptide', 'Peptides', 'Short amino-acid chains. Not the same thing as a hydrolysed protein.'),
    ('paraben', 'Parabens', 'Preservatives whose names end in -paraben. The EU treats each one differently.'),
    ('phthalate', 'Phthalates', 'Chemicals used to carry fragrance and soften plastics. Names end in -phthalate.'),
]

# Tags that describe where an ingredient is used rather than what a product is for.
# A product never takes these on from its ingredients: a leave-in for the lengths
# that happens to contain a scalp active is still not a scalp product. If product
# tagging ever learns to read ingredient rows, it has to skip these.
NEVER_INHERIT = {'scalp active', 'scalp & fiber active', 'peptide / scalp & fiber active'}


def inheritable(tags):
    """The ingredient tags a product may be described by. See NEVER_INHERIT."""
    return [t for t in tags if t.strip().lower() not in NEVER_INHERIT]

SCALP_STEPS = {'scalp', 'treat'}


def scalp_product(p):
    """True only when the catalog says so: the step, or an explicit property."""
    props = {t.strip().lower() for t in (p.get('properties') or '').split(',')}
    if props & NEVER_INHERIT:
        return True
    step = (p.get('step') or '').strip().lower()
    name = ((p.get('name') or '') + ' ' + (p.get('notes') or '')).lower()
    return step in SCALP_STEPS or 'scalp' in name


def first_sentence(text, cap=190):
    t = ' '.join((text or '').split())
    m = re.search(r'(?<=[.!?])\s', t)
    if m and m.start() > 40:
        t = t[:m.start() + 1]
    return t if len(t) <= cap else t[:cap].rsplit(' ', 1)[0] + '…'


def tips_json():
    """A slim lookup so any ingredient link anywhere can show a preview on hover."""
    out = {}
    for i in ing:
        out[i['_slug']] = [i['_title'], (i.get('category') or '').strip(),
                           first_sentence(i.get('what_it_does')), i['_tags'][:3]]
    write('data/tips.json', json.dumps(out, ensure_ascii=False, separators=(',', ':')))
    return len(out)


def check_by_name(t):
    """Name patterns, used only for label words that have no ingredient row yet."""
    n = norm(t)
    if re.search(r'(cone|conol|siloxane|silane)$', n) or 'siloxane' in n or 'methicone' in n:
        return 'silicone'
    if 'sulfate' in n and 'methosulfate' not in n and 'sulfosuccinate' not in n:
        if re.search(r'(lauryl|laureth|coco|myreth|coceth|decyl)', n):
            return 'sulfate'
    return None

def groups_for(t, i=None):
    """The check groups a single label word belongs to."""
    import watchlist
    i = i if i is not None else lookup(t)
    if i:
        return [k for k, _, _ in CHECK_GROUPS if k in i['_tags']] + [w for w in watchlist.groups(t, i['inci_name'], *i['_aliases']) if w not in i['_tags']]
    g = check_by_name(t)
    return ([g] if g else []) + watchlist.groups(t)


def check_label(items):
    """What a label contains, out of the four groups, and how much of it we could not read."""
    found = {k: [] for k, _, _ in CHECK_GROUPS}   # ingredient rows
    guessed = {k: [] for k, _, _ in CHECK_GROUPS}  # matched by name only
    unknown = 0
    for t in items:
        i = lookup(t)
        if i:
            for k in groups_for(t, i):
                if i not in found[k]:
                    found[k].append(i)
        else:
            unknown += 1
            for g in groups_for(t, None):
                if t not in guessed[g]:
                    guessed[g].append(t)
    return found, guessed, unknown

def check_strip(items, r='', tags=(), js=True):
    """The quick-check strip. items=None when we have not typed the label out yet."""
    if items is None:
        cells = ''.join(
            f'''<div class="chk-item {'is-tag' if k in tags else 'is-unread'}" data-g="{k}"><b>{e(label)}</b>
      <span class="chk-state">{'Tagged in our catalog' if k in tags else 'Not checked'}</span><p>{e(desc)}</p></div>'''
            for k, label, desc in CHECK_GROUPS)
        return f'<div class="chk">{cells}</div><p class="chk-note">We have not typed this label out yet, so this is what our catalog says rather than what the bottle says.</p>'
    found, guessed, unknown = check_label(items)
    cells = ''
    for k, label, desc in CHECK_GROUPS:
        hits = [f'<a href="{r}{i["_slug"]}/">{e(i["_title"])}</a>' for i in found[k]] + [e(t) for t in guessed[k]]
        if hits:
            cells += f'''<div class="chk-item is-yes" data-g="{k}"><b>{e(label)}</b><span class="chk-state">Yes, {len(hits)}</span><p>{', '.join(hits)}</p>
      <button type="button" class="chk-lite" data-g="{k}" aria-pressed="false">Show these</button></div>'''
        else:
            cells += f'''<div class="chk-item is-no" data-g="{k}"><b>{e(label)}</b><span class="chk-state">None found</span><p>{e(desc)}</p></div>'''
    note = f'Based on the {len(items)} ingredients on this label.'
    if unknown:
        note += f' {unknown} of them are not in our library yet, so we cannot say for certain about those.'
    if any(guessed.values()):
        note += ' Some are recognised by the shape of their name and do not have a page yet.'
    more = f'<p class="chk-more"><a href="{r}groups/silicones/">The four kinds of silicone, and what each one does →</a></p>' if found['silicone'] or guessed['silicone'] else ''
    return f'<div class="chk" data-chk>{cells}</div><p class="chk-note">{e(note)}</p>{more}{CHK_JS if js else ""}'


CHK_JS = '''<script>
(function () {
  document.querySelectorAll('.chk-lite').forEach(function (btn) {
    var label = document.querySelector('.inci');
    if (!label) { btn.remove(); return; }
    btn.addEventListener('click', function () {
      var on = btn.getAttribute('aria-pressed') === 'true';
      document.querySelectorAll('.chk-lite').forEach(function (b) {
        b.setAttribute('aria-pressed', 'false');
        b.textContent = 'Show these';
      });
      label.querySelectorAll('.lit').forEach(function (w) { w.classList.remove('lit'); });
      if (on) return;
      btn.setAttribute('aria-pressed', 'true');
      btn.textContent = "Hide";
      var g = btn.dataset.g, first = null;
      label.querySelectorAll('[data-c]').forEach(function (w) {
        if (w.dataset.c.split(' ').indexOf(g) > -1) { w.classList.add('lit'); first = first || w; }
      });
      if (first) first.scrollIntoView({ block: 'center', behavior: 'smooth' });
    });
  });
}());
</script>'''

# Wording that can read as a drug or hair-growth claim in the US. Reported at build time, never changed.
CLAIM_WORDS = re.compile(r'\b(hair[- ]growth|healthier hair growth|grows? hair|follicle\w*|shedding|density|thicker|stimulat\w*|regrow\w*|hair loss|1,?000x)', re.I)

# ---------- page parts ----------
def ordinal(n):
    return {1: '1st', 2: '2nd', 3: '3rd'}.get(n, f'{n}th')

ICON = '<svg width="15" height="15" viewBox="0 0 16 16" aria-hidden="true"><circle cx="7" cy="7" r="5" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M11 11l3.5 3.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>'

QUIZ_URL = 'https://thegoodcoil.com/what-does-my-hair-need'
def utm(url, medium, campaign='jara_beta', content=''):
    """Add tracking to links that leave this site, so each other site can see where a visit came from."""
    base, _, frag = url.partition('#')
    q = f'utm_source=library&utm_medium={medium}&utm_campaign={campaign}' + (f'&utm_content={content}' if content else '')
    out = base + ('&' if '?' in base else '?') + q
    return out + ('#' + frag if frag else '')

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
<div class="eco-bar"><nav aria-label="The Good Coil sites"><a href="{utm('https://thegoodcoil.com', 'utility_bar', 'ecosystem')}">The Good Coil</a><a href="{r}" aria-current="true">Ingredient Library</a><a href="{utm('https://itsjara.com', 'utility_bar', 'jara_beta')}">JARA Hair Tracker</a></nav></div>
<header class="site-header">
  <a href="{r}" class="wordmark" aria-label="The Good Coil Library home"><span class="brand-symbol" aria-hidden="true">◎</span> the<span class="brand-amp">good</span>coil<span class="wordmark-sub">Library</span></a>
  <nav class="nav" aria-label="Main">
    <a href="{r}#find" class="hide-sm"{cur('home')}>Label Decoder</a>
    <a href="{r}ingredients/" class="hide-sm"{cur('ingredients')}>Ingredients</a>
    <a href="{r}products/" class="hide-sm"{cur('products')}>Products</a>
    <a href="{r}plans/" class="hide-sm"{cur('plans')}>Hair Edits</a>
    <a class="nav-cta" href="{utm(QUIZ_URL, 'nav_cta', 'hair_quiz')}">Take Hair Quiz</a>
  </nav>
</header>
<nav class="subnav" aria-label="Library sections"><a href="{r}#find">Label Decoder</a><a href="{r}ingredients/">Ingredients</a><a href="{r}products/">Products</a><a href="{r}plans/">Hair Edits</a></nav>
<main id="main" class="wrap">
{body}
</main>
<footer class="site-footer">
  <form class="foot-search" action="{r}ingredients/" method="get" role="search"><label for="fq">Look up an ingredient</label><input id="fq" name="q" type="search" placeholder="Try glycerin, BTAC or shea" autocomplete="off"><button type="submit">Search</button></form>
  <div><a href="{r}" class="wordmark"><span class="brand-symbol" aria-hidden="true">◎</span> the<span class="brand-amp">good</span>coil</a><p>Good knowledge. Happy hair.<br>A journey that's yours.</p></div>
  <nav class="footer-links" aria-label="Footer"><a href="{r}ingredients/">All ingredients</a><a href="{r}plans/">Hair edits</a><a href="{r}products/">Products</a><a href="{r}properties/">By property</a><a href="{r}groups/">Ingredient families</a><a href="{r}label-check/">Parabens &amp; phthalates</a><a href="{r}about/">How we write</a><a href="{r}about/#affiliate">Affiliate disclosure</a><a href="{utm('https://thegoodcoil.com', 'footer', 'ecosystem')}">The Good Coil</a><a href="{utm('https://itsjara.com', 'footer')}">JARA hair journal</a></nav>
  <div class="footer-bottom"><span>© {datetime.date.today().year} The Good Coil</span><span>Descriptions, not verdicts: every head of hair is different.</span><span>Educational guidance, not medical advice.</span></div>
</footer>
<script src="{r}assets/tips.js" data-root="{r}" defer></script>
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
    import watchlist
    r = '../'
    hits = hits_for(g)
    title = g['_title']
    # The page's H1 is the common name from the sheet (display_name wins if one is set).
    h1 = col(g, 'display_name') or (g.get('common_name') or '').strip() or title
    summary = (g.get('plain_english_summary') or '').strip()
    deep = (g.get('how_it_works_deep_dive') or '').strip()
    howto = (g.get('how_to_use_and_pair') or '').strip()
    evid = (g.get('evidence_and_nuance') or '').strip()
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
    if deep:
        sections.append(f'''<section class="section" id="why">
    <div class="intro"><span class="eyebrow">The science, simplified</span><h2>Why your curls care</h2></div>
    <div class="prose"><p>{e(deep)}</p></div>
  </section>''')
    if g.get('buildup_sensitivity_notes') or howto:
        good = f'<h3>Good to know</h3><p class="note">{e(g["buildup_sensitivity_notes"])}</p>' if g.get('buildup_sensitivity_notes') else ''
        use = f'<h3>How to get the most out of it</h3><p>{e(howto)}</p>' if howto else ''
        sections.append(f'''<section class="section" id="good">
    <div class="intro"><span class="eyebrow">{'Good to know and how to use it' if howto else 'Good to know'}</span></div>
    <div class="prose">{good}{use}</div>
  </section>''')
    hair = col(g, 'hair_type_notes', 'hair_type_porosity_fit')
    if hair:
        sections.append(f'''<section class="section" id="hair">
    <div class="intro"><span class="eyebrow">Hair types</span><h2>Ideal for</h2></div>
    <div class="hair"><p>{e(hair)}</p><small>General patterns from our research, not rules. Hair of the same type can respond differently, so your own results count most.</small></div>
  </section>''')

    if evid:
        tag, _, rest = evid.partition('. ')
        if rest and len(tag) <= 70 and re.match(r'(Established|Cosmetic|Emerging|Promising|Regulated|Universal|Standard)', tag):
            ev = f'<p><span class="evi">{e(tag)}</span> {e(rest)}</p>'
        else:
            ev = f'<p>{e(evid)}</p>'
        sections.append(f'''<section class="section" id="research">
    <div class="intro"><span class="eyebrow">Honest context</span><h2>What the research says</h2></div>
    <div class="prose">{ev}</div>
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
        rows = ''.join(f'''<li id="p{k}"><span class="pos">{n}<small>of {len(items)}</small></span><div><span class="step">{e(STEP.get(p.get('step', ''), p.get('step', '').capitalize()))}</span><a href="{r}products/{p.get('_slug', '')}/"><b>{e(p.get('brand', '').strip())}</b> {e(p.get('name', '').strip())}</a></div></li>''' for k, (p, items, n) in enumerate(hits))
        sections.append(f'''<section class="across" id="across">
    <div class="intro">
      <span class="eyebrow">Found in these products</span>
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

    ORDER = ['id="why"', 'id="research"', 'id="good"', 'id="across"', 'id="hair"']
    def rank(h):
        for k, o in enumerate(ORDER):
            if o in h[:80]:
                return k
        return len(ORDER)
    sections.sort(key=rank)
    links = ''.join([
        '<a href="#why">Why your curls care</a>' if deep else '',
        '<a href="#research">The research</a>' if evid else '',
        '<a href="#good">Good to know</a>' if (g.get('buildup_sensitivity_notes') or howto) else '',
        f'<a href="#across">Found in {len(hits)} product{"s" if len(hits) != 1 else ""}</a>' if hits else '',
        '<a href="#hair">Ideal for</a>' if hair else '',
    ])
    names = []
    for n in [g['inci_name']] + g['_aliases']:
        if norm(n) != norm(h1) and norm(n) not in [norm(x) for x in names]:
            names.append(n)
    aka = f'<p class="aka"><em>also on labels as</em> {" · ".join(e(a) for a in names)}</p>' if names else ''
    body = f'''  <a class="crumb" href="{r}ingredients/">← All ingredients</a>
  <section class="first">
    <div class="name">
      <span class="eyebrow"><span class="little-dot"></span>{e(g.get('category', ''))}</span>
      <h1>{e(h1)}</h1>
      {aka}
      <p class="lead">{e(summary or g.get('what_it_does', ''))}</p>
      {watchlist.ingredient_note(g)}
      <div class="meta">{tags}{links}</div>
    </div>
    {hero}
  </section>
  {''.join(sections)}
  <p class="source"><span>Source: {e(g['_source'])} · Ref {e(g['id'])}</span><a href="{r}data/ingredients.json">Get this as data (JSON)</a><a href="{r}about/">How we write these</a></p>
<script>if(matchMedia('(max-width:760px)').matches)document.querySelectorAll('.inci').forEach(p=>{{const b=p.querySelector('.more-btn');if(!b)return;p.classList.add('clamped');b.hidden=false;b.onclick=()=>{{p.classList.remove('clamped');b.remove()}}}})</script>'''
    desc = f"{title} ({g['inci_name']}) in hair products: what it is, what it does, how it's written on labels, and notes for different hair."
    write(f"{g['_slug']}/index.html", shell(r, f"{title} in hair products: what it is and what it does · The Good Coil Library", desc, body, f"{g['_slug']}/"))
    return len(hits)

# ---------- index ----------
def index_page(counts):
    tags = sorted({t for i in ing for t in i['_tags']}, key=lambda t: (-sum(t in i['_tags'] for i in ing), t))
    chips = '<button class="chip" type="button" aria-pressed="true" data-tag="">All</button>' + ''.join(
        f'<button class="chip" type="button" aria-pressed="false" data-tag="{e(t)}">{e(t)}</button>' for t in tags)
    items = ''.join(
        f'''<li data-tags="{e('|'.join(i['_tags']))}" data-q="{e(norm(' '.join([i['inci_name'], i.get('common_name', '')] + i['_aliases'])))}"><a href="../{i['_slug']}/"><b>{e(i['_title'])}</b><span>{e(', '.join(i['_tags']) or i.get('category', ''))}</span>{f'<i>{counts[i["id"]]} label{"s" if counts[i["id"]] != 1 else ""}</i>' if counts[i['id']] else ''}</a></li>'''
        for i in sorted(ing, key=lambda i: i['_title'].lower()))
    body = f'''  <section class="home-head">
    <div><a class="crumb" href="../">← Home</a><span class="eyebrow" style="margin-top:22px"><span class="little-dot"></span>Ingredient library</span>
    <h1>All ingredients</h1></div>
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
const pq=new URLSearchParams(location.search).get('q');if(pq){{q.value=pq;run()}}
if(location.hash==='#find')q.focus();}})();
</script>'''
    write('ingredients/index.html', shell('../', 'All ingredients · The Good Coil Library', 'A library of hair-care ingredients, each described by what it is and what it does, with notes for different hair. No scores, no verdicts.', body, 'ingredients/', 'ingredients'))

# ---------- properties ----------
def property_pages():
    tags = sorted({t for i in ing for t in i['_tags']}, key=lambda t: (-sum(t in i['_tags'] for i in ing), t))
    rows = ''.join(f'''<li><a href="{prop_slug(t)}/"><h2>{e(t)}</h2><p>{e(PROPS.get(t, ''))}</p><span>{sum(t in i['_tags'] for i in ing)}</span></a></li>''' for t in tags)
    import groups as GRP
    fams = [(f, sl, n) for f, sl, n in (GRP.built or [])]
    fam_html = ''
    if fams:
        cards = ''.join(
            f'<li><a href="../groups/{sl}/"><h2>{e(f)}</h2>'
            f'<p>{e(GRP.INTRO.get(f, ("", ""))[0])}</p><span>{n} kinds</span></a></li>'
            for f, sl, n in fams)
        fam_html = ('<section class="fam"><span class="eyebrow">Families</span>'
                    '<p class="fam-lead">Some ingredients split into kinds that behave differently. '
                    'These pages take one family apart.</p>'
                    f'<ul class="prop-list fam-list">{cards}</ul></section>')
    body = f'''  <a class="crumb" href="../ingredients/">← All ingredients</a>
  <section class="page-head"><span class="eyebrow"><span class="little-dot"></span>By property</span><h1>What ingredients do</h1>
  <p>Properties group ingredients by the job they do in a product. Many ingredients do more than one job, so they show up in more than one group.</p></section>
  {fam_html}
  <ul class="prop-list">{rows}</ul>'''
    write('properties/index.html', shell('../', 'Ingredients by property · The Good Coil Library', 'Hair-care ingredients grouped by what they do: humectants, oils and butters, proteins, film-formers and more.', body, 'properties/', 'props'))
    for t in tags:
        members = sorted([i for i in ing if t in i['_tags']], key=lambda i: i['_title'].lower())
        items = ''.join(f'''<li><a href="../../{i['_slug']}/"><b>{e(i['_title'])}</b><span>{e(i.get('category', ''))}</span></a></li>''' for i in members)
        body = f'''  <a class="crumb" href="../">← All properties</a>
  <section class="page-head"><span class="eyebrow"><span class="little-dot"></span>Property</span><h1>{e(t.capitalize())}</h1><p>{e(PROPS.get(t, ''))}</p></section>
  <p class="count-line">{len(members)} ingredients</p>
  <ul class="ing-list">{items}</ul>'''
        write(f'properties/{prop_slug(t)}/index.html', shell('../../', f'{t.capitalize()} ingredients in hair care · The Good Coil Library', PROPS.get(t, f'{t} ingredients'), body, f'properties/{prop_slug(t)}/', 'props'))
    return tags

# ---------- about ----------
def about_page():
    body = f'''  <a class="crumb" href="../">← Home</a>
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
    write('about/index.html', shell('../', 'How we write these · The Good Coil Library', 'How The Good Coil describes hair-care ingredients: descriptions, not verdicts; sources; affiliate disclosure.', body, 'about/'))

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
            'good_to_know': i.get('buildup_sensitivity_notes', ''),
            'plain_english_summary': i.get('plain_english_summary', ''), 'how_it_works': i.get('how_it_works_deep_dive', ''),
            'how_to_use_and_pair': i.get('how_to_use_and_pair', ''), 'evidence_and_nuance': i.get('evidence_and_nuance', ''), 'source': i['_source'], 'labels_seen_on': counts[i['id']],
        } for i in ing],
    }
    write('data/ingredients.json', json.dumps(out, ensure_ascii=False, indent=1))

def extras(tags, plan_urls=()):
    write('CNAME', 'library.thegoodcoil.com\n')
    write('.nojekyll', '')
    write('robots.txt', f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
    urls = [''] + [f"{i['_slug']}/" for i in ing] + ['properties/'] + [f'properties/{prop_slug(t)}/' for t in tags] + ['ingredients/', 'about/', 'plans/', 'products/', 'label-check/'] + [f"products/{p['_slug']}/" for p in products] + list(plan_urls)
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
          ''.join(f'  <url><loc>{SITE}/{u}</loc></url>\n' for u in urls) + '</urlset>\n')
    write('favicon.svg', '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="#DCF473"/><circle cx="16" cy="16" r="10" fill="none" stroke="#432731" stroke-width="3"/><circle cx="16" cy="16" r="4" fill="#432731"/></svg>')
    body = '''  <section class="page-head"><span class="eyebrow"><span class="little-dot"></span>Not found</span><h1>That page isn't here</h1>
  <p>The ingredient may have a different name, or it isn't in the library yet. <a class="crumb" href="/">Search all ingredients</a></p></section>'''
    write('404.html', shell('/', 'Page not found · The Good Coil Library', 'Page not found.', body, '404.html'))

def checks(counts):
    notes = []
    for i in ing:
        text = ' '.join(i.get(k, '') for k in ('common_name', 'category', 'what_it_does', 'hair_type_porosity_fit', 'hair_type_notes', 'buildup_sensitivity_notes', 'plain_english_summary', 'how_it_works_deep_dive', 'how_to_use_and_pair', 'evidence_and_nuance'))
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
    names = [f"- {i['id']} {i.get('inci_name','')}: H1 \"{col(i, 'display_name') or (i.get('common_name') or '').strip() or i['_title']}\" (from {'display_name' if col(i, 'display_name') else 'common_name'}); sheet columns: {len(i)}" for i in ing if 'Behentrim' in i['inci_name'] or 'BTMS' in (i.get('common_name') or '')]
    cats = {}
    for i in ing:
        cats.setdefault((i.get('category') or '').strip() or '(none)', []).append(i['id'])
    catlines = [f'- {c}: {len(v)}' for c, v in sorted(cats.items(), key=lambda kv: -len(kv[1]))]
    report = ['## Build report', f'{len(ing)} ingredients, {len(labels)} labels, {recognised} of {total} label entries recognised.', '',
              '### Page names (sample)'] + names + ['', '### Ingredients per category'] + catlines + ['', '### Wording to review (not changed)'] + (notes or ['- none']) + ['', '### Most common label words without an ingredient row'] + \
             [f'- {k} ({n})' for k, n in sorted(unknown.items(), key=lambda kv: -kv[1])[:60]]
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
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    counts = {i['id']: ingredient_page(i) for i in ing}
    index_page(counts)
    tips_json()
    write('assets/tips.js', open(os.path.join(ROOT, 'src', 'tips.js'), encoding='utf-8').read())
    write('assets/guide.js', open(os.path.join(ROOT, 'src', 'guide.js'), encoding='utf-8').read())
    import groups as GRP_PRE
    GRP_PRE.build()
    tags = property_pages()
    about_page()
    data_files(counts)
    sys.modules.setdefault('build', sys.modules[__name__])
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import plans
    _, plan_notes = plans.build()          # earlier layout, now under /test-program/, still writes data/plans.json
    import guide
    guides = guide.build()                 # the live hair plans
    plan_urls = [f"plans/{g['slug']}/" for g in guides]
    import products as PR
    PR.build()
    import home
    home.build()                                            # the homepage at /
    home.build(out='previous-home/', root='../', quiet=False)  # the first one, noindex
    import home_test
    home_test.build(out='home-test/', root='../', test=True)   # the standalone quiet page
    import test_program  # TEST layout at /test-program/
    test_program.build()
    import programs_full  # TEST pages at /programs/ (noindex, kept out of the sitemap)
    programs_full.build()
    import guided_test  # TEST guided steps + email gate (noindex)
    guided_test.build()
    import watchlist
    watchlist.build()
    import ecosystem_tests  # TEST JARA landing + Good Coil homepage (noindex)
    ecosystem_tests.build()
    extras(tags, plan_urls)
    checks(counts)
    text = '### Hair edits\n' + (f'{len(plan_urls)} plans built.\n' + '\n'.join(plan_notes) if plan_urls else 'No programs found.') + '\n'
    print(text)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as fh:
            fh.write(text)

if __name__ == '__main__':
    main()

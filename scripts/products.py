"""Products: /products/ list, one page per product (tools are listed only), data/catalog.json.

Reads the catalog sheet (data/catalog.csv). Published fields: name, brand, kind, step, properties
and the ingredient list. A product page shows its shop link (often an affiliate link) as a button
with a short disclosure; links are left out of catalog.json. Notes and barcodes are never published.
"""
import json, os, shutil
import build as B
import similar as SIM
import dupes as DUP

# Product photos: src/products/<catalog id>.webp (800x1000, 4:5). A product with a file gets a photo
# on its page and as its sharing image; one without keeps the text-only layout.
PHOTO_DIR = os.path.join(B.ROOT, 'src', 'products')

def photo_of(p):
    fn = f"{p['id']}.webp"
    return fn if os.path.exists(os.path.join(PHOTO_DIR, fn)) else None

e = B.e
STEP_ORDER = ['cleanse', 'condition', 'treatment', 'leave-in', 'style', 'seal', 'tool']
STEP_LABEL = {'cleanse': 'Cleanse', 'condition': 'Condition', 'treatment': 'Treat', 'leave-in': 'Leave-in',
              'style': 'Style', 'seal': 'Seal', 'tool': 'Tools'}

def step_of(p):
    return 'tool' if (p.get('kind') == 'tool' or p.get('step') == 'tool') else (p.get('step') or '').lower()

def props_of(p):
    return [t.strip() for t in (p.get('properties') or '').split(',') if t.strip() and t.strip().lower() != 'none']

def items_of(p):
    return B.split_label(p['full ingredient list']) if p.get('full ingredient list') else []

READ_MORE = '<a class="read-more" href="#check"><u>Read more</u><span aria-hidden="true">&#8595;</span></a>'

def shop_link(p, r):
    """The shop button and its affiliate note, or '' when the row has no usable https link."""
    url = (p.get('link') or '').strip()
    if not url.lower().startswith('https://'):
        return f'<div class="shop"><div class="shop-row">{READ_MORE}</div></div>'
    host = url.split('/')[2].lower()
    amazon = 'amazon.' in host or host in ('amzn.to', 'a.co') or host.startswith('link.amazon')
    where = 'Shop on Amazon' if amazon else f"Shop at {(p.get('brand') or '').strip() or 'the brand'}"
    note = ('Affiliate link. As an Amazon Associate, The Good Coil earns from qualifying purchases, at no extra cost to you.'
            if amazon else 'Some shop links on The Good Coil are affiliate links: we may earn a small commission at no extra cost to you.')
    return (f'<div class="shop"><div class="shop-row"><a class="shop-btn" href="{e(url)}" target="_blank" rel="sponsored nofollow noopener">{e(where)} <span aria-hidden="true">&#8599;</span></a>{READ_MORE}</div>'
            f'<p class="shop-note">{note} <a href="{r}about/#affiliate">Disclosure</a></p></div>')

SIMILAR = {}  # product id -> similar-label matches, filled in build()
DUPE_PAGES = {}  # product id -> its dupe page path (scripts/dupes.py)
DUPE_URLS = []  # for the sitemap

def product_page(p):
    r = '../../'
    items = items_of(p)
    step = step_of(p)
    strip = B.check_strip(items if items else None, r, props_of(p))
    tags = ''.join(f'<a class="tag" href="{r}properties/{B.prop_slug(t)}/">{e(t)}</a>' for t in props_of(p))
    photo = photo_of(p)
    pin = f'<img class="label-photo" src="{r}assets/products/{photo}" alt="" width="800" height="1000">' if photo else ''
    if items:
        found = [(t, B.lookup(t)) for t in items]
        def word(t, i):
            g = B.groups_for(t, i)
            a = f' data-c="{" ".join(g)}"' if g else ''
            return f'<a href="{r}{i["_slug"]}/"{a}>{e(t)}</a>' if i else (f'<span{a}>{e(t)}</span>' if g else e(t))
        words = ', '.join(word(t, i) for t, i in found)
        known = [i for _, i in found if i]
        groups = {}
        for ing in {id(x): x for x in known}.values():
            for t in (ing['_tags'] or [ing.get('category', 'Other')]):
                groups.setdefault(t, []).append(ing)
        def ing_link(i):
            return f'<a href="{r}{i["_slug"]}/">{e(i["_title"])}</a>'
        group_rows = ''.join(
            f'<li><a class="tag" href="{r}properties/{B.prop_slug(t)}/">{e(t)}</a><span>{", ".join(ing_link(i) for i in v)}</span></li>'
            for t, v in sorted(groups.items(), key=lambda kv: -len(kv[1])))
        inside = f'''<figure class="label label-product" aria-labelledby="lbl">
      <div class="label-top"><span>Ingredients · as printed</span><b id="lbl">{e(B.product_full_name(p))}</b></div>
      <p class="inci">{pin}{words}.</p>
      <figcaption class="label-foot"><span><b>{len(items)} ingredients</b>, {len({id(i) for i in known})} with their own page.</span><span>Dotted words have their own page.</span></figcaption>
    </figure>'''
        grouped = f'''<section class="section" id="groups">
    <div class="intro"><span class="eyebrow">By property</span><h2>What these ingredients do</h2><p>Only the ingredients in our library are grouped here. We add more every week, so an empty group never means "none".</p></div>
    <ul class="groups">{group_rows or '<li>None of these ingredients are in our library yet.</li>'}</ul>
  </section>''' if items else ''
    else:
        inside = f'''<figure class="label label-empty" aria-labelledby="lbl">
      <div class="label-top"><span>Ingredients</span><b id="lbl">{e(B.product_full_name(p))}</b></div>
      <p class="inci">We haven't added this label yet.</p>
      <figcaption class="label-foot"><span>Labels are read by hand from brand sites and packaging.</span></figcaption>
    </figure>'''
        grouped = ''
    side = f'''<div class="meta">{tags}</div>
      {shop_link(p, r)}'''
    body = f'''  <a class="crumb" href="../">← All products</a>
  <section class="first">
    <div class="name">
      <span class="eyebrow"><span class="little-dot"></span>{e(STEP_LABEL.get(step, step.capitalize() or 'Product'))}</span>
      <h1 class="prod-h1{' prod-h1-long' if len(p.get('name', '').strip()) > 32 else ''}">{e(p.get('name', '').strip())}</h1>
      <p class="aka"><em>by</em> {e(p.get('brand', '').strip())}</p>
      {side if not photo else f'<div class="prod-row{' pinned' if items else ''}"><figure class="prod-photo"><img src="{r}assets/products/{photo}" alt="{e(B.product_full_name(p))}" width="800" height="1000"></figure><div class="prod-side">{side}</div></div>'}
    </div>
    {inside}
  </section>
  <section class="section chk-sec" id="check">
    <div class="intro"><span class="eyebrow">Quick check</span><h2>Does it have…</h2></div>
    <div>{strip}</div>
  </section>
  {grouped}
  {SIM.section(p, SIMILAR.get(p['id']), step, r)}
  {f'<p class="dupe-more"><a href="{r}{DUPE_PAGES[p["id"]]}">See the full comparison: closest wash and closest overall <span aria-hidden="true">&#8594;</span></a></p>' if p['id'] in DUPE_PAGES else ''}
  <p class="source"><span>The Good Coil catalog · Ref {e(p['id'])}. Properties come from our catalog tags and describe what the product contains, not how it will work on your hair.</span><a href="{r}data/catalog.json">Get this as data (JSON)</a><a href="{r}about/">How we write these</a></p>'''
    name = B.product_full_name(p)
    desc = f"What's inside {name}: the full ingredient list, decoded." if items else f"{name} in The Good Coil catalog."
    B.write(f"products/{p['_slug']}/index.html", B.shell(r, f"{name}: ingredients · The Good Coil", desc, body, f"products/{p['_slug']}/", 'products', image=f"assets/products/{photo}" if photo else None))

def index_page(prods):
    steps = [s for s in STEP_ORDER if any(step_of(p) == s for p in prods)]
    chips = '<button class="chip" type="button" aria-pressed="true" data-tag="">All</button>' + ''.join(
        f'<button class="chip" type="button" aria-pressed="false" data-tag="{s}">{STEP_LABEL[s]}</button>' for s in steps)
    def checks_of(p):
        its = items_of(p)
        if not its:
            return ''
        f, g, _ = B.check_label(its)
        return ' '.join(k for k, _, _ in B.CHECK_GROUPS if f[k] or g[k])

    def row(p):
        has = bool(items_of(p))
        inner = f'''<b>{e(p.get('name', '').strip())}</b><span>{e(p.get('brand', '').strip())} · {e(STEP_LABEL.get(step_of(p), step_of(p)))}</span>{'<i>label read</i>' if has else ''}'''
        q = B.norm(f"{p.get('brand', '')} {p.get('name', '')}")
        link = f'<a href="{p["_slug"]}/">{inner}</a>' if step_of(p) != 'tool' else f'<div class="nolink">{inner}</div>'
        return f'<li data-tags="{step_of(p)}" data-q="{e(q)}" data-label="{1 if has else 0}" data-checks="{checks_of(p)}">{link}</li>'
    rows = ''.join(row(p) for p in sorted(prods, key=lambda p: (p.get('brand', '').lower(), p.get('name', '').lower())))
    n_lab = sum(1 for p in prods if items_of(p))
    body = f'''  <section class="page-head"><span class="eyebrow"><span class="little-dot"></span>The Good Coil catalog</span><h1>Products</h1>
  <p>Every product in our catalog, with what's inside when we've read its label ({n_lab} of {len(prods)} so far). This is a reference list, not a ranking.</p></section>
  <section class="finder" id="find" aria-label="Find a product">
    <label for="q">Search by product or brand</label>
    <input id="q" type="search" placeholder="Try Pattern, leave-in or curl cream" autocomplete="off">
    <div class="chips" role="group" aria-label="Filter by step">{chips}</div>
    <div class="chips chips-has" role="group" aria-label="Filter by what the label contains"><button class="chip" type="button" aria-pressed="false" data-has="protein">Has protein</button><button class="chip" type="button" aria-pressed="false" data-has="ceramides">Has ceramides</button><button class="chip" type="button" aria-pressed="false" data-has="silicone">Has silicones</button><button class="chip" type="button" aria-pressed="false" data-has="sulfate">Has sulfates</button></div>
    <label class="check"><input type="checkbox" id="lab"> Only products with an ingredient list</label>
  </section>
  <p class="count-line" id="count" aria-live="polite">{len(prods)} products</p>
  <ul class="ing-list" id="list">{rows}</ul>
  <p class="empty-msg" id="none" hidden>Nothing matches. Try the brand name, or clear the filters.</p>
<script>
(()=>{{const q=document.getElementById('q'),lab=document.getElementById('lab'),list=[...document.querySelectorAll('#list li')],chips=[...document.querySelectorAll('.chips:not(.chips-has) .chip')],hasChips=[...document.querySelectorAll('.chips-has .chip')],count=document.getElementById('count'),none=document.getElementById('none');let tag='',has=new Set();
const n=s=>s.toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
function run(){{const v=n(q.value);let k=0;list.forEach(li=>{{const c=(li.dataset.checks||'').split(' ');const ok=(!v||li.dataset.q.includes(v))&&(!tag||li.dataset.tags===tag)&&(!lab.checked||li.dataset.label==='1')&&[...has].every(x=>c.includes(x));li.hidden=!ok;if(ok)k++}});count.textContent=k+' of {len(prods)} products';none.hidden=k>0}}
q.addEventListener('input',run);lab.addEventListener('change',run);chips.forEach(c=>c.addEventListener('click',()=>{{tag=c.dataset.tag;chips.forEach(x=>x.setAttribute('aria-pressed',x===c));run()}}));
hasChips.forEach(c=>c.addEventListener('click',()=>{{const k=c.dataset.has;has.has(k)?has.delete(k):has.add(k);c.setAttribute('aria-pressed',has.has(k));run()}}));}})();
</script>'''
    B.write('products/index.html', B.shell('../', 'Products: what\'s inside · The Good Coil', 'Every product in The Good Coil catalog, with its ingredient list decoded.', body, 'products/', 'products'))

def build():
    prods = B.products
    if os.path.isdir(PHOTO_DIR):
        os.makedirs(os.path.join(B.OUT, 'assets', 'products'), exist_ok=True)
        for f in os.listdir(PHOTO_DIR):
            if f.endswith('.webp'):
                shutil.copy(os.path.join(PHOTO_DIR, f), os.path.join(B.OUT, 'assets', 'products', f))
    try:
        SIMILAR.update(SIM.build_index(prods, step_of, items_of))
    except Exception as err:  # never let this section stop the rest of the site from publishing
        print(f'Warning: similar labels skipped ({err!r})')
    try:
        DUPE_PAGES.update(DUP.build(prods, step_of, items_of))
        DUPE_URLS.extend(DUPE_PAGES.values())
    except Exception as err:  # never let these pages stop the rest of the site from publishing
        print(f'Warning: dupe pages skipped ({err!r})')
    for p in prods:
        if step_of(p) != 'tool':
            product_page(p)
            # Short, permanent address by catalog id (/p/tgc-001/) so JARA can link a Stash product
            # to its page without knowing the slug. Keeps the query string (UTM tags, visitor ids).
            dest = f"../../products/{p['_slug']}/"
            B.write(f"p/{p['id'].lower()}/index.html", f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>{e(B.product_full_name(p))}</title>
<link rel="canonical" href="{B.SITE}/products/{p['_slug']}/"><meta name="robots" content="noindex">
<script>location.replace({json.dumps(dest)} + location.search + location.hash)</script>
<noscript><meta http-equiv="refresh" content="0; url={dest}"></noscript></head>
<body><a href="{dest}">Continue</a></body></html>
''')
    index_page(prods)
    data = {
        'generated': B.datetime.datetime.now(B.datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source': 'The Good Coil product catalog',
        'products': [{'id': p['id'], 'slug': p['_slug'], 'url': f"{B.SITE}/products/{p['_slug']}/" if step_of(p) != 'tool' else None,
                      'name': p.get('name', '').strip(), 'brand': p.get('brand', '').strip(), 'kind': p.get('kind') or 'product',
                      'step': step_of(p), 'properties': props_of(p), 'ingredients': items_of(p),
                      'ingredient_ids': [i['id'] for i in (B.lookup(t) for t in items_of(p)) if i],
                      'similar': [q['id'] for q, _, _, _ in SIMILAR.get(p['id'], [])]} for p in prods],
    }
    B.write('data/catalog.json', json.dumps(data, ensure_ascii=False, indent=1))

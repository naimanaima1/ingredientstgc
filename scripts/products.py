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
  {SIM.section(p, SIMILAR.get(p['id']), step, r, items_of)}
  {f'<p class="dupe-more"><a href="{r}{DUPE_PAGES[p["id"]]}">See the full comparison: closest wash and closest overall <span aria-hidden="true">&#8594;</span></a></p>' if p['id'] in DUPE_PAGES else ''}
  <p class="source"><span>The Good Coil catalog · Ref {e(p['id'])}. Properties come from our catalog tags and describe what the product contains, not how it will work on your hair.</span><a href="{r}data/catalog.json">Get this as data (JSON)</a><a href="{r}about/">How we write these</a></p>'''
    name = B.product_full_name(p)
    desc = f"What's inside {name}: the full ingredient list, decoded." if items else f"{name} in The Good Coil catalog."
    B.write(f"products/{p['_slug']}/index.html", B.shell(r, f"{name}: ingredients · The Good Coil", desc, body, f"products/{p['_slug']}/", 'products', image=f"assets/products/{photo}" if photo else None))

# Short names for the "Label has" filters, from the Label Decoder's groups (build.CHECK_GROUPS).
HAS_LABEL = {'humectant': 'Water binders', 'slip/detangler': 'Slip', 'butter/oil': 'Oils & butters', 'protein': 'Protein',
             'ceramides': 'Ceramides', 'peptide': 'Peptides', 'scalp-active': 'Scalp actives', 'silicone': 'Silicones',
             'sulfate': 'Sulfates', 'strong-cleanser': 'Non-sulfate cleansers', 'paraben': 'Parabens', 'phthalate': 'Phthalates'}


def index_page(prods):
    steps = [s for s in STEP_ORDER if any(step_of(p) == s for p in prods)]
    chips = '<button class="chip" type="button" aria-pressed="true" data-tag="">All</button>' + ''.join(
        f'<button class="chip" type="button" aria-pressed="false" data-tag="{s}">{STEP_LABEL[s]}</button>' for s in steps)
    def checks_of(p):
        its = items_of(p)
        if not its:
            return ''
        f, g, _ = B.check_label(its)
        return ' '.join(k.replace('/', '-') for k, _, _ in B.CHECK_GROUPS if f[k] or g[k])

    def ings_of(p):
        """One entry per label word, in label order: the word plus the library's names for it,
        so 'hyaluronic acid' finds Sodium Hyaluronate. Entries are separated by '|'."""
        out = []
        for t in items_of(p):
            i = B.lookup(t)
            names = [t] + ([i['inci_name'], i.get('common_name') or ''] + i['_aliases'] if i else [])
            out.append(' '.join(dict.fromkeys(B.norm(x) for x in names if x)))
        return '|'.join(out)

    def row(p):
        has = bool(items_of(p))
        inner = f'''<b>{e(p.get('name', '').strip())}</b><span>{e(p.get('brand', '').strip())} · {e(STEP_LABEL.get(step_of(p), step_of(p)))}</span>{'<i>label read</i>' if has else ''}<em class="ing-hit" hidden></em>'''
        q = B.norm(f"{p.get('brand', '')} {p.get('name', '')}")
        link = f'<a href="{p["_slug"]}/">{inner}</a>' if step_of(p) != 'tool' else f'<div class="nolink">{inner}</div>'
        return f'<li data-tags="{step_of(p)}" data-q="{e(q)}" data-label="{1 if has else 0}" data-checks="{checks_of(p)}" data-ings="{e(ings_of(p))}">{link}</li>'
    rows = ''.join(row(p) for p in sorted(prods, key=lambda p: (p.get('brand', '').lower(), p.get('name', '').lower())))
    n_lab = sum(1 for p in prods if items_of(p))
    has_chips = ''.join(
        f'<button class="chip chip3" type="button" data-has="{k.replace("/", "-")}" data-name="{e(HAS_LABEL.get(k, lbl))}" data-state="">{e(HAS_LABEL.get(k, lbl))}</button>'
        for k, lbl, _ in B.CHECK_GROUPS)
    body = f'''  <section class="page-head"><span class="eyebrow"><span class="little-dot"></span>The Good Coil catalog</span><h1>Products</h1>
  <p>Every product in our catalog, with what's inside when we've read its label ({n_lab} of {len(prods)} so far). This is a reference list, not a ranking.</p></section>
  <section class="finder" id="find" aria-label="Find a product">
    <label for="q">Search by product or brand</label>
    <input id="q" type="search" placeholder="Try Pattern, leave-in or curl cream" autocomplete="off">
    <div class="chips" role="group" aria-label="Filter by step">{chips}</div>
    <div class="finder-ing">
      <label for="ing">Has these ingredients</label>
      <div class="ing-row"><input id="ing" type="search" placeholder="Try hyaluronic acid, then ceramide" autocomplete="off" enterkeyhint="done"><button class="btn-add" id="ing-add" type="button">Add</button></div>
      <p class="finder-hint" id="ing-hint">Add as many as you like. Products need all of them. Other names for the same ingredient count too.</p>
      <ul class="ing-tokens" id="tokens" aria-label="Ingredients you added"></ul>
    </div>
    <fieldset class="chips chips-has">
      <legend>What the label has <span>Tap once for has, twice for doesn't have, again to clear</span></legend>
      {has_chips}
    </fieldset>
    <label class="check"><input type="checkbox" id="lab"> Only products with an ingredient list</label>
    <p class="finder-share"><button class="btn-link" id="clear" type="button" hidden>Clear all filters</button><button class="btn-link" id="share" type="button" hidden>Copy a link to this search</button><span id="copied" role="status"></span></p>
  </section>
  <p class="count-line" id="count" aria-live="polite">{len(prods)} products</p>
  <ul class="ing-list" id="list">{rows}</ul>
  <p class="empty-msg" id="none" hidden>Nothing matches. Try fewer filters, another name for the ingredient, or clear the filters.</p>
<script>
(()=>{{const $=id=>document.getElementById(id);const q=$('q'),lab=$('lab'),ing=$('ing'),tokEl=$('tokens'),list=[...document.querySelectorAll('#list li')],chips=[...document.querySelectorAll('.chips:not(.chips-has) .chip')],hasChips=[...document.querySelectorAll('.chips-has .chip')],count=$('count'),none=$('none'),share=$('share'),clear=$('clear'),copied=$('copied');
let tag='',state={{}},toks=[];const TOTAL={len(prods)};
const n=s=>s.toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
const STOP=new Set(['acid','extract','oil','the','and']);
function core(w){{return w.length>=7?w.slice(0,w.length-2):w}}
function hit(entries,t){{for(let i=0;i<entries.length;i++){{const en=entries[i];if(en.includes(t))return i;}}
const ws=t.split(' ').filter(w=>w&&!STOP.has(w)).map(core);if(!ws.length)return -1;
for(let i=0;i<entries.length;i++){{const en=entries[i];if(ws.every(w=>en.includes(w)))return i;}}return -1}}
function label(t){{return t.charAt(0).toUpperCase()+t.slice(1)}}
function drawTokens(){{tokEl.innerHTML='';toks.forEach((t,i)=>{{const li=document.createElement('li');const b=document.createElement('button');b.type='button';b.className='tok';b.textContent=label(t)+' ';const x=document.createElement('span');x.setAttribute('aria-hidden','true');x.textContent='×';b.appendChild(x);b.setAttribute('aria-label','Remove '+t);b.addEventListener('click',()=>{{toks.splice(i,1);drawTokens();run()}});li.appendChild(b);tokEl.appendChild(li)}})}}
function addTok(){{ing.value.split(/[,;]+/).map(n).filter(Boolean).forEach(t=>{{if(!toks.includes(t))toks.push(t)}});ing.value='';drawTokens();run()}}
function drawChip(c){{const st=state[c.dataset.has]||'';c.dataset.state=st;c.textContent=(st==='has'?'Has ':st==='no'?'No ':'')+(st?c.dataset.name.toLowerCase():c.dataset.name);c.setAttribute('aria-label',c.dataset.name+(st==='has'?': has':st==='no'?': does not have':': any'))}}
function run(){{const v=n(q.value);const want=Object.entries(state).filter(([k,s])=>s);let k=0;
list.forEach(li=>{{const c=(li.dataset.checks||'').split(' ');const read=li.dataset.label==='1';let ok=(!v||li.dataset.q.includes(v))&&(!tag||li.dataset.tags===tag)&&(!lab.checked||read);
if(ok&&want.length)ok=read&&want.every(([g,s])=>s==='has'?c.includes(g):!c.includes(g));
const em=li.querySelector('.ing-hit');let found=[];
if(ok&&toks.length){{const entries=(li.dataset.ings||'').split('|');for(const t of toks){{const i=hit(entries,t);if(i<0){{ok=false;break}}found.push(label(t)+' at #'+(i+1))}}}}
if(em){{em.hidden=!(ok&&found.length);em.textContent=found.join(' · ')}}
li.hidden=!ok;if(ok)k++}});
count.textContent=k+' of '+TOTAL+' products';none.hidden=k>0;
const active=v||tag||lab.checked||want.length||toks.length;share.hidden=!active;clear.hidden=!active;save(v)}}
function save(v){{const p=new URLSearchParams();if(q.value.trim())p.set('q',q.value.trim());if(tag)p.set('step',tag);
const h=Object.keys(state).filter(k=>state[k]==='has'),o=Object.keys(state).filter(k=>state[k]==='no');if(h.length)p.set('has',h.join(','));if(o.length)p.set('no',o.join(','));
if(toks.length)p.set('ing',toks.join(','));if(lab.checked)p.set('read','1');const s=p.toString();try{{history.replaceState(null,'',location.pathname+(s?'?'+s:''))}}catch(e){{}}}}
function load(){{const p=new URLSearchParams(location.search);if(p.get('q'))q.value=p.get('q');const st=p.get('step');if(st){{const c=chips.find(x=>x.dataset.tag===st);if(c){{tag=st;chips.forEach(x=>x.setAttribute('aria-pressed',x===c))}}}}
(p.get('has')||'').split(',').filter(Boolean).forEach(k=>state[k]='has');(p.get('no')||'').split(',').filter(Boolean).forEach(k=>state[k]='no');
toks=(p.get('ing')||'').split(',').map(n).filter(Boolean);if(p.get('read')==='1')lab.checked=true;hasChips.forEach(drawChip);drawTokens()}}
q.addEventListener('input',run);lab.addEventListener('change',run);
chips.forEach(c=>c.addEventListener('click',()=>{{tag=c.dataset.tag;chips.forEach(x=>x.setAttribute('aria-pressed',x===c));run()}}));
hasChips.forEach(c=>c.addEventListener('click',()=>{{const k=c.dataset.has,s=state[k]||'';state[k]=s===''?'has':s==='has'?'no':'';drawChip(c);run()}}));
$('ing-add').addEventListener('click',addTok);ing.addEventListener('keydown',ev=>{{if(ev.key==='Enter'){{ev.preventDefault();addTok()}}}});
clear.addEventListener('click',()=>{{q.value='';tag='';chips.forEach((x,i)=>x.setAttribute('aria-pressed',i===0));state={{}};hasChips.forEach(drawChip);toks=[];drawTokens();lab.checked=false;run();q.focus()}});
share.addEventListener('click',async()=>{{try{{await navigator.clipboard.writeText(location.href);copied.textContent='Link copied'}}catch(e){{copied.textContent='Copy the address from your browser bar'}}setTimeout(()=>copied.textContent='',2500)}});
load();run()}})();
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
        import dupes_v1  # PREVIEW: the first version at /dupes/<slug>/v1/ for side-by-side review
        dupes_v1.build(prods, step_of, items_of)
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

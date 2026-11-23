"""PREVIEW ONLY: product page v2, written at /products/<slug>/v2/ (noindex, not in the sitemap) for the
products in PREVIEW, so the new layout can be judged next to the live page. Nothing else links here.

What changes from the live page (scripts/products.py product_page):
  - The brand is part of the headline ("Cécred Hydrating Shampoo"), with a one-line summary of the label.
    A "subline" column in the catalog sheet replaces that line for a product; left empty, it is written
    from the label (_summary).
  - "What's in it" replaces the 12-cell "Does it have..." grid AND the "By property" list: the groups the
    label has, each with its ingredients and where they start on the label, then one line for what it
    doesn't have.
  - Similar labels without card borders: what's the same and what's different, side by side.
  - With a photo, the printed label card sits on the photo like a tag; without one, it stands alone.

Delete this file and its two lines in products.py when the preview is done.
"""
import build as B
import similar as SIM

e = B.e

# Two previews: one product with a photo, one without. Matched by words in brand + name.
PREVIEW = ['amika hydro rush intense moisture shampoo', 'cecred hydrating shampoo']

SHORT = {'humectant': 'Water binders', 'slip/detangler': 'Slip & detangling', 'butter/oil': 'Oils & butters',
         'protein': 'Protein', 'ceramides': 'Ceramides', 'peptide': 'Peptides', 'scalp-active': 'Scalp actives',
         'silicone': 'Silicones', 'sulfate': 'Sulfates', 'strong-cleanser': 'Non-sulfate cleansers',
         'paraben': 'Parabens', 'phthalate': 'Phthalates'}
WHAT = {'humectant': 'draw water into the hair', 'slip/detangler': 'help strands slide apart',
        'butter/oil': 'soften and cut friction', 'protein': 'cling to the hair surface and add strength',
        'ceramides': 'lipids like the ones in the hair’s outer layer', 'peptide': 'short amino-acid chains',
        'scalp-active': 'aimed at the scalp', 'silicone': 'coat for slip and shine', 'sulfate': 'strong cleansers',
        'strong-cleanser': 'cleansers that are not sulfates', 'paraben': 'preservatives', 'phthalate': 'carry fragrance'}


def _find(prods, words):
    want = B.norm(words.replace('é', 'e'))
    for p in prods:
        if want in B.norm(B.product_full_name(p).replace('é', 'e').replace('É', 'E')):
            return p
    return None


def _groups(items):
    """[(key, label, [(position, html)])] for the groups this label has, in check order."""
    found, guessed, _ = B.check_label(items)
    out = []
    for k, label, _ in B.CHECK_GROUPS:
        ids = {id(i) for i in found[k]}
        hits = []
        for n, t in enumerate(items, 1):
            i = B.lookup(t)
            if i is not None and id(i) in ids:
                hits.append((n, f'<a href="../../../{i["_slug"]}/">{e(i["_title"])}</a>'))
                ids.discard(id(i))
            elif t in guessed[k]:
                hits.append((n, e(t)))
        if hits:
            out.append((k, SHORT.get(k, label), hits))
    return out


def _summary(p, step, groups, items):
    keys = [k for k, _, _ in groups]
    lvl = SIM.profile(p, items)['level'][1] if step == 'cleanse' else ''
    kind = {'cleanse': 'shampoo', 'condition': 'conditioner', 'leave-in': 'leave-in', 'style': 'styler',
            'seal': 'oil or sealant', 'treatment': 'treatment'}.get(step, 'product')
    parts = [SHORT[k].lower() for k in keys if k in ('humectant', 'slip/detangler', 'butter/oil', 'protein', 'ceramides', 'silicone')]
    lead = f'A {kind} built on {lvl}' if lvl and lvl != 'no cleanser' else f'A {kind}'
    if parts:
        lead += (', with ' if lvl else ' with ') + (', '.join(parts[:-1]) + ' and ' + parts[-1] if len(parts) > 1 else parts[0])
    return lead + '.'


def _label_card(p, items, photo=''):
    words = []
    for t in items:
        i = B.lookup(t)
        words.append(f'<a href="../../../{i["_slug"]}/">{e(t)}</a>' if i else e(t))
    known = len({id(i) for i in (B.lookup(t) for t in items) if i})
    pin = (f'<img class="v2-pin" src="../../../assets/products/{photo}" alt="{e(B.product_full_name(p))}" width="800" height="1000">'
           if photo else '')
    return f'''<figure class="label label-product v2-label{' has-pin' if photo else ''}" aria-labelledby="lbl">
      <div class="label-top"><span>Ingredients · as printed</span><b id="lbl">{e(B.product_full_name(p))}</b></div>
      <p class="inci">{pin}{', '.join(words)}.</p>
      <figcaption class="label-foot"><span><b>{len(items)} ingredients</b>, {known} with their own page.</span><span>Dotted words have their own page.</span></figcaption>
    </figure>'''


def _similar(p, matches, step):
    if not matches:
        return ''
    rows = []
    for q, cmp, n, total in matches:
        same = ''.join(f'<li>{e(line)}</li>' for s, line, _ in cmp if s)
        diff = ''.join(f'<li>{e(line)}</li>' for s, line, _ in cmp if not s)
        rows.append(f'''<li class="v2-sim">
        <div class="v2-sim-head"><a href="../../{q['_slug']}/"><b>{e(q.get('brand', '').strip())}</b> {e(q.get('name', '').strip())}</a><span>Same on {n} of {total}</span></div>
        <div class="v2-sim-cols{'' if diff else ' v2-one'}"><div><h4>Same</h4><ul>{same}</ul></div>{f'<div><h4>Different</h4><ul>{diff}</ul></div>' if diff else ''}</div>
        <a class="v2-cmp" href="../../../label-decoder/#compare=p:{p['_slug']}~p:{q['_slug']}">Compare the two labels side by side &#8594;</a>
      </li>''')
    word = SIM.STEP_WORD.get(step, ('products', 'product'))
    return f'''<section class="v2-sec" id="similar">
    <h2>Built like <em>this one</em></h2>
    <p class="v2-intro">Looking for a dupe? These {e(word[0])} in our catalog have labels built the same way. A similar label says what's in the bottle, not how it will feel on your hair.</p>
    <ul class="v2-sims">{''.join(rows)}</ul>
  </section>'''


def page(p, photo, shop_html, similar, dupe_path):
    items = B.split_label(p['full ingredient list']) if p.get('full ingredient list') else []
    if len(items) < 3:
        return False
    step = 'tool' if p.get('kind') == 'tool' else (p.get('step') or '').lower()
    groups = _groups(items)
    have = {k for k, _, _ in groups}
    missing = [SHORT[k].lower() for k, _, _ in B.CHECK_GROUPS if k not in have]
    _, _, unknown = B.check_label(items)
    brand, name = (p.get('brand') or '').strip(), (p.get('name') or '').strip()
    rows = ''.join(
        f'''<li><div class="v2-has-k"><b>{e(label)}</b><span>{e(WHAT.get(k, ''))}</span></div>
        <div class="v2-has-v">{', '.join(h for _, h in hits)}<span class="v2-pos">from #{hits[0][0]}</span></div></li>'''
        for k, label, hits in groups)
    note = SIM.cleanser_note(SIM.profile(p, items)) if step == 'cleanse' else ''
    unread = (f' {unknown} of the {len(items)} ingredients aren’t in our library yet, so treat “not on this label” as “not that we can see”.'
              if unknown else '')
    known = len(items) - unknown
    if not groups:
        not_line = (f'<p class="v2-empty"><b>We haven’t read most of these ingredients yet.</b> {known} of the {len(items)} have a page in our library, '
                    f'so we can’t group this label by what it does. The full label is above, and we add ingredients every week.</p>')
    elif unknown * 2 > len(items):
        not_line = (f'<p class="v2-not">{unknown} of the {len(items)} ingredients aren’t in our library yet, so this list may be missing groups.</p>')
    else:
        not_line = f'<p class="v2-not"><b>Not on this label, as far as we can see:</b> {e(", ".join(missing))}.</p>'
    next_main = ('<a class="v2-go" href="#similar">Compare with a similar label <span aria-hidden="true">&#8595;</span></a>' if similar
                 else '<a class="v2-go" href="#check">See what’s in it <span aria-hidden="true">&#8595;</span></a>')
    r = '../../../'
    hero_media = f'<div class="v2-media v2-media-solo">{_label_card(p, items, photo)}</div>'
    dupe = (f'<p class="v2-dupe"><a href="{r}{dupe_path}">See the full dupe check: closest wash and closest overall &#8594;</a></p>' if dupe_path else '')
    body = f'''  <p class="dupe-preview">Preview of a new product page layout ({'with' if photo else 'without'} a photo). <a href="../">See the live page</a></p>
  <a class="crumb" href="{r}products/">← All products</a>
  <section class="v2-hero{' has-photo' if photo else ''}">
    <div class="v2-title">
      <span class="eyebrow"><span class="little-dot"></span>{e(step.capitalize() or 'Product')}</span>
      <h1><em>{e(brand)}</em> {e(name)}</h1>
      <p class="v2-sum">{e(B.col(p, 'subline', 'Subline') or _summary(p, step, groups, items))}</p>
      <div class="v2-next">{next_main}<a class="v2-jara" href="{B.utm('https://itsjara.com', 'product_v2_cta', 'jara_beta', p['_slug'])}">Check it against your hair in JARA <span aria-hidden="true">&#8599;</span></a></div>
      {shop_html.replace('<a class="read-more" href="#check"><u>Read more</u><span aria-hidden="true">&#8595;</span></a>', '')}
    </div>
    {hero_media}
  </section>
  <section class="v2-sec" id="check">
    <h2>What&#8217;s <em>in it</em></h2>
    {f'<p class="v2-note">{e(note)}</p>' if note else ''}
    {f'<ul class="v2-has">{rows}</ul>' if rows else ''}
    {not_line}
  </section>
  {_similar(p, similar, step)}
  {dupe}
  <p class="source"><span>The Good Coil catalog · Ref {e(p['id'])}. What a product contains, not how it will work on your hair.</span><a href="{r}about/">How we write these</a></p>'''
    path = f"products/{p['_slug']}/v2/"
    html = B.shell(r, f"{B.product_full_name(p)} (preview) · The Good Coil", f"Preview of a new layout for {B.product_full_name(p)}.", body, path, 'products')
    B.write(path + 'index.html', html.replace('<head>', '<head>\n<meta name="robots" content="noindex">', 1))
    return True

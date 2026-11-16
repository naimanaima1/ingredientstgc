"""Hair plans: guide-shaped pages at /plans/<slug>/, plus the /plans/ index.

One section per question, in a single column, plain language. Content files are
content/guide-*.json; every section except the hero is optional, so a plan that has
no "causes" or no weekly schedule simply leaves that key out.
"""
import json, re, os, glob
import build as B

e = B.e
LABELS = {'established': 'Established', 'promising': 'Promising', 'emerging': 'Emerging', 'cosmetic': 'Cosmetic support'}

def links(r, ls):
    out = []
    for label, target in ls:
        if target.startswith('properties/') or target.startswith('groups/'):
            out.append(f'<a href="{r}{target}">{e(label)}</a>')
        else:
            i = B.lookup(target)
            if i:
                out.append(f'<a href="{r}{i["_slug"]}/">{e(label)}</a>')
    return ' · '.join(out)

JARA_URL = 'https://itsjara.com'
JARA_PRICE = '$19 lifetime'

JARA_DEFAULT = {
    'track': ('Want this in your pocket?',
              'Log your wash days and monthly photos in JARA, and see them side by side.'),
    'end': ('Keep the proof.',
            'JARA keeps your photos and wash days in one place, on every device.'),
}


def jara_card(r, head, text, cls=''):
    """One quiet prompt: small app picture, a short line, one button."""
    return f'''<aside class="jara {cls}" aria-label="About JARA"><div class="jara-in">
    <a class="jara-shot" href="{JARA_URL}" tabindex="-1" aria-hidden="true"><img src="{r}assets/img/jara-promo.jpg" alt="" width="1000" height="1000" loading="lazy"></a>
    <div class="jara-txt"><h2>{e(head)}</h2><p>{e(text)}</p></div>
    <a class="btn" href="{JARA_URL}">Get JARA &middot; {JARA_PRICE}</a>
  </div></aside>'''


def jara(where, r='../../', over=None):
    """A prompt to carry the plan into JARA. Two per guide: one where the plan
    first asks you to write things down, one at the end. A plan can word its own
    in its json under "jara": {"track": [head, text], "end": [head, text]}."""
    head, text = (over or {}).get(where) or JARA_DEFAULT[where]
    return jara_card(r, head, text, 'jara-end' if where == 'end' else '')


def explainer(d, key, id_, cls=''):
    c = d.get(key)
    if not c:
        return None
    items = ''.join(
        f'<li><h3>{e(i[0])}</h3><p>{e(i[1])}</p>' + (f'<p class="gd-why">{e(i[2])}</p>' if len(i) > 2 and i[2] else '') + '</li>'
        for i in c['items'])
    return section(id_, c['title'], c.get('intro'), f'<ul class="gd-causes">{items}</ul>', cls), (id_, c.get('jump', c['title']))

def shortlist(r, rows):
    """Name + purpose rows. A name links to its product page when the catalog has it
    (so rows light up after a later catalog pull), and stays plain text until then."""
    def norm(x): return re.sub(r'[^a-z0-9]', '', x.lower().replace('é', 'e'))
    idx = {norm(B.product_full_name(p)): p for p in B.products}
    li = []
    for name, purpose in rows:
        p = idx.get(norm(name)) or next((q for k, q in idx.items() if norm(name) in k or k in norm(name)), None)
        nm = f'<a href="{r}products/{p["_slug"]}/">{e(name)}</a>' if p else e(name)
        li.append(f'<li><b>{nm}</b><span>{e(purpose)}</span></li>')
    return f'<ul class="gd-short">{"".join(li)}</ul>'


SYNTH = ('carbomer', 'pvp', 'vp/va', 'vp copolymer', 'acrylates', 'polyquaternium')

def _norm(x):
    return re.sub(r'[^a-z0-9]', '', x.lower().replace('é', 'e').replace("'", ''))

def find_product(ref):
    """A catalog id (TGC-046) or a name, matched loosely. None if we do not have it yet."""
    if re.match(r'TGC-\d+$', ref or ''):
        return next((p for p in B.products if p.get('id') == ref), None)
    idx = {_norm(B.product_full_name(p)): p for p in B.products}
    n = _norm(ref)
    return idx.get(n) or next((q for k, q in idx.items() if n in k or k in n), None)

def prod_card(r, entry, screen=False):
    """[id or name, tag, note]. Links when we have the product; plain text until then."""
    ref, tag, note = (list(entry) + ['', ''])[:3]
    p = find_product(ref)
    label = B.product_full_name(p) if p else ref
    if re.match(r'TGC-\d+$', ref or '') and not p:
        return ''
    name = f'<a href="{r}products/{p["_slug"]}/">{e(label)}</a>' if p else e(label)
    flag = ''
    if screen and p:
        inci = (p.get('full ingredient list') or '').lower()
        hit = [w for w in SYNTH if w in inci]
        if hit:
            flag = f'<span class="pc-flag">Has {e(hit[0])} in its list</span>'
    return (f'<li class="pc">{f"<span class=pc-tag>{e(tag)}</span>" if tag else ""}'
            f'<b>{name}</b>{f"<small>{e(note)}</small>" if note else ""}{flag}</li>')

def prod_strip(r, entries, screen=False, label='What to use'):
    cards = ''.join(prod_card(r, x, screen) for x in entries)
    if not cards:
        return ''
    return f'<div class="pc-wrap"><span class="pc-label">{e(label)}</span><ul class="pc-strip">{cards}</ul></div>'

def section(id_, title, intro, inner, cls=''):
    return f'''<section class="gd-sec {cls}" id="{id_}"><div class="tp-in">
  <h2>{e(title)}</h2>
  {f'<p class="gd-lead">{e(intro)}</p>' if intro else ''}
  {inner}
</div></section>'''

def page(d):
    r = '../../'
    cat = {c.get('id'): c for c in B.cat}
    out = []
    jump = []

    # 1. why
    if d.get('causes'):
        c = d['causes']
        items = ''.join(f'<li><h3>{e(t)}</h3><p>{e(what)}</p><p class="gd-why">{e(why)}</p></li>' for t, what, why in c['items'])
        out.append(section('why', c['title'], c.get('intro'), f'<ul class="gd-causes">{items}</ul>'))
        jump.append(('why', c.get('jump', c['title'])))

    # 2. before you start
    if d.get('stock'):
        s = d['stock']
        items = ''.join(f'<li><b>{e(a)}</b><span>{e(b)}</span></li>' for a, b in s['items'])
        out.append(section('stock', s['title'], s.get('intro'), f'<ul class="gd-stock">{items}</ul>', 'gd-paper'))
        jump.append(('stock', s.get('jump', s['title'])))
        out.append(jara('track', r, d.get('jara')))

    # 2b. are you ready? swipeable yes / not yet cards, and the optional prep
    if d.get('ready'):
        rd = d['ready']
        cards = ''.join(
            f'<li class="rd-card" data-i="{n}"><span class="rd-n">{n + 1} of {len(rd["items"])}</span><b>{e(a)}</b><p>{e(b)}</p>'
            f'<div class="rd-btns" role="group" aria-label="{e(a)}"><button type="button" data-v="1">Yep</button><button type="button" data-v="0">Not yet</button></div></li>'
            for n, (a, b) in enumerate(rd['items']))
        v = rd['verdict']
        prep = ''
        if rd.get('prep'):
            pr = rd['prep']
            rows = ''.join(f'<li><span class="ro-n">{e(n)}</span><b>{e(t)}</b><p>{e(w)}</p></li>' for n, t, w in pr['items'])
            pn = f'<p class="ro-note">{e(pr["note"])}</p>' if pr.get('note') else ''
            prep = (f'<details class="gd-fold rd-prep" id="prep"><summary>{e(pr["title"])}<small>{e(pr["sub"])}</small></summary>'
                    f'<p class="gd-lead">{e(pr["intro"])}</p><ol class="ro-weeks">{rows}</ol>{pn}</details>')
        inner = f'''<div class="rd" data-total="{len(rd['items'])}">
  <ul class="rd-cards" aria-label="Readiness cards, swipe to see more">{cards}</ul>
  <p class="rd-hint" aria-hidden="true">Swipe for the next one &rarr;</p>
  <div class="rd-out" role="status" aria-live="polite" hidden
       data-all="{e(v['all'])}" data-four="{e(v['four'])}" data-few="{e(v['few'])}"
       data-wait="{e(v['wait'])}"><p class="rd-msg"></p><a class="rd-go" href="#routine">Go to the routine &rarr;</a></div>
</div>{prep}'''
        out.append(section('ready', rd['title'], rd.get('intro'), inner, 'gd-paper'))
        jump.append(('ready', rd.get('jump', rd['title'])))

    # 3. routine: wash day open, between wash days folded
    if d.get('routine'):
        ro = d['routine']
        def one(n, st):
            t, x = st[0], st[1]
            extra = st[2] if len(st) > 2 else {}
            note = f'<p class="gd-stepnote">{e(extra["note"])}</p>' if extra.get('note') else ''
            if extra.get('link'):
                note += f'<p class="gd-stepnote"><a class="gd-link" href="{r}{extra["link"][1]}">{e(extra["link"][0])} &rarr;</a></p>'
            strip = prod_strip(r, extra['use'], extra.get('screen', False), extra.get('label', 'What to use')) if extra.get('use') else ''
            return f'<li><span>{n}</span><div><b>{e(t)}</b><p>{e(x)}</p>{note}{strip}</div></li>'
        bits = ''
        for w in (ro.get('washes') or [ro['wash']]):
            steps = ''.join(one(n, st) for n, st in enumerate(w['steps'], 1))
            bits += f'''<div class="gd-washday"><h3>{e(w['title'])}<small>{e(w['sub'])}</small></h3><ol class="gd-steps">{steps}</ol></div>'''
        if ro.get('between'):
            bt = ro['between']
            groups = ''.join(f'<div><h4>{e(k)}</h4><ul class="ticks">' + ''.join(f'<li>{e(x)}</li>' for x in v) + '</ul></div>' for k, v in bt['groups'])
            bits += f'''<details class="gd-fold"><summary>{e(bt['title'])}<small>{e(bt['sub'])}</small></summary><div class="gd-between">{groups}</div></details>'''
        out.append(section('routine', ro['title'], ro.get('intro'), bits, 'gd-mist'))
        jump.append(('routine', ro.get('jump', ro['title'])))
        if d.get('book') and d['book'].get('url'):
            bkd = d['book']
            out.append(f'''<aside class="book" aria-label="The book"><div class="book-in">
    <div class="book-txt"><span class="eyebrow">{e(bkd.get('eyebrow', 'The book'))}</span><h2>{e(bkd['title'])}</h2><p>{e(bkd['text'])}</p></div>
    <a class="btn" href="{e(bkd['url'])}">{e(bkd.get('button', 'Get the book'))}</a>
  </div></aside>''')

    # 4a. a winding week-by-week timeline: one idea at a time on a phone
    if d.get('timeline'):
        tl = d['timeline']
        kit = ''
        if tl.get('kit'):
            kit = f'<div class="tl-kit">{prod_strip(r, tl["kit"]["use"], False, tl["kit"]["label"])}</div>'
        lis, dots = '', ''
        for n, it in enumerate(tl['items'], 1):
            notes = ''.join(f'<p class="tl-note"><b>{e(a)}</b> {e(b)}</p>' for a, b in it.get('notes', []))
            use = prod_strip(r, it['use'], False, it.get('label', 'What to use')) if it.get('use') else ''
            lis += (f'<li class="tl-item" id="week-{n}"><span class="tl-dot" aria-hidden="true">{n}</span>'
                    f'<div class="tl-card"><span class="tl-tag">Week {n} &middot; {e(it["tag"])}</span>'
                    f'<h3>{e(it["title"])}</h3><p>{e(it["text"])}</p>{use}{notes}</div></li>')
            dots += f'<button type="button" data-i="{n - 1}" aria-label="Week {n}: {e(it["title"])}"{" aria-current=true" if n == 1 else ""}>{n}</button>'
        inner = (kit + f'<nav class="tl-path" aria-label="Weeks">{dots}</nav>'
                 f'<ol class="tl-list">{lis}</ol><p class="rd-hint tl-hint" aria-hidden="true">Swipe for the next week &rarr;</p>')
        out.append(section('weeks', tl['title'], tl.get('intro'), inner, 'gd-paper tl-sec'))
        jump.append(('weeks', tl.get('jump', tl['title'])))

    # 4. a card per week (styles, or what each week does)
    if d.get('weeks'):
        wk = d['weeks']
        # one grid, every style the same size. A style without a photo gets a
        # drawn tile rather than being hidden behind a hover.
        cards = ''
        for n, it in enumerate(wk['items']):
            t, x = it[0], it[1]
            if len(it) > 2:
                top = (f'<img src="{r}assets/img/{e(it[2])}" alt="{e(it[3])}" '
                       f'width="799" height="1344" loading="lazy">')
                cls = 'has-photo'
            else:
                top = f'<span class="gd-tile" aria-hidden="true"><em>{e(t)}</em></span>'
                cls = f'no-photo tint-{n % 3}'
            cards += f'<li class="{cls}">{top}<b>{e(t)}</b><p>{e(x)}</p></li>'
        out.append(section('weeks', wk['title'], wk.get('intro'),
                           f'<ul class="gd-styles2">{cards}</ul>'))
        jump.append(('weeks', wk.get('jump', wk['title'])))

    x = explainer(d, 'techniques', 'tech')
    if x:
        out.append(x[0]); jump.append(x[1])

    # 4b. a twelve-week treatment rotation (glass hair)
    if d.get('rota'):
        ro = d['rota']
        ph = ''.join(
            f'<li><span class="eyebrow">{e(a)}</span><b>{e(b)}</b><p>{e(c)}</p></li>'
            for a, b, c in ro.get('phases', []))
        rows = ''.join(
            f'<li><span class="ro-n">{e(n)}</span><b>{e(t)}</b><p>{e(w)}</p></li>'
            for n, t, w in ro['items'])
        inner = (f'<ol class="ro-phases">{ph}</ol>' if ph else '') + f'<ol class="ro-weeks">{rows}</ol>'
        if ro.get('note'):
            inner += f'<p class="ro-note">{e(ro["note"])}</p>'
        out.append(section('rota', ro['title'], ro.get('intro'), inner))
        jump.append(('rota', ro.get('jump', ro['title'])))

    # 5. what to use
    if d.get('use'):
        u = d['use']
        rows = ''
        for name, job, how, ids in u['items']:
            picks = [cat[i] for i in ids if i in cat]
            names = ', '.join(f'<a href="{r}products/{p["_slug"]}/">{e(B.product_full_name(p))}</a>' for p in picks)
            rows += f'''<li><div class="gd-job"><b>{e(name)}</b><span class="pill">{e(how)}</span></div>
          <p>{e(job)}</p>
          {f'<p class="gd-picks">From our catalog: {names}</p>' if names else '<p class="gd-picks gd-none">Nothing in our catalog yet.</p>'}</li>'''
        out.append(section('use', u['title'], u.get('intro'), f'<ul class="gd-use">{rows}</ul>', 'gd-paper'))
        jump.append(('use', u.get('jump', u['title'])))

    x = explainer(d, 'strength', 'strength', 'gd-paper')
    if x:
        out.append(x[0]); jump.append(x[1])

    # 6. how many at once
    if d.get('choose'):
        ch = d['choose']
        paras = ''.join(f'<div class="gd-choice"><h3>{e(t)}</h3><p>{e(x)}</p></div>' for t, x in ch['items'])
        lead = f'<p class="gd-lead">{e(ch["intro"])}</p>' if ch.get('intro') else ''
        out.append(f'''<section class="gd-sec" id="choose"><div class="tp-in">
  <h2>{e(ch['title'])}</h2>{lead}
  <div class="gd-choices">{paras}</div>
  {(f'<h3 class="gd-short-h">{e(ch["shortlist"]["title"])}</h3>' + shortlist(r, ch["shortlist"]["items"]) + f'<p class="gd-short-n">{e(ch["shortlist"]["note"])}</p>') if ch.get("shortlist") else ''}
</div></section>''')
        jump.append(('choose', ch.get('jump', ch['title'])))

    # 7. what to look for on a label
    if d.get('ing'):
        g = d['ing']
        items = ''.join(f'''<li><div class="gd-job"><b>{e(n)}</b><span class="ev ev-{k}">{e(LABELS[k])}</span></div><p>{e(t)}</p><p class="tp-links">{links(r, ls)}</p></li>''' for n, t, k, ls in g['items'])
        out.append(section('label', g['title'], g.get('intro'), f'<ul class="gd-ing">{items}</ul>', 'gd-mist'))
        jump.append(('label', g.get('jump', g['title'])))

    x = explainer(d, 'climate', 'climate')
    if x:
        out.append(x[0]); jump.append(x[1])

    # 8. troubleshooting
    if d.get('trouble'):
        tr = d['trouble']
        items = ''.join(f'<div><h4>{e(a)}</h4><p>{e(b)}</p></div>' for a, b in tr['items'])
        out.append(section('help', tr['title'], tr.get('intro'), f'<div class="gd-trouble">{items}</div>'))
        jump.append(('help', tr.get('jump', tr['title'])))

    # 9. closing band
    if d.get('end'):
        en = d['end']
        lst = ''.join(f'<li>{e(x)}</li>' for x in en.get('list', []))
        nxt = ''.join(f'<a href="{r}{u}"><small>{e(why)}</small><b>{e(n)} →</b></a>' for n, why, u in en.get('next', []))
        right = (f'<ul>{lst}</ul>' if lst else '') + (f'<div class="tp-next">{nxt}</div>' if nxt else '')
        src = f'<p class="tp-ref">Source: {e(en["source"])}</p>' if en.get('source') else ''
        notes = ''.join(f'<p>{e(x)}</p>' for x in en.get('notes', []))
        out.append(f'''<section class="gd-sec gd-ink" id="end"><div class="tp-in">
  <div class="gd-derm"><div><h2>{e(en['title'])}</h2>{notes}{src}</div><div>{right}</div></div>
</div></section>''')
        out.append(jara('end', r, d.get('jara')))

    jump_html = ''.join(f'<a href="#{a}">{e(b)}</a>' for a, b in jump)
    body = f'''<section class="gd-hero">
  <div class="gd-copy">
    <span class="eyebrow">{e(d['eyebrow'])}</span>
    <h1>{e(d['name'])}</h1>
    <p class="gd-tag"><em>{e(d['tagline'])}</em></p>
    <p class="gd-intro">{e(d['intro'])}</p>
    <a class="gd-go" href="#routine">{e(d.get('go', 'Start with the routine'))} →</a>
  </div>
  <div class="tp-photo"><img src="{r}assets/img/{e(d['image'])}" alt="{e(d['image_alt'])}" width="848" height="1424"></div>
</section>
<nav class="gd-jump" aria-label="On this page">{jump_html}</nav>
{''.join(out)}
<script src="{r}assets/guide.js" defer></script>
<p class="source tp-in tp-source"><span>The Good Coil hair plan · Ref {e(d['id'])}</span><a href="{r}plans/">All hair plans</a><a href="{r}about/">How we write these</a></p>'''
    html = B.shell(r, f"{d['name']} · The Good Coil", d.get('description', d['tagline']), body, f"plans/{d['slug']}/", 'plans')
    html = html.replace('<main id="main" class="wrap">', '<main id="main" class="gd">', 1)
    B.write(f"plans/{d['slug']}/index.html", html)
    return d

def index_page(guides):
    cards = ''.join(f'''<li><a href="{g['slug']}/"><img src="../assets/img/{e(g['image'])}" alt="" width="848" height="1424" loading="lazy"><span class="eyebrow">{e(g['eyebrow'].split(' · ')[-1])}</span><h2>{e(g['name'])}</h2><p><em>{e(g['tagline'])}</em></p></a></li>''' for g in guides)
    body = f'''  <section class="page-head"><span class="eyebrow"><span class="little-dot"></span>The Good Coil</span><h1>Hair plans</h1>
  <p>{len(guides)} guides: what is going on, what to do each week, and what to look for on a label. Steps are jobs, not brands, so you can follow them with what you already own.</p></section>
  <ul class="plan-cards">{cards}</ul>
  <p class="fine">These are guides to cosmetic hair care, not medical advice. For hair loss, scalp conditions or allergies, talk to a dermatologist or doctor.</p>'''
    B.write('plans/index.html', B.shell('../', 'Hair plans · The Good Coil', f'{len(guides)} hair-care guides from The Good Coil: edges, length retention, moisture, shine, wash and goes and winter care.', body, 'plans/', 'plans'))

REDIRECTS = {'healthy-edges': 'edge-growth-plan', 'deep-moisture-protein-balance': 'moisture-and-protein', 'mega-growth-retention': 'mega-growth-and-retention'}

def build():
    out = [json.load(open(f, encoding='utf-8')) for f in sorted(glob.glob(os.path.join(B.ROOT, 'content', 'guide-*.json')))]
    out.sort(key=lambda g: g.get('order', 99))
    for g in out:
        page(g)
    index_page(out)
    live = {g['slug'] for g in out}
    for old, new in REDIRECTS.items():  # the plan pages these replaced
        if new in live:
            B.write(f'plans/{old}/index.html', f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Moved</title><link rel="canonical" href="{B.SITE}/plans/{new}/">
<meta http-equiv="refresh" content="0; url=../{new}/"><meta name="robots" content="noindex"></head>
<body><p>This plan is now at <a href="../{new}/">/plans/{new}/</a>.</p></body></html>
''')
    return out

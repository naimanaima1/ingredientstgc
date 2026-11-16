"""Hair plans: guide-shaped pages at /plans/<slug>/, plus the /plans/ index.

One section per question, in a single column, plain language. Content files are
content/guide-*.json; every section except the hero is optional, so a plan that has
no "causes" or no weekly schedule simply leaves that key out.
"""
import json, os, glob
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
JARA_PRICE = '$19 once'


def jara(where, r='../../'):
    """A prompt to carry the plan into JARA. Two per guide: one where the plan
    first asks you to write things down, one at the end."""
    if where == 'track':
        return f'''<section class="jara"><div class="jara-in">
    <div><span class="eyebrow">Keeping track</span>
      <h2>Keep this on paper, or keep it in JARA.</h2>
      <p>This plan asks you to note where your hair is today and check the same
      things again at week 4 and week 8. JARA is our app for exactly that: wash
      days, what you used, how it felt, and your photos lined up side by side so
      the change is something you can see rather than remember.</p></div>
    <div class="jara-do"><a class="jara-shot" href="{JARA_URL}"><img src="{r}assets/img/jara-promo.jpg" alt="The JARA app on a tablet: this week, last wash day, average rating, and what care is next." width="1000" height="1000" loading="lazy"></a>
      <a class="btn" href="{JARA_URL}">Get JARA · {JARA_PRICE}</a>
      <p>One payment, no subscription. Works on your phone and your laptop.</p></div>
  </div></section>'''
    return f'''<section class="jara jara-end"><div class="jara-in">
    <div><span class="eyebrow">After week 8</span>
      <h2>The next eight weeks are the ones that show.</h2>
      <p>Keep logging wash days and photos and by next spring you will have your
      own evidence instead of a guess about what worked. That is the whole point
      of JARA.</p></div>
    <div class="jara-do"><a class="jara-shot" href="{JARA_URL}"><img src="{r}assets/img/jara-promo.jpg" alt="The JARA app on a tablet: this week, last wash day, average rating, and what care is next." width="1000" height="1000" loading="lazy"></a>
      <a class="btn" href="{JARA_URL}">Get JARA · {JARA_PRICE}</a>
      <p>One payment, no subscription.</p></div>
  </div></section>'''


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
        out.append(jara('track', r))

    # 3. routine: wash day open, between wash days folded
    if d.get('routine'):
        ro = d['routine']
        w = ro['wash']
        steps = ''.join(f'<li><span>{n}</span><div><b>{e(t)}</b><p>{e(x)}</p></div></li>' for n, (t, x) in enumerate(w['steps'], 1))
        bits = f'''<div class="gd-washday"><h3>{e(w['title'])}<small>{e(w['sub'])}</small></h3><ol class="gd-steps">{steps}</ol></div>'''
        if ro.get('between'):
            bt = ro['between']
            groups = ''.join(f'<div><h4>{e(k)}</h4><ul class="ticks">' + ''.join(f'<li>{e(x)}</li>' for x in v) + '</ul></div>' for k, v in bt['groups'])
            bits += f'''<details class="gd-fold"><summary>{e(bt['title'])}<small>{e(bt['sub'])}</small></summary><div class="gd-between">{groups}</div></details>'''
        out.append(section('routine', ro['title'], ro.get('intro'), bits, 'gd-mist'))
        jump.append(('routine', ro.get('jump', ro['title'])))

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

    # 6. how many at once
    if d.get('choose'):
        ch = d['choose']
        paras = ''.join(f'<div class="gd-choice"><h3>{e(t)}</h3><p>{e(x)}</p></div>' for t, x in ch['items'])
        lead = f'<p class="gd-lead">{e(ch["intro"])}</p>' if ch.get('intro') else ''
        out.append(f'''<section class="gd-sec" id="choose"><div class="tp-in">
  <h2>{e(ch['title'])}</h2>{lead}
  <div class="gd-choices">{paras}</div>
</div></section>''')
        jump.append(('choose', ch.get('jump', ch['title'])))

    # 7. what to look for on a label
    if d.get('ing'):
        g = d['ing']
        items = ''.join(f'''<li><div class="gd-job"><b>{e(n)}</b><span class="ev ev-{k}">{e(LABELS[k])}</span></div><p>{e(t)}</p><p class="tp-links">{links(r, ls)}</p></li>''' for n, t, k, ls in g['items'])
        out.append(section('label', g['title'], g.get('intro'), f'<ul class="gd-ing">{items}</ul>', 'gd-mist'))
        jump.append(('label', g.get('jump', g['title'])))

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
        out.append(jara('end', r))

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
    B.write('plans/index.html', B.shell('../', 'Hair plans · The Good Coil', 'Three hair-care guides from The Good Coil: edges, length retention, and moisture and protein.', body, 'plans/', 'plans'))

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

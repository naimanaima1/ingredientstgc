"""TEST: a guide-shaped hair plan at /test-program/healthy-edges/ (noindex, unlinked).

Shorter and plainer than the program pages: causes first, then what to note, then the routine
(wash day and between wash days side by side), then a style for each week, then products by job
with how often, then ingredients, troubleshooting and the dermatologist note.
Content: content/guide-edges.json.
"""
import json, os
import build as B

e = B.e
LABELS = {'established': 'Established', 'promising': 'Promising', 'emerging': 'Emerging', 'cosmetic': 'Cosmetic support'}

def links(r, ls):
    out = []
    for label, target in ls:
        if target.startswith('properties/'):
            out.append(f'<a href="{r}{target}">{e(label)}</a>')
        else:
            i = B.lookup(target)
            if i:
                out.append(f'<a href="{r}{i["_slug"]}/">{e(label)}</a>')
    return ' · '.join(out)

def page(d):
    r = '../../'
    cat = {c.get('id'): c for c in B.cat}

    causes = ''.join(f'''<li><h3>{e(t)}</h3><p>{e(what)}</p><p class="gd-why">{e(why)}</p></li>''' for t, what, why in d['causes'])
    stock = ''.join(f'<li><b>{e(a)}</b><span>{e(b)}</span></li>' for a, b in d['stock'])
    wash = ''.join(f'<li><span>{n}</span><p>{e(x)}</p></li>' for n, x in enumerate(d['wash'], 1))
    between = ''.join(f'<div><h4>{e(k)}</h4><ul class="ticks">' + ''.join(f'<li>{e(x)}</li>' for x in v) + '</ul></div>' for k, v in d['between'])
    styles = ''.join(f'<li><span>{n}</span><b>{e(t)}</b><p>{e(x)}</p></li>' for n, (t, x) in enumerate(d['styles'], 1))

    use = ''
    for name, job, how, ids in d['use']:
        picks = [cat[i] for i in ids if i in cat]
        names = ', '.join(f'<a href="{r}products/{p["_slug"]}/">{e(B.product_full_name(p))}</a>' for p in picks)
        use += f'''<li><div class="gd-job"><b>{e(name)}</b><p>{e(job)}</p></div>
        <div class="gd-how"><span class="pill">{e(how)}</span>{f'<p class="gd-picks">From our catalog: {names}</p>' if names else '<p class="gd-picks gd-none">Nothing in our catalog yet.</p>'}</div></li>'''

    ing = ''.join(f'''<li><div><b>{e(n)}</b><p>{e(t)}</p><p class="tp-links">{links(r, ls)}</p></div><span class="ev ev-{k}">{e(LABELS[k])}</span></li>''' for n, t, k, ls in d['ingredients'])
    trouble = ''.join(f'<div><h4>{e(a)}</h4><p>{e(b)}</p></div>' for a, b in d['trouble'])
    derm = ''.join(f'<li>{e(x)}</li>' for x in d['derm'])
    stack = ''.join(f'<p>{e(x)}</p>' for x in d['stack'])

    body = f'''<p class="pf-test tp-test" role="note"><b>Test layout.</b> Not linked from the site and hidden from search engines.</p>
<section class="gd-hero">
  <div class="gd-copy">
    <span class="eyebrow">{e(d['eyebrow'])}</span>
    <h1>{e(d['name'])}</h1>
    <p class="gd-tag"><em>{e(d['tagline'])}</em></p>
    <p class="gd-intro">{e(d['intro'])}</p>
    <a class="gd-go" href="#routine">Start with the routine →</a>
  </div>
  <div class="tp-photo"><img src="{r}assets/img/{e(d['image'])}" alt="{e(d['image_alt'])}" width="799" height="1344"></div>
</section>
<nav class="gd-jump" aria-label="On this page">
  <a href="#why">Why edges get thin</a><a href="#stock">Before you start</a><a href="#routine">Your routine</a><a href="#styles">Styles to try</a><a href="#use">What to use</a><a href="#help">If something feels off</a>
</nav>

<section class="gd-sec" id="why"><div class="tp-in">
  <h2>Why edges get thin</h2>
  <p class="gd-lead">{e(d['causes_intro'])}</p>
  <ul class="gd-causes">{causes}</ul>
</div></section>

<section class="gd-sec gd-paper" id="stock"><div class="tp-in">
  <h2>Before you start</h2>
  <p class="gd-lead">{e(d['stock_intro'])}</p>
  <ul class="gd-stock">{stock}</ul>
</div></section>

<section class="gd-sec gd-mist" id="routine"><div class="tp-in">
  <h2>Your routine</h2>
  <p class="gd-lead">{e(d['routine_intro'])}</p>
  <div class="gd-routine">
    <div><h3>{e(d['wash_title'])}<small>{e(d['wash_sub'])}</small></h3><ol class="tp-steps">{wash}</ol></div>
    <div><h3>{e(d['between_title'])}<small>{e(d['between_sub'])}</small></h3><div class="gd-between">{between}</div></div>
  </div>
</div></section>

<section class="gd-sec" id="styles"><div class="tp-in">
  <h2>A different style each week</h2>
  <p class="gd-lead">{e(d['styles_intro'])}</p>
  <ol class="gd-styles">{styles}</ol>
</div></section>

<section class="gd-sec gd-paper" id="use"><div class="tp-in">
  <h2>What to use</h2>
  <p class="gd-lead">{e(d['use_intro'])}</p>
  <ul class="gd-use">{use}</ul>
  <div class="gd-stack"><h3>{e(d['stack_title'])}</h3>{stack}</div>
  <h3 class="gd-h3">What to look for on a label</h3>
  <p class="gd-lead">{e(d['ing_intro'])}</p>
  <ul class="gd-ing">{ing}</ul>
</div></section>

<section class="gd-sec" id="help"><div class="tp-in">
  <h2>If something feels off</h2>
  <div class="gd-trouble">{trouble}</div>
</div></section>

<section class="gd-sec gd-ink" id="derm"><div class="tp-in">
  <div class="gd-derm">
    <div><h2>{e(d['derm_title'])}</h2><p>{e(d['derm_note'])}</p><p class="tp-ref">Source: {e(d['derm_source'])}</p></div>
    <ul>{derm}</ul>
  </div>
</div></section>
<p class="source tp-in tp-source"><span>The Good Coil · Ref {e(d['id'])} · Test layout</span><a href="{r}test-program/">Other test layouts</a></p>'''
    html = B.shell(r, f"{d['name']}: a guide to your edges · The Good Coil", f"{d['tagline']} What wears edges down, a weekly routine, styles that give them a break, and what to look for on a label.", body, f"test-program/{d['slug']}/", 'plans')
    html = html.replace('<main id="main" class="wrap">', '<main id="main" class="gd">', 1).replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex">', 1)
    B.write(f"test-program/{d['slug']}/index.html", html)
    return d

def build():
    path = os.path.join(B.ROOT, 'content', 'guide-edges.json')
    if not os.path.exists(path):
        return None
    return page(json.load(open(path, encoding='utf-8')))

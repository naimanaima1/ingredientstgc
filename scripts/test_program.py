"""TEST layout for one hair plan at /test-program/ (noindex, unlinked).
Content: content/test-program.json. Three acts (Start, The 8 weeks, Finish) around a week planner
with protein tracks; ticks and track are remembered on the visitor's device only.
"""
import json, os
import build as B

e = B.e
LABELS = {'established': 'Established', 'promising': 'Promising', 'emerging': 'Emerging', 'cosmetic': 'Cosmetic support'}

def lis(items, cls=''):
    return f'<ul class="{cls}">' + ''.join(f'<li>{e(x)}</li>' for x in items) + '</ul>'

def page(d):
    r = '../../'
    T = d['tracks']
    principle = ''.join(f'<li>{e(x)}</li>' for x in d['principle'])
    best = dict(d['overview'])
    facts = ''.join(f'<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k, v in d['overview'])
    pillars = ''.join(f'<li><span>{n}</span><b>{e(t)}</b><p>{e(x)}</p></li>' for n, (t, x) in enumerate(d['pillars'], 1))
    baseline = ''.join(f'<li><b>{e(a)}</b><span>{e(b)}</span></li>' for a, b in d['baseline'])
    kit = ''.join(f'<div class="tp-kit"><h4>{e(t)}{f"<small>{e(s)}</small>" if s else ""}</h4><ul>' + ''.join(f'<li><b>{e(a)}</b><span>{e(b)}</span></li>' for a, b in items) + '</ul></div>' for t, s, items in d['kit'])

    def track_card(k):
        t = T[k]
        wk = ''.join(f'<li><b>Week {w}</b> {e(x)}</li>' for w, x in t['weeks'].items())
        return f'''<label class="tp-track"><input type="radio" name="track" value="{k}"><span class="tp-track-in"><small>{e(t['name'])}</small><b>{e(t['title'])}</b><span>{e(t['who'])}</span><ul>{wk}</ul></span></label>'''
    rail = ''.join(f'<a href="#w{n}" data-w="{n}"><em>{n}</em><span>{e(w[0])}</span></a>' for n, w in enumerate(d['weeks'], 1))
    panels = ''
    for n, (short, title, focus, decision, todo) in enumerate(d['weeks'], 1):
        alt = ''.join(f'<p class="tp-dec t-{k}"><small>{e(T[k]["name"])}</small>{e(T[k]["weeks"][str(n)])}</p>' for k in ('a', 'b') if str(n) in T[k]['weeks'])
        checks = ''.join(f'<li><label><input type="checkbox" data-k="w{n}-{i}"><span>{e(x)}</span></label></li>' for i, x in enumerate(todo))
        panels += f'''<article class="tp-week{' has-alt' if alt else ''}" id="w{n}">
        <div><span class="eyebrow">Week {n} of {len(d['weeks'])}</span><h3>{e(title)}</h3><p class="tp-focus">{e(focus)}.</p>
        <p class="tp-dec t-none"><small>The decision</small>{e(decision)}.</p>{alt}</div>
        <ul class="tp-checks">{checks}</ul></article>'''
    wash = ''.join(f'<li><span>{n}</span><p>{e(x)}</p></li>' for n, x in enumerate(d['wash_day'], 1))
    daily = ''.join(f'<div><h4>{e(k)}</h4>{lis(v, "ticks")}</div>' for k, v in d['daily'].items())
    adjust = ''.join(f'<div class="tp-adjust"><h4>{e(t)}</h4><ol>' + ''.join(f'<li>{e(x)}</li>' for x in steps) + '</ol></div>' for t, steps in d['adjust'])

    def links(ls):
        out = []
        for label, target in ls:
            if target.startswith('properties/'):
                out.append(f'<a href="{r}{target}">{e(label)}</a>')
            else:
                i = B.lookup(target)
                if i:
                    out.append(f'<a href="{r}{i["_slug"]}/">{e(label)}</a>')
        return ' · '.join(out)
    ing = ''.join(f'''<li><div><b>{e(n)}</b><p>{e(f)}</p><p class="tp-links">{links(ls)}</p></div><div><span class="ev ev-{k}">{e(LABELS[k])}</span><p>{e(note)}</p></div></li>''' for n, f, k, note, ls in d['ingredients'])
    expl = ''.join(f'<details><summary>{e(t)}</summary>' + ''.join(f'<p>{e(x)}</p>' for x in ps) + (f'<p class="tp-ref">Source: {e(ref)}</p>' if ref else '') + '</details>' for t, ps, ref in d['explainers'])
    F = d['finish']
    nxt = ''.join(f'<a href="{r}{u}"><small>{e(why)}</small><b>{e(n)} →</b></a>' for n, why, u in F['next'])

    body = f'''<p class="pf-test tp-test" role="note"><b>Test layout.</b> Not linked from the site and hidden from search engines.</p>
<section class="tp-hero">
  <div class="tp-copy">
    <span class="eyebrow">8-week program · conditioning and moisture</span>
    <h1>{e(d['name'])}</h1>
    <ol class="tp-principle">{principle}</ol>
    <p class="tp-best"><b>Best suited for</b> {e(best.get('Best suited for', '').lower())}.</p>
  </div>
  <div class="tp-photo"><img src="{r}assets/img/{e(d['image'])}" alt="{e(d['image_alt'])}" width="799" height="1344"></div>
</section>
<nav class="tp-acts" aria-label="The program in three parts">
  <a href="#start"><em>1</em><b>Start</b><span>Is it for you, take stock, gather your kit</span></a>
  <a href="#weeks"><em>2</em><b>The 8 weeks</b><span>Week by week, wash day, daily habits</span></a>
  <a href="#finish"><em>3</em><b>Finish</b><span>Compare, then build your maintenance routine</span></a>
</nav>

<section class="tp-act tp-mist" id="start"><div class="tp-in">
  <header class="tp-head"><em>1</em><h2>Start</h2><p>Before your first wash day.</p></header>
  <div class="tp-two">
    <div><h3>The goal</h3><p class="tp-lead">{e(d['goal'])}</p><p>{e(d['goal_note'])}</p></div>
    <dl class="tp-facts">{facts}</dl>
  </div>
  <h3>The four pillars</h3>
  <ol class="tp-pillars">{pillars}</ol>
  <div class="tp-two tp-gap">
    <div><h3>Take stock</h3><p>Note these down on day one, with photos, so week 8 has something to compare against.</p><ul class="tp-baseline">{baseline}</ul><p class="tp-small">{e(d['baseline_note'])}</p></div>
    <div><h3>Gather your kit</h3><p>Products by the job they do, not by brand.</p>{kit}</div>
  </div>
</div></section>

<section class="tp-act" id="weeks" data-track="none"><div class="tp-in">
  <header class="tp-head"><em>2</em><h2>The 8 weeks</h2><p>One wash day a week. Each week has a focus and one decision.</p></header>
  <fieldset class="tp-tracks"><legend>Your protein track</legend><p>{e(T['intro'])}</p>
    <div class="tp-track-row">{track_card('a')}{track_card('b')}</div>
    <label class="tp-unsure"><input type="radio" name="track" value="none" checked> Not sure yet: show the general schedule</label>
  </fieldset>
  <nav class="tp-rail" aria-label="Choose a week">{rail}</nav>
  <div class="tp-panels">{panels}</div>
  <p class="tp-small tp-saved">Ticks and your track are saved on this device only.</p>

  <div class="tp-two tp-gap">
    <div><h3>Every wash day</h3><ol class="tp-steps">{wash}</ol></div>
    <div><h3>Every day</h3><div class="tp-daily">{daily}</div>
      <h3 class="tp-h3gap">If something feels off</h3>{adjust}</div>
  </div>
</div></section>

<section class="tp-act tp-why" id="why"><div class="tp-in">
  <header class="tp-head"><em class="tp-q">?</em><h2>Why it works</h2><p>What each ingredient family does, and how strong the evidence is.</p></header>
  <ul class="tp-ing">{ing}</ul>
  <div class="tp-expl">{expl}</div>
</div></section>

<section class="tp-act tp-ink" id="finish"><div class="tp-in">
  <header class="tp-head"><em>3</em><h2>Finish</h2><p>End of week 8.</p></header>
  <div class="tp-two">
    <div><h3>Compare baseline and week 8</h3>{lis(F['compare'], 'tp-compare')}</div>
    <div><h3>Your maintenance routine</h3><p class="tp-lead">{e(F['maintenance'])}</p>
      <h3 class="tp-h3gap">Where to next</h3><div class="tp-next">{nxt}</div></div>
  </div>
</div></section>
<p class="source tp-in tp-source"><span>The Good Coil Signature Care Program · Ref {e(d['id'])} · Test layout</span><a href="{r}programs/{e(d['slug'])}/">Earlier version of this page</a></p>
<script src="{r}assets/test-program.js" defer></script>'''
    html = B.shell(r, f"{d['name']}: 8-week care program · The Good Coil", f"{d['name']}: {d['tagline']} An 8-week care program from The Good Coil.", body, f"test-program/{d['slug']}/", 'plans')
    html = html.replace('<main id="main" class="wrap">', '<main id="main" class="tp">', 1).replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex">', 1)
    B.write(f"test-program/{d['slug']}/index.html", html)

def build():
    path = os.path.join(B.ROOT, 'content', 'test-program.json')
    if not os.path.exists(path):
        return
    d = json.load(open(path, encoding='utf-8'))
    page(d)
    B.shutil.copy(os.path.join(B.ROOT, 'src', 'test-program.js'), os.path.join(B.OUT, 'assets', 'test-program.js'))
    body = f'''<section class="page-head"><span class="eyebrow"><span class="little-dot"></span>Test</span><h1>Test program layouts</h1><p>Layouts being tried before they replace the live plan pages.</p></section>
  <ul class="ing-list"><li><a href="{d['slug']}/"><b>{e(d['name'])}</b><span>Three acts with a week planner</span></a></li></ul>'''
    B.write('test-program/index.html', B.shell('../', 'Test program layouts · The Good Coil', 'Test layouts.', body, 'test-program/', 'plans').replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex">', 1))

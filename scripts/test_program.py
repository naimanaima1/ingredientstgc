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

def fold(calm, title, count, inner, intro=''):
    """Calm pages tuck reference material into fold-outs; full pages show it under a heading."""
    if calm:
        return f'<details class="tp-fold"><summary>{e(title)}<small>{e(count)}</small></summary>{f"<p>{e(intro)}</p>" if intro else ""}{inner}</details>'
    return f'<div><h3>{e(title)}</h3>{f"<p>{e(intro)}</p>" if intro else ""}{inner}</div>'

def page(d):
    r = '../../'
    calm = bool(d.get('calm'))
    T = d.get('tracks')
    F = d['finish']
    principle = ''.join(f'<li>{e(x)}</li>' for x in d['principle'])
    best = dict(d['overview'])
    facts = ''.join(f'<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k, v in d['overview'])
    pillars = ''.join(f'<li><span>{n}</span><b>{e(t)}</b><p>{e(x)}</p></li>' for n, (t, x) in enumerate(d['pillars'], 1))
    baseline = '<ul class="tp-baseline">' + ''.join(f'<li><b>{e(a)}</b><span>{e(b)}</span></li>' for a, b in d['baseline']) + f'</ul><p class="tp-small">{e(d.get("baseline_note", ""))}</p>'
    kit = ''.join(f'<div class="tp-kit"><h4>{e(t)}{f"<small>{e(s)}</small>" if s else ""}</h4><ul>' + ''.join(f'<li><b>{e(a)}</b><span>{e(b)}</span></li>' for a, b in items) + '</ul></div>' for t, s, items in d['kit'])
    n_kit = sum(len(items) for _, _, items in d['kit'])
    guard = ''
    if d.get('guardrail'):
        src = f'<p class="tp-ref">Source: {e(d["guardrail_source"])}</p>' if d.get('guardrail_source') else ''
        guard = f'<div class="guard tp-guard"><b>When to see a dermatologist</b><p>{e(d["guardrail"])}</p>{src}</div>'

    tracks = ''
    if T:
        def track_card(k):
            t = T[k]
            wk = ''.join(f'<li><b>Week {w}</b> {e(x)}</li>' for w, x in t['weeks'].items())
            return f'''<label class="tp-track"><input type="radio" name="track" value="{k}"><span class="tp-track-in"><small>{e(t['name'])}</small><b>{e(t['title'])}</b><span>{e(t['who'])}</span><ul>{wk}</ul></span></label>'''
        tracks = f'''<fieldset class="tp-tracks"><legend>Your protein track</legend><p>{e(T['intro'])}</p>
    <div class="tp-track-row">{track_card('a')}{track_card('b')}</div>
    <label class="tp-unsure"><input type="radio" name="track" value="none" checked> Not sure yet: show the general schedule</label>
  </fieldset>'''
    rail = ''.join(f'<a href="#w{n}" data-w="{n}"><em>{n}</em><span>{e(w[0])}</span></a>' for n, w in enumerate(d['weeks'], 1))
    panels = ''
    for n, (short, title, focus, decision, todo) in enumerate(d['weeks'], 1):
        alt = ''.join(f'<p class="tp-dec t-{k}"><small>{e(T[k]["name"])}</small>{e(T[k]["weeks"][str(n)])}</p>' for k in ('a', 'b') if T and str(n) in T[k]['weeks'])
        checks = ''.join(f'<li><label><input type="checkbox" data-k="w{n}-{i}"><span>{e(x)}</span></label></li>' for i, x in enumerate(todo))
        panels += f'''<article class="tp-week{' has-alt' if alt else ''}" id="w{n}">
        <div><span class="eyebrow">Week {n} of {len(d['weeks'])}</span><h3>{e(title)}</h3>{f'<p class="tp-focus">{e(focus)}.</p>' if focus else ''}
        {f'<p class="tp-dec t-none"><small>The decision</small>{e(decision)}.</p>' if decision else ''}{alt}</div>
        <ul class="tp-checks">{checks}</ul></article>'''
    wash = '<ol class="tp-steps">' + ''.join(f'<li><span>{n}</span><p>{e(x)}</p></li>' for n, x in enumerate(d['wash_day'], 1)) + '</ol>' + (f'<p class="tp-small">{e(d["wash_day_note"])}</p>' if d.get('wash_day_note') else '')
    daily = '<div class="tp-daily">' + ''.join(f'<div><h4>{e(k)}</h4>{lis(v, "ticks")}</div>' for k, v in d['daily'].items()) + '</div>'
    adjust = ''.join(f'<div class="tp-adjust"><h4>{e(t)}</h4><ol>' + ''.join(f'<li>{e(x)}</li>' for x in steps) + '</ol></div>' for t, steps in d.get('adjust', []))

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
    ing = '<ul class="tp-ing">' + ''.join(f'''<li><div><b>{e(n)}</b><p>{e(f)}</p><p class="tp-links">{links(ls)}</p></div><div><span class="ev ev-{k}">{e(LABELS[k])}</span><p>{e(note)}</p></div></li>''' for n, f, k, note, ls in d['ingredients']) + '</ul>'
    expl = ''.join(f'<details><summary>{e(t)}</summary>' + ''.join(f'<p>{e(x)}</p>' for x in ps) + (f'<p class="tp-ref">Source: {e(ref)}</p>' if ref else '') + '</details>' for t, ps, ref in d['explainers'])
    nxt = ''.join(f'<a href="{r}{u}"><small>{e(why)}</small><b>{e(n)} →</b></a>' for n, why, u in F['next'])

    if calm:
        start = f'''<div class="tp-two">
    <div><h3>The goal</h3><p class="tp-lead">{e(d['goal'])}</p><p>{e(d['goal_note'])}</p>{guard}</div>
    <div><h3>The {len(d['pillars'])} pillars</h3><ol class="tp-pillars tp-plain">{pillars}</ol></div>
  </div>
  <div class="tp-folds">{fold(True, 'Take stock before you start', f"{len(d['baseline'])} things to note", baseline)}{fold(True, 'Gather your kit', f'{n_kit} products, by job', kit)}</div>'''
        during = f'''<h3 class="tp-h3gap">Every day</h3>{daily}
  <div class="tp-folds">{fold(True, 'Every wash day', f"{len(d['wash_day'])} steps", wash)}{fold(True, 'If something feels off', f"{len(d['adjust'])} situations", adjust) if adjust else ''}</div>'''
        why = f'''<div class="tp-folds">{fold(True, 'Ingredients and the evidence', f"{len(d['ingredients'])} ingredient families", ing)}</div><div class="tp-expl">{expl}</div>'''
    else:
        start = f'''<div class="tp-two">
    <div><h3>The goal</h3><p class="tp-lead">{e(d['goal'])}</p><p>{e(d['goal_note'])}</p>{guard}</div>
    <dl class="tp-facts">{facts}</dl>
  </div>
  <h3>The {len(d['pillars'])} pillars</h3>
  <ol class="tp-pillars">{pillars}</ol>
  <div class="tp-two tp-gap">{fold(False, 'Take stock', '', baseline, 'Note these down on day one, with photos, so week 8 has something to compare against.')}{fold(False, 'Gather your kit', '', kit, 'Products by the job they do, not by brand.')}</div>'''
        during = f'''<div class="tp-two tp-gap">
    <div><h3>Every wash day</h3>{wash}</div>
    <div><h3>Every day</h3>{daily}{f'<h3 class="tp-h3gap">If something feels off</h3>{adjust}' if adjust else ''}</div>
  </div>'''
        why = f'{ing}<div class="tp-expl">{expl}</div>'

    fin_left = (f'<h3>Compare baseline and week 8</h3>{lis(F["compare"], "tp-compare")}' if F.get('compare') else
                '<h3>What to expect</h3>' + ''.join(f'<p class="tp-lead">{e(x)}</p>' for x in F.get('expect', [])[:1]) + ''.join(f'<p>{e(x)}</p>' for x in F.get('expect', [])[1:]))
    fin_right = (f'<h3>Your maintenance routine</h3><p class="tp-lead">{e(F["maintenance"])}</p><h3 class="tp-h3gap">Where to next</h3>' if F.get('maintenance') else '<h3>Where to next</h3>') + f'<div class="tp-next">{nxt}</div>'

    body = f'''<p class="pf-test tp-test" role="note"><b>Test layout.</b> Not linked from the site and hidden from search engines.</p>
<section class="tp-hero">
  <div class="tp-copy">
    <span class="eyebrow">{e(d.get('eyebrow', '8-week program · conditioning and moisture'))}</span>
    <h1>{e(d['name'])}</h1>
    <ol class="tp-principle">{principle}</ol>
    <p class="tp-best"><b>Best suited for</b> {e(best.get('Best suited for', '').lower())}.</p>
  </div>
  <div class="tp-photo"><img src="{r}assets/img/{e(d['image'])}" alt="{e(d['image_alt'])}" width="799" height="1344"></div>
</section>
<nav class="tp-acts" aria-label="The program in three parts">
  <a href="#start"><em>1</em><b>Start</b><span>Is it for you, take stock, gather your kit</span></a>
  <a href="#weeks"><em>2</em><b>The 8 weeks</b><span>Week by week, wash day, daily habits</span></a>
  <a href="#finish"><em>3</em><b>Finish</b><span>{'Compare, then build your maintenance routine' if F.get('compare') else 'What to expect, and where to next'}</span></a>
</nav>

<section class="tp-act tp-mist" id="start"><div class="tp-in">
  <header class="tp-head"><em>1</em><h2>Start</h2><p>Before your first wash day.</p></header>
  {start}
</div></section>

<section class="tp-act" id="weeks" data-track="none"><div class="tp-in">
  <header class="tp-head"><em>2</em><h2>The 8 weeks</h2><p>{e(d.get('weeks_intro', 'One wash day a week. Each week has a focus and one decision.'))}</p></header>
  {tracks}
  <nav class="tp-rail" aria-label="Choose a week">{rail}</nav>
  <div class="tp-panels">{panels}</div>
  <p class="tp-small tp-saved">Ticks{' and your track' if T else ''} are saved on this device only.</p>
  {during}
</div></section>

<section class="tp-act tp-why" id="why"><div class="tp-in">
  <header class="tp-head"><em class="tp-q">?</em><h2>Why it works</h2><p>What each ingredient family does, and how strong the evidence is.</p></header>
  {why}
</div></section>

<section class="tp-act tp-ink" id="finish"><div class="tp-in">
  <header class="tp-head"><em>3</em><h2>Finish</h2><p>End of week 8.</p></header>
  <div class="tp-two"><div>{fin_left}</div><div>{fin_right}</div></div>
</div></section>
<p class="source tp-in tp-source"><span>The Good Coil Signature Care Program · Ref {e(d['id'])} · Test layout</span><a href="{r}programs/{e(d['slug'])}/">Earlier version of this page</a></p>
<script src="{r}assets/test-program.js" defer></script>'''
    html = B.shell(r, f"{d['name']}: 8-week care program · The Good Coil", f"{d['name']}: {d['tagline']} An 8-week care program from The Good Coil.", body, f"test-program/{d['slug']}/", 'plans')
    html = html.replace('<main id="main" class="wrap">', f'<main id="main" class="tp{" tp-calm" if calm else ""}">', 1).replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex">', 1)
    B.write(f"test-program/{d['slug']}/index.html", html)

def build():
    folder = os.path.join(B.ROOT, 'content')
    files = sorted(f for f in os.listdir(folder) if f.startswith('test-program') and f.endswith('.json'))
    if not files:
        return
    progs = [json.load(open(os.path.join(folder, f), encoding='utf-8')) for f in files]
    for d in progs:
        page(d)
    B.shutil.copy(os.path.join(B.ROOT, 'src', 'test-program.js'), os.path.join(B.OUT, 'assets', 'test-program.js'))
    import guide
    guides = guide.build()
    rows = ''.join(f'<li><a href="{d["slug"]}/"><b>{e(d["name"])}</b><span>{"Calmer version: reference material folded away" if d.get("calm") else "Full version: everything open"}</span></a></li>' for d in progs)
    rows = ''.join(f'<li><a href="{g["slug"]}/"><b>{e(g["name"])}</b><span>Guide shape: plain language, single column</span></a></li>' for g in guides) + rows
    body = f'''<section class="page-head"><span class="eyebrow"><span class="little-dot"></span>Test</span><h1>Test program layouts</h1><p>Layouts being tried before they replace the live plan pages.</p></section>
  <ul class="ing-list">{rows}</ul>'''
    B.write('test-program/index.html', B.shell('../', 'Test program layouts · The Good Coil', 'Test layouts.', body, 'test-program/', 'plans').replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex">', 1))

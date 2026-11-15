"""TEST: the earlier, simpler plan pages, now at /test-program/simple-<slug>/ (noindex, unlinked).

Still the source of data/plans.json, the machine-readable file JARA will copy.

Inputs:
    data/programs.csv       one row per program (the "Programs Overview" tab)
    data/program-steps.csv  one row per step (the "Program steps" tab)

program-steps columns:
    program_id, order, step, when, weeks, wash_day_role, property, condition, product_ids, notes
    when = every_wash | every_<N>_days | daily | nightly | weeks   (weeks uses the "weeks" column, e.g. "3,6"; 0 = before you start)
"""
import json, os, re
import build as B

e = B.e
ROLE_ORDER = ['cleanse', 'condition', 'treatment', 'leave-in', 'style', 'seal']
ROLE_LABEL = {'cleanse': 'Cleanse', 'condition': 'Condition', 'treatment': 'Treat', 'leave-in': 'Leave-in', 'style': 'Style', 'seal': 'Seal'}
DEFAULT_IMAGES = ['hairline.jpg', 'ends.jpg']
IMAGE_ALT = {
    'hairline.jpg': 'A woman with long, dark curly hair presses her fingertips along her hairline and side part.',
    'ends.jpg': 'A woman with long, dark curly hair, in profile, holds the ends of a curl between her fingers.',
}

def split_outside_parens(s, sep=','):
    return [p.strip() for p in re.split(rf'{re.escape(sep)}(?![^()]*\))', s or '') if p.strip()]

def when_of(s):
    w = (s.get('when') or '').strip().lower()
    m = re.match(r'every_(\d+)_days?$', w)
    weeks = [int(x) for x in re.findall(r'\d+', s.get('weeks') or '')]
    if m:
        return {'type': 'every_n_days', 'days': int(m.group(1))}
    if w == 'weeks':
        return {'type': 'weeks', 'weeks': weeks}
    if w in ('every_wash', 'daily', 'nightly'):
        return {'type': w}
    return {'type': 'note'}

def when_label(wh):
    t = wh['type']
    if t == 'every_wash': return 'Every wash day'
    if t == 'daily': return 'Every day'
    if t == 'nightly': return 'Every night'
    if t == 'every_n_days':
        d = wh['days']
        return 'Every week' if d == 7 else 'Every 2 weeks' if d == 14 else f'Every {d} days'
    if t == 'weeks':
        ws = ['before you start' if w == 0 else str(w) for w in wh['weeks']]
        nums = [w for w in ws if w.isdigit()]
        pre = ['Before you start'] if 'before you start' in ws else []
        if nums:
            pre.append(('Week ' if len(nums) == 1 else 'Weeks ') + (' and '.join(nums) if len(nums) < 3 else ', '.join(nums[:-1]) + ' and ' + nums[-1]))
        return ' · '.join(pre)
    return ''

def weeks_on(wh, total):
    t = wh['type']
    if t == 'every_n_days':
        step = max(1, round(wh['days'] / 7))
        return [w for w in range(1, total + 1) if w % step == 0]
    if t == 'weeks':
        return [w for w in wh['weeks'] if 0 <= w <= total]
    return []

def load():
    progs = [p for p in B.read_csv('programs.csv') if p.get('program_id') and p.get('program_name')]
    steps = B.read_csv('program-steps.csv')
    cat_by_id = {c.get('id'): c for c in B.cat}
    out = []
    for n, p in enumerate(progs):
        total = int(re.sub(r'\D', '', p.get('duration_weeks') or '') or 8)
        rows = sorted([s for s in steps if s.get('program_id') == p['program_id']], key=lambda s: int(re.sub(r'\D', '', s.get('order') or '') or 99))
        st = []
        for s in rows:
            wh = when_of(s)
            picks = []
            for pid in re.split(r'[,\s]+', s.get('product_ids') or ''):
                c = cat_by_id.get(pid)
                if c:
                    picks.append({'id': pid, 'name': c.get('name', '').strip(), 'brand': c.get('brand', '').strip()})
            st.append({'order': len(st) + 1, 'name': s.get('step', ''), 'when': wh, 'wash_day_role': (s.get('wash_day_role') or '').lower() or None,
                       'property': s.get('property') or None, 'condition': s.get('condition') or None, 'products': picks, 'notes': s.get('notes') or None})
        gp = re.split(r'(Medical guardrail:|Guardrail:)', p.get('editorial_promise_and_guardrails') or '', maxsplit=1)
        promise = re.sub(r'^\s*Promise:\s*', '', gp[0]).strip()
        guardrail = gp[2].strip() if len(gp) > 2 else ''
        pillars = []
        for part in split_outside_parens(p.get('pillars')):
            pillars += [x.strip() for x in part.split(' + ') if x.strip()]
        cleanse = [s for s in st if s['wash_day_role'] == 'cleanse' and s['when']['type'] == 'every_n_days']
        img = (p.get('image') or '').strip() or ('hairline.jpg' if re.search(r'hairline|edge', p.get('focus_area', '') + p['program_name'], re.I) else DEFAULT_IMAGES[n % 2])
        out.append({
            'id': p['program_id'], 'slug': B.col(p, 'slug') or B.slugify(p['program_name']), 'version': B.col(p, 'version') or '1',
            'name': p['program_name'], 'tagline': p.get('tagline', ''), 'focus_area': p.get('focus_area', ''), 'duration_weeks': total,
            'pillars': pillars, 'objective': p.get('objective', ''),
            'assessment': [a.strip() for a in (p.get('starting_assessment_fields') or '').rstrip('.').split(';') if a.strip()],
            'track': [a.strip() for a in (p.get('success_measurements') or '').rstrip('.').split(';') if a.strip()],
            'wash_every_days': cleanse[0]['when']['days'] if cleanse else None,
            'steps': st, 'cadence_summary': p.get('core_cadence_summary', ''), 'promise': promise, 'guardrail': guardrail,
            'image': img,
        })
    return out

def pill(text, cls=''):
    return f'<span class="pill {cls}">{e(text)}</span>'

def label_and_detail(s):
    m = re.match(r'(.*?)\s*\((.*)\)\s*$', s)
    return (m.group(1), m.group(2)) if m else (s, '')

def plan_page(p):
    r = '../../'
    total = p['duration_weeks']
    test_note = '<p class="pf-test tp-test" role="note"><b>Earlier layout.</b> Kept for reference; not linked from the site.</p>'
    recipe = sorted([s for s in p['steps'] if s['wash_day_role']], key=lambda s: (ROLE_ORDER.index(s['wash_day_role']) if s['wash_day_role'] in ROLE_ORDER else 9, s['order']))
    habits = [s for s in p['steps'] if s['when']['type'] in ('daily', 'nightly')]
    tracking = [s for s in p['steps'] if not s['wash_day_role'] and s['when']['type'] in ('weeks', 'every_n_days')]

    def extras(s):
        bits = []
        if s['property']:
            bits.append(f'<a class="prop" href="{r}properties/{B.prop_slug(s["property"])}/">{e(s["property"])}</a>')
        if s['condition']:
            bits.append(f'<span class="cond">{e(s["condition"])}</span>')
        if s['notes']:
            bits.append(f'<span class="cond">{e(s["notes"])}</span>')
        if s['products']:
            bits.append('<span class="cond">Our pick: ' + ', '.join(f'{e(x["brand"])} {e(x["name"])}' for x in s['products']) + '</span>')
        return f'<div class="step-extra">{"".join(bits)}</div>' if bits else ''

    rec_rows = ''.join(f'''<li><span class="role">{e(ROLE_LABEL.get(s['wash_day_role'], s['wash_day_role'].capitalize()))}</span><div><b>{e(s['name'])}</b>{pill(when_label(s['when']), 'soft' if s['when']['type'] == 'every_wash' else '')}{extras(s)}</div></li>''' for s in recipe)
    wash_line = f"Wash every {'week' if p['wash_every_days'] == 7 else str(p['wash_every_days']) + ' days'}. " if p['wash_every_days'] else ''

    grid_steps = [s for s in p['steps'] if weeks_on(s['when'], total)]
    head = '<th scope="col"><span class="sr">Step</span></th><th scope="col">Start</th>' + ''.join(f'<th scope="col">{w}</th>' for w in range(1, total + 1))
    body = ''
    for s in grid_steps:
        on = set(weeks_on(s['when'], total))
        mark = 'wk-check' if s['when']['type'] == 'weeks' else 'wk-dot'
        cells = ''.join(f'<td>{f"<i class={chr(34)}{mark}{chr(34)} aria-label={chr(34)}yes{chr(34)}></i>" if w in on else ""}</td>' for w in range(0, total + 1))
        body += f'<tr><th scope="row">{e(s["name"])}<small>{e(when_label(s["when"]))}</small></th>{cells}</tr>'
    grid = f'''<div class="grid-wrap" tabindex="0" role="region" aria-label="{total} weeks, step by step"><table class="weeks"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>
      <p class="legend"><span><i class="wk-dot"></i> repeats</span><span><i class="wk-check"></i> set weeks</span></p>'''

    hab_rows = ''.join(f'<li><b>{e(s["name"])}</b>{pill(when_label(s["when"]), "soft")}{extras(s)}</li>' for s in habits)
    assess = ''.join(f'<li><b>{e(a)}</b>{f"<span>{e(d)}</span>" if d else ""}</li>' for a, d in map(label_and_detail, p['assessment']))
    track = ''.join(f'<li>{e(t)}</li>' for t in p['track'])
    track_steps = ''.join(f'<li><b>{e(s["name"])}</b>{pill(when_label(s["when"]), "soft")}{extras(s)}</li>' for s in tracking)
    pillars = ''.join(f'<span class="tag">{e(re.sub(r"\s*\(.*?\)", "", x))}</span>' for x in p['pillars'])
    img = p['image']

    sections = f'''
  <section class="section" id="wash">
    <div class="intro"><span class="eyebrow">On wash day</span><h2>Your wash-day recipe</h2><p>{e(wash_line)}Steps are roles, not brands: use products you already own that do the job.</p></div>
    <ol class="recipe">{rec_rows}</ol>
  </section>
  <section class="section" id="weeks">
    <div class="intro"><span class="eyebrow">{total} weeks</span><h2>Week by week</h2><p>What repeats, and what happens in set weeks. Start is the day before week 1.</p></div>
    <div>{grid}</div>
  </section>'''
    if habits:
        sections += f'''
  <section class="section" id="daily">
    <div class="intro"><span class="eyebrow">Between wash days</span><h2>Small daily habits</h2></div>
    <ul class="plain">{hab_rows}</ul>
  </section>'''
    if assess:
        sections += f'''
  <section class="section" id="start">
    <div class="intro"><span class="eyebrow">Before you start</span><h2>Take stock first</h2><p>Note these down on day one, so you can compare at the end.</p></div>
    <ul class="assess">{assess}</ul>
  </section>'''
    if track or track_steps:
        sections += f'''
  <section class="section" id="track">
    <div class="intro"><span class="eyebrow">Progress</span><h2>What to track</h2></div>
    <div><ul class="plain">{track_steps}</ul>{f'<h3 class="sub">How you\'ll know it\'s working</h3><ul class="ticks">{track}</ul>' if track else ''}</div>
  </section>'''
    if p['promise'] or p['guardrail']:
        sections += f'''
  <section class="section" id="promise">
    <div class="intro"><span class="eyebrow">Our promise</span><h2>What this plan is</h2></div>
    <div class="promise">{f'<p class="note">{e(p["promise"])}</p>' if p['promise'] else ''}{f'<div class="guard"><b>See a dermatologist</b><p>{e(p["guardrail"])}</p></div>' if p['guardrail'] else ''}</div>
  </section>'''

    body = f'''  {test_note}
  <a class="crumb" href="../">← Test layouts</a>
  <section class="plan-hero">
    <figure class="plan-photo"><img src="{r}assets/img/{e(img)}" alt="{e(IMAGE_ALT.get(img, ''))}" width="799" height="1344"></figure>
    <div class="plan-intro">
      <span class="eyebrow"><span class="little-dot"></span>Signature program · {total} weeks</span>
      <h1>{e(p['name'])}</h1>
      <p class="tagline"><em>{e(p['tagline'])}</em></p>
      <p class="lead">{e(p['objective'])}</p>
      <div class="pillars">{pillars}</div>
      <nav class="jump" aria-label="On this page"><a href="#wash">Wash-day recipe</a><a href="#weeks">Week by week</a>{'<a href="#daily">Daily habits</a>' if habits else ''}<a href="#track">What to track</a></nav>
      <p class="jara-soon"><b>Coming to JARA:</b> follow this plan with a reminder for each step and a check-in every few weeks. <a href="https://itsjara.com">About JARA</a></p>
    </div>
  </section>
  {sections}
  <p class="source"><span>The Good Coil signature program · Ref {e(p['id'])} · Version {e(p['version'])}</span><a href="{r}data/plans.json">Get this as data (JSON)</a><a href="{r}about/">How we write these</a></p>'''
    desc = f"{p['name']}: an {total}-week hair-care plan from The Good Coil. {p['tagline']}"
    html = B.shell(r, f"{p['name']}: {total}-week hair plan · The Good Coil", desc, body, f"test-program/simple-{p['slug']}/", 'plans')
    B.write(f"test-program/simple-{p['slug']}/index.html", html.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex">', 1))

def plans_index(plans):
    r = '../'
    cards = ''.join(f'''<li><a href="../simple-{p['slug']}/"><img src="../../assets/img/{e(p['image'])}" alt="" width="799" height="1344" loading="lazy"><span class="eyebrow">{e(p['focus_area'])} · {p['duration_weeks']} weeks</span><h2>{e(p['name'])}</h2><p><em>{e(p['tagline'])}</em></p></a></li>''' for p in plans)
    body = f'''  <p class="pf-test tp-test" role="note"><b>Earlier layout.</b> Kept for reference; not linked from the site.</p>
  <section class="page-head"><span class="eyebrow"><span class="little-dot"></span>Earlier layout</span><h1>Simple plans</h1>
  <p>Structured {plans[0]['duration_weeks'] if plans else 8}-week plans: a wash-day recipe, what happens each week, small daily habits and what to track. Steps are roles, not brands, so you can use what you already own.</p></section>
  <ul class="plan-cards">{cards}</ul>'''
    B.write('test-program/simple-plans/index.html', B.shell('../../', 'Simple plans (earlier layout) · The Good Coil', 'Earlier plan layout.', body, 'test-program/simple-plans/', 'plans').replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex">', 1))

def build():
    plans = load()
    if not plans:
        return [], []
    os.makedirs(os.path.join(B.OUT, 'assets', 'img'), exist_ok=True)
    src = os.path.join(B.ROOT, 'src', 'img')
    for f in os.listdir(src):
        B.shutil.copy(os.path.join(src, f), os.path.join(B.OUT, 'assets', 'img', f))
    for p in plans:
        plan_page(p)
    plans_index(plans)
    data = {
        'schema': 1,
        'generated': B.datetime.datetime.now(B.datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source': 'The Good Coil signature programs',
        'plans': [{k: v for k, v in p.items() if k != 'image'} | {'url': f"{B.SITE}/plans/{p['slug']}/"} for p in plans],
    }
    B.write('data/plans.json', json.dumps(data, ensure_ascii=False, indent=1))
    notes = []
    for p in plans:
        if not p['steps']:
            notes.append(f"- {p['id']} {p['name']}: no rows in the Program steps tab yet (the page shows no schedule)")
        for s in p['steps']:
            if s['when']['type'] == 'note':
                notes.append(f"- {p['id']} step {s['order']} \"{s['name']}\": 'when' not recognised")
    return [], notes

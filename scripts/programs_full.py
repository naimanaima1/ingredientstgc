"""TEST: the full Signature Care Programs at /programs/ (noindex, not linked from the menu).

Content: content/programs-full.json, transcribed from the owner's "Intensive Care Collection"
document. The existing /plans/ pages and data/plans.json are untouched.
"""
import json, os, re
import build as B

e = B.e
LABELS = {'established': 'Established practice', 'promising': 'Promising', 'emerging': 'Emerging',
          'cosmetic': 'Cosmetic support', 'formulation': 'Formulation-dependent'}
IMAGE_ALT = {
    'hairline.jpg': 'A woman with long, dark curly hair presses her fingertips along her hairline and side part.',
    'ends.jpg': 'A woman with long, dark curly hair, in profile, holds the ends of a curl between her fingers.',
}
TEST_BANNER = '<p class="pf-test" role="note"><b>Test version.</b> This page isn\'t linked from the site yet and is hidden from search engines.</p>'

def load():
    with open(os.path.join(B.ROOT, 'content', 'programs-full.json'), encoding='utf-8') as fh:
        return json.load(fh)

def noindex(html):
    return html.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex">', 1)

def linkify(text, r):
    """Link ingredient names that have a page in the library."""
    out = []
    for part in [p.strip() for p in re.split(r',(?![^()]*\))', text) if p.strip()]:
        bare = re.sub(r'^(and|or)\s+', '', part)
        i = B.lookup(bare) or B.lookup(bare.rstrip('s'))
        out.append(f'<a href="{r}{i["_slug"]}/">{e(part)}</a>' if i else e(part))
    return ', '.join(out)

def badge(key):
    return f'<span class="ev ev-{e(key)}">{e(LABELS.get(key, key))}</span>'

def table(cols, rows, cls='pf-table'):
    head = ''.join(f'<th scope="col">{e(c)}</th>' for c in cols)
    body = ''.join('<tr>' + ''.join((f'<th scope="row">{e(v)}</th>' if k == 0 else f'<td>{e(v)}</td>') for k, v in enumerate(row)) + '</tr>' for row in rows)
    return f'<div class="pf-scroll"><table class="{cls}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'

def section(id_, eyebrow, title, intro, body):
    intro_html = ''.join(f'<p>{e(p)}</p>' for p in ([intro] if isinstance(intro, str) and intro else intro or []))
    return f'''
  <section class="section" id="{id_}">
    <div class="intro"><span class="eyebrow">{e(eyebrow)}</span><h2>{e(title)}</h2>{intro_html}</div>
    <div class="pf-body">{body}</div>
  </section>'''

def program_page(p, col, by_id):
    r = '../../'
    cat = {c.get('id'): c for c in B.cat}
    chapters = [('why', 'Why'), ('start', 'Before you start'), ('protocol', 'Protocol'), ('wash', 'Wash day'),
                ('daily', 'Every day') if p['daily'] else None, ('weeks', 'Week by week'), ('use', 'What to use'),
                ('science', 'Ingredient science'), ('trouble', 'Troubleshooting'), ('track', 'Track'), ('after', 'After week 8')]
    chapters = [c for c in chapters if c]
    jump = ''.join(f'<a href="#{a}">{e(b)}</a>' for a, b in chapters)

    pillars = ''.join(f'<li><b>{e(n)}</b>{f"<p>{e(t)}</p>" if t else ""}</li>' for n, t in p['pillars'])
    why = f'<p class="pf-philosophy"><em>{e(col["philosophy"])}</em></p>' + (f'<p class="pf-lead2">{e(p["intro"])}</p>' if p['intro'] else '') + f'<ul class="pf-pillars">{pillars}</ul>'

    assess = ''.join(f'<li><b>{e(a)}</b><span>{e(d)}</span></li>' for a, d in p['assessment'])
    start = f'<ul class="assess">{assess}</ul>' + (f'<p class="pf-note">{e(p["assessment_note"])}</p>' if p['assessment_note'] else '')
    if p['guardrail']:
        start += f'<div class="guard"><b>When to see a dermatologist</b><p>{e(p["guardrail"])}</p></div>'

    protocol = ''
    for g in p['protocol']:
        has_purpose = any(row[2] for row in g['rows'])
        cols = ['Component', 'Cadence', 'Purpose'] if has_purpose else ['Component', 'Cadence']
        rows = [row if has_purpose else row[:2] for row in g['rows']]
        protocol += (f'<h3 class="sub">{e(g["title"])}</h3>' if g['title'] else '') + table(cols, rows)
    if p['protocol_note']:
        protocol += f'<p class="pf-note">{e(p["protocol_note"])}</p>'

    wash = '<ol class="pf-steps">' + ''.join(f'<li><span>{n}</span><p>{e(s)}</p></li>' for n, s in enumerate(p['wash_day'], 1)) + '</ol>'
    if p['wash_day_note']:
        wash += f'<p class="pf-note"><b>Label first:</b> {e(p["wash_day_note"])}</p>'

    daily = ''
    if p['daily']:
        daily = '<div class="pf-daily">' + ''.join(f'<div><h3 class="sub">{e(k)}</h3><ul class="ticks">' + ''.join(f'<li>{e(x)}</li>' for x in v) + '</ul></div>' for k, v in p['daily'].items()) + '</div>'

    weeks = table(p['progression']['columns'], p['progression']['rows'], 'pf-table pf-weeks')
    weeks += '<p class="pf-note">' + ' · '.join(f'<b>{e(a)}</b> {e(b.lower())}' for a, b in col['photos']) + '</p>'

    use_rows = ''
    for name, ings, role, picks in p['products']:
        def full(c):
            b, n = c.get('brand', '').strip(), c.get('name', '').strip()
            return e(n if n.lower().startswith(b.lower()) else f'{b} {n}')
        names = [full(cat[i]) for i in picks if i in cat]
        use_rows += f'''<li><div class="pf-use-head"><b>{e(name)}</b>{f'<span>{e(role)}</span>' if role else ''}</div>
        <p><span class="pf-k">Ingredients to look for</span> {linkify(ings, r)}</p>
        {f'<p class="pf-picks"><span class="pf-k">Examples from our catalog <i class="pf-draft">draft</i></span> {"; ".join(names)}</p>' if names else '<p class="pf-picks"><span class="pf-k">Examples from our catalog</span> none yet</p>'}</li>'''
    use = f'<ul class="pf-use">{use_rows}</ul><p class="pf-note">Steps are roles, not brands: any product that does the job works. Examples are listed for reference, not as paid placements.</p>'

    def card_link(n, l):
        if l:
            return l
        i = B.lookup(n)
        return f"{i['_slug']}/" if i else ''
    cards = ''.join(f'''<li class="pf-card">{badge(k)}<h3>{e(n)}</h3><p>{e(t)}</p>{f'<a href="{r}{card_link(n, l)}">More about it</a>' if card_link(n, l) else ''}</li>''' for n, k, t, l in p['science'])
    legend = ''.join(f'<li>{badge(k)}<span>{e(d)}</span></li>' for k, _, d in col['evidence_labels'])
    science = f'<ul class="pf-cards">{cards}</ul><details class="pf-legend"><summary>What the evidence labels mean</summary><ul>{legend}</ul></details>'

    trouble = table(['If you notice', 'What to look at'], col['troubleshooting']) + f'<p class="pf-note">{e(col["troubleshooting_note"])}</p>'

    track = ''
    if p['success']:
        track += f'<h3 class="sub">How you\'ll know it\'s working{(" · " + e(p["success_when"])) if p["success_when"] else ""}</h3><ul class="ticks">' + ''.join(f'<li>{e(s.rstrip("."))}</li>' for s in p['success']) + '</ul>'
    track += '<h3 class="sub">Scores for each check-in</h3>' + table(['Measure', 'Scale', 'Direction'], col['tracking']) + f'<p class="pf-note">{e(col["tracking_note"])}</p>'

    nxt = by_id.get(p.get('next', ''))
    paths = ''.join(f'<li><span class="pf-n">{n}</span><b>{e(t)}</b><p>{e(d)}</p></li>' for n, (t, d) in enumerate(col['graduation'], 1))
    after = f'<ol class="pf-paths">{paths}</ol>' + (f'<p class="pf-note">Next program after this one: <a href="../{nxt["slug"]}/">{e(nxt["name"])}</a></p>' if nxt else '')

    promise = f'<div class="promise"><p class="note"><b>The outcome we promise:</b> {e(p["promise"])}</p><p class="pf-note">{e(col["timing_note"])}</p></div>'

    sections = (section('why', 'Why this plan', 'The thinking behind it', '', why)
                + section('start', 'Before you start', 'Take stock first', 'Complete this before your first treatment, so week 8 has something to compare against.', start)
                + section('protocol', 'The core protocol', 'What happens, how often', '', protocol)
                + section('wash', 'Wash day', 'Step by step', 'The default order for every wash day.', wash)
                + (section('daily', 'Between wash days', 'Every day', '', daily) if daily else '')
                + section('weeks', '8 weeks', 'Week by week', '', weeks)
                + section('use', 'What to use', 'Products by job', 'Choose products by the job they do in the protocol, not by brand.', use)
                + section('science', 'Ingredient science', 'What the research says', 'Each ingredient family carries an evidence label, so you can see how strong the science behind it is.', science)
                + section('trouble', 'Troubleshooting', 'If something feels off', '', trouble)
                + section('track', 'Progress', 'Track your progress', '', track)
                + section('after', 'After week 8', 'Choose your next step', '', after)
                + section('promise', 'Our promise', 'What this program is', '', promise))

    body = f'''  {TEST_BANNER}
  <a class="crumb" href="../">← Intensive Care Collection</a>
  <section class="plan-hero">
    <figure class="plan-photo"><img src="{r}assets/img/{e(p['image'])}" alt="{e(IMAGE_ALT.get(p['image'], ''))}" width="799" height="1344"></figure>
    <div class="plan-intro">
      <span class="eyebrow"><span class="little-dot"></span>8-week intensive program · {e(p['focus'])}</span>
      <h1>{e(p['name'])}</h1>
      <p class="tagline"><em>{e(p['tagline'])}</em></p>
      <p class="lead">{e(p['objective'])}</p>
      <nav class="jump" aria-label="On this page">{jump}</nav>
      <p class="jara-soon"><b>Coming to JARA:</b> follow this program with reminders for each step, check-ins and photo milestones. <a href="https://itsjara.com">About JARA</a></p>
    </div>
  </section>
  {sections}
  <p class="source"><span>The Good Coil Signature Care Program · Ref {e(p['id'])} · Test</span><a href="{r}data/programs-full.json">Get this as data (JSON)</a></p>'''
    html = B.shell(r, f"{p['name']}: 8-week care program · The Good Coil", f"{p['name']}: {p['tagline']} An 8-week care program from The Good Coil.", body, f"programs/{p['slug']}/", 'plans')
    B.write(f"programs/{p['slug']}/index.html", noindex(html))

def index_page(data):
    col, progs = data['collection'], data['programs']
    cards = ''.join(f'''<li><a href="{p['slug']}/"><img src="../assets/img/{e(p['image'])}" alt="" width="799" height="1344" loading="lazy"><span class="eyebrow">{e(p['focus'])} · 8 weeks</span><h2>{e(p['name'])}</h2><p><em>{e(p['tagline'])}</em></p></a></li>''' for p in progs)
    legend = ''.join(f'<li>{badge(k)}<span>{e(d)}</span></li>' for k, _, d in col['evidence_labels'])
    body = f'''  {TEST_BANNER}
  <section class="page-head"><span class="eyebrow"><span class="little-dot"></span>{e(col['edition'])}</span><h1>{e(col['name'])}</h1>
  <p class="pf-philosophy"><em>{e(col['philosophy'])}</em></p>
  {''.join(f'<p>{e(x)}</p>' for x in col['intro'])}</section>
  <ul class="plan-cards">{cards}</ul>
  {section('standards', 'Shared standards', 'How every program works', col['timing_note'], table(['Standard', 'The Good Coil recommendation'], col['standards']))}
  {section('evidence', 'Evidence labels', 'How we label the science', 'Every ingredient family in these programs carries one of these labels.', f'<ul class="pf-legend-list">{legend}</ul>')}
  {section('responsible', 'Editorial guardrails', 'What we can responsibly say', 'For hair loss, the difference between breakage and shedding matters. A dermatologist can find the cause and decide whether medical treatment is needed; prolonged traction can cause permanent hair loss.', table(['Topic', 'What we can responsibly say'], col['responsible']))}
  {section('refs', 'Research library', 'References', '', '<ul class="ticks">' + ''.join(f'<li>{e(x)}</li>' for x in col['references']) + '</ul>')}'''
    B.write('programs/index.html', noindex(B.shell('../', 'Intensive Care Collection: signature care programs · The Good Coil', 'Three 8-week hair-care programs from The Good Coil.', body, 'programs/', 'plans')))

def build():
    path = os.path.join(B.ROOT, 'content', 'programs-full.json')
    if not os.path.exists(path):
        return []
    data = load()
    by_id = {p['id']: p for p in data['programs']}
    for p in data['programs']:
        program_page(p, data['collection'], by_id)
    index_page(data)
    B.write('data/programs-full.json', json.dumps(data, ensure_ascii=False, indent=1))
    return [p['slug'] for p in data['programs']]

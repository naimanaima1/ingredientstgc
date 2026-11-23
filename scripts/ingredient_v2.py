"""PREVIEW ONLY: ingredient page v2, written at /<slug>/v2/ (noindex, not in the sitemap) for the
ingredients in PREVIEW, so the new layout can be judged next to the live page. Nothing else links here.

What changes from the live page (build.py ingredient_page), from the ingredient pages review:
  - One count, said one way: "In 81 of 134 labels we've read", with where it usually sits.
  - The label names sit right under the headline ("On labels: Glycerin · Glycerine").
  - No eyebrow that repeats the heading; the property tags appear once.
  - The product list shows 12, then "Show all"; the product already on the label card isn't repeated.
  - The position chart has three labelled bands, and its dots are no longer one tab stop each.
  - Step filter buttons keep an outline in Windows High Contrast.
  - Meta description doesn't repeat the name; JSON-LD describes the ingredient.
  - The opening line is the sheet's plain_english_summary, as on the live page.

Delete this file and its lines in build.py when the preview is done.
"""
import json
import build as B

e = B.e

# Matched against the INCI name, the page title and the slug.
PREVIEW = ['glycerin', 'parfum']

DRAFT_LEAD = {}  # the opening line always comes from the sheet (plain_english_summary)

CAP = 12


def _key(g):
    return [B.norm(g.get('inci_name', '')), B.norm(g.get('_title', '')), g.get('_slug', '')]


def find(ing):
    out = []
    for w in PREVIEW:
        for g in ing:
            if any(k == w or k.startswith(w + ' ') or k.endswith(' ' + w) for k in _key(g)):
                out.append((w, g))
                break
    return out


def _h1(text):
    words = text.split(' ')
    if len(words) < 2:
        return e(text)
    return f'{e(" ".join(words[:-1]))} <em>{e(words[-1])}</em>'


def page(g, draft=''):
    import watchlist
    r = '../../'
    hits = B.hits_for(g)
    labels = B.labels
    title = g['_title']
    h1 = B.col(g, 'display_name') or (g.get('common_name') or '').strip() or title
    summary = draft or (g.get('plain_english_summary') or '').strip() or g.get('what_it_does', '')
    deep = (g.get('how_it_works_deep_dive') or '').strip()
    howto = (g.get('how_to_use_and_pair') or '').strip()
    evid = (g.get('evidence_and_nuance') or '').strip()
    note = (g.get('buildup_sensitivity_notes') or '').strip()
    hair = B.col(g, 'hair_type_notes', 'hair_type_porosity_fit')

    # ---- names on labels, right under the headline
    names = []
    for n in [g['inci_name']] + g['_aliases']:
        if B.norm(n) not in [B.norm(x) for x in names]:
            names.append(n)
    same = len(names) == 1 and B.norm(names[0]) == B.norm(h1)
    onlabel = '' if same else f'<p class="iv2-on"><span>On labels</span> {" · ".join(e(a) for a in names)}</p>'

    # ---- the one count
    if hits:
        top = sum(1 for h in hits if h[2] <= 5)
        where = ', usually in the top 5' if top * 2 >= len(hits) and len(hits) > 1 else ''
        fact = f'<p class="iv2-fact">In <b>{len(hits)} of {len(labels)}</b> labels we’ve read{where}.</p>'
    else:
        fact = f'<p class="iv2-fact">Not on any of the {len(labels)} labels we’ve read yet.</p>'

    tags = ''.join(f'<a class="tag" href="{r}properties/{B.prop_slug(t)}/">{e(t)}</a>' for t in g['_tags'])
    cta = (f'<a class="iv2-cta" href="#across">See the {len(hits)} product{"s" if len(hits) != 1 else ""} with it <span aria-hidden="true">&#8595;</span></a>'
           if len(hits) > 1 else '')

    # ---- label card (same as live: it's on the keep list)
    if hits:
        p, items, n = hits[0]
        def word(t):
            i = B.lookup(t)
            if i is g:
                return f'<mark class="hit">{e(t)}</mark>'
            if i:
                return f'<a href="{r}{i["_slug"]}/">{e(t)}</a>'
            return e(t)
        cut = max(10, n + 4)
        head = ', '.join(word(t) for t in items[:cut])
        rest = ', '.join(word(t) for t in items[cut:])
        more = f'<span class="rest">, {rest}</span>.<button class="more-btn" type="button" hidden>Show all {len(items)} ingredients</button>' if rest else '.'
        after = 'right after water' if n == 2 and B.norm(items[0]).startswith(('aqua', 'water', 'eau')) else f'{B.ordinal(n)} of {len(items)}'
        name = f"{p.get('brand', '').strip()} {p.get('name', '').strip()}".strip()
        hero = f'''<figure class="label" id="example" aria-labelledby="lbl">
      <div class="sticker" aria-hidden="true"><em>#{n}</em><small>of {len(items)}</small></div>
      <div class="label-top"><span>Ingredients · as printed</span><b id="lbl"><a href="{r}products/{p.get('_slug', '')}/">{e(name)}</a></b></div>
      <p class="inci">{head}{more}</p>
      <figcaption class="label-foot"><span><b>{e(title)} is {B.ordinal(n)}</b>, {after}.</span><span>#{n} = its spot on this label. Dotted words have their own page.</span></figcaption>
    </figure>'''
    else:
        spell = ''.join(f'<li>{e(a)}</li>' for a in names)
        hero = f'''<figure class="label label-empty" aria-labelledby="lbl">
      <div class="label-top"><span>How it's written</span><b id="lbl">On a label, look for</b></div>
      <ul class="spell">{spell}</ul>
      <figcaption class="label-foot"><span>We haven't read a label with it yet.</span><span>We've read {len(labels)} so far.</span></figcaption>
    </figure>'''

    # Why, research and good-to-know as one section with small subheadings
    parts = []
    if deep:
        parts.append(f'<p>{e(deep)}</p>')
    if evid:
        tag, _, rest = evid.partition('. ')
        if rest and len(tag) <= 70 and B.re.match(r'(Established|Cosmetic|Emerging|Promising|Regulated|Universal|Standard)', tag):
            ev = f'<p><span class="evi">{e(tag)}</span> {e(rest)}</p>'
        else:
            ev = f'<p>{e(evid)}</p>'
        src = B.col(g, 'sources', 'research_sources')
        src = f'<p class="iv2-src"><b>Sources</b> {e(src)}</p>' if src else \
            '<p class="iv2-src iv2-todo"><b>Sources</b> One linked study or review per claim goes here (new sheet column: <code>sources</code>).</p>'
        parts.append(f'<h3 id="research">What the research says</h3>{ev}{src}')
    if note:
        parts.append(f'<h3 id="good">Good to know</h3><p class="note">{e(note)}</p>')
    if howto:
        parts.append(f'<h3>How to use it</h3><p>{e(howto)}</p>')
    merged = f'''<section class="iv2-sec" id="why">
    <h2>Why your curls care</h2>
    <div class="prose iv2-prose">{''.join(parts)}</div>
  </section>''' if parts else ''

    if hits:
        x = lambda n: round(2.5 + (min(n, 40) - 1) / 39 * 95, 1)
        per = {}
        for p, items, n in hits:
            per[min(n, 40)] = per.get(min(n, 40), 0) + 1
        tall = max(per.values())
        near = sum(1 for h in hits if h[2] <= 5); mid = sum(1 for h in hits if 5 < h[2] <= 15); low = len(hits) - near - mid
        ticks = ''.join(f'<span class="tick" style="left:{x(n)}%">{B.ordinal(n)}</span>' for n in (1, 10, 20, 30, 40))
        bands = (f'<span class="iv2-band" style="left:0;width:{x(5.5)}%"><b>Near the top</b><span> 1–5</span></span>'
                 f'<span class="iv2-band" style="left:{x(5.5)}%;width:{x(15.5) - x(5.5)}%"><b>Middle</b><span> 6–15</span></span>'
                 f'<span class="iv2-band" style="left:{x(15.5)}%;right:0"><b>Lower down</b><span> 16+</span></span>')
        if tall <= 4:   # few products: one dot each, stacked
            stack, marks = {}, ''
            for k, (p, items, n) in enumerate(hits):
                h = stack.get(n, 0); stack[n] = h + 1
                marks += (f'<a class="dot" tabindex="-1" aria-hidden="true" data-step="{e(p.get("step", ""))}" href="#{"example" if k == 0 else f"p{k}"}" '
                          f'style="left:{x(n)}%;bottom:{58 + h * 24}px;animation-delay:{1.3 + min(k, 40) * .04:.2f}s"></a>')
            mode = 'dots'
        else:           # many products: a bar per position, with its count
            marks = ''.join(f'<span class="iv2-bar" aria-hidden="true" data-pos="{n}" style="left:{x(n)}%;height:{round(c / tall * 100)}px"><i>{c}</i></span>'
                            for n, c in sorted(per.items()))
            mode = 'bars'
        data = e(json.dumps([[min(n, 40), p.get('step', '')] for p, items, n in hits]))
        def step_f(s, lbl):
            c = sum(1 for h in hits if h[0].get('step') == s)
            if not c:
                return ''
            return f'<button type="button" class="step-f" data-step="{s}" aria-pressed="false" aria-controls="labels-list">{lbl} <b>{c}</b></button>'
        steps = ''.join(step_f(s, lbl) for s, lbl in B.STEPS)
        rows = ''
        for k, (p, items, n) in enumerate(hits[1:], 1):
            extra = ' class="iv2-more"' if k > CAP else ''
            rows += (f'<li id="p{k}"{extra} data-step="{e(p.get("step", ""))}"><span class="pos">{n}<small>of {len(items)}</small></span>'
                     f'<div><span class="step">{e(B.STEP.get(p.get("step", ""), p.get("step", "").capitalize()))}</span>'
                     f'<a href="{r}products/{p.get("_slug", "")}/"><b>{e(p.get("brand", "").strip())}</b> {e(p.get("name", "").strip())}</a></div></li>')
        rest_n = len(hits) - 1 - CAP
        show = f'<button type="button" class="iv2-all" aria-controls="labels-list">Show all {len(hits) - 1} products</button>' if rest_n > 0 else ''
        chart = (f'<div class="strip iv2-strip iv2-{mode}" data-hits="{data}" role="img" aria-label="Where {e(title)} sits on {len(hits)} labels: {near} near the top, {mid} in the middle, {low} lower down">'
                 f'{bands}{marks}<div class="axis"></div>{ticks}</div>') if len(hits) >= 5 else ''
        S_ACROSS = f'''<section class="iv2-sec iv2-across" id="across">
    <h2>Where it sits on {len(hits)} label{'s' if len(hits) != 1 else ''}</h2>
    <p class="iv2-why">Labels list ingredients from most to least, down to about 1%. Below that, the order is free.{' Each bar counts the products with it at that spot.' if chart and mode == 'bars' else (' Each dot is one product.' if chart else '')}</p>
    {chart}
    {f'<div class="iv2-steps" role="group" aria-label="Show one step"><span>Show only</span>{steps}</div>' if steps else ''}
    {f'<ol class="labels iv2-list" id="labels-list">{rows}</ol>{show}' if rows else ''}
    <p class="fine">Labels we’ve read by hand from brand sites and packaging, not a list of recommendations. The first one is on the label card above.</p>
  </section>'''
    else:
        S_ACROSS = ''

    S = [x for x in (S_ACROSS, merged) if x]
    if hair:
        S.append(f'''<section class="iv2-sec" id="hair">
    <h2>Ideal for</h2>
    <div class="hair"><p>{e(hair)}</p><small>General patterns from our research, not rules. Your own results count most.</small></div>
  </section>''')

    mytags = set(g['_tags'])
    related = [i for i in B.ing if i is not g and (set(i['_tags']) & mytags if mytags else i.get('category') == g.get('category'))]
    if related:
        rel = ''.join(f'<a href="{r}{i["_slug"]}/">{e(i["_short"])}</a>' for i in related)
        what = g['_tags'][0] if g['_tags'] else (g.get('category') or 'like it')
        S.append(f'''<section class="iv2-sec">
    <h2>Other ingredients: {e(what)}</h2>
    <nav class="related" aria-label="Related ingredients">{rel}</nav>
  </section>''')

    body = f'''  <div class="iv2">
  <a class="crumb" href="{r}ingredients/">← All ingredients</a>
  <section class="first">
    <div class="name">
      <span class="eyebrow"><span class="little-dot"></span>{e(g.get('category', ''))}</span>
      <h1>{_h1(h1)}</h1>
      {onlabel}
      <p class="lead">{e(summary)}</p>
      {fact}
      {watchlist.ingredient_note(g)}
      <div class="iv2-tags">{cta}{tags}</div>
    </div>
    {hero}
  </section>
  {''.join(S)}
  <p class="source"><span>Source: {e(g['_source'])} · Ref {e(g['id'])}</span><a href="{r}about/">How we write these</a></p>
  </div>
<script>
(function () {{
  if (matchMedia('(max-width:760px)').matches) document.querySelectorAll('.inci').forEach(function (p) {{
    var b = p.querySelector('.more-btn'); if (!b) return; p.classList.add('clamped'); b.hidden = false;
    b.onclick = function () {{ p.classList.remove('clamped'); b.remove(); }};
  }});
  var list = document.getElementById('labels-list'), all = document.querySelector('.iv2-all');
  if (all) all.onclick = function () {{ list.classList.add('open'); all.remove(); }};
  var btns = document.querySelectorAll('.step-f');
  btns.forEach(function (btn) {{
    btn.addEventListener('click', function () {{
      var on = btn.getAttribute('aria-pressed') !== 'true', step = btn.dataset.step;
      btns.forEach(function (b) {{ b.setAttribute('aria-pressed', b === btn && on ? 'true' : 'false'); }});
      if (list) list.classList.toggle('filtered', on);
      document.querySelectorAll('#labels-list > li, .strip .dot').forEach(function (el) {{
        el.hidden = on && el.dataset.step !== step;
      }});
      var strip = document.querySelector('.iv2-bars');
      if (strip) {{
        var data = JSON.parse(strip.dataset.hits), per = {{}}, tall = 0;
        data.forEach(function (h) {{ if (!on || h[1] === step) {{ per[h[0]] = (per[h[0]] || 0) + 1; tall = Math.max(tall, per[h[0]]); }} }});
        strip.querySelectorAll('.iv2-bar').forEach(function (b) {{
          var c = per[b.dataset.pos] || 0;
          b.style.height = (c ? Math.round(c / tall * 100) : 0) + 'px';
          b.querySelector('i').textContent = c || '';
          b.classList.toggle('zero', !c);
        }});
      }}
      var stack = {{}};
      document.querySelectorAll('.strip .dot').forEach(function (d) {{
        if (d.hidden) return;
        var h = stack[d.style.left] || 0; stack[d.style.left] = h + 1;
        d.style.bottom = (58 + h * 24) + 'px';
      }});
    }});
  }});
}})();
</script>'''
    inci = g['inci_name']
    desc = (f"{title} in hair products: what it does, where it sits on {len(hits)} real labels, and notes for different hair."
            if B.norm(inci) == B.norm(title) else
            f"{title} ({inci}) in hair products: what it does, where it sits on {len(hits)} real labels, and notes for different hair.")
    ld = {'@context': 'https://schema.org', '@type': 'DefinedTerm', 'name': h1, 'alternateName': names,
          'description': summary, 'url': f"{B.SITE}/{g['_slug']}/",
          'inDefinedTermSet': {'@type': 'DefinedTermSet', 'name': 'The Good Coil Ingredient Library', 'url': f'{B.SITE}/ingredients/'}}
    html = B.shell(r, f"{title} in hair products: what it is and what it does · The Good Coil Library", desc, body,
                   f"{g['_slug']}/", current='ingredients')
    html = html.replace('<head>', '<head>\n<meta name="robots" content="noindex">', 1)
    html = html.replace('</head>', f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n</head>', 1)
    B.write(f"{g['_slug']}/v2/index.html", html)
    return f"{g['_slug']}/v2/"


def build():
    out = []
    for w, g in find(B.ing):
        out.append(page(g, DRAFT_LEAD.get(w, '')))
    print('Ingredient v2 previews:', ', '.join(out) or 'none matched')
    return out

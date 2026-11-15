"""TEST homepage at /home-test/ (noindex, unlinked).

A quieter take on the same job: ask the question first, answer it in four lines,
and keep the full ingredient list folded away until someone wants it.
"""
import json
import build as B

e = B.e


def build(out='', root='', test=False):
    chips = ''.join(
        f'<button type="button" class="t-chip" data-g="{k}" aria-pressed="false">{e(n)}</button>'
        for k, n, _ in B.CHECK_GROUPS)
    rows = ''.join(
        f'''<li class="t-row" data-g="{k}">
        <span class="t-name">{e(n)}</span>
        <span class="t-ans">?</span>
        <span class="t-detail">{e(d)}</span>
      </li>''' for k, n, d in B.CHECK_GROUPS)

    eyebrow = 'The Good Coil Library · test layout' if test else 'The Good Coil Library'
    import glob
    n_ing = len(B.ing)
    n_prod = len([x for x in B.products if (x.get('kind') or 'product') == 'product'])
    n_lab = len(B.labels)
    n_plan = len(glob.glob(B.os.path.join(B.ROOT, 'content', 'guide-*.json')))
    body = f'''<section class="t-wrap">
  <p class="t-eyebrow"><span class="little-dot"></span>{eyebrow}</p>
  <h1 class="t-h1">Does your product have…</h1>

  <div class="t-chips" role="group" aria-label="Jump to one answer">{chips}</div>

  <div class="t-find">
    <label for="tf">Your product</label>
    <input id="tf" type="text" autocomplete="off" role="combobox" aria-expanded="false"
           aria-controls="tf-list" placeholder="Type a name, e.g. Quench">
    <ul class="t-list" id="tf-list" role="listbox" hidden></ul>
  </div>

  <ol class="t-answers" id="t-answers" aria-live="polite">{rows}</ol>

  <p class="t-note" id="t-note">Pick a product and we will read its label for you.</p>

  <details class="t-more" id="t-more" hidden>
    <summary>See the full ingredient list</summary>
    <p class="inci" id="t-inci"></p>
    <p class="t-foot" id="t-foot"></p>
  </details>

  <nav class="t-doors" aria-label="The rest of the library">
    <a href="{root}ingredients/"><b>{n_ing}</b><span>Ingredients</span><em>Each one by what it is and what it does.</em></a>
    <a href="{root}products/"><b>{n_prod}</b><span>Products</span><em>{n_lab} labels read, ingredient by ingredient.</em></a>
    <a href="{root}plans/"><b>{n_plan}</b><span>Hair plans</span><em>What to do each week, and what to look for.</em></a>
  </nav>

  <details class="t-paste">
    <summary>Our library does not have your product yet?</summary>
    <form id="t-form">
      <label for="tt">Paste the ingredient list from the bottle</label>
      <textarea id="tt" rows="3" placeholder="Water, Glycerin, Cetearyl Alcohol, …"></textarea>
      <button class="go" type="submit">Read this label</button>
    </form>
  </details>
</section>
<script src="{root}assets/home-test.js" defer></script>'''

    title = ('Does your product have… · test' if test
             else 'The Good Coil Library: what is in the bottle?')
    desc = ('A quieter layout for the product checker.' if test else
            'Name a hair-care product and see whether it has protein, ceramides, silicones, '
            'sulfates or peptides in it, with every ingredient explained by what it does.')
    html = B.shell(root, title, desc, body, out, '' if test else 'home')
    if test:
        html = html.replace('</head>', '<meta name="robots" content="noindex">\n</head>')
    B.write(out + 'index.html', html)

    keys = {k: [v['_slug'], v['_title'], [g for g, _, _ in B.CHECK_GROUPS if g in v['_tags']]]
            for k, v in B.keys.items()}
    js = ('window.TLIB=' + json.dumps(
        {'root': root, 'keys': keys, 'checks': [[k, n, d] for k, n, d in B.CHECK_GROUPS]},
        ensure_ascii=False, separators=(',', ':')) + ';\n'
        + open(B.os.path.join(B.ROOT, 'src', 'home-test.js'), encoding='utf-8').read())
    B.write('assets/home-test.js', js)

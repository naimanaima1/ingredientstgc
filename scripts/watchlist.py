"""Label check extras: parabens and phthalates. Matched by name, so no sheet work is needed.

Plain facts only: what the EU has decided, with a source. We do not call any single ingredient
"harmful" or label it an endocrine disruptor. We say what it is and what the EU rule is.
"""
import re
import build as B

e = B.e

PARABEN = 'paraben'
PHTH = 'phthalate'
STRONG = 'strong-cleanser'

SRC_358 = 'https://www.legislation.gov.uk/eur/2014/358/data.html'
SRC_1004 = 'https://www.legislation.gov.uk/eur/2014/1004'
EUR = 'https://eur-lex.europa.eu/eli/reg/2009/1223/oj'

PARABEN_RX = re.compile(r'paraben')
STRONG_RX = re.compile(r'olefin sulfonate')
PHTH_RX = re.compile(r'^(?!.*(tere|iso)phthalate).*phthalate$')

PARABEN_STATUS = {
    'banned': ('Isopropylparaben, isobutylparaben, phenylparaben, benzylparaben, pentylparaben',
               'Banned in cosmetics in the EU since 2014.', SRC_358),
    'capped': ('Propylparaben, butylparaben', 'Capped at 0.14% in the EU.', SRC_1004),
    'ok': ('Methylparaben, ethylparaben', "The EU's safety committee confirmed they are safe at the maximum allowed amounts.", SRC_1004),
}
PHTH_BANNED = 'Dibutyl phthalate (DBP), diethylhexyl phthalate (DEHP), benzyl butyl phthalate (BBP) and diisobutyl phthalate (DIBP)'


def groups(*names):
    out = []
    for t in names:
        n = B.norm(t or '')
        if not n:
            continue
        if PARABEN_RX.search(n) and PARABEN not in out:
            out.append(PARABEN)
        if PHTH_RX.search(n) and PHTH not in out:
            out.append(PHTH)
        if STRONG_RX.search(n) and STRONG not in out:
            out.append(STRONG)
    return out


def js_rules():
    return [[PARABEN, 'paraben'], [PHTH, PHTH_RX.pattern], [STRONG, 'olefin sulfonate']]


def paraben_kind(name):
    n = B.norm(name or '')
    if re.search(r'(isopropyl|isobutyl|phenyl|benzyl|pentyl)paraben', n):
        return 'banned'
    if re.search(r'(propyl|butyl)paraben', n):
        return 'capped'
    if re.search(r'(methyl|ethyl)paraben', n):
        return 'ok'
    return None


def phth_banned(name):
    n = B.norm(name or '')
    return bool(re.search(r'(dibutyl|diethylhexyl|bis 2 ethylhexyl|benzyl butyl|diisobutyl|di 2 ethylhexyl) phthalate|^(dbp|dehp|bbp|dibp)$', n))


def ingredient_note(g):
    names = [g['inci_name']] + g['_aliases']
    gs = groups(*names)
    if not gs:
        return ''
    bits = []
    if PARABEN in gs:
        kind = paraben_kind(g['inci_name'])
        if kind:
            _, what, src = PARABEN_STATUS[kind]
            bits.append(f'<p><b>A paraben.</b> {e(what)} <a href="{src}" rel="noopener">Source</a></p>')
        else:
            bits.append('<p><b>A paraben.</b></p>')
    if PHTH in gs:
        if any(phth_banned(n) for n in names):
            what = 'Banned in cosmetics in the EU.'
        else:
            what = f'Some phthalates are banned in cosmetics in the EU ({PHTH_BANNED}). Rules differ for each one.'
        bits.append(f'<p><b>A phthalate.</b> {e(what)} <a href="{EUR}" rel="noopener">Source</a></p>')
    if STRONG in gs:
        bits.append('<p><b>A stronger cleanser.</b> Not a sulfate, but a high-detergency cleanser. "Sulfate-free" does not by itself mean gentle. A shampoo built on it can feel more stripping on dry or tightly coiled hair.</p>')
    return f'<aside class="wl-note" aria-label="Label check">{"".join(bits)}<p class="fine"><a href="../label-check/">About these label checks</a></p></aside>'


def page():
    par = ''.join(f'<li><b>{e(who)}</b><span>{e(what)} <a href="{src}" rel="noopener">Source</a></span></li>' for who, what, src in PARABEN_STATUS.values())
    body = f'''  <a class="crumb" href="../">← Library</a>
  <section class="first"><div class="name">
    <span class="eyebrow"><span class="little-dot"></span>Label check</span>
    <h1>Parabens and phthalates</h1>
    <p class="lead">Two kinds of ingredient people often want to spot on a label. Here is what each one is, and what the EU has decided about it, in plain words.</p>
  </div></section>
  <section class="section" id="parabens"><div class="intro"><span class="eyebrow">Parabens</span><h2>Not all parabens are treated the same</h2></div>
    <div class="prose"><p>Parabens are preservatives. Any ingredient whose name ends in "-paraben" is one. The EU has made different rules for different parabens:</p>
    <ul class="gp-spot">{par}</ul>
    <p class="fine">These are EU rules. Other countries have their own.</p></div></section>
  <section class="section" id="phthalates"><div class="intro"><span class="eyebrow">Phthalates</span><h2>What a phthalate is</h2></div>
    <div class="prose"><p>Phthalates are a family of chemicals used to make fragrance last and to soften plastics. On a label, the name ends in "phthalate", like diethyl phthalate or dimethyl phthalate. Sometimes they sit inside "fragrance" and are not listed by name.</p>
    <p>In the EU, {e(PHTH_BANNED)} are banned in cosmetics. Other phthalates are treated one by one, so a phthalate on a label is not automatically a banned one. <a href="{EUR}" rel="noopener">EU Cosmetics Regulation (EC) 1223/2009</a></p>
    <p class="fine">These are EU rules. Other countries have their own.</p></div></section>
  <section class="section"><div class="intro"><span class="eyebrow">Try it</span><h2>Check a label</h2></div>
    <div class="prose"><p>Paste any ingredient list into the <a href="../#find">Label Decoder</a> and we will tell you if it has a paraben or a phthalate. This is information, not advice. If you have a health concern, talk to your doctor.</p></div></section>
'''
    B.write('label-check/index.html', B.shell('../', 'Parabens and phthalates · The Good Coil Library',
            'What parabens and phthalates are on an ingredient list, and what the EU has decided about each.', body, 'label-check/', 'ingredients'))


def build():
    page()

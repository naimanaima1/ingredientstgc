"""Label check extras: parabens, and ingredients on the European Commission's priority list
for possible endocrine-disrupting properties.

Plain facts only. "On the EU review list" means the Commission has put an ingredient on a list to
assess. It does not mean the ingredient is proven harmful. Sources are named on /label-check/.
"""
import re
import build as B

e = B.e

PARABEN = 'paraben'
EU = 'eu-review'

EU_SRC = 'https://single-market-economy.ec.europa.eu/sectors/cosmetics/cosmetic-products-specific-topics/endocrine-disruptors_en'
SRC_358 = 'https://www.legislation.gov.uk/eur/2014/358/data.html'
SRC_1004 = 'https://www.legislation.gov.uk/eur/2014/1004'

# (display name, regex on the normalised label word). The 28 substances the Commission lists.
EU_LIST = [
    ('Benzophenone-3 (oxybenzone)', r'^(benzophenone 3|oxybenzone)$'),
    ('Kojic acid', r'^kojic acid$'),
    ('4-Methylbenzylidene camphor', r'^(4 )?methylbenzylidene camphor$'),
    ('Propylparaben', r'propylparaben$'),
    ('Triclosan', r'^triclosan$'),
    ('Resorcinol', r'^resorcinol$'),
    ('Octocrylene', r'^octocrylene$'),
    ('Triclocarban', r'^triclocarban$'),
    ('BHT (butylated hydroxytoluene)', r'^(bht|butylated hydroxytoluene)$'),
    ('Benzophenone', r'^benzophenone$'),
    ('Homosalate', r'^homosalate$'),
    ('Benzyl salicylate', r'^benzyl salicylate$'),
    ('Genistein', r'^genistein$'),
    ('Daidzein', r'^daidzein$'),
    ('Butylparaben', r'butylparaben$'),
    ('BHA (butylated hydroxyanisole)', r'^(bha|butylated hydroxyanisole|tert butyl 4 hydroxyanisole)$'),
    ('Ethylhexyl methoxycinnamate (octinoxate)', r'^(ethylhexyl methoxycinnamate|octinoxate|octyl methoxycinnamate)$'),
    ('Benzophenone-1', r'^benzophenone 1$'),
    ('Benzophenone-2', r'^benzophenone 2$'),
    ('Benzophenone-4', r'^benzophenone 4$'),
    ('Benzophenone-5', r'^benzophenone 5$'),
    ('Methylparaben', r'methylparaben$'),
    ('Cyclopentasiloxane (D5)', r'^(cyclopentasiloxane|decamethylcyclopentasiloxane)$'),
    ('Cyclomethicone', r'^cyclomethicone$'),
    ('Salicylic acid', r'^salicylic acid$'),
    ('Butylphenyl methylpropional (BMHCA)', r'^(butylphenyl methylpropional|bmhca)$'),
    ('Triphenyl phosphate', r'^triphenyl phosphate$'),
    ('Deltamethrin', r'^deltamethrin$'),
]
EU_RX = [(n, re.compile(p)) for n, p in EU_LIST]
PARABEN_RX = re.compile(r'paraben')

# What the EU has decided about each paraben (Regulations 358/2014 and 1004/2014).
PARABEN_STATUS = {
    'banned': ('Isopropylparaben, isobutylparaben, phenylparaben, benzylparaben, pentylparaben',
               'Banned in cosmetics in the EU since 2014.', SRC_358),
    'capped': ('Propylparaben, butylparaben', 'Capped at 0.14% in the EU.', SRC_1004),
    'ok': ('Methylparaben, ethylparaben', "The EU's safety committee confirmed they are safe at the maximum allowed amounts.", SRC_1004),
}


def groups(*names):
    """Which of the two groups any of these names belong to."""
    out = []
    for t in names:
        n = B.norm(t or '')
        if not n:
            continue
        if PARABEN_RX.search(n) and PARABEN not in out:
            out.append(PARABEN)
        if any(rx.search(n) for _, rx in EU_RX) and EU not in out:
            out.append(EU)
    return out


def js_rules():
    """The same rules for the browser, as [group, regex source] pairs."""
    rules = [[PARABEN, 'paraben']]
    rules += [[EU, rx.pattern] for _, rx in EU_RX]
    return rules


def eu_name(*names):
    for t in names:
        n = B.norm(t or '')
        for disp, rx in EU_RX:
            if rx.search(n):
                return disp
    return None


def paraben_kind(name):
    n = B.norm(name or '')
    if re.search(r'(isopropyl|isobutyl|phenyl|benzyl|pentyl)paraben', n):
        return 'banned'
    if re.search(r'(propyl|butyl)paraben', n):
        return 'capped'
    if re.search(r'(methyl|ethyl)paraben', n):
        return 'ok'
    return None


def ingredient_note(g):
    """A short, sourced note for an ingredient page. '' when neither group applies."""
    names = [g['inci_name']] + g['_aliases']
    gs = groups(*names)
    if not gs:
        return ''
    bits = []
    if PARABEN in gs:
        kind = paraben_kind(g['inci_name'])
        if kind:
            who, what, src = PARABEN_STATUS[kind]
            bits.append(f'<p><b>A paraben.</b> {e(what)} <a href="{src}" rel="noopener">Source</a></p>')
        else:
            bits.append('<p><b>A paraben.</b></p>')
    if EU in gs:
        bits.append(f'<p><b>On the EU review list.</b> The European Commission has put {e(eu_name(*names) or g["_title"])} on its priority list to check for possible endocrine-disrupting properties. Being on the list means it is under review, not that it is proven harmful. <a href="{EU_SRC}" rel="noopener">Source</a></p>')
    return f'<aside class="wl-note" aria-label="Label check">{"".join(bits)}<p class="fine"><a href="../label-check/">About these label checks</a></p></aside>'


def page():
    ids = {}
    rows = ''
    for disp, rx in EU_RX:
        hit = next((i for i in B.ing if rx.search(B.norm(i['inci_name'])) or any(rx.search(B.norm(a)) for a in i['_aliases'])), None)
        name = f'<a href="../{hit["_slug"]}/">{e(disp)}</a>' if hit else e(disp)
        rows += f'<li>{name}</li>'
    par = ''.join(f'<li><b>{e(who)}</b><span>{e(what)} <a href="{src}" rel="noopener">Source</a></span></li>' for who, what, src in PARABEN_STATUS.values())
    body = f'''  <a class="crumb" href="../">← Library</a>
  <section class="first"><div class="name">
    <span class="eyebrow"><span class="little-dot"></span>Label check</span>
    <h1>Parabens and the EU review list</h1>
    <p class="lead">Two things people often want to spot on a label: parabens, and ingredients the European Commission is reviewing for possible endocrine-disrupting properties. Here is what each one means, in plain words.</p>
  </div></section>
  <section class="section" id="parabens"><div class="intro"><span class="eyebrow">Parabens</span><h2>Not all parabens are treated the same</h2></div>
    <div class="prose"><p>Parabens are preservatives. Any ingredient whose name ends in "-paraben" is one. The EU has made different rules for different parabens:</p>
    <ul class="gp-spot">{par}</ul>
    <p class="fine">These are EU rules. Other countries have their own.</p></div></section>
  <section class="section" id="eu"><div class="intro"><span class="eyebrow">Under review</span><h2>The EU priority list</h2></div>
    <div class="prose"><p>The European Commission has made a priority list of {len(EU_LIST)} cosmetic ingredients to assess for possible endocrine-disrupting properties. <b>Being on the list means an ingredient is under review. It does not mean it has been shown to be harmful.</b> Here is the list. Names that link have a page in our library.</p>
    <ul class="wl-list">{rows}</ul>
    <p class="fine"><a href="{EU_SRC}" rel="noopener">European Commission: endocrine disruptors in cosmetics</a>. We check this list against the Commission's page and update it when it changes.</p></div></section>
  <section class="section"><div class="intro"><span class="eyebrow">Try it</span><h2>Check a label</h2></div>
    <div class="prose"><p>Paste any ingredient list into the <a href="../#find">Label Decoder</a> and we will tell you if it has a paraben or an ingredient on the EU list. This is information, not advice. If you have a health concern, talk to your doctor.</p></div></section>
'''
    B.write('label-check/index.html', B.shell('../', 'Parabens and the EU review list · The Good Coil Library',
            'What parabens are, how the EU treats each one, and the ingredients on the European Commission priority list for possible endocrine-disrupting properties.', body, 'label-check/', 'ingredients'))


def build():
    page()

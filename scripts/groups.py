"""Ingredient family pages at /groups/<family>/, built from the Group Guides sheet.

One page per ingredient_family. Each sub_classification becomes a numbered
section: what it is, which ingredients belong to it, and the sheet's own
wash-out guidance. Ingredient names link to their page when the ingredient
sheet has a row for them, and read as plain text when it does not yet.
"""
import re
import build as B

e = B.e

# Families published so far. Add a name here once its rows have been reviewed.
LIVE = ['Silicones']

INTRO = {
    'Silicones': (
        'Not all silicones behave the same way on coily hair.',
        'They get talked about as one thing, but a silicone that rinses out in water '
        'and one that seals the strand until you clarify are doing different jobs. '
        'There are four kinds on labels, and the name on the bottle tells you which '
        'one you are holding.'),
    # Written by the owner, 15 Nov. One sentence each, used as the page headline.
    'Alcohols': (
        'Not all alcohols dry out coily hair: fatty alcohols soften and detangle, aromatic alcohols preserve the bottle, and only short-chain alcohols evaporate moisture.',
        ''),
    'Proteins': (
        'Protein strength comes down to size: amino acids hydrate inside the strand, silk, rice and quinoa add lightweight bounce, and keratin and wheat patch heavy damage.',
        ''),
    'Scalp Actives': (
        'Healthy edges start at the skin: niacinamide calms the scalp barrier, caffeine and EGCG offer promising follicle support, and peptides target root anchoring (without replacing medical hair-loss care).',
        ''),
    'Surfactants & Cleansers': (
        'Cleansing is a dial, not an all-or-nothing choice: gentle non-sulfate cleansers protect weekly moisture, while sulfates and chelators reset heavy buildup.',
        ''),
}

# Callouts the owner asked for on specific family pages. Not rendered yet: they go in
# when the page is built. Keyed by family.
NOTES = {
    'Scalp Actives': [
        'Topical actives support scalp health and the look of density. They do not treat medical hair loss.',
        'Peptides like Procapil and Capixyl are made for scalp serums. Copper Tripeptide-1 (GHK-Cu) also appears in some hair-shaft bond and repair leave-ins, where it is there for the fibre, not the scalp.',
    ],
    'Surfactants & Cleansers': [
        'Chelators (citric acid, tartaric acid, EDTA) bind minerals from hard water. They are not foaming detergents like sulfates.',
    ],
}

HOW_TO_SPOT = {
    'Silicones': [
        ('Ends in -cone or -conol', 'Dimethicone, Dimethiconol, Amodimethicone.'),
        ('Starts with PEG- and ends in -cone', 'PEG-6 Methyl Ether Dimethicone. The PEG part is what makes it rinse out in water.'),
        ('Starts with Cyclo-', 'Cyclopentasiloxane. These evaporate.'),
        ('Contains -siloxane or -silane', 'Another way the same chemistry gets written.'),
        ('Contains Amino- or Amo-', 'Amodimethicone, Aminopropyl Dimethicone. The amino part is what makes them seek out damage.'),
    ],
}


def family_slug(name):
    return B.prop_slug(name)


def parse_members(cell):
    """Pull (id, name) out of 'ING-077(Amodimethicone), ING-080 (Aminopropyl Dimethicone)'.

    Rows that name ingredients with no id yet come back with id None.
    """
    out = []
    for m in re.finditer(r'(ING-\d+)\s*\(([^)]*)\)', cell or ''):
        out.append((m.group(1), m.group(2).strip()))
    if out:
        return out
    # no ids at all: the sheet is naming ingredients that have no row yet
    body = re.sub(r'\((?:[^)]*not yet[^)]*)\)', '', cell or '', flags=re.I)
    for part in re.split(r',| and ', body):
        part = part.strip(' . ')
        if part:
            out.append((None, part))
    return out


def by_id():
    return {i['id']: i for i in B.ing if i.get('id')}


def member_html(members, ids):
    bits = []
    for gid, name in members:
        row = ids.get(gid) if gid else None
        if row is None and name:
            row = B.lookup(name)
        if row:
            bits.append(f'<a class="gp-ing" href="../../{row["_slug"]}/">{e(row["_title"])}</a>')
        else:
            bits.append(f'<span class="gp-ing is-soon">{e(name)}</span>')
    return ''.join(bits)


def words(s):
    return set(re.findall(r'[a-z]{4,}', (s or '').lower()))


def overlap(a, b):
    wa, wb = words(a), words(b)
    return len(wa & wb) / len(wa) if wa else 0


def paragraphs(cell):
    """The sheet writes a long line, then a short restatement on the next line."""
    parts = [p.strip() for p in (cell or '').replace('\r', '').split('\n') if p.strip()]
    return parts


def page(family, rows, ids):
    head, lead = INTRO.get(family, (family, ''))
    secs = ''
    for n, r in enumerate(rows, 1):
        ps = paragraphs(r.get('how_it_behaves_on_coily_hair'))
        long_p = ps[0] if ps else ''
        short_p = ps[1] if len(ps) > 1 else ''
        if short_p and overlap(short_p, long_p) > .6:
            short_p, long_p = long_p, ''
        members = parse_members(r.get('linked_inci_ids'))
        guide = (r.get('porosity_and_wash_out_guidance') or '').strip()
        secs += f'''  <section class="gp-sec" id="{family_slug(r['sub_classification'])}">
    <div class="gp-num"><span>{n:02d}</span></div>
    <div class="gp-body">
      <h2>{e(r['sub_classification'])}</h2>
      {f'<p class="gp-short">{e(short_p)}</p>' if short_p else ''}
      <p class="gp-long">{e(long_p)}</p>
      <div class="gp-ings">{member_html(members, ids)}</div>
      {f'<p class="gp-guide"><b>On the hair</b>{e(guide)}</p>' if guide else ''}
    </div>
  </section>
'''
    spot = HOW_TO_SPOT.get(family)
    spot_html = ''
    if spot:
        rowsh = ''.join(f'<li><b>{e(a)}</b><span>{e(b)}</span></li>' for a, b in spot)
        spot_html = f'''<section class="section" id="spot">
    <div class="intro"><span class="eyebrow">On a label</span><h2>How to spot one</h2>
      <p>The name does the work. You do not need to memorise the list.</p></div>
    <ul class="gp-spot">{rowsh}</ul>
  </section>'''

    members = [m for r in rows for m in parse_members(r.get('linked_inci_ids'))]
    soon = sum(1 for gid, nm in members if not (ids.get(gid) if gid else None) and not B.lookup(nm))
    total = len(members)
    note = ''
    if soon:
        how = f'None of the {total}' if soon == total else f'{soon} of the {total}'
        note = (f'<p class="gp-soon">{how} ingredients named below have their own page yet. '
                'Their rows are on the way, and the names here will become links as soon as they land.</p>')

    body = f'''  <a class="crumb" href="../../properties/">← By property</a>
  <section class="gp-first">
    <span class="eyebrow"><span class="little-dot"></span>Ingredient family</span>
    <h1>{e(family)}</h1>
    <p class="gp-lead">{e(head)}</p>
    <p class="lead">{e(lead)}</p>
    {note}
  </section>
{secs}  {spot_html}
'''
    return B.shell('../../', f'{family} · The Good Coil Library',
                   f'The {len(rows)} kinds of {family.lower()} on hair-care labels, and what each one does.',
                   body, f'groups/{family_slug(family)}/index.html')


built = []


def build():
    global built
    rows = B.read_csv('groups.csv')
    if not rows:
        print(f'::warning::data/groups.csv is missing, so {len(LIVE)} ingredient family '
              f'page(s) were not built: {", ".join(LIVE)}. Check .gitignore is not '
              'excluding it and that the sheet link is set.')
        print('### Ingredient family pages\n**Not built**: data/groups.csv was missing.\n')
        return []
    ids = by_id()
    made = []
    for family in LIVE:
        fam = [r for r in rows if (r.get('ingredient_family') or '').strip() == family]
        if not fam:
            continue
        B.write(f'groups/{family_slug(family)}/index.html', page(family, fam, ids))
        made.append((family, family_slug(family), len(fam)))
    built = made
    if made:
        print('### Ingredient family pages\n' + '\n'.join(
            f'- {f}: {n} kinds at /groups/{s}/' for f, s, n in made) + '\n')
    return made

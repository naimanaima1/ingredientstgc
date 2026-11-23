"""Ingredient family pages at /groups/<family>/, built from the Group Guides sheet.

One page per ingredient_family. Each sub_classification becomes a numbered
section: what it is, which ingredients belong to it, and the sheet's own
wash-out guidance. Ingredient names link to their page when the ingredient
sheet has a row for them, and read as plain text when it does not yet.
"""
import re
import build as B

e = B.e

# Families published. Add a name here once its rows have been reviewed and it has a
# how-to-spot list.
LIVE = ['Silicones', 'Alcohols', 'Proteins', 'Scalp Actives', 'Peptides', 'Surfactants & Cleansers',
        'Conditioning Agents', 'Humectants', 'Ceramides', 'Lipids', 'Oils & Butters', 'Film Formers']

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
        'Healthy edges start at the skin: niacinamide calms the scalp barrier, while caffeine and EGCG offer promising follicle support (without replacing medical hair-loss care).',
        ''),
    'Peptides': (
        'Peptides are precision messengers, not heavy proteins: follicle peptides like Procapil™ and Capixyl™ target root anchoring at the scalp, while Copper Peptides (GHK-Cu) and bond peptides support both scalp comfort and stressed strands.',
        ''),
    'Surfactants & Cleansers': (
        'Cleansing is a dial, not an all-or-nothing choice: gentle non-sulfate cleansers protect weekly moisture, while sulfates and chelators reset heavy buildup.',
        ''),
    'Conditioning Agents': (
        'Slip comes from conditioning agents: cationic agents like BTMS smooth and detangle, fatty alcohols make the cream, and polyquats add a light conditioning film.',
        ''),
    'Humectants': (
        'Humectants pull water toward your hair: light sugars hydrate without stickiness, classics like glycerin do the heavy lifting, and plant gels add slip and hold.',
        ''),
    'Ceramides': (
        'Ceramides are lipids that sit between the cuticle scales: named ceramides do the work, building blocks like phytosphingosine support them, and pseudo-ceramides are look-alikes.',
        ''),
    'Lipids': (
        'Lipids are the fats in and on hair: ceramides are one kind, cholesterol and phospholipids are others, and none of them is just another name for a plant oil.',
        ''),
    'Oils & Butters': (
        'Oils and butters seal moisture in: light oils soften without weight, richer oils cushion dry strands, and butters and occlusives lock it in until you wash.',
        ''),
    'Film Formers': (
        'Film formers wrap hair in a thin, flexible layer: conditioning polyquats add slip and frizz control, hold polymers set the curl, plant gels give a softer botanical hold, and gel thickeners give a gel its body.',
        ''),
}

# Callouts the owner asked for on specific family pages. Not rendered yet: they go in
# when the page is built. Keyed by family.
NOTES = {
    'Scalp Actives': [
        'Topical actives support scalp health and the look of density. They do not treat medical hair loss.',
    ],
    'Peptides': [
        'Topical peptides support scalp comfort and the look of density. They do not treat medical hair loss.',
    ],
    'Surfactants & Cleansers': [
        'Chelators (citric acid, tartaric acid, EDTA) bind minerals from hard water. They are not foaming detergents like sulfates.',
        '"Sulfate-free" does not, by itself, tell you how gentle a shampoo will feel. Sodium C14-16 olefin sulfonate, for example, is not a sulfate, but it is a stronger anionic cleanser than the mild ones on this page, and a shampoo built on it can feel more stripping. Check which cleanser comes first on the label.',
    ],
}

NOTES.update({
    'Humectants': [
        'Humectants work with the air around you. In high humidity they can add frizz, and in very dry air glycerin can pull moisture out of your hair. Seal with a leave-in or oil, and check the forecast on wash day.',
    ],
    'Ceramides': [
        'A front-of-pack "ceramide complex" does not tell you which ceramides are inside. Look for the specific names on the label: Ceramide NP, AP or EOP.',
    ],
    'Lipids': [
        'Ceramides are one type of lipid. Cholesterol and phospholipids are other types. They are different from plant oils, and a formula can combine them.',
    ],
    'Conditioning Agents': [
        'Behentrimonium Methosulfate has "sulfate" in its name but is a conditioning agent, not a sulfate cleanser.',
    ],
})

# Links between families: (text before, link text, family slug)
CROSS = {
    'Scalp Actives': ('Looking for Procapil™, Capixyl™, or Copper Peptides? ', 'Explore our Peptides guide', 'peptides'),
    'Ceramides': ('Ceramides are one kind of lipid. ', 'Explore Lipids', 'lipids'),
    'Lipids': ('Looking at plant oils? ', 'Explore Oils & Butters', 'oils-butters'),
    'Conditioning Agents': ('Fatty alcohols and polyquats have their own pages: ', 'Alcohols', 'alcohols'),
    'Film Formers': ('Plant gels hold water as well as hair, so they are on the Humectants page too, next to slip-only botanicals like marshmallow root. ', 'Explore Humectants', 'humectants'),
}

HOW_TO_SPOT = {
    'Silicones': [
        ('Ends in -cone or -conol', 'Dimethicone, Dimethiconol, Amodimethicone.'),
        ('Starts with PEG- and ends in -cone', 'PEG-6 Methyl Ether Dimethicone. The PEG part is what makes it rinse out in water.'),
        ('Starts with Cyclo-', 'Cyclopentasiloxane. These evaporate.'),
        ('Contains -siloxane or -silane', 'Another way the same chemistry gets written.'),
        ('Contains Amino- or Amo-', 'Amodimethicone, Aminopropyl Dimethicone. The amino part is what makes them seek out damage.'),
    ],
    'Alcohols': [
        ('Names ending in -yl alcohol', 'Cetyl, Cetearyl, Stearyl and Behenyl Alcohol are the fatty, softening kind. Despite the word, they are not drying.'),
        ('Benzyl Alcohol', 'A preservative. Usually near the end of the list, in a small amount.'),
        ('Alcohol Denat., SD Alcohol, Ethanol, Isopropyl Alcohol', 'The evaporating kind. Where they sit matters: near the top of the list means a lot, near the bottom means a trace.'),
        ('The word "alcohol" alone is not the tell', 'Read the whole name. It tells you which of the three you are looking at.'),
    ],
    'Proteins': [
        ('Starts with Hydrolyzed', 'Hydrolyzed Silk, Rice, Quinoa, Wheat or Keratin. The word after it is the source, and the source is a clue to how heavy it is.'),
        ('Silk, Rice and Quinoa', 'The lightweight group.'),
        ('Wheat and Keratin', 'The heavier group, the ones that patch damage and can leave hair stiff if overused.'),
        ('Contains Amino Acids, or an amino acid name', 'Silk Amino Acids, Wheat Amino Acids, Arginine, Creatine. The smallest pieces.'),
        ('Ends in -peptide or Tripeptide', 'Not the same thing. Peptides are counted separately from hydrolysed proteins on this site.'),
    ],
    'Scalp Actives': [
        ('Niacinamide', 'Vitamin B3. Sometimes written as Niacinamide (Vitamin B3).'),
        ('Caffeine', 'Written plainly.'),
        ('Camellia Sinensis Leaf Extract', 'Green tea. EGCG is the part of it this family is about.'),
        ('Where it sits in the list', 'These are often used in small amounts, so low on the list is normal. Position alone does not tell you whether a product is any good.'),
    ],
    'Peptides': [
        ('Names ending in -peptide, or containing Tripeptide or Tetrapeptide', 'Copper Tripeptide-1, Biotinoyl Tripeptide-1, Acetyl Tetrapeptide-3. The number tells you which one.'),
        ('Procapil™ and Capixyl™', 'Brand names for scalp complexes. On a label you will usually see the peptide name instead, sometimes with the brand in brackets.'),
        ('sh-Oligopeptide-78', 'The bond-repair peptide behind K18. It is a repair ingredient for the strand, not a scalp one.'),
        ('Where it sits in the list', 'Peptides are used in small amounts, so low on the list is normal. Position alone does not tell you whether a product is any good.'),
    ],
    'Conditioning Agents': [
        ('Starts with Behentrimonium or Cetrimonium', 'The cationic conditioning agents. Behentrimonium Methosulfate is not a sulfate cleanser.'),
        ('Ends in -yl alcohol', 'Cetyl, Cetearyl, Stearyl and Behenyl Alcohol. The creamy base of a conditioner.'),
        ('Starts with Polyquaternium-', 'Conditioning polymers. The number tells you which one.'),
    ],
    'Humectants': [
        ('Glycerin, Panthenol, Hyaluronic Acid or Sodium Hyaluronate', 'The classic humectants.'),
        ('Betaine, Trehalose', 'The light, non-sticky ones.'),
        ('Ends in -diol or -glycol', 'Propanediol, Butylene Glycol. Lightweight carriers that also hold water.'),
        ('Gums, extracts and seeds', 'Chia, Xanthan Gum, Pectin, Marshmallow Root, Slippery Elm. The plant gels.'),
    ],
    'Ceramides': [
        ('Ceramide NP, AP, EOP', 'The named ceramides. Older labels may call them Ceramide 3, 6-II and 1.'),
        ('Phytosphingosine', 'A building block that sits next to ceramides in fuller formulas.'),
        ('Ends in -amide with Stearamide or Lauramide', 'Pseudo-ceramides, the look-alikes.'),
    ],
    'Lipids': [
        ('Cholesterol', 'Written plainly.'),
        ('Phospholipids, Lecithin, Hydrogenated Lecithin', 'Lipids that come from lecithin.'),
        ('Linoleic, Oleic, Stearic Acid', 'Fatty acids, often listed one by one.'),
        ('Squalane', 'A lightweight, stable lipid.'),
    ],
    'Oils & Butters': [
        ('Contains Oil or Seed Oil', 'Grapeseed, Sweet Almond, Olive, Pumpkin Seed. The Latin name is on the label, with the common name sometimes in brackets.'),
        ('Contains Butter', 'Shea (Butyrospermum Parkii) Butter is the common one.'),
        ('Paraffinum Liquidum', 'Mineral oil. It sits on top of the strand.'),
        ('Where it sits in the list', 'A butter or oil near the top is a big part of the formula. Near the bottom it is a trace.'),
    ],
    'Film Formers': [
        ('Starts with Polyquaternium-', 'Conditioning polymers. Polyquaternium-69 is the hold type.'),
        ('PVP', 'A classic styling resin.'),
        ('Carbomer', 'The gel thickener.'),
        ('Pectin, Xanthan Gum, Chia (Salvia Hispanica) or Sea Moss (Chondrus Crispus)', 'Plant gels. The base of most botanical gels and custards.'),
        ('Ends in Copolymer or Crosspolymer', 'VP/VA Copolymer, Maltodextrin/VP Copolymer, Acrylates Copolymer. More hold polymers, often next to PVP.'),
    ],
    'Surfactants & Cleansers': [
        ('Ends in -sulfate', 'Sodium Lauryl Sulfate and Sodium Laureth Sulfate. Note that Methosulfate, as in Behentrimonium Methosulfate, is a conditioning ingredient, not a cleanser.'),
        ('Ends in -isethionate, -taurate, -betaine or -glucoside', 'The gentle group. Sodium Lauroyl Methyl Isethionate, Cocamidopropyl Betaine, Coco-Glucoside.'),
        ('Near the top, after Water', 'In a shampoo, the cleanser is usually one of the first few ingredients.'),
        ('Citric Acid, Tartaric Acid, Disodium or Tetrasodium EDTA', 'Chelators. They bind minerals from hard water and do not foam like cleansers.'),
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


# Families whose sections run along a scale. Section order is the scale order. Group ids not
# listed in `levels` are shown as supporting ingredients, with no level.
SCALES = {
    'Surfactants & Cleansers': {'axis': 'Cleansing strength', 'low': 'Gentlest', 'high': 'Strongest',
                                'levels': {'GRP-016': 1, 'GRP-023': 2, 'GRP-015': 3}},
    'Silicones': {'axis': 'Buildup', 'low': 'Rinses out', 'high': 'Stays until you clarify',
                  'levels': {'GRP-001': 1, 'GRP-002': 2, 'GRP-003': 3, 'GRP-004': 4}},
    'Alcohols': {'axis': 'Drying', 'low': 'Softening', 'high': 'Drying',
                 'levels': {'GRP-005': 1, 'GRP-006': 2, 'GRP-007': 3}},
    'Proteins': {'axis': 'Weight', 'low': 'Lightest', 'high': 'Heaviest',
                 'levels': {'GRP-008': 1, 'GRP-009': 2, 'GRP-010': 3}},
    'Oils & Butters': {'axis': 'Richness', 'low': 'Lightest', 'high': 'Richest',
                       'levels': {'GRP-040': 1, 'GRP-041': 2, 'GRP-042': 3}},
}
# Catalog products shown as examples under a group (owner's picks, 18 Nov; widened 22 Nov).
# Shampoos sit at the level of the strongest cleanser in their list: any olefin sulfonate
# makes it level 2, any sulfate level 3. Products with no ingredient list are left out.
EXAMPLES = {
    # Level 1: only gentle cleansers (isethionates, taurates, glucosides, amphoterics)
    'GRP-016': ['TGC-096', 'TGC-154', 'TGC-069', 'TGC-074', 'TGC-105', 'TGC-175'],
    # Level 2: olefin sulfonate first
    'GRP-023': ['TGC-001', 'TGC-135', 'TGC-063', 'TGC-065', 'TGC-185'],
    # Level 3: sulfates
    'GRP-015': ['TGC-024', 'TGC-036', 'TGC-103'],
    # Chelating shampoos (EDTA, phytate/phytic acid, gluconate)
    'GRP-025': ['TGC-002', 'TGC-023', 'TGC-003', 'TGC-130'],
    # Ceramides
    'GRP-026': ['TGC-163', 'TGC-009', 'TGC-168', 'TGC-161', 'TGC-173', 'TGC-170', 'TGC-169', 'TGC-172'],
    'GRP-027': ['TGC-163', 'TGC-009', 'TGC-172'],
    'GRP-028': ['TGC-163', 'TGC-009', 'TGC-149'],
    # Film formers
    'GRP-044': ['TGC-068', 'TGC-062', 'TGC-061', 'TGC-060', 'TGC-144', 'TGC-058'],
    'GRP-046': ['TGC-034', 'TGC-035', 'TGC-046', 'TGC-022', 'TGC-152', 'TGC-182'],
    'GRP-045': ['TGC-058', 'TGC-059', 'TGC-178', 'TGC-133'],
}
EX_LABEL = {
    'GRP-025': 'Chelating shampoos in our catalog',
    'GRP-026': 'Products in our catalog with named ceramides',
    'GRP-027': 'Products in our catalog with phytosphingosine',
    'GRP-028': 'Products in our catalog with pseudo-ceramides',
    'GRP-044': 'Stylers in our catalog with hold polymers',
    'GRP-046': 'Botanical gels in our catalog',
    'GRP-045': 'Gels in our catalog thickened with carbomer',
}
STOPS = [('#DCF473', '#432731'), ('#DCE6F0', '#432731'), ('#2548D7', '#fff'), ('#432731', '#fff')]


def tone(level, top):
    i = 0 if top <= 1 else round((level - 1) / (top - 1) * 3)
    return STOPS[i]


def short_name(sub):
    return re.sub(r'\s*\(.*$', '', sub).strip()


def lvl_badge(r, lv, sc):
    if not sc:
        return ''
    g = r.get('group_id')
    if g in lv:
        top = max(lv.values())
        bg = tone(lv[g], top)[0]
        return f'<p class="gp-sub"><span class="gp-sub-dot" style="--c:{bg}"></span>Level {lv[g]} of {top} · {e(sc["axis"].lower())}</p>'
    return '<p class="gp-sub">Supporting ingredient · no level</p>'


def example_html(gid):
    ids_ = EXAMPLES.get(gid)
    if not ids_:
        return ''
    byid = {p['id']: p for p in B.products}
    links = []
    for i in ids_:
        p = byid.get(i)
        if not p:
            continue
        nm = (p['name'] or '').strip()
        br = (p.get('brand') or '').strip()
        full = nm if nm.lower().startswith(br.lower()) else f'{br} {nm}'.strip()
        links.append(f'<a href="../../products/{p["_slug"]}/">{e(full)}</a>')
    if not links:
        return ''
    label = EX_LABEL.get(gid, 'Shampoos in our catalog built on this kind of cleanser')
    return f'<p class="gp-ex"><b>{e(label)}</b>{"".join(links)}</p>'


def page(family, rows, ids):
    head, lead = INTRO.get(family, (family, ''))
    secs = ''
    sc = SCALES.get(family)
    lv = {}
    dial = ''
    if sc:
        lv = {r['group_id']: sc['levels'][r['group_id']] for r in rows if r.get('group_id') in sc['levels']}
        top = max(lv.values()) if lv else 0
        if top:
            lvl_rows = [r for r in rows if r.get('group_id') in lv]
            strip = ''.join(f'<i style="--c:{tone(lv[r["group_id"]], top)[0]}"></i>' for r in lvl_rows)
            def kinds(sub):
                m = re.search(r'\((.*)\)', sub)
                return m.group(1) if m else ''
            stops = ''.join(
                f'<li><a href="#{family_slug(r["sub_classification"])}"><small>Level {lv[r["group_id"]]}</small><b>{e(short_name(r["sub_classification"]))}</b>'
                + (f'<span>{e(kinds(r["sub_classification"]))}</span>' if kinds(r["sub_classification"]) else '') + '</a></li>'
                for r in lvl_rows)
            dial = f'''<div class="gp-dial">
      <h2 class="gp-top-t">{e(sc["axis"])}</h2>
      <div class="gp-strip" aria-hidden="true">{strip}</div>
      <ol class="gp-stops" style="--n:{len(lvl_rows)}">{stops}</ol>
      <p class="gp-scale-ends"><span>&larr; {e(sc["low"])}</span><span>{e(sc["high"])} &rarr;</span></p>
    </div>'''
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
      {lvl_badge(r, lv, sc)}
      {f'<p class="gp-short">{e(short_p)}</p>' if short_p else ''}
      <p class="gp-long">{e(long_p)}</p>
      <div class="gp-ings">{member_html(members, ids)}</div>
      {f'<p class="gp-guide"><b>On the hair</b>{e(guide)}</p>' if guide else ''}
      {example_html(r.get('group_id'))}
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
        if soon == total:
            msg = f'None of the {total} ingredients named below have their own page yet.'
        else:
            msg = f'{soon} of the {total} ingredients named below {"does" if soon == 1 else "do"} not have {"its" if soon == 1 else "their"} own page yet.'
        note = (f'<li class="gp-know-soon">{msg} '
                'The row is on the way, and the name here will become a link as soon as it lands.</li>')

    def know(t):
        """A note as a list item: its first sentence in bold, the rest plain."""
        m = re.match(r'(.+?[.!?])\s+(.+)$', t.strip(), re.S)
        return f'<li><b>{e(m.group(1))}</b> {e(m.group(2))}</li>' if m else f'<li>{e(t)}</li>'
    callouts = ''.join(know(t) for t in NOTES.get(family, []))
    if family in CROSS:
        pre, txt, slug = CROSS[family]
        callouts += f'<li>{e(pre)}<a href="../{slug}/">{e(txt)} &rarr;</a></li>'
    fam_words = family.split(' ')
    h1 = (f'{e(" ".join(fam_words[:-1]))} <em>{e(fam_words[-1].lower())}</em>' if len(fam_words) > 1 else e(family))
    know_html = (f'''<div class="gp-know"><h2 class="gp-top-t">Good to know</h2><ul>{callouts}{note}</ul></div>'''
                 if (callouts or note) else '')
    top_html = f'<div class="gp-top{" gp-top-solo" if not dial else ""}">{dial}{know_html}</div>' if (dial or know_html) else ''
    body = f'''  <a class="crumb" href="../../groups/">← Ingredient families</a>
  <section class="gp-first">
    <h1>{h1}</h1>
    <p class="gp-lead">{e(head)}</p>
    {f'<p class="lead">{e(lead)}</p>' if lead else ''}
  </section>
  {top_html}
{secs}  {spot_html}
'''
    return B.shell('../../', f'{family} · The Good Coil Library',
                   f'The {len(rows)} kinds of {family.lower()} on hair-care labels, and what each one does.',
                   body, f'groups/{family_slug(family)}/index.html', 'groups')


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
    # Diagnostics for the build log: which ingredients sit in no family, and which family names have no row.
    inf = {gid for r in rows if (r.get('ingredient_family') or '').strip() in LIVE for gid, _ in parse_members(r.get('linked_inci_ids')) if gid}
    free = [i for i in B.ing if i['id'] not in inf]
    print('### Ingredients in no family page (id | page name | category)\n' + '\n'.join(
        f"- {i['id']} | {i['_title']} | {(i.get('category') or '').strip()}" for i in free) + '\n')
    miss = []
    for r in rows:
        for gid, nm in parse_members(r.get('linked_inci_ids')):
            if not (ids.get(gid) if gid else None) and not B.lookup(nm):
                miss.append(f"- {r.get('ingredient_family')}: {nm}")
    print('### Family names with no ingredient row\n' + ('\n'.join(miss) or '- none') + '\n')
    if made:
        index_page(made)
        print('### Ingredient family pages\n' + '\n'.join(
            f'- {f}: {n} kinds at /groups/{s}/' for f, s, n in made) + '\n')
    return made


def index_page(made):
    cards = ''.join(
        f'<li><a href="{sl}/"><h2>{e(f)}</h2><p>{e(INTRO.get(f, ("", ""))[0])}</p><span>{n} kinds</span></a></li>'
        for f, sl, n in made)
    body = f'''  <section class="page-head"><span class="eyebrow"><span class="little-dot"></span>Ingredient families</span><h1>Kinds of ingredients</h1>
  <p>Some ingredients go by one name but behave in different ways on coily hair. Each page takes one family apart, shows what to look for on a label, and links to the ingredients in it.</p></section>
  <ul class="prop-list fam-list">{cards}</ul>'''
    B.write('groups/index.html', B.shell('../', 'Ingredient families · The Good Coil Library',
            'Cleansers, conditioning agents, humectants, ceramides, lipids, oils, silicones and more: the kinds in each family and what they do on coily hair.',
            body, 'groups/index.html', 'groups'))

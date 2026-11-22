"""The full Label Decoder at /label-decoder/: paste any ingredient list (or pick a product) and every
ingredient is sorted into detailed categories, highlighted on the label and explained row by row.

Two sources, in this order:
1. The ingredient sheet: a row's tags and category, its page and its "what it does" line.
2. Name patterns (RULES below), for every word, so ingredients without a row are still sorted and
   rows get the finer categories (butter vs oil, which kind of silicone, which kind of cleanser).

Plain descriptions only, no verdicts. Regulatory notes say what the EU has decided, nothing more.
"""
import json, re
import build as B
import watchlist as W

e = B.e

# Families: the colour a word gets on the label. key, name, one line.
FAMILIES = [
    ('clean', 'Cleansers', 'What lifts oil, dirt and buildup.'),
    ('slip', 'Slip and conditioning', 'What makes hair slide, detangle and feel smooth.'),
    ('moist', 'Water binders', 'What draws water in and holds on to it.'),
    ('oils', 'Oils, butters and emollients', 'What softens and coats the outside of the hair.'),
    ('strength', 'Strength and repair', 'Proteins, peptides, lipids and bond builders.'),
    ('texture', 'Hold and texture', 'Film-formers, thickeners and emulsifiers.'),
    ('scalp', 'Scalp care', 'Ingredients made for the scalp.'),
    ('keep', 'Preservatives', 'What keeps a water-based product free of mould and bacteria.'),
    ('scent', 'Scent', 'Fragrance, the allergens inside it, and essential oils.'),
    ('basics', 'Formula basics', 'Water, pH, minerals, antioxidants, extracts and colour.'),
]

# Categories, in priority order: a word is coloured by its first category's family.
# key, name, family, what it is.
CATS = [
    ('sulfate', 'Sulfates', 'clean', 'Strong cleansers, the kind that make a shampoo lather hard and strip oil and buildup fast.'),
    ('strong', 'Strong non-sulfate cleansers', 'clean', 'Not sulfates, but high-detergency cleansers such as olefin sulfonates. Sulfate-free does not always mean gentle.'),
    ('mild', 'Mild cleansers', 'clean', 'Gentler cleansers such as isethionates, taurates, glucosides, sarcosinates and glutamates.'),
    ('cosurf', 'Co-cleansers and foam boosters', 'clean', 'Betaines, sultaines and similar: they soften a cleanser blend, boost foam and thicken.'),
    ('cleanser', 'Cleansers', 'clean', 'A cleanser (surfactant).'),
    ('quat', 'Conditioning agents (quats)', 'slip', 'Positively charged conditioners that cling to hair and detangle, like behentrimonium, cetrimonium and polyquaterniums.'),
    ('fatty', 'Fatty alcohols', 'slip', 'Waxy, softening alcohols that thicken conditioners and add slip. Not drying.'),
    ('sil-water', 'Water-soluble silicones', 'slip', 'Silicones made to dissolve in water (PEG or PPG in the name): light slip that rinses out with water.'),
    ('sil-light', 'Evaporating silicones', 'slip', 'Light silicones that give slip, then evaporate (cyclopentasiloxane and similar).'),
    ('sil-amino', 'Amino silicones', 'slip', 'Silicones that cling mostly to damaged spots and resist stacking up (amodimethicone and similar).'),
    ('silicone', 'Silicones', 'slip', 'Coating ingredients that add slip, shine and frizz control.'),
    ('cond', 'Conditioners and detanglers', 'slip', 'Ingredients that add slip so hair detangles more easily.'),
    ('humectant', 'Water binders (humectants)', 'moist', 'They draw water in and hold on to it: glycerin, glycols, aloe, honey, panthenol and similar.'),
    ('butter', 'Butters', 'oils', 'Rich, solid fats such as shea, cocoa and mango butter.'),
    ('mineral', 'Mineral oil and petrolatum', 'oils', 'Petroleum-derived oils and jellies that seal and coat.'),
    ('wax', 'Waxes', 'oils', 'Beeswax, candelilla, lanolin and similar: they seal and add hold.'),
    ('ester', 'Light emollients (esters)', 'oils', 'Lab-made oils that feel light and non-greasy, like caprylic/capric triglyceride or isopropyl myristate.'),
    ('oil', 'Oils', 'oils', 'Plant oils and squalane: they soften and coat the outside of the hair.'),
    ('protein', 'Proteins', 'strength', 'Proteins broken into pieces small enough to cling to the hair (hydrolyzed wheat, rice, silk, keratin and similar).'),
    ('amino', 'Amino acids', 'strength', 'The smallest building blocks of protein. Light, and usually fine for protein-sensitive hair.'),
    ('peptide', 'Peptides', 'strength', 'Short amino-acid chains, often in scalp serums or bond repair. Not the same as a hydrolyzed protein.'),
    ('lipid', 'Ceramides and lipids', 'strength', "Lipids like the hair's own, the ones that hold its outer layer together: ceramides, cholesterol, phytosphingosine, 18-MEA. Oils and butters are lipids too, but they coat the outside, so they are counted under Oils and butters."),
    ('bond', 'Bond builders', 'strength', 'Ingredients made to work on the bonds inside the hair, often after bleach, colour or heat.'),
    ('film', 'Film-formers (hold)', 'texture', 'They leave a flexible film as hair dries, for definition and hold.'),
    ('thick', 'Thickeners and gums', 'texture', 'Gums, cellulose and polymers that give a product its texture.'),
    ('emuls', 'Emulsifiers', 'texture', 'They keep oil and water mixed so the product does not separate.'),
    ('clay', 'Clays', 'texture', 'Clays such as bentonite and kaolin, used to draw out buildup or add body.'),
    ('scalp', 'Scalp ingredients', 'scalp', 'Ingredients made for the scalp, like caffeine, niacinamide, piroctone olamine or salicylic acid.'),
    ('formaldehyde', 'Formaldehyde releasers', 'keep', 'Preservatives that slowly release small amounts of formaldehyde. A known contact allergen for some people.'),
    ('isothiazolinone', 'Isothiazolinones', 'keep', 'Strong preservatives and common contact allergens. In the EU, methylisothiazolinone is not allowed in leave-on products.'),
    ('paraben', 'Parabens', 'keep', 'Preservatives whose names end in -paraben. The EU treats each one differently.'),
    ('preserv', 'Preservatives', 'keep', 'Anything made with water needs them, usually under 1% and near the end of the list.'),
    ('phthalate', 'Phthalates', 'scent', 'Chemicals used to carry fragrance and soften plastics. Names end in -phthalate.'),
    ('allergen', 'Fragrance allergens', 'scent', 'One of the fragrance allergens the EU requires to be named on a label above a set amount.'),
    ('essential', 'Essential oils', 'scent', 'Concentrated plant oils used for scent, like rosemary, peppermint or tea tree.'),
    ('fragrance', 'Fragrance', 'scent', 'Scent. "Fragrance" or "parfum" can stand for many ingredients that are not listed one by one.'),
    ('drying', 'Drying alcohols', 'basics', 'Short-chain alcohols that evaporate fast. High on a list, they can leave hair feeling dry.'),
    ('water', 'Water and base', 'basics', 'Water, or a floral water or juice that takes its place. Usually most of the bottle.'),
    ('ph', 'pH adjusters and acids', 'basics', "They set the product's pH, like citric acid or sodium hydroxide."),
    ('chelator', 'Chelators', 'basics', 'They bind minerals from hard water so they rinse away.'),
    ('antiox', 'Antioxidants', 'basics', 'They protect oils in the formula from going off, like vitamin E (tocopherol).'),
    ('extract', 'Plant extracts', 'basics', 'Extracts, juices, powders and ferments from plants.'),
    ('colorant', 'Colourants', 'basics', 'Dyes and pigments that colour the product.'),
    ('uv', 'UV filters', 'basics', 'They absorb UV light to protect the product, or the hair.'),
    ('ethanolamine', 'Ethanolamines (DEA, TEA, MEA)', 'basics', 'pH adjusters and foam boosters made from ethanolamine.'),
    ('peg', 'PEGs and PPGs', 'basics', 'Ingredients with PEG- or PPG- in the name, used as emulsifiers, cleansers or to make things dissolve in water.'),
    ('coconut', 'Coconut-derived', 'basics', 'Made from coconut, like cocamidopropyl betaine, coco-glucoside or coconut oil.'),
    ('gluten', 'Wheat, barley, rye or oat', 'basics', 'Comes from wheat, barley, rye or oat. Listed so you can spot it. If you have an allergy, check with the brand.'),
]

# Name patterns on the normalised word (lowercase, anything else a single space). cat, pattern, unless.
# Written for both Python re and JavaScript RegExp (no lookbehind).
ESS = r'(peppermint|mentha|tea tree|melaleuca|rosemary|rosmarinus|lavender|lavandula|eucalyptus|lemon|citrus|orange|bergamot|ylang|geranium|pelargonium|cedarwood|cedrus|clary|salvia|patchouli|pogostemon|grapefruit|lime|spearmint|basil|ocimum|clove|eugenia|cinnamon|cinnamomum|ginger|zingiber|chamomile|anthemis|chamomilla|frankincense|boswellia|sandalwood|santalum|thyme|thymus|juniper|juniperus|vetiver|neroli|cymbopogon|lemongrass|litsea|fennel|foeniculum|cypress|cupressus|pine|pinus|myrrh|commiphora|palmarosa|petitgrain)'
RULES = [
    ('sulfate', r'\b(lauryl|laureth|coco|cocoyl|myreth|coceth|decyl|deceth|tridecyl|trideceth|pareth|cetyl|cetearyl|alkyl|alkyleth|myristyl)\b.*\bsulfate\b', None),
    ('strong', r'olefin sulfonate|dodecylbenzene sulfonate|alkylbenzene sulfonate', None),
    ('mild', r'isethionate|taurate|glucoside\b|sarcosinate|sulfosuccinate|amphoacetate|amphodiacetate|amphopropionate|amphodipropionate|glutamate|glycinate|alaninate|lactylate|glyceryl cocoate|polyglucose|coco glucoside', r'glutamate diacetate|stearoyl lactylate|cetearyl glucoside|glyceryl glucoside|methyl glucoside|tetrasodium glutamate|monosodium glutamate'),
    ('cosurf', r'betaine\b.*|sultaine|amine oxide|\bcocamide\b|lauramide|amphoteric', r'^betaine$|^trimethylglycine$'),
    ('quat', r'trimonium|polyquaternium|quaternium|dimethylamine\b|hydroxyethylmonium|ethyl ethonium|dimonium|esterquat|ammonium chloride\b|methosulfate', r'quaternium 15$|^ammonium chloride$|benzalkonium|benzethonium'),
    ('fatty', r'\b(cetyl|stearyl|cetearyl|behenyl|myristyl|arachidyl|oleyl|lauryl|isostearyl|caprylic|brassica|lanolin) alcohols?\b|\boctyldodecanol\b|\bc\d+ \d+ alcohols?\b|^cetostearyl alcohol', None),
    ('sil-water', r'\b(peg|ppg) \d+.*(methicone|siloxane)|methicone copolyol|bis peg|bis ppg', None),
    ('sil-light', r'cyclo(penta|hexa|tetra)siloxane|cyclomethicone|\btrisiloxane\b|caprylyl methicone', None),
    ('sil-amino', r'amodimethicone|amino\w* ?\w*methicone|aminopropyl dimethicone|bis aminopropyl dimethicone|trideceth \d+ amodimethicone', None),
    ('silicone', r'methicone|siloxane|silane\b|conol\b|silsesquioxane|dimethicone|silicone', None),
    ('humectant', r'glycerin|glycerine|propanediol|butylene glycol|propylene glycol|pentylene glycol|hexylene glycol|sorbitol|\bhoney\b|\bmel\b|agave|panthenol|sodium pca|\bpca\b|hyaluron|\burea\b|sodium lactate|^betaine$|trimethylglycine|aloe .*(juice|gel)|aloe barbadensis|\binulin\b|glyceryl glucoside|fructose|glucose|sucrose|saccharide isomerate|tremella|polyglycerin|diglycerin|hydroxyethyl urea|methyl gluceth|glycereth|sodium hyaluronate|\bxylitol\b|erythritol|trehalose|\bmaltitol\b|caprylyl glycol', r'ethylhexylglycerin|ethylhexyl glycerin|imidazolidinyl urea|diazolidinyl urea|polyoxymethylene urea|glyceryl (stearate|oleate|cocoate|caprylate|laurate)|glycerin(e)? (stearate|oleate)|caprylyl glycol$'),
    ('butter', r'\bbutter\b|butyrospermum|\bshea\b|theobroma cacao seed|mangifera indica seed|murumuru|cupuacu|illipe|kokum|sal seed', r'oil$|glycerides?$|ethyl ester'),
    ('mineral', r'mineral oil|paraffinum liquidum|petrolatum|\bparaffin\b|microcrystalline wax|ozokerite|ceresin|isoparaffin', None),
    ('wax', r'\bwax\b|\bcera\b|beeswax|candelilla|carnauba|euphorbia cerifera|copernicia|\blanolin\b|cetyl esters|rice bran wax|sunflower seed wax', r'emulsifying wax|lanolin alcohol'),
    ('ester', r'isopropyl (myristate|palmitate|isostearate)|caprylic capric triglyceride|coco caprylate|ethylhexyl (palmitate|stearate|isononanoate|olivate|cocoate)|alkyl benzoate|isoamyl (laurate|cocoate)|dicaprylyl|isododecane|isohexadecane|hemisqualane|neopentanoate|isononanoate|triethylhexanoin|\bc\d+ \d+ alkane|undecane|tridecane|heptyl undecylenate|myristyl myristate|cetyl (palmitate|ethylhexanoate)|decyl oleate|octyl palmitate|propanediol dicaprylate|diisopropyl adipate', None),
    ('oil', r'\boil\b|squalane|squalene|\bjojoba\b|simmondsia|triglycerides?\b|\boleum\b', r'essential oil blend|^peg |\bpeg \d+|mineral oil|hydrogenated castor oil|castor oil (peg|glycerides)|caprylic capric|sulfated castor'),
    ('protein', r'hydrolyzed.*\b(protein|keratin|collagen|silk|wheat|rice|quinoa|soy|oat|pea|elastin|baobab|corn|milk|casein|lupin|almond|sesame|vegetable|jojoba|potato|hemp|yeast|bean|amaranth|sericin|conchiolin|pearl)|\bkeratin\b|\bcollagen\b|\bsericin\b|\bgelatin\b|\bprotein\b|\belastin\b|\bsilk\b|serica|\bconchiolin\b', r'silk amino|amino acids'),
    ('amino', r'amino acids?\b|\barginine\b|\bcysteine\b|\bcystine\b|\bserine\b|\bglycine\b|\balanine\b|\blysine\b|\bhistidine\b|\bthreonine\b|\bproline\b|glutamic acid|aspartic acid|\bleucine\b|\bisoleucine\b|\bvaline\b|\bmethionine\b|\btyrosine\b|\bcreatine\b|\bglutamine\b|\btaurine\b', None),
    ('peptide', r'peptide|\bk18\b', None),
    ('lipid', r'ceramide|phytosphingosine|sphingolipid|sphingosine|\bcholesterol\b|\b18 mea\b|methyl eicosenoate|glycosphingolipid', None),
    ('bond', r'bis aminopropyl diglycol dimaleate|dimaleate|maleic acid|sh oligopeptide 78|\bk18 ?peptide|bond ?build|sodium (citrate|malate) succinate|succinic acid|tartaric acid', r'^tartaric acid$|^succinic acid$'),
    ('film', r'\bpvp\b|polyvinylpyrrolidone|\bvp\b.*copolymer|vinyl caprolactam|polyquaternium (4|10|11|28|37|55|69|72)\b|acrylates? (copolymer|octylacrylamide)|octylacrylamide|linum usitatissimum|flax ?seed|\bshellac\b|polyurethane|chitosan|polyvinyl alcohol|\bpva\b|corn starch modified|polyimide|polyester 5|ethylcellulose', None),
    ('thick', r'\bgum\b|xanthan|\bguar\b|carbomer|cellulose|carrageenan|\bagar\b|alginate|sclerotium|\bpectin\b|starch|hectorite|crosspolymer|polyacrylate|polyacrylamide|chondrus|acacia senegal|cassia|tara gum|sodium chloride|magnesium aluminum silicate|silica\b|ammonium acryloyldimethyltaurate', r'hydroxypropyltrimonium|corn starch modified'),
    ('emuls', r'polysorbate|ceteareth|steareth|\blaureth \d|\boleth\b|ceteth|\bpeg \d+ (stearate|glyceryl|hydrogenated castor|castor|distearate|laurate|oleate|sorbitan|dilaurate|isostearate|cocoate)|glyceryl (stearate|oleate|caprylate|laurate|stearate citrate|stearate se)|sorbitan|lecithin|cetearyl glucoside|polyglyceryl|ppg \d+ ceteth|stearoyl lactylate|cetyl phosphate|cetearyl olivate|sorbitan olivate|emulsifying wax|methyl glucose (dioleate|sesquistearate)|sucrose (stearate|cocoate|laurate)|glyceryl citrate|arachidyl glucoside|hydrogenated lecithin|cetearyl wheat straw glycosides|isosteareth', None),
    ('clay', r'kaolin|bentonite|montmorillonite|rhassoul|ghassoul|illite|\bclay\b|moroccan lava', None),
    ('scalp', r'caffeine|niacinamide|piroctone olamine|zinc pyrithione|ketoconazole|salicylic acid|selenium sulfide|coal tar|\bmenthol\b|menthyl lactate|\bbiotin\b|biotinoyl|camellia sinensis|green tea|redensyl|capixyl|procapil|\bsaw palmetto\b|serenoa|apigenin|\badenosine\b|climbazole|\bsulfur\b|\bichthammol\b|willow bark|salix alba|pyrithione|sodium salicylate|glycyrrhiza|licorice|dihydroquercetin|anagain|baicapil|caffeic', None),
    ('formaldehyde', r'dmdm hydantoin|imidazolidinyl urea|diazolidinyl urea|^quaternium 15$|bronopol|2 bromo 2 nitropropane|sodium hydroxymethylglycinate|methenamine|polyoxymethylene urea|benzylhemiformal|glyoxal', None),
    ('isothiazolinone', r'isothiazolinone', None),
    ('paraben', W.PARABEN_RX.pattern, None),
    ('preserv', r'phenoxyethanol|\bbenzoate\b|\bsorbate\b|sorbic acid|benzoic acid|dehydroacetic|dehydroacetate|ethylhexylglycerin|caprylyl glycol|chlorphenesin|benzyl alcohol|hydantoin|iodopropynyl|benzethonium|benzalkonium|triclosan|\bhexanediol\b|1 2 hexanediol|levulinic acid|levulinate|anisic acid|anisate|glyceryl caprylate|lactobacillus|leuconostoc|phenethyl alcohol|o cymen 5 ol|chloroxylenol|polyaminopropyl biguanide|sodium hydroxymethylglycinate|caprylhydroxamic|gluconolactone|ethylhexyl glycerin|undecylenoyl glycine|potassium sorbate|sodium benzoate|bronopol|piroctone olamine', r'alkyl benzoate|benzyl benzoate|\bc\d+ \d+ alkyl'),
    ('phthalate', W.PHTH_RX.pattern, None),
    ('allergen', r'amyl cinnamal|amylcinnamyl alcohol|anis(e|yl) alcohol|benzyl alcohol|benzyl benzoate|benzyl cinnamate|benzyl salicylate|^cinnamal$|cinnamyl alcohol|\bcitral\b|citronellol|coumarin|\beugenol\b|farnesol|geraniol|hexyl cinnamal|hydroxycitronellal|hydroxyisohexyl 3 cyclohexene|isoeugenol|butylphenyl methylpropional|\blilial\b|limonene|linalool|methyl 2 octynoate|alpha isomethyl ionone|evernia prunastri|evernia furfuracea|oakmoss|treemoss', None),
    ('essential', ESS + r'.*\b(leaf|peel|flower|herb|bark|root|seed|wood|fruit|rind|needle|resin|leaf stem|aerial)?\s*oil\b|essential oil', r'seed oil$|kernel oil$|\bbutter\b|nut oil$|pinus pinaster bark extract'),
    ('fragrance', r'\bfragrance\b|\bparfum\b|\bperfume\b|\baroma\b|\bflavor\b|\bflavour\b|essential oil blend', None),
    ('drying', r'\balcohol denat\b|\bsd alcohol\b|^alcohol$|\bethanol\b|\bethyl alcohol\b|\bisopropyl alcohol\b|^denatured alcohol|^alcohol \(|^alcohol denatured|\bisopropanol\b', None),
    ('water', r'^(deionized |distilled |purified )?(water|aqua|eau)( (water|aqua|eau|purified|deionized))*$|flower water|hydrosol|leaf water|\bdistillate\b|^coconut water$|fruit water', None),
    ('ph', r'citric acid|lactic acid|glycolic acid|malic acid|tartaric acid|sodium hydroxide|potassium hydroxide|triethanolamine|aminomethyl propanol|sodium citrate|apple cider vinegar|\bvinegar\b|acetic acid|succinic acid|phosphoric acid|sodium bicarbonate|ammonium hydroxide|\bethanolamine\b|sodium phosphate|potassium citrate|tromethamine|\barginine\b|sodium lactate|ascorbic acid', None),
    ('chelator', r'\bedta\b|edetate|phytate|phytic acid|etidronic|gluconate|\bglda\b|glutamate diacetate|ethylenediamine disuccinate|\bmgda\b|methylglycinediacetic|pentetate|iminodisuccinate|sodium citrate|gluconolactone|citric acid|\bhedp\b', None),
    ('antiox', r'tocopherol|tocopheryl|ascorbic|ascorbyl|\bbht\b|\bbha\b|butylated|ferulic|retinyl|ubiquinone|\bresveratrol\b|rosmarinus officinalis leaf extract|rosemary leaf extract|astaxanthin|carotene', None),
    ('extract', r'\bextract\b|\bjuice\b|\bpowder\b|\bflour\b|\bferment\b|\bfiltrate\b|leaf\b|\broot\b|\bflower\b', r'\boil\b|\bbutter\b|\bwax\b|aloe .*(juice|gel)|flower water|\bwater\b'),
    ('colorant', r'^ci \d{5}|\b(red|yellow|blue|green|violet|orange|ext violet) \d+\b|\bcaramel\b|iron oxides?|titanium dioxide|\bmica\b|annatto|\bfd c\b|ultramarines?|chromium oxide|\bd c\b', None),
    ('uv', r'benzophenone|methoxycinnamate|octinoxate|octocrylene|avobenzone|butyl methoxydibenzoylmethane|cinnamidopropyltrimonium|ethylhexyl salicylate|homosalate|\boxybenzone\b|ethylhexyl triazone|bis ethylhexyloxyphenol', None),
    ('ethanolamine', r'\b(dea|tea|mea|mipa)\b|diethanolamine|triethanolamine|monoethanolamine|\bethanolamine\b|cocamide (dea|mea)', None),
    ('peg', r'\b(peg|ppg) \d+|\bpeg\b|\bppg\b', None),
    ('coconut', r'\bcoco\b|cocos nucifera|coconut|cocamid|cocoyl|cocoate|\bcocoamphoacetate\b|cocoamphodiacetate|coco caprylate|cocoyl|cocamine', None),
    ('gluten', r'triticum|hordeum|secale|avena|\bwheat\b|\bbarley\b|\brye\b|\boat\b|\boats\b', r'buckwheat|fagopyrum'),
]

# Sheet tags and categories, mapped to the categories above.
TAG_MAP = {'protein': 'protein', 'ceramides': 'lipid', 'silicone': 'silicone', 'sulfate': 'sulfate', 'peptide': 'peptide',
           'humectant': 'humectant', 'butter/oil': 'oil', 'slip/detangler': 'cond', 'film-former': 'film',
           'chelating': 'chelator', 'bond repair': 'bond', 'paraben': 'paraben', 'phthalate': 'phthalate', 'strong-cleanser': 'strong'}

# Quick checks: always shown, found or not. Water binders, oils and butters first (owner, Nov 21), then the homepage's eight.
QUICK = ['humectant', 'oil', 'butter', 'protein', 'lipid', 'silicone', 'sulfate', 'peptide', 'paraben', 'strong', 'phthalate',
         'drying', 'fragrance', 'allergen', 'essential', 'mineral', 'formaldehyde', 'isothiazolinone', 'coconut', 'gluten']

EXAMPLE = ('Water (Aqua), Cetearyl Alcohol, Behentrimonium Methosulfate, Glycerin, Butyrospermum Parkii (Shea) Butter, '
           'Cocos Nucifera (Coconut) Oil, Amodimethicone, Hydrolyzed Wheat Protein, Ceramide NP, Panthenol, '
           'Aloe Barbadensis Leaf Juice, Polyquaternium-10, Xanthan Gum, Citric Acid, Tocopherol, Phenoxyethanol, '
           'Ethylhexylglycerin, Fragrance (Parfum), Linalool, Limonene')


def lib_cats(i):
    tags = {t.lower() for t in i['_tags']}
    cat = (i.get('category') or '').lower()
    out = [v for k, v in TAG_MAP.items() if k in tags]
    if any('scalp' in t for t in tags):
        out.append('scalp')
    if 'surfactant' in cat or 'cleanser' in cat:
        out.append('cleanser')
    if 'preserv' in cat:
        out.append('preserv')
    if 'fragrance' in cat:
        out.append('fragrance')
    return list(dict.fromkeys(out))


def data():
    rows, index = [], {}
    for i in B.ing:
        index[id(i)] = len(rows)
        rows.append([i['_slug'], i['_title'], B.first_sentence(i.get('what_it_does') or '', 160), lib_cats(i), i['inci_name']])
    keys = {k: index[id(i)] for k, i in B.keys.items()}
    return {
        'keys': keys, 'rows': rows,
        'fams': [list(f) for f in FAMILIES], 'cats': [list(c) for c in CATS],
        'rules': [[c, p, u] for c, p, u in RULES], 'quick': QUICK,
        'paraben': {k: v[1] for k, v in W.PARABEN_STATUS.items()}, 'phthBanned': W.PHTH_BANNED,
    }


def check_rules():
    """Every pattern must compile (they also run in the browser)."""
    for c, p, u in RULES:
        re.compile(p)
        if u:
            re.compile(u)
    known = {c[0] for c in CATS}
    assert all(c in known for c, _, _ in RULES), 'a rule names an unknown category'
    assert all(c in known for c in QUICK) and all(v in known for v in TAG_MAP.values())


def build():
    check_rules()
    R = '../'
    js = 'window.DX=' + json.dumps(data(), ensure_ascii=False, separators=(',', ':')) + ';\n' + \
         open(B.os.path.join(B.ROOT, 'src', 'decoder.js'), encoding='utf-8').read()
    B.write('assets/decoder.js', js)
    legend = ''.join(f'<button type="button" class="dx-fam" data-f="{k}" aria-pressed="false"><i class="dx-sw f-{k}"></i>{e(n)}</button>' for k, n, _ in FAMILIES)
    body = f'''  <a class="crumb" href="../">← Library</a>
  <div class="dx-tabs" role="tablist" aria-label="Decoder mode"><button type="button" role="tab" id="tab-one" aria-selected="true" aria-controls="dx-one">Break down one label</button><button type="button" role="tab" id="tab-cmp" aria-selected="false" aria-controls="dx-cmp">Compare labels</button></div>
  <div id="dx-one" role="tabpanel" aria-labelledby="tab-one">
  <section class="dx-head">
    <span class="eyebrow"><span class="little-dot"></span>Label Decoder · Full breakdown</span>
    <h1>Paste a label. See <em>every</em> ingredient.</h1>
    <p class="lead">Cleansers, silicones, proteins, ceramides, humectants, oils, preservatives, fragrance allergens, phthalates and more, highlighted on the label and explained one by one. No scores, no verdicts.</p>
    <form class="paste dx-form" id="dx-form">
      <label for="dx-t">Ingredient list</label>
      <textarea id="dx-t" rows="5" placeholder="Water, Glycerin, Cetearyl Alcohol, …"></textarea>
      <div class="paste-row"><button class="go" type="submit">Break it down</button><button class="link-btn" type="button" id="dx-ex">Try an example</button><button class="link-btn" type="button" id="dx-clear" hidden>Clear and start over</button></div>
    </form>
    <div class="finder dx-finder">
      <label for="dx-f">Or pick a product we have read</label>
      <input id="dx-f" type="text" autocomplete="off" role="combobox" aria-expanded="false" aria-controls="dx-fl" placeholder="Start typing a product or brand">
      <ul class="f-list" id="dx-fl" role="listbox" hidden></ul>
    </div>
  </section>
  <section class="dx-out" id="dx-out" hidden aria-live="polite">
    <div class="dx-sum" id="dx-sum"></div>
    <h2 class="dx-h">Quick checks</h2>
    <div class="dx-quick" id="dx-quick"></div>
    <h2 class="dx-h">The label, highlighted</h2>
    <div class="dx-legend" role="group" aria-label="Highlight one family">{legend}</div>
    <ol class="dx-words" id="dx-words"></ol>
    <h2 class="dx-h">What's in it</h2>
    <div class="dx-fams" id="dx-fams"></div>
    <h2 class="dx-h">Ingredient by ingredient</h2>
    <div class="dx-table-wrap"><table class="dx-table"><thead><tr><th scope="col">#</th><th scope="col">Ingredient</th><th scope="col">What it is</th><th scope="col">What it does</th></tr></thead><tbody id="dx-rows"></tbody></table></div>
    <p class="fine dx-fine">We sort every ingredient by its library page where there is one, and by its name where there is not, so a few may be sorted loosely. Grey words are ones we cannot sort yet. Regulatory notes are EU rules; other countries have their own. This is information, not advice. If you have an allergy or a health concern, check with the brand or your doctor. <a href="../label-check/">About parabens and phthalates</a></p>
    <p class="dx-share"><button class="link-btn" type="button" id="dx-copy">Copy a link to this breakdown</button></p>
  </section>
  </div>
  <div id="dx-cmp" role="tabpanel" aria-labelledby="tab-cmp" hidden>
  <section class="dx-head">
    <span class="eyebrow"><span class="little-dot"></span>Label Decoder · Compare</span>
    <h1>Put two labels <em>side by side</em>.</h1>
    <p class="lead">Which one has more water binders, more protein, a stronger cleanser, more oils? Pick a product or paste each list. Higher up the list usually means more of it in the bottle.</p>
    <div class="dx-slots" id="dx-slots"></div>
    <div class="paste-row"><button class="go" type="button" id="dx-cmp-go">Compare</button><button class="link-btn" type="button" id="dx-add">Add a third label</button><button class="link-btn" type="button" id="dx-cmp-clear">Clear all</button></div>
  </section>
  <section class="dx-out" id="dx-cmp-out" hidden aria-live="polite">
    <div class="dx-table-wrap"><table class="dx-table dx-ctable" id="dx-ctable"></table></div>
    <p class="fine dx-fine">Counts show how many ingredients of each kind a label has; "first at #3" shows where the first one sits. Labels list ingredients from most to least, down to about 1%, so higher up usually means more. Neither count tells you the exact amount. This is information, not advice.</p>
  </section>
  </div>
  <script>window.DX_ROOT='../';window.DX_EXAMPLE={json.dumps(EXAMPLE)};</script>
  <script src="../assets/decoder.js" defer></script>
'''
    B.write('label-decoder/index.html', B.shell(R, 'Label Decoder: full ingredient breakdown · The Good Coil Library',
            'Paste any hair-care ingredient list and see every ingredient sorted and explained: cleansers, silicones, proteins, ceramides, humectants, oils, preservatives, fragrance allergens, phthalates and more.',
            body, 'label-decoder/', 'decoder'))

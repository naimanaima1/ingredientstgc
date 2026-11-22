# The Good Coil Library

Source for **library.thegoodcoil.com**: a library of hair-care ingredients, each described by what it is and what it does. It's part of [The Good Coil](https://thegoodcoil.com) and feeds [JARA](https://itsjara.com).

## How it works

```
Google Sheets (master copies)
  ├─ Ingredient database ─┐
  └─ Product catalog ─────┤  published as CSV ("File > Share > Publish to web")
                          ▼
GitHub Action (.github/workflows/publish.yml): nightly, on every push, or "Run workflow"
  1. downloads both CSVs into data/          (links are repository secrets)
  2. python3 scripts/build.py → _site/       (standard library only, no installs)
  3. publishes _site/ to GitHub Pages
                          ▼
library.thegoodcoil.com
  /                         search + list of every ingredient
  /glycerin/                one page per ingredient
  /properties/, /properties/humectant/
  /label-decoder/           full label breakdown and compare (scripts/decoder.py, src/decoder.js)
  /plans/                   hair plans (content/guide-*.json)
  /about/                   how we write, sources, affiliate disclosure
  /data/ingredients.json    the published data (JARA copies this nightly)
```

To publish a sheet change right away: **Actions → Build and publish → Run workflow**. Otherwise it goes live overnight.

If a download fails or a sheet comes back empty, the job stops and the live site stays as it was.

## The sheets

Columns are read by name, so adding columns never breaks the build.

**Ingredient database:** `id` (never changes), `inci_name`, `common_name`, `category`, `property_tag` (comma-separated), `what_it_does`, `hair_type_porosity_fit` (shown as "Notes for different hair"), `buildup_sensitivity_notes` (shown as "Good to know"), `aliases_also_listed_as` (comma-separated).
Optional, understood when present:
- `slug`: freezes the page address (e.g. `glycerin`). Without it the address comes from the page title, so renaming an ingredient would move its page.
- `source`: e.g. `own research` or `Open Beauty Facts` (shown on the page; Open Beauty Facts data is share-alike).
- `hair_type_notes`: used instead of `hair_type_porosity_fit` if you rename that column.
- `display_name`: the name used for the page title, lists and the address (e.g. Glycerin).
- `featured`: `yes` on up to six rows picks the ingredients shown on the homepage's Ingredients door. Without it, the door shows one standout per job (strength, water binders, slip, softness, hold), skipping basics and rows with claim-like wording.

**Programs Overview** (`data/programs.csv`) and **Program steps** (`data/program-steps.csv`): the hair plans at `/plans/` and `data/plans.json`. Until the repository secrets `PROGRAMS_CSV_URL` and `PROGRAM_STEPS_CSV_URL` exist, the copies saved in `data/` are used. Program steps columns: `program_id, order, step, when, weeks, wash_day_role, property, condition, product_ids, notes`, where `when` is `every_wash`, `every_7_days` (any number), `daily`, `nightly` or `weeks` (with `weeks` like `3,6`; `0` means before you start). Optional overview columns: `slug`, `version`, `image` (a file in `src/img/`).

**Product catalog:** only `kind`, `brand`, `name`, `step` and `full ingredient list` are used, to show where an ingredient sits on real labels. Links, notes and prices are not published.

Every build prints a report (in the Action's summary): how many label words are recognised, the most common label words that have no ingredient row yet, and wording that could read as a hair-growth or drug claim. The report never changes any text.

## Similar labels on product pages

Every product page lists up to three catalog products whose labels are built the same way (`scripts/similar.py`). Products are compared only with others at the same step, and only when both labels have been read (5+ ingredients). Each pair is checked on five things: for shampoos, the main cleanser (strength and kind), conditioning agents, water binders, protein and oils; for everything else, slip and conditioning agents, water binders, protein, oils or butters, and silicones. A match needs 3 of 5 to be the same, and shampoos must also share the strength of their main cleanser. Each match shows what is the same and what is different, plus a link to the side-by-side compare. Words are sorted with the Label Decoder's own categories, so the two always agree. `data/catalog.json` lists each product's matches under `similar`. Prices are not used.

## Run it locally

```
# put ingredients.csv and catalog.csv in data/ (download from the published links)
python3 scripts/build.py
cd _site && python3 -m http.server 8000   # open http://localhost:8000
```

## Look and feel

Styles are in `src/site.css` and follow The Good Coil: paper `#F8F7F2`, ink `#432731`, cobalt `#2548D7`, citrus `#DCF473`, blue mist `#DCE6F0`; Manrope with Instrument Serif italic. Page templates live in `scripts/build.py`.

## Test: full programs at /programs/

`content/programs-full.json` holds the full Signature Care Programs (Intensive Care Collection), transcribed from the owner's original document. `scripts/programs_full.py` builds `/programs/` and `/data/programs-full.json`. These pages carry `noindex`, aren't in the menu or the sitemap, and don't touch `/plans/` or `data/plans.json`. Edit the JSON file to change the content; product examples use catalog ids (e.g. `TGC-063`).

## Full Label Decoder at /label-decoder/

Paste a list or pick a product: every ingredient is sorted into detailed categories (kinds of cleanser and silicone, humectants, oils vs butters vs esters, proteins, amino acids, peptides, ceramides, bond builders, film-formers, preservatives including parabens, formaldehyde releasers and isothiazolinones, fragrance allergens, essential oils, phthalates, drying alcohols, PEGs, coconut-derived, wheat/barley/rye/oat and more), highlighted on the label and explained row by row. "Compare labels" puts two or three side by side (strongest cleanser, water binders, protein, oils, slip and so on, with where each first appears). Sheet rows come first; name patterns in `scripts/decoder.py` (RULES) sort everything else, so adding a pattern needs no sheet work. Links can be shared: `#t=<list>`, `#p=<product>`, `#compare=p:<product>~t:<list>`.

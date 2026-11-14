# The Good Coil Ingredients

Source for **ingredients.thegoodcoil.com**: a library of hair-care ingredients, each described by what it is and what it does. It's part of [The Good Coil](https://thegoodcoil.com) and feeds [JARA](https://itsjara.com).

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
ingredients.thegoodcoil.com
  /                         search + list of every ingredient
  /glycerin/                one page per ingredient
  /properties/, /properties/humectant/
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

**Programs Overview** (`data/programs.csv`) and **Program steps** (`data/program-steps.csv`): the hair plans at `/plans/` and `data/plans.json`. Until the repository secrets `PROGRAMS_CSV_URL` and `PROGRAM_STEPS_CSV_URL` exist, the copies saved in `data/` are used. Program steps columns: `program_id, order, step, when, weeks, wash_day_role, property, condition, product_ids, notes`, where `when` is `every_wash`, `every_7_days` (any number), `daily`, `nightly` or `weeks` (with `weeks` like `3,6`; `0` means before you start). Optional overview columns: `slug`, `version`, `image` (a file in `src/img/`).

**Product catalog:** only `kind`, `brand`, `name`, `step` and `full ingredient list` are used, to show where an ingredient sits on real labels. Links, notes and prices are not published.

Every build prints a report (in the Action's summary): how many label words are recognised, the most common label words that have no ingredient row yet, and wording that could read as a hair-growth or drug claim. The report never changes any text.

## Run it locally

```
# put ingredients.csv and catalog.csv in data/ (download from the published links)
python3 scripts/build.py
cd _site && python3 -m http.server 8000   # open http://localhost:8000
```

## Look and feel

Styles are in `src/site.css` and follow The Good Coil: paper `#F8F7F2`, ink `#432731`, cobalt `#2548D7`, citrus `#DCF473`, blue mist `#DCE6F0`; Manrope with Instrument Serif italic. Page templates live in `scripts/build.py`.

# The Good Coil Library — roadmap

Last updated 15 November 2026.

**Live at library.thegoodcoil.com.** Rebuilds nightly from the owner's Google Sheets, or on demand from Actions → Build and publish → Run workflow.

| | Now |
|---|---|
| Ingredients | 74, each with a page |
| Products | 126, plus 12 tools |
| Labels read | 34 of 126 products (27%) |
| Label words recognised | 349 of 730 (48%) |
| Hair plans | 3 |
| Pages | ~300 |

Sections are ordered by what blocks what, not by size. **Owner** means it needs Naima's words or data; **Claude** means it's build work.

---

## 1. Before sharing the site widely

Five things. Everything else can happen after people are already reading.

| | Who | Size |
|---|---|---|
| **Display names.** Paste `display_name` and `slug` into the ingredient sheet from `display-names-suggested.csv`. Until then pages read "Aqua", "Parfum", "Paraffinum Liquidum". This is the most visible problem on the site. | Owner | 20 min |
| **Review the claim-flagged wording.** The build report lists them every night: ING-015, 025, 029, 044, 045, 046, 049, 050, plus the category name "Scalp & Follicle Active". These sit on public pages and in the plans. | Owner | 1 hour |
| **Decide the growth wording** on plan pages: serum rows and the "what to look for" headings. Three options were set out on 15 Nov. | Owner | a decision |
| **Read the parts of the plans Claude wrote**, not from your documents: the "why it happens" section on all three plans, the eight low-tension styles, and the troubleshooting rows on growth and moisture. | Owner | 1 hour |
| **Fix the glycerin dew-point line** (ING-008 says "40–70% dew point"; dew point is a temperature). | Owner | 2 min |

---

## 2. The sheets: data that makes the site better

Roughly in order of payoff per hour spent.

- [ ] **Add the common missing ingredients.** The top misses are silicones (dimethicone, amodimethicone), sodium hydroxide, propanediol, avocado oil, sunflower oil, rosemary extract, sodium laureth sulfate, sodium C14-16 olefin sulfonate, glycol distearate, caprylyl glycol, dehydroacetic acid, isopropyl alcohol, coumarin, benzyl salicylate. Each one lifts the recognition rate on every label at once. — *Owner*
- [ ] **Keep typing ingredient lists.** 34 of 126 products. Every label added makes the decoder, the product pages and the "found in these products" sections better. — *Owner, ongoing*
- [ ] **Add a `source` column** (own research / Open Beauty Facts). Every page currently says "The Good Coil research" because there is nothing else to read. Open Beauty Facts data is share-alike, so this matters once any of it is used. — *Owner*
- [ ] **Add `evidence` and `why_it_works` columns.** Then the evidence labels on plan pages come from the sheet instead of being written into the code, and ingredient pages can show them too. — *Owner, then Claude*
- [ ] **Add a `featured` column**, `yes` on up to six rows, to choose what the homepage shows. — *Owner*
- [ ] **Rewrite the porosity column.** `hair_type_porosity_fit` shows on pages as "Notes for different hair", and it is still full of verdicts: "gold-standard", "essential", "great for". — *Owner*
- [ ] **Tag the 38 products with no properties**, so they appear in property filters and in plan product rows. — *Owner*
- [ ] **Fill the catalog gaps the plans exposed:** no edge controls at all, nothing satin or silk, one scalp serum, one scalp cleanser. — *Owner*
- [ ] **Merge the 52-product affiliate shelf** from thegoodcoil.com (`src/data/products.ts`) into the catalog sheet. 21 match by name; about 30 need new rows. — *Owner, with Claude's match list*
- [ ] **Tag products by plan job** (gentle cleanser, scalp serum, deep conditioner, lipid, bond, protein, low-tension accessory), so plan product rows fill themselves. — *Owner*

---

## 3. Build work

### Soon
- [ ] **Four style cards with photos** on the Edge Growth Plan, replacing eight. Needs four images. — *Owner images, Claude build*
- [ ] **Shop links on product pages**, with the affiliate disclosure on every page that carries one. Ingredient pages stay link-free. Needs a decision first. — *Owner decision, Claude build*
- [ ] **Social preview image and touch icons.** Right now a shared link has no picture. — *Claude*
- [ ] **"Find your product" on the homepage**, so the first option is searching the catalog rather than pasting a label. The owner doubts many people will paste; product pages already decode their labels, so most of the work is done. — *Claude*

### Later
- [ ] Fold the week grid from the old program pages back into the plans, once it can be done without crowding them.
- [ ] A printable version of each plan.
- [ ] Ingredient pages: show the evidence label once the sheet has one.
- [ ] Product photos. Only with permission; Open Beauty Facts images need attribution.
- [ ] Ratings. Only if the "no scores, no verdicts" promise is rewritten. If it happens: rate products, not ingredients; publish the method; keep ratings away from affiliate links. Results from JARA users would need a privacy policy change first.

---

## 4. Decisions waiting

1. **Growth wording** on plan pages (above).
2. **Plan names.** "Edge Growth Plan" is kept. "Mega growth and retention" and "Deep moisture and protein" are still rewrites of the document names.
3. **Shop links on product pages:** yes or no.
4. **Reference guides.** Send two or three guides you like and the next design pass can start from a shape you have already judged.

---

## 5. JARA (separate track)

Nothing here blocks the library, and the library does not block JARA until the plans are final.

- [ ] **Push the JARA roadmap update.** Drafted 14 Nov, not pushed, because JARA's repo syncs to Lovable. It records the library's address, what it publishes, and what the plans will need.
- [ ] **Lovable prompt, database only** (updated 15 Nov): `plan_enrollments` (plan id and version, variant such as core or maintenance, round number, the person's choices, previous enrollment, start and end, status including paused, one current plan per person, paid-access RLS like `saved_routines`); `plan_id` and `plan_version` on `saved_routines`; `catalog_id` on `products`. Send once the plans are settled.
- [ ] **Then, without Lovable credits:** nightly copy of the library's published JSON; plan preview and "Start this plan"; a reminder per step; "Week 3 of 8" on Week; check-ins with 1–5 scores; photo milestones; week-8 paths and history; "What's inside" on Stash products.
- [ ] **Later:** ticking off daily habits needs a log table.

**Note on data shape:** the library publishes `catalog.json` with the products inside a wrapper (`{generated, source, products: [...]}`), while JARA's own `src/data/catalog.json` is a bare list with the same field names. The copy job has to unwrap it. Until that job exists, JARA's copy is a manual export and can go stale.

---

## 6. How it fits together

```
Google Sheets (master)          GitHub Action, nightly
 ├─ Ingredient database  ──┐    1. download both CSVs
 ├─ Product catalog ───────┤ →  2. python3 scripts/build.py
 └─ (plans live in the repo,    3. publish to GitHub Pages
     content/guide-*.json)              ↓
                            library.thegoodcoil.com
                              /                 homepage + label decoder
                              /ingredients/     74 pages
                              /products/        126 pages
                              /plans/           3 guides
                              /properties/, /about/
                              /data/*.json  ──→ JARA copies these nightly (not built yet)
                              /test-program/    earlier layouts, kept for reference
```

Plan content lives in `content/guide-*.json` in this repo, not in a sheet. Moving it to Sheets is possible but has not been worth it while the wording is still changing.

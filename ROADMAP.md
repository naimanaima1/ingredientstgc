# Roadmap: The Good Coil library (ingredients.thegoodcoil.com)

Owner's Google Sheets are the master copies. The site rebuilds nightly (or via Actions → Run workflow).
JARA work is listed at the end and waits until the programs are settled.

## Size check (Nov 14)
Today: 69 pages, 1.4 MB (two photos are 220 KB of that), builds in half a second.
At 75 ingredients + 200 products: about 300 pages, roughly 4–5 MB, builds in 1–2 seconds. GitHub Pages allows 1 GB, so size is not a concern. The products list page would be about 60 KB, and search stays instant in the browser.
The real work is data entry: product ingredient lists (19 of 138 have one today) and new ingredient rows.

## 1. Now (small, before sharing any links)
- [ ] **Names people actually use.** Add a `display_name` column to the ingredient sheet (page title, list name, address), e.g. Glycerin, Panthenol, Biotin, Mineral Oil, Aloe Vera, Mango Extract. The current `common_name` column has descriptions mixed in ("Vegetable Glycerin", "Pro-Vitamin B5", "Vitamin B7", "Organic Mango Fruit Extract"). Fallback when blank: common name without the bracket.
- [ ] **Freeze addresses.** Add a `slug` column (e.g. `glycerin`) at the same time, so renaming never moves a page.
- [ ] **Decide the address:** ingredients.thegoodcoil.com vs library.thegoodcoil.com. Then add the Hostinger DNS record and the GitHub custom domain.
- [ ] **"Found in these products"** on ingredient pages: rename the "Across labels" section and link each product to its product page (needs 2).

## 2. Products (next build)
- [ ] `/products/`: a simple list of every catalog product (search, filter by step: cleanse, condition, leave-in, style, seal, treatment, tools).
- [ ] One page per product: name, brand, step, properties, and "What's inside" (the label decoded, each ingredient linked) when its ingredient list exists; otherwise "Ingredient list coming soon".
- [ ] Decide: shop links on product pages? If yes, affiliate disclosure on every product page (ingredient pages stay link-free).
- [ ] Merge the website's 52-product shelf (src/data/products.ts) into the catalog sheet: 21 match by name; about 30 need a row (long Amazon titles, combos, satin and silk accessories, tools, "Coming Soon" placeholders to skip).
- [ ] Owner: tag products by program function (gentle cleanser, scalp serum, deep conditioner, ceramide/lipid, bond, protein, low-tension accessories), as the programs document suggests.

## 3. Ingredient coverage (owner data entry, any time)
- [ ] Add the most common label words with no row yet: water/aqua, phenoxyethanol, ethylhexylglycerin, potassium sorbate, sodium benzoate, benzyl alcohol, cetearyl alcohol, behentrimonium methosulfate, polyquaternium-10/-37, tocopherol, shea butter, olive oil, fragrance/parfum, and the fragrance allergens (limonene, linalool, hexyl cinnamal, amyl cinnamal, citronellol).
- [ ] Add the program ingredients: green tea/EGCG, caffeine, niacinamide, hydrolyzed keratin, silk and rice proteins, fatty acids, cationic polymers.
- [ ] Add `evidence` (Established practice / Promising / Emerging / Cosmetic support) and `why_it_works` columns, so ingredient pages and program pages share one source.
- [ ] Optional `source` column (own research / Open Beauty Facts).
- [ ] Fill product ingredient lists toward 50% of the catalog.
- [ ] Review wording flagged by the build report (ING-015, 025, 029, 044, 045, 046) and the glycerin "dew point" line.

## 4. Programs (iterate page by page)
- [x] Test pages at `/programs/` from the original Intensive Care Collection document (noindex, unlinked). `/plans/` stays as the earlier version.
- [ ] Resolve the flags: Mega's bond weeks (2 and 6 vs 3 and 6) and lipid cadence (weekly vs weeks 2 and 5); mismatched evidence labels (ceramides, panthenol, hydrolyzed proteins); Edge name (Edge Growth Plan vs Edge Recovery); Deep Moisture pillar explanations; reference links.
- [ ] Owner edits, page by page.
- [ ] Product picks: replace the draft examples; add a scalp serum with the program's ingredients; add night-protection items to the catalog.
- [ ] Third photo for Deep Moisture.
- [ ] Move the content from `content/programs-full.json` into sheet tabs (layout drafted Nov 14) so it's edited in Sheets.
- [ ] Launch: `/programs/` replaces `/plans/` (redirect), added to the menu and sitemap, noindex removed.
- [ ] Printable version of each program.

## 5. Label decoder
- [ ] On the library home page: paste a label, get every ingredient matched, grouped by property and explained. No verdicts.

## 6. JARA (after programs are settled, since they decide the database)
- [ ] Lovable, database only: `plan_enrollments` (plan id and version, version name "core" or "maintenance", round number, each person's choices, start/end, status, one active per person, paid-access RLS like saved_routines); `plan_id` and `plan_version` on saved_routines; `catalog_id` on Stash products.
- [ ] Claude, no credits: nightly copy of the published JSON; plan preview and "Start this program"; reminders per step; "Week 3 of 8" on Week; check-ins with 1–5 scores (hair_checkins.answers); photo milestones; week 8 paths and history; "What's inside" on Stash products.
- [ ] Later: ticking off daily habits (needs a log table).

## Later
- Product or ingredient ratings: only if the "no scores, no verdicts" promise is rewritten; rate products, not ingredients; publish the method; JARA results need a privacy policy change.
- Product images: only with permission (Open Beauty Facts photos need attribution).

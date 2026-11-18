# Ingredient families: target map (owner's list, 17 Nov)

This is the full set of families we want eventually. "Live" = a family page exists today.
Rows needed = what the sheet must hold before the page can be written. Nothing here is built
until the rows are reviewed.

## What your hair needs
| Family | Live? | Notes |
|---|---|---|
| Hydration (water + humectants) | No | Overlaps Humectants. Decide: one family or two. |
| Moisture (emollients, oils, butters) | No | Oils & Butters page. |
| Protein | Yes | Add the amino-acid and "updated protein blend" angle. Stretch test lives here. |
| Ceramides | No | Ceramide NP / AP / EOP exist (ING-022/023/024). |
| Lipids | No | Needs rows: Cholesterol, Phospholipids, Hydrogenated Lecithin, Glycosphingolipids, Phytosphingosine (ING-026 exists), Jojoba Esters (ING-037 exists). Ceramides are one kind of lipid. |

## Cleansing
| Family | Live? | Notes |
|---|---|---|
| Sulfate cleansers | Part of Surfactants & Cleansers | SLS ING-083, SLES ING-084. |
| Sulfate-free cleansers | Part of Surfactants & Cleansers | Needs a strength dial: mild (isethionate, taurate, glucosides, betaine) vs stronger anionic non-sulfates. |
| Chelators | Part of Surfactants & Cleansers | Citric acid ING-021 exists; EDTA row missing. |

Row needed: **Sodium C14-16 Olefin Sulfonate** (not a sulfate, a stronger anionic cleanser; used in
Design Essentials Honey Creme). Also worth adding: Sodium Cocoyl Isethionate, Decyl Glucoside,
Lauryl Glucoside, Sodium Cocoyl Glutamate, Disodium Laureth Sulfosuccinate, Sodium Lauroyl Sarcosinate.
Suggested sheet column for the dial: `cleanser_strength` = mild / moderate / strong, with a source or
formulator note for each. We will not label a whole shampoo gentle or harsh from one ingredient.

Winter / Moisture edits: you want shampoos with the milder cleansers (the "SEHT" style). Hold until
the cleanser rows and the strength dial exist, then the edit can say which cleanser to look for.

## Styling and protection
Silicones (live) · Humectants (glycerin, honey, aloe, panthenol, sorbitol; honey and sorbitol rows missing)
· Film formers (polyquaternium, PVP, gels) · Heat protectant (one row today: ING-004).

## Conditioning
Conditioning agents for slip: BTMS ING-055, behentrimonium chloride ING-001, cetrimonium chloride
ING-002, polyquaternium-10. Fatty alcohols are live under Alcohols.

## Scalp and repair
Peptides (live) · Scalp actives (live). Missing rows: salicylic acid, ketoconazole, zinc pyrithione.

## Peptide vs protein vs bond repair: keep them separate
- **Peptide** = a type of molecule. sh-Oligopeptide-78 (K18's proprietary peptide). Row missing.
- **Bond repair** = a claimed function or technology. Bis-Aminopropyl Diglycol Dimaleate (Olaplex).
  Row missing.
- **Protein** = e.g. Hydrolyzed Wheat Protein (ING-004), Laurdimonium Hydroxypropyl Hydrolyzed
  Barley Protein (row missing).
A formula can hold several (K18 mask: sh-Oligopeptide-78 and hydrolyzed wheat protein). The page must
say a result for one technology does not transfer to the whole category.

## Rows to add to the Ingredient Database (list for tonight)
Sodium C14-16 Olefin Sulfonate · Cholesterol · Phospholipids · Hydrogenated Lecithin ·
Glycosphingolipids · Laurdimonium Hydroxypropyl Hydrolyzed Barley Protein · sh-Oligopeptide-78 ·
Bis-Aminopropyl Diglycol Dimaleate · Sorbitol · Honey · EDTA · Salicylic Acid · Ketoconazole ·
Zinc Pyrithione · Sodium Cocoyl Isethionate · Decyl Glucoside.

## Build order suggestion
1. Cleansers: strength dial + olefin sulfonate (the note on the page is live now).
2. Ceramides & Lipids (rows mostly there).
3. Conditioning Agents, Humectants, Film formers, Heat protectant.
4. Peptides vs protein vs bond repair explainer.
5. Hydration / Moisture / "What your hair needs" quiz-style page.

## Ingredients that belong in two families (18 Nov)

Rule: **an ingredient can be listed in every family where it does real work, but it has one "home" family.**
- The home page tells the full story. The other page shows it as a short row with a link ("See Ceramides for how these fit together").
- The build already allows this: `linked_inci_ids` can repeat an ID across families (today: fatty alcohols, polyquats, phytosphingosine, squalane, creatine, gluconolactone).
- Pick the home by *what the ingredient does to the hair*, not where it is applied. Examples: Cetearyl alcohol -> Conditioning Agents (Alcohols page explains fatty vs drying). Polyquaterniums -> Film Formers. Squalane -> Lipids. Creatine -> Bond Builders (also listed under Proteins so people looking for protein find it). Gluconolactone -> Humectants (Scalp Actives and Chelators link back).
- Peptides vs Scalp Actives: peptides stay on the Peptides page; Scalp Actives only lists a peptide if it is used for scalp care, with a link.

## Pages to prep next

**Bond Builders** (sheet row GRP-017, ING-017/018/019, K18 peptide on Peptides). Best as one explainer: protein vs peptide vs bond builder, who each suits. Needs: ING-018/019 ingredient pages checked, one product example each.

**Antioxidants** (new family, not in the sheet yet). Candidates already in the database: Tocopherol (ING-066), Camellia Sinensis / green tea (ING-049), Rosemary leaf extract (ING-091). Likely missing: ascorbic acid and derivatives, ferulic acid, resveratrol, BHT. Keep the copy to what they do in a formula (protect oils and the formula from going off; skin-care antioxidant role) and avoid growth or "anti-ageing for hair" claims until reviewed. Green tea and rosemary keep Scalp Actives as a second home.

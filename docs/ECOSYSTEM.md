# The Good Coil ecosystem: one path, three sites

## The path (what every page points to)
Quiz (thegoodcoil.com) -> Your result + matching Hair Plan (library) -> Products and ingredients (library) -> Track it in JARA (itsjara.com)

| Site | Job | The one action |
|---|---|---|
| thegoodcoil.com | Discover your hair. Sell the $5-$25 guides. | Take the Hair Quiz (https://thegoodcoil.com/routine-builder) |
| library.thegoodcoil.com | The quiz's next step: plan, products, ingredients | Save the plan to JARA |
| itsjara.com | Keep the record | Try JARA |

Library destinations: My Hair Plans, Product Finder, Ingredient Guide (nav labels: Label Decoder, Ingredients, Products, Hair Plans + Take Hair Quiz).
All three sites carry the 32px top bar: The Good Coil | Ingredient Library | JARA Hair Tracker.

## UTM rules
`utm_source` = the site the link is on (library, goodcoil, jara). `utm_medium` = where on the page (utility_bar, nav_cta, plan_cta, plan_resource, quiz_results, footer, home_banner, label_decoder). `utm_campaign` = the goal (jara_beta, routine_quiz, ecosystem, ebook, jara_freebie). `utm_content` = plan or section. The library does this already (see `B.utm` in scripts/build.py).

## Email system (set up once in one provider; every form sends a `source` tag)
| Entry | Tag | First email | Next action |
|---|---|---|---|
| Routine Quiz result | quiz_result + hair profile | Your routine + your plan link | Open the plan, then "Try JARA" |
| Free JARA tracker | jara_freebie | The printable + how to start | Day 3: try JARA free (log last wash day) |
| Wash and Go Guide ($10) | buyer_washngo | Download + receipt | Day 2: the matching plan; Day 5: JARA |
| JARA purchase | jara_buyer | Welcome + how to log a first wash day | Day 7: monthly photo reminder |
| Library "save this plan" click | none (link only) | n/a | n/a |
Rules: one next step per email, same price everywhere, unsubscribe in every email, buyers stop getting sales emails for what they own.

## Product ladder
$0 quiz + Library -> $5 art / $10 guide (trust, a quick win, never competes with the app) -> $19 JARA (the habit) -> later ($29 web, $39 iOS).
Studio artwork gets its own page so it is not mixed in with hair tools.

## Prompt for the Hostinger AI (thegoodcoil.com)
Paste this as-is:

> I run three connected sites: thegoodcoil.com (this one), library.thegoodcoil.com and itsjara.com. Please make this site the "discover" front door of one simple path: Routine Builder quiz -> Library hair plan -> Products and ingredients -> Track in JARA. Keep our brand: warm paper background (#F8F7F2), ink text (#432731), cobalt buttons (#2548D7), citrus accent (#DCF473), blue mist (#DCE6F0), Manrope for text and Instrument Serif italic for big headlines. Lots of whitespace, pill-shaped buttons, no popups on first load.
> 1. Add a 32px bar at the very top of every page with three links: "The Good Coil" -> https://thegoodcoil.com, "Ingredient Library" -> https://library.thegoodcoil.com?utm_source=goodcoil&utm_medium=utility_bar&utm_campaign=ecosystem, "JARA Hair Tracker" -> https://itsjara.com?utm_source=goodcoil&utm_medium=utility_bar&utm_campaign=jara_beta.
> 2. Homepage order: (a) hero with one main button, "Take Your Hair Quiz" (it goes to https://thegoodcoil.com/routine-builder); (b) two short lines on our approach; (c) "Discover your hair": featured quizzes; (d) "Your hair routine": introduce the Library with a button to https://library.thegoodcoil.com?utm_source=goodcoil&utm_medium=home_section&utm_campaign=library; (e) "Track your progress": introduce JARA with a "Try JARA" button to https://itsjara.com?utm_source=goodcoil&utm_medium=home_section&utm_campaign=jara_beta; (f) "Hair-care resources": ebooks and a link to Studio; (g) real reviews only (leave this out until we have real ones); (h) a final JARA call to action.
> 3. Quiz results: show the hair profile first. Then ask for email to send the full routine plus the link to the matching Library hair plan. On the confirmation view show two cards: "Master Your Styling: The Wash & Go Guide ($10)" -> https://thegoodcoil.com/wash-and-go-guide and "Track Your Results in JARA" -> https://itsjara.com/try?utm_source=goodcoil&utm_medium=quiz_results&utm_campaign=jara_beta. Save the email with a tag "source=quiz_result" and the hair profile answers.
> 4. Create a "Studio" page and menu link for all $5-$25 artwork. Remove artwork cards from the quiz and ebook pages. If checkout allows it, add a $5 wallpaper order bump checkbox at the $10 ebook checkout.
> 5. After every ebook purchase, the confirmation page and email should link to one next step: the matching Library plan, then JARA.
> 6. Use the same prices everywhere: JARA is $19 right now instead of $39; keep that out of buttons (they just say "Try JARA") and state it once, on the JARA page. Do not add countdowns, fake stock or invented reviews.
> Show me the changes before publishing, and tell me if any of this is not possible with Hostinger.

## JARA checkout review (read-only; nothing in JARA was changed)
What is fine: hosted Stripe Checkout, one line item, buyer email prefilled, no extra fields, cancel returns to /unlock, "try first, pay to keep" (/try).
Fix before pushing paid traffic:
1. **No payment webhook.** A purchase is only saved when the buyer comes back to /unlock?session_id=... If someone pays and closes the tab, Stripe has the money but JARA has no purchase row. Add a Stripe `checkout.session.completed` webhook that writes the same row.
2. **Duplicate purchase prevention is client-side only.** The page redirects paid users, but `createCheckout` does not check for an existing purchase. Add a server check.
3. **Price story** (confirmed): $19 now instead of $39; $29 for the public web release later; $39 on iOS. Only the JARA page needs to show this. Update the live checkout text ("regular $39") when the public release price changes.
4. **Stripe product name** is "JARA Hair Journal — lifetime access". You asked to drop "lifetime" from copy; this name shows on the receipt.
5. **Receipts and recovery.** No receipt email or abandoned-checkout follow-up in code. Turn on Stripe receipts, and send one email to people who started checkout and did not pay.
6. **UTMs are not saved.** Store utm_* at sign-up and pass them to Stripe `metadata`, so you can see which site and button produced each sale.
7. **Access delivery** looks right (redirects to /week or /welcome after confirm). Could not test mobile checkout live from here.

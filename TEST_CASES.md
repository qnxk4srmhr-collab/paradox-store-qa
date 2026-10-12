# Test cases: Paradox store and shopping cart

**System under test:** https://www.paradoxinteractive.com/our-games (live production)
**User:** guest (no account, no login)
**Explored on:** 11 October 2026, desktop viewport 1366x850 and narrow viewport (~580 px), locale en-US

## Approach

- **Prioritisation** is based on risk to revenue and to the player. Anything that stops a player getting a product into the cart, or shows them a wrong total, is High.
- **No fixed products or prices.** Catalog content changes weekly, so every case picks its product at runtime ("the first product on the On Sale page that has an Add to cart button") and compares prices *between pages* instead of against hardcoded values.
- **Live-site rules respected.** No purchases, no payment details, no accounts. "Proceed to checkout" is only checked for presence and enabled state, never clicked.
- **Automation choice.** I automate the cases that protect the core buying path, are stable against changing data, and are cheap to run. Cases that need human judgement, depend on content rules, or currently fail because of a known bug stay manual for now.

## Summary

| ID | Title | Area | Type | Priority | Automate |
|---|---|---|---|---|---|
| CAT-01 | Search returns matching products | Catalog | Positive | High | Core (flow 1) |
| CAT-02 | Search with no matches shows the empty state | Catalog | Negative | Medium | Stretch |
| CAT-03 | Brand filter shows only that brand and is kept in the URL | Catalog | Positive | High | Core |
| CAT-04 | Product type and OS filters narrow the results | Catalog | Positive | Medium | Manual |
| CAT-05 | Sorting by price, low to high, orders the results | Catalog | Positive | Medium | Stretch |
| PDP-01 | Buy page shows name, price, platform and an enabled Add to cart | Product page | Positive | High | Core (in flow 1) |
| PDP-02 | Discounted product shows consistent pricing | Product page | Positive | Medium | Stretch |
| PDP-03 | "Buy now" on the product info page opens the buy page with that item | Product page | Positive | Low | Manual |
| PDP-04 | Age-restricted product shows an age gate, and its rating carries through to the cart | Product page / Cart | Positive, negative, edge | High | Manual (fails, BUG-01, BUG-03) |
| ADD-01 | Adding from a listing tile updates the header cart counter | Add to cart | Positive | High | Core (flow 2) |
| ADD-02 | Item added from the buy page appears in the cart with the same name and price | Add to cart | Positive | High | Core (flow 1) |
| ADD-03 | An item already in the cart cannot be added twice | Add to cart | Edge | Medium | Stretch |
| ADD-04 | Tile "Add to cart" works with keyboard and on narrow screens | Add to cart | Edge / a11y | Medium | Manual (fails, BUG-04, BUG-05) |
| CART-01 | Cart summary adds up and checkout is available | Cart | Positive | High | Core (flow 3) |
| CART-02 | Removing the only item shows the empty cart state | Cart | Positive | High | Core (flow 4) |
| CART-03 | Removing one of two items updates the list, counter and totals | Cart | Positive | High | Stretch (flow 4) |
| CART-04 | Cart contents persist after a page reload | Cart | Positive | High | Core (flow 5) |
| CART-05 | Invalid promo code shows an error and leaves totals unchanged | Cart | Negative | Medium | Manual (fails, BUG-02) |
| CART-06 | "Continue shopping" and "Go to all games" return to the catalog | Cart | Positive | Low | Manual |
| CART-07 | Cart warns when items overlap (season pass plus an add-on it contains) | Cart | Edge | Low | Manual (fails, BUG-07) |

**Legend:** Core = automated in this submission. Stretch = good automation candidate, added if time allows. Manual = kept manual, reason given in the case.

### Mapping to the required automated flows

| Required flow | Covered by |
|---|---|
| 1. Find a product with search or a filter, then add it to the cart | CAT-01 + PDP-01 + ADD-02 (one end-to-end test) |
| 2. Header cart counter updates after adding | ADD-01 |
| 3. Subtotal minus discount equals total | CART-01 |
| 4. Remove an item, cart updates or shows the empty state | CART-02 (CART-03 as stretch) |
| 5. Cart contents persist after reload | CART-04 |

---

## Catalog

### CAT-01: Search returns matching products
**Priority:** High. Search is the fastest route to a purchase; if it breaks, players can't find what they came for.
**Automate:** Core. Part of required flow 1. Stable because the search term is taken from the live catalog at runtime.
**Preconditions:** Guest user, All games page open, cookie banner dismissed.

**Steps**
1. Open `/our-games/all-games`.
2. Note one distinctive word from the title of a listed product (manual: use "Stellaris").
3. Type that word into the Search field.

**Expected result**
- The URL contains `Search=<term>`.
- At least one product card is shown, and every card title contains the search term (case-insensitive).
- "Showing X of Y" is shown, with Y lower than the unfiltered total.

---

### CAT-02: Search with no matches shows the empty state
**Priority:** Medium. A blank or broken page on a failed search looks like an outage, but it doesn't block buying.
**Automate:** Stretch. Cheap and fully stable: a nonsense term never matches real products.
**Preconditions:** Guest user.

**Steps**
1. Open `/our-games/all-games?Search=qwxzqwxz`.

**Expected result**
- "Sorry, no products to show" is displayed.
- "Showing 0 of 0" is displayed.
- No product cards are shown and no error is shown.
- The Search field contains `qwxzqwxz` and "Clear all (1)" is available.

---

### CAT-03: Brand filter shows only that brand and is kept in the URL
**Priority:** High. Most players shop by franchise; a wrong filter hides products they want to buy.
**Automate:** Core. Can be checked through each card's brand data, so it doesn't depend on specific titles.
**Preconditions:** Guest user, All games page open.

**Steps**
1. Click **Filter**.
2. Tick one brand checkbox (manual: "Europa Universalis").
3. Click **Done**.
4. Reload the page.

**Expected result**
- After step 3, the URL contains `Brand=<brand>` and every card belongs to that brand.
- "Showing X of Y" reports a count lower than the unfiltered total.
- After the reload in step 4, the brand filter is still applied and the same results are shown.

---

### CAT-04: Product type and OS filters narrow the results
**Priority:** Medium. Wrong results here mislead players (for example a Mac user buying a Windows-only DLC), but the product page still shows platform info.
**Automate:** Manual. Checking OS compatibility needs each product's platform data, which the listing cards don't expose; verifying it means opening many product pages.
**Preconditions:** Guest user, All games page open.

**Steps**
1. Click **Filter** and tick Product type **DLC**. Click **Done**.
2. Open three results and check their product type.
3. Clear filters. Tick OS compatibility **macOS**. Click **Done**.
4. Open three results and check the supported platforms on their pages.
5. Tick both **DLC** and **macOS** together.

**Expected result**
- Step 2: every opened product is a DLC.
- Step 4: every opened product lists macOS as supported.
- Step 5: the count is equal to or lower than either filter alone, and results satisfy both conditions.

---

### CAT-05: Sorting by price, low to high, orders the results
**Priority:** Medium. Wrong sorting is confusing for bargain hunters, but players can still find products.
**Automate:** Stretch. Stable: it checks the order of whatever prices are live today.
**Preconditions:** Guest user, All games page open.

**Steps**
1. Select **Price - Low to High** in the sort menu.
2. Read the price of every card that shows a price.
3. Repeat with **Price - High to Low**.

**Expected result**
- The URL contains `sort=price_low` (then `sort=price_high`).
- Priced cards are in ascending order (then descending order).
- Cards without a price (Coming soon, free items) are grouped together and don't interrupt the ordering of priced cards.

---

## Product page

> Note: each product has an info page (`/games/<game>`) and a buy page (`/games/<game>/buy?item=<SKU>`). Price, discount, platform and "Add to cart" are on the **buy page**, so that's what "product page" means in these cases.

### PDP-01: Buy page shows name, price, platform and an enabled Add to cart
**Priority:** High. This is where most add-to-cart actions happen.
**Automate:** Core. Covered inside the flow 1 test.
**Preconditions:** Guest user, empty cart.

**Steps**
1. Open any purchasable product's info page from the All games list.
2. Click **Buy now**.
3. Find the selected product on the buy page.

**Expected result**
- The product name matches the card that was opened.
- A price is shown, in the same currency as the listing.
- A platform or key type is shown (for example "Steam key").
- The **Add to cart** button is visible and enabled.

---

### PDP-02: Discounted product shows consistent pricing
**Priority:** Medium. Wrong sale prices damage trust and can create pricing or legal issues.
**Automate:** Stretch. Stable: the product is picked from the On Sale page at runtime and the check is arithmetic.
**Preconditions:** Guest user, at least one product on sale.

**Steps**
1. Open `/our-games/on-sale`.
2. Open the buy page for the first product that has a single price (not "From ...").
3. Read "Was" price, discount percentage and sale price.

**Expected result**
- "Was" price is higher than the sale price.
- Sale price equals Was × (1 − discount %), within 0.01 for rounding.
- The sale price matches the price on the listing card from step 1.

---

### PDP-03: "Buy now" on the product info page opens the buy page with that item
**Priority:** Low. Players can still reach the buy page through the game's main page.
**Automate:** Manual. Low risk, and it's already exercised indirectly by the flow 1 test.
**Preconditions:** Guest user.

**Steps**
1. Open any add-on's info page, for example from the On Sale list.
2. Click **Buy now**.

**Expected result**
- The buy page opens with the **Add-ons** tab selected.
- The URL contains `item=<SKU of that add-on>`.
- That add-on is shown in the list with an enabled **Add to cart** button.

---

### PDP-04: Age-restricted product shows an age gate, and its rating carries through to the cart
**Priority:** High. Age ratings are a legal and platform compliance requirement (PEGI, USK, ESRB). Letting under-age visitors through is a compliance risk; wrongly blocking adults loses sales.
**Automate:** Manual for now. Currently fails (BUG-01, BUG-03). Needs a known age-restricted product, and which products are gated isn't exposed on the listing, so runtime selection is unreliable. The automated tests still handle the gate if it appears (adult date of birth), so they don't break on gated products.
**Preconditions:** Guest user, fresh browser session (no previous age confirmation), empty cart. An age-restricted product is known (one with a high age rating).

**Steps**
1. Open the age-restricted product's info page.
2. Enter a date of birth that makes the visitor **under** the required age and confirm.
3. Start a new session. Open the same page and enter an invalid date (for example a future date, or 31 February).
4. Start a new session. Open the same page and enter a date of birth that makes the visitor **over** the required age.
5. Open other pages of the same product (buy page, add-ons) and reload.
6. Add the product to the cart and open the cart.
7. In the same session as step 2 (after the under-age refusal), go to a listing and add the same product with its tile **Add to cart** button.

**Expected result**
- Step 1: an age gate asking for the date of birth is shown **before** any product content (trailers, screenshots, description).
- Step 2: access is refused with a clear, translated message (no raw string keys); no product content is shown.
- Step 3: the date is rejected with a validation message; no access is granted.
- Step 4: the product page is shown.
- Step 5: the confirmation is remembered for the session; the gate doesn't reappear on every page.
- Step 6: the cart line shows the **same** age rating icon and content descriptors (for example "Bad Language") as the product page.
- Step 7: the product can't be added after an under-age declaration, or the quick add triggers the same age check.

**Actual today:** step 2 shows the raw key `General.ageGate.sorry` (BUG-03), and step 7 adds the game to the cart (BUG-01).

**Notes:** the rating system shown (PEGI, USK, ESRB) depends on the visitor's region, so this is also worth repeating by region (see "Age ratings by region" under "What I'd test next").

---

## Adding to cart

### ADD-01: Adding from a listing tile updates the header cart counter
**Priority:** High. The counter is the player's only confirmation that the click worked.
**Automate:** Core. Required flow 2. The product is picked at runtime.
**Preconditions:** Guest user, empty cart, desktop viewport.

**Steps**
1. Open `/our-games/on-sale`.
2. Hover over the first product card that has an Add to cart button.
3. Click **Add to cart**.

**Expected result**
- Before step 3, the header cart link is named "View cart" with no count.
- After step 3, the header shows **1** and the link is named "View cart, 1 item".
- The counter updates without a page reload.

---

### ADD-02: Item added from the buy page appears in the cart with the same name and price
**Priority:** High. A mismatch between what the player chose and what's in the cart means a wrong order.
**Automate:** Core. End of required flow 1.
**Preconditions:** Guest user, empty cart.

**Steps**
1. Find a product using search (CAT-01) and open its buy page.
2. Note the product name and price.
3. Click **Add to cart**.
4. Click the header cart icon.

**Expected result**
- After step 3, the button changes to **Added to cart** and the counter shows 1.
- The cart shows "1 item" with exactly one line.
- The line's name and price match the values noted in step 2.

---

### ADD-03: An item already in the cart cannot be added twice
**Priority:** Medium. Digital keys are one per account; a duplicate would be a wasted purchase and a refund request.
**Automate:** Stretch. Stable, uses any purchasable product.
**Preconditions:** Guest user, one item already in the cart.

**Steps**
1. Open the buy page of the item that's already in the cart.
2. Look at its button.
3. Go back to the listing and click its tile **Add to cart** again (if available).
4. Open the cart.

**Expected result**
- Step 2: the button reads **Added to cart**.
- Step 4: the item appears once, the header counter still shows 1, and the subtotal hasn't changed.

---

### ADD-04: Tile "Add to cart" works with keyboard and on narrow screens
**Priority:** Medium. Affects keyboard users and mobile shoppers. They can still add from the buy page, so it isn't a blocker.
**Automate:** Manual. Currently fails (BUG-04, BUG-05); automate once a fix is agreed.
**Preconditions:** Guest user, empty cart.

**Steps**
1. Desktop: open `/our-games/on-sale`. Use only the **Tab** key to move through the first product card.
2. Resize the window to about 580 px wide (or open on a phone) and look at the same card.

**Expected result**
- Step 1: keyboard focus reaches the card's **Add to cart** button, and pressing Enter adds the item.
- Step 2: an **Add to cart** control is visible and usable on the card, or the card clearly leads to a page where the item can be added.

---

## Cart

### CART-01: Cart summary adds up and checkout is available
**Priority:** High. A wrong total is the most damaging bug a store can show: lost sales, complaints and legal risk.
**Automate:** Core. Required flow 3. Uses a sale item so the discount is not zero; amounts are read from the page, never hardcoded.
**Preconditions:** Guest user, empty cart, at least one product on sale.

**Steps**
1. Add one discounted product (from On Sale) and one full-price product to the cart.
2. Open the cart.
3. Read each line's original and current price, then Subtotal, Discount and Total.

**Expected result**
- Subtotal = sum of the lines' original prices.
- Discount = sum of (original − current) for discounted lines, shown as a negative amount.
- Total = Subtotal − Discount = sum of the lines' current prices (all within 0.01).
- All amounts use the same currency.
- **Proceed to checkout** is visible and enabled (not clicked).

---

### CART-02: Removing the only item shows the empty cart state
**Priority:** High. Players must be able to correct their cart; a stuck item blocks checkout.
**Automate:** Core. Required flow 4.
**Preconditions:** Guest user, exactly one item in the cart.

**Steps**
1. Open `/our-games/cart`.
2. Click **Remove `<product name>` from cart** (the bin icon).

**Expected result**
- A "Removed product from cart" confirmation appears.
- "Your cart is empty" and "Have a look at our games to add items to your cart." are shown, with a **Go to all games** link.
- The summary and **Proceed to checkout** are no longer shown.
- The header cart link is named "View cart" with no count.

---

### CART-03: Removing one of two items updates the list, counter and totals
**Priority:** High. Partial removal is common, and totals must recalculate correctly.
**Automate:** Stretch. Extends required flow 4.
**Preconditions:** Guest user, two different items in the cart.

**Steps**
1. Open the cart and note the Subtotal and Total.
2. Remove the first item.

**Expected result**
- Only the second item remains; the heading reads "1 item".
- The header counter shows 1.
- Subtotal and Total each drop by exactly the removed item's original and current price.
- The summary still adds up (as in CART-01).

---

### CART-04: Cart contents persist after a page reload
**Priority:** High. Losing the cart on refresh or when returning to the site loses sales.
**Automate:** Core. Required flow 5.
**Preconditions:** Guest user, empty cart.

**Steps**
1. Add two items to the cart.
2. Open the cart and note the item names, Subtotal and Total.
3. Reload the page.
4. Navigate to another store page and back to the cart.

**Expected result**
- After steps 3 and 4, the same two items are shown, with the same Subtotal and Total.
- The header counter still shows 2.

---

### CART-05: Invalid promo code shows an error and leaves totals unchanged
**Priority:** Medium. Doesn't block buying, but unclear feedback causes confusion and support tickets.
**Automate:** Manual for now. Currently fails (BUG-02). Once fixed, it's a good automation candidate.
**Preconditions:** Guest user, one item in the cart.

**Steps**
1. Open the cart and note the Total.
2. Type `NOTAREALCODE123` into the promo code field.
3. Press Enter.

**Expected result**
- A clear, fully translated error message is shown (for example "Invalid promo code"), with no raw string keys, and it's announced to screen readers.
- The message uses the same term as the field ("promo code", not "voucher").
- The entered code stays in the field so the player can correct it.
- Discount and Total are unchanged.

---

### CART-06: "Continue shopping" and "Go to all games" return to the catalog
**Priority:** Low. Players can always use the main navigation.
**Automate:** Manual. Low risk; a plain link check.
**Preconditions:** Guest user.

**Steps**
1. With one item in the cart, open the cart and click **Continue shopping**.
2. Empty the cart and click **Go to all games**.

**Expected result**
- Both links open `/our-games/all-games`.
- After step 1, the header counter still shows 1 (navigating away doesn't clear the cart).

---

### CART-07: Cart warns when items overlap
**Priority:** Low. Rare, but means paying twice for the same content.
**Automate:** Manual. Depends on which bundles and season passes exist, which changes over time.
**Preconditions:** Guest user, empty cart. A season pass or bundle exists, together with an add-on it includes.

**Steps**
1. Add an individual add-on to the cart (for example a BATTLETECH expansion).
2. Add the season pass that already includes it.
3. Open the cart.

**Expected result**
- The cart warns that one item is already included in another, or prevents the overlap.

**Actual today:** both items are added with no warning (BUG-07).

---

## What I'd test next with more time

### Automated check for raw localization keys
Two untranslated string keys turned up in one short session: `toast.invalid_voucher` (BUG-02) and `General.ageGate.sorry` (BUG-03). A cheap automated check could trigger the main messages (toasts, errors, age gate) in every store language and fail if any visible text looks like a string key, such as `word.word_word`.

### Region, currency and VPN use
The store appears to set the currency from the visitor's location. I'd run the cart tests from a few regions, using a VPN or a Playwright proxy per region, and add two cases:

**Switching region mid-session keeps the cart consistent** (Medium: VPN use is common among PC players, and a mixed currency means wrong totals)
1. With region A active, add an item and note the currency and total.
2. Switch to region B, which uses a different currency.
3. Reload the cart, then open the listing again.

Expected: one currency throughout, line prices match region B's listing (or a notice explains the change), the summary adds up, and nothing is duplicated or lost.

**Prices from a cheaper region can't be carried over** (High for the business: some players use a VPN to buy in a cheaper currency)
1. With a VPN set to a cheaper region, add an item and note the price.
2. Switch to a more expensive region, or turn the VPN off.
3. Reload the cart and continue as far as checkout allows in a test environment.

Expected: the cart re-prices to the current region. At checkout, the price is validated against the billing country, and keys are region-locked where required. This needs a staging environment with test payments, since checkout is out of scope on the live site.

### Age ratings by region
The rating system depends on the visitor's region (USK in Germany, PEGI in most of Europe, ESRB in North America), and the minimum age for the same game can differ. I'd repeat PDP-04 from several regions and check that the gate uses the minimum age of the rating shown, the rating matches on product page and cart, and switching region doesn't leave a cart item with the wrong rating.

### Other areas
- **Mobile viewport:** the whole buying path on a phone-sized screen (header, filter panel, cards, cart).
- **Second browser:** run the suite in Firefox or WebKit as well as Chromium.
- **Network-level checks:** compare the Commerce Layer cart API (`paradox.commercelayer.io/api/orders/<id>`) with what the cart page shows.
- **Edition choice:** for multi-edition games ("From ..." prices), the chosen edition and price reach the cart.
- **Accessibility pass:** the whole path with a screen reader, beyond BUG-04 and BUG-06.
- **Pagination:** "View 20 more" with filters and sorting applied, with no duplicates, gaps or order changes.

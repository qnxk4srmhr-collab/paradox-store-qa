# Note: assumptions, what I'd test next, bugs found

Gerry, QA take-home for Paradox Tinto, 11–12 October 2026.
Details are in [TEST_CASES.md](TEST_CASES.md) (test scenarios), [BUGS.md](BUGS.md) (bug reports) and [README.md](README.md) (automation: setup, how to run, design decisions).

## Assumptions

- **Scope:** the public store under `/our-games` (listings, product and buy pages, cart), used as a **guest**. No accounts, no login.
- **Live production:** no purchases and no payment details. "Proceed to checkout" is only checked for being visible and enabled. Tests run one at a time, without retries, and only on demand. The store does rate-limit heavy use (I hit HTTP 429 once), which confirms that care was needed.
- **Changing data:** the catalogue, sales and prices change weekly, so no test depends on a specific product or price. Products are picked at runtime and values are compared between pages (listing, buy page, cart).
- **Environment:** desktop Chromium at 1366×850 with the English store. The narrow screen (~580 px) and the Chinese (beta) store were explored manually but aren't automated.
- **Cart:** the cart is identified by an order ID in the browser's localStorage and stored in Commerce Layer, so a fresh browser always starts with an empty cart.
- **Age gate:** the automation answers it with an adult date of birth. Under-age behaviour is covered by a manual case (PDP-04).
- **Priorities:** risk to revenue and to the player. Anything that stops a product reaching the cart, or shows a wrong total, is High.
- **Known bugs aren't automated as passing tests.** Cases that currently fail stay manual until the bug is fixed.

## What I'd test next with more time

1. **Raw localization keys everywhere.** Three turned up in two days (BUG-02, BUG-03, BUG-10). I'd add a build-time check that every key the code uses exists in the translation files, plus a UI scan of messages, toasts and gates in each store language.
2. **BUG-09 (cart losing an item).** Reproduce it with network throttling, ideally on a staging environment, and add network-level checks that compare the Commerce Layer order with what the cart page shows.
3. **Regions and currency.** Run the cart tests from several regions (VPN or a proxy per region), including switching region mid-session and making sure cheaper-region prices can't be carried over.
4. **Age ratings by region:** the gate's minimum age and the rating shown on the product page and in the cart, for PEGI, USK and ESRB regions.
5. **Mobile, second browser, accessibility:** the buying path on a phone-sized screen, Firefox or WebKit, and a screen-reader pass.
6. **Remaining automation candidates:** CART-03 (remove one of two items), ADD-03 (no duplicates), CAT-05 (price sort), CAT-02 (empty search), PDP-02 (discount maths).

The full lists are in [TEST_CASES.md](TEST_CASES.md#what-id-test-next-with-more-time) and the README's "What I'd add next".

## Bugs found

| ID | Bug | Severity |
|---|---|---|
| BUG-01 | Age gate allows adding to cart after an under-age date of birth (tile quick-add skips the check) | High |
| BUG-02 | Invalid promo code shows the raw key `toast.invalid_voucher` (the translation exists; the lookup is wrong) | Medium |
| BUG-03 | Age gate refusal shows the raw key `General.ageGate.sorry` (no translation exists) | Medium |
| BUG-04 | Tile "Add to cart" can't be reached with the keyboard | Medium |
| BUG-05 | No tile "Add to cart" on narrow or mobile screens | Low |
| BUG-06 | All tile "Add to cart" buttons share the same accessible name | Low |
| BUG-07 | No warning when cart items overlap (season pass plus an add-on it includes) | Low |
| BUG-08 | Minor polish: cart page title, label casing, trailing space in product data | Trivial |
| BUG-09 | **Suspected:** the cart can silently lose an item after opening another page | High if confirmed |
| BUG-10 | Removing a creator referral code shows the raw key `removed_referal_code` | Low |

**Found through the automation work:** BUG-09 came from a test that failed intermittently. Instead of adding a retry, I logged the network calls and caught the store deleting a cart line on its own (Playwright trace in `evidence/`). BUG-10 came from comparing the translation keys in the store's scripts with its translation data, using files already captured during testing, and was then confirmed on screen. Screenshots and the trace are in [evidence/](evidence/).

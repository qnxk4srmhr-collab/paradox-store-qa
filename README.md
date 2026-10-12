# Paradox store QA: test cases, bug reports and automation

Take-home for the Experienced QA Analyst role at Paradox Tinto. The system under test is the live Paradox Interactive store, https://www.paradoxinteractive.com/our-games, used as a guest.

| File | What it is |
|---|---|
| [TEST_CASES.md](TEST_CASES.md) | Test cases, prioritised by risk, each marked Core / Stretch / Manual for automation |
| [BUGS.md](BUGS.md) | Bugs and UX issues found, with steps, expected and actual results |
| [evidence/](evidence/) | Screenshots and a Playwright trace backing up the bug reports |
| `tests/`, `pages/`, `utils/` | Automated tests (Python, pytest, Playwright) |

Automation built with help from Claude Code; exploration, test design and bug reports are my own, and I reviewed every file.

## Setup on a clean machine

You need **Python 3.10 or newer** and git.

```bash
git clone <this repository's URL>
cd paradox-store-qa
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium      # Linux CI: playwright install --with-deps chromium
```

The virtual environment (`.venv`) keeps the project's packages separate from the rest of the machine. Activate it again in every new terminal before running the tests.

## Running the tests

```bash
pytest                          # all tests, about 30 seconds
pytest -v                       # one line per test, with its name
pytest tests/test_cart.py       # one file
pytest -k cart01                # tests whose name contains "cart01"
pytest -k cart01 --headed --slowmo 500   # watch it in a visible browser, half a second per step
```

Tests run **one at a time and are never retried**. See "Design decisions" for why.

### Report, screenshots and traces

Every run writes **`reports/report.html`**, a single self-contained file. Open it in any browser:

```bash
open reports/report.html        # macOS; on Windows: start reports\report.html
```

For each **failed** test the report shows the error, a **screenshot** of the page at the moment it failed, and a **Trace** link. The trace is saved under `test-results/<test name>/trace.zip` and replays the whole test step by step, with screenshots, the page structure and every network call:

```bash
playwright show-trace test-results/<test name>/trace.zip
```

Passed tests keep no trace, to save space. `reports/` and `test-results/` are git-ignored.

### Running in GitHub Actions (CI)

The workflow in [.github/workflows/tests.yml](.github/workflows/tests.yml) runs the same suite on a clean GitHub-hosted Linux machine, following the setup steps above.

It **only runs when started by hand**, never on push or on a schedule, because the tests use the live store. To start it: open the repository's **Actions** tab, choose **Store tests**, then **Run workflow**. When it finishes, download the **test-report** artifact from the run's page. It holds `reports/report.html` and, for failed tests, their traces.

## What's automated

| Test | Test cases | Required flow |
|---|---|---|
| `test_flow1_search_then_add_from_the_buy_page` | CAT-01, PDP-01, ADD-02 | 1. Find a product with search, add it to the cart |
| `test_add01_adding_from_a_tile_updates_the_header_counter` | ADD-01 | 2. Header cart counter updates |
| `test_cart01_summary_adds_up_and_checkout_is_available` | CART-01 | 3. Subtotal − discount = total |
| `test_cart02_removing_the_only_item_shows_the_empty_cart` | CART-02 | 4. Remove an item, empty state |
| `test_cart04_cart_contents_persist_after_reload_and_navigation` | CART-04 | 5. Cart persists after reload |
| `test_store_opens_with_an_empty_cart` | (smoke) | Quick check that the store and setup work |

What each test checks, in short:

- **Flow 1:** searches with a word taken from a live product title; the URL holds the search and every result contains the word. Opens a result's info page, follows its "Buy now", checks the buy page shows price, platform and an enabled Add to cart, with the same price as the listing. Adds it: the button becomes a disabled "Added to cart", the header shows 1, and the cart holds exactly that product at that price.
- **ADD-01:** adds an On sale item from its listing tile; the header goes from "View cart" to "View cart, 1 item" without a reload.
- **CART-01:** with one discounted and one full-price item: subtotal = sum of original prices, discount = total savings (shown negative), total = subtotal − discount = sum of current prices, one currency throughout, and "Proceed to checkout" is visible and enabled.
- **CART-02:** removing the only item shows "Your cart is empty" with its message and "Go to all games" link, hides the summary and checkout, and resets the header.
- **CART-04:** after a reload, and after leaving through "Continue shopping" and returning through the header cart link, the same items, subtotal, total and header count are shown.

## Project structure

```
conftest.py            fixtures: browser settings, cookie consent, pop-up handling, screenshot on failure
pytest.ini             base URL, report and trace options
.github/workflows/     GitHub Actions workflow (manual trigger only)
requirements.txt       exact package versions
pages/                 page objects: one class per page or component, holding its selectors
  header.py            header cart link and its item count
  catalog_page.py      All games / On sale listings, search
  product_card.py      one product tile on a listing
  product_info_page.py product info page and its "Buy now" link
  buy_page.py          buy page and one product on it
  cart_page.py         cart lines, summary, empty state
utils/
  cookie_banner.py     declines the OneTrust cookie banner
  age_gate.py          enters an adult date of birth if a product asks
  money.py             turns "19.99 EUR" into whole cents plus currency
  navigation.py        opens a page and fails fast on HTTP errors such as 429
tests/                 the tests, named after the test case IDs
evidence/              screenshots and a trace for the bug reports
```

Tests only describe *what* happens ("add the first available product", "check the header shows 2"). *How* to find things on the page lives in the page objects, so every selector is written once.

## Design decisions

**Products are chosen at runtime, never hardcoded.** The catalogue and prices change weekly. Each test picks "the first product on this page that has an Add to cart button" (or the first full-price one, or the first result of a search), remembers it by its SKU, and compares values *between pages* (listing → buy page → cart) instead of against fixed numbers. The search word is the longest word of a live product's title. Prices are read with their currency from the page; the tests never assume one.

**Selectors use roles, accessible names and test attributes.** For example the header link "View cart, 2 items", "Remove <product> from cart", and the `data-testid` (SKU) on product tiles. No generated CSS class names (like `ProductCard_product-card__wHKx0`), which change with every site build. The one exception is the cart summary: its rows have no labels, roles or test IDs, so the page object finds the label text ("Subtotal") and reads the element next to it. That lives in one method, so a markup change means a one-line fix.

**No fixed sleeps.** Every wait is for a condition: Playwright's `expect(...)` retries until the condition is true (5 seconds by default), and actions wait for elements to be ready. The store loads several things in two stages (cart lines and buy page items first show "undefined", then the real name; tile buttons appear after the tiles), so tests wait for the *exact product name* or for a matching element, never for time.

**Every test starts with an empty cart.** pytest-playwright creates a fresh browser context, like a new private window, for every test. The cart is identified by an order ID in localStorage, and a fresh context has none, so no clean-up code is needed and tests can't affect each other.

**Cookie banner.** It appears a moment after page load, at an unpredictable time. If it pops up between a hover and a click, it breaks the hover-only tile button (this happened during development). So a session fixture declines it **once per run** through the real banner, keeps only OneTrust's consent cookies, and gives them to every test's fresh context. A Playwright *locator handler* stays as a safety net and clicks Decline if the banner shows up anyway. Decline is the privacy-preserving choice.

**Age gate.** Some age-rated products ask for a date of birth first. Which ones isn't known in advance, so a locator handler enters an adult date (1 Jan 1990) whenever the "Enter your birth date" gate appears.

**Hover-only "Add to cart" on tiles.** The tile button is `display: none` until the mouse is over the card, and never appears on narrow screens (BUG-05). Tests use a desktop viewport (1366×850), hover the card, then click the button **inside that card**. All tile buttons share the name "Add to cart" (BUG-06), so a page-wide lookup would hit the wrong one.

**One worker, no retries.** This is a live production store with real customers. Tests run one at a time (plain pytest; no parallel plugin installed) and failures are not retried (no retry plugin installed). A retry would also hide intermittent problems instead of exposing them: see BUG-09. Please don't run the suite in a loop.

**Never checkout.** "Proceed to checkout" is only checked for being visible and enabled, never clicked. No accounts, no logins, no payment details.

## Known issues and limitations

- **CART-01 and CART-04 can fail intermittently because of a suspected store bug (BUG-09).** Both tests add an item, open a second page and add another. In some runs the store deleted the existing cart line by itself while the new page was loading the cart. The tests fail with a message naming BUG-09 rather than retrying. Evidence, including a Playwright trace, is in [BUGS.md](BUGS.md#bug-09-suspected-cart-can-silently-lose-an-item-after-opening-another-page).
- **The store rate-limits heavy use.** After many runs in a short time it answers **HTTP 429 Too Many Requests**. Tests then fail straight away with a message saying so. Wait a while before running again.
- **Each run creates real guest carts** on the production store's cart service (Commerce Layer). They're abandoned and contain no personal data, but on a real team I'd run this suite against a staging environment, or agree it with the site owners.
- **Desktop Chromium only.** Mobile can't use tile quick-add (BUG-05), and no second browser is configured yet.
- **English store only.** Tests read English text such as "Showing 20 of 446" and "Your cart is empty".
- **Known bugs aren't automated as passing tests.** For example the invalid promo code test (CART-05) stays manual until BUG-02 is fixed.

## What I'd add next

- **CAT-03 brand filter:** pick a brand from the live filter list, check every result's `data-ga_brand` matches, and that the filter survives a reload.
- **Stretch cases from TEST_CASES.md:** CART-03 (remove one of two items), ADD-03 (no duplicates), CAT-05 (price sort order), CAT-02 (empty search), PDP-02 (discount maths on the buy page).
- **Network checks:** wait for the Commerce Layer order response (`GET /api/orders/<id>`) and compare its line items and totals with what the cart page shows.
- **Mobile viewport** for the cart-only tests, and a **second browser** (Firefox or WebKit).

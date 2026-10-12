import pytest

from utils.age_gate import pass_age_gate_when_shown
from utils.cookie_banner import decline_cookies, decline_cookies_when_shown
from utils.navigation import open_url


@pytest.fixture(scope="session")
def cookie_consent(browser, base_url):
    """Decline the cookie banner once per run and keep the consent cookies.

    The banner appears a moment after page load, at an unpredictable time. If it
    pops up in the middle of a hover and click, it breaks the hover-only
    "Add to cart" button. So we answer it once, here, and start every test
    with the answer already given.

    We keep only OneTrust's own cookies (names starting with "Optanon"), nothing
    else, so each test still starts with an empty cart.
    """
    context = browser.new_context(locale="en-US")
    page = context.new_page()
    open_url(page, f"{base_url}/our-games/all-games")
    decline_cookies(page)
    consent_cookies = [c for c in context.cookies() if c["name"].startswith("Optanon")]
    context.close()
    return {"cookies": consent_cookies, "origins": []}


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, cookie_consent):
    """Settings for every browser context (pytest-playwright creates a new one per test).

    A desktop-sized window, because the product tiles only show their
    "Add to cart" button on hover, which doesn't happen on narrow screens.
    English locale, because the tests read English text such as "Showing X of Y".
    The saved cookie consent, so the banner doesn't appear.
    """
    return {
        **browser_context_args,
        "viewport": {"width": 1366, "height": 850},
        "locale": "en-US",
        "storage_state": cookie_consent,
    }


@pytest.fixture(autouse=True)
def handle_popups(page):
    """Runs before every test.

    Declines the cookie banner if it still shows up for any reason, and gets past
    the age gate with an adult date of birth if an age-restricted product asks.
    """
    decline_cookies_when_shown(page)
    pass_age_gate_when_shown(page)

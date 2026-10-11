import pytest

from utils.cookie_banner import decline_cookies_when_shown


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Settings for every browser context (pytest-playwright creates a new one per test).

    A desktop-sized window, because the product tiles only show their
    "Add to cart" button on hover, which doesn't happen on narrow screens.
    English locale, because the tests read English text such as "Showing X of Y".
    """
    return {
        **browser_context_args,
        "viewport": {"width": 1366, "height": 850},
        "locale": "en-US",
    }


@pytest.fixture(autouse=True)
def handle_cookie_banner(page):
    """Runs before every test: dismiss the cookie banner whenever it appears."""
    decline_cookies_when_shown(page)

from playwright.sync_api import expect


def _cookie_banner(page):
    return page.get_by_role("region", name="Cookies and targeting")


def decline_cookies(page):
    """Click "Decline" on the OneTrust cookie banner and wait until it's gone."""
    banner = _cookie_banner(page)
    banner.get_by_role("button", name="Decline", exact=True).click()
    expect(banner).to_be_hidden()


def decline_cookies_when_shown(page):
    """Safety net: if the banner ever appears during a test, decline it.

    A "locator handler" makes Playwright check for the banner before every
    click or assertion, and run this first if the banner is visible.
    """
    banner = _cookie_banner(page)
    page.add_locator_handler(banner, lambda: decline_cookies(page))

def decline_cookies_when_shown(page):
    """Click "Decline" on the OneTrust cookie banner whenever it appears.

    The banner shows up a moment after the page loads, and not on every page,
    so we can't just click it once at the start. Instead we register a
    "locator handler": before every click or assertion, Playwright checks
    whether the banner is visible and, if it is, runs this handler first.
    """
    banner = page.get_by_role("region", name="Cookies and targeting")
    decline = banner.get_by_role("button", name="Decline", exact=True)
    page.add_locator_handler(banner, lambda: decline.click())

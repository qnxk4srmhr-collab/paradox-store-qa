import re

from playwright.sync_api import expect


class Header:
    """The site header, shown on every store page."""

    def __init__(self, page):
        # The link's accessible name carries the item count:
        # "View cart", "View cart, 1 item", "View cart, 2 items".
        self.cart_link = page.get_by_role("link", name=re.compile(r"^View cart"))

    def expect_cart_count(self, count, message=None):
        """Check the header cart link reports `count` items (0 means an empty cart).

        `message` replaces Playwright's default failure text, for checks where a
        plain "expected X, got Y" wouldn't explain what went wrong.
        """
        if count == 0:
            expected_name = "View cart"
        elif count == 1:
            expected_name = "View cart, 1 item"
        else:
            expected_name = f"View cart, {count} items"
        expect(self.cart_link, message).to_have_accessible_name(expected_name)

import re


class Header:
    """The site header, shown on every store page."""

    def __init__(self, page):
        # The link's accessible name carries the item count:
        # "View cart", "View cart, 1 item", "View cart, 2 items".
        self.cart_link = page.get_by_role("link", name=re.compile(r"^View cart"))

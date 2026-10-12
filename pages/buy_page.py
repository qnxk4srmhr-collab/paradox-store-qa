import re

from utils.money import MONEY_PATTERN, parse_money


class BuyPageItem:
    """One product on the buy page: type, name, price, platform and its Add to cart button."""

    def __init__(self, root):
        self.root = root
        # The current price is a paragraph holding just the amount, e.g. "24.99 EUR".
        self.price = root.get_by_role("paragraph").filter(has_text=MONEY_PATTERN)
        # How the game is delivered, e.g. "Steam key".
        self.platform = root.get_by_text(re.compile(r"\bkey\b", re.IGNORECASE))
        self.add_to_cart_button = root.get_by_role("button", name="Add to cart", exact=True)
        self.added_to_cart_button = root.get_by_role("button", name="Added to cart", exact=True)

    def current_price(self):
        return parse_money(self.price.inner_text())


class BuyPage:
    """The buy page, for example /games/stellaris/buy?tab=add-ons&item=<SKU>.

    It lists many products, each with its own Add to cart button, and also
    contains hidden buttons for the other tab. Role locators skip hidden
    elements, so we only ever see the visible tab.
    """

    def __init__(self, page):
        self.page = page

    def item(self, product_name):
        # Each product is a list item with a link named after it. The name (and price)
        # arrive a moment after the item appears, so finding the item by its exact
        # name also waits for it to finish loading.
        name_link = self.page.get_by_role("link", name=product_name, exact=True)
        return BuyPageItem(self.page.get_by_role("main").get_by_role("listitem").filter(has=name_link))

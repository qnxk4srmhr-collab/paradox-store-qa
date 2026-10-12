from utils.money import MONEY_PATTERN, parse_money


class ProductCard:
    """One product tile on a listing page (an <li> with data-testid="<SKU>")."""

    def __init__(self, root):
        self.root = root
        self.title = root.get_by_role("heading")
        # Every tile's button has the same name, so we only ever look inside this card.
        self.add_to_cart_button = root.get_by_role("button", name="Add to cart")
        # The tile's prices: the current one first, then the struck-through original if on sale.
        self.prices = root.get_by_text(MONEY_PATTERN)
        self.link = root.get_by_role("link").first

    def sku(self):
        return self.root.get_attribute("data-testid")

    def brand(self):
        # The franchise the product belongs to, e.g. "Age of Wonders". It matches
        # the names of the Brand checkboxes in the filter.
        return self.root.get_attribute("data-ga_brand")

    def current_price(self):
        return parse_money(self.prices.first.inner_text())

    def page_url(self):
        """Address of the product's info page.

        We read the link instead of clicking it: hovering the tile shows the
        Add to cart overlay, which covers the title link.
        """
        return self.link.get_attribute("href")

    def add_to_cart(self):
        # The button is hidden (display: none) until the mouse is over the card.
        self.root.hover()
        self.add_to_cart_button.click()

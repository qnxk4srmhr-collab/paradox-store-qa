from utils.navigation import open_url


class ProductInfoPage:
    """A product's info page, for example /games/stellaris/add-ons/stellaris-nomads.

    It has no price and no Add to cart, only "Buy now" links to the buy page.
    """

    def __init__(self, page):
        self.page = page

    def open(self, url):
        open_url(self.page, url)

    def buy_now_link(self, sku):
        # The page can have several "Buy now" links (header, related products).
        # The one we want points to the buy page with this product selected: ...buy?...&item=<SKU>
        return self.page.get_by_role("link", name="Buy now").and_(
            self.page.locator(f'[href*="item={sku}"]')
        ).first

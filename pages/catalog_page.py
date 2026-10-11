import re

from pages.product_card import ProductCard


class CatalogPage:
    """Product listing pages: All games and On sale."""

    ALL_GAMES_URL = "/our-games/all-games"
    ON_SALE_URL = "/our-games/on-sale"

    def __init__(self, page):
        self.page = page
        # Each product tile is an <li> whose data-testid is the product's SKU.
        # That attribute is meant for tests, so it's more stable than the generated class names.
        self.product_cards = page.locator("li[data-testid]")
        # "Showing 20 of 446"
        self.results_summary = page.get_by_text(re.compile(r"^Showing \d+ of \d+$"))

    def open_all_games(self):
        self.page.goto(self.ALL_GAMES_URL)

    def open_on_sale(self):
        self.page.goto(self.ON_SALE_URL)

    def first_card_with_add_to_cart(self):
        """Pick the first tile that has an "Add to cart" button, whatever product it is today.

        Not every tile has one (multi-edition games, Coming soon and free items don't).
        The button is hidden until hover, so we include hidden elements when searching.
        """
        self.product_cards.first.wait_for()
        hidden_button = self.page.get_by_role("button", name="Add to cart", include_hidden=True)
        cards_with_button = self.product_cards.filter(has=hidden_button)
        assert cards_with_button.count() > 0, "No product on this page has an Add to cart button"

        # Remember the card by its SKU, so we keep pointing at the same product
        # even if the list re-renders or changes order.
        sku = cards_with_button.first.get_attribute("data-testid")
        return ProductCard(self.page.get_by_test_id(sku))

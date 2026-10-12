import re

from pages.product_card import ProductCard
from utils.navigation import open_url


class CatalogPage:
    """Product listing pages: All games and On sale."""

    ALL_GAMES_URL = "/our-games/all-games"
    ON_SALE_URL = "/our-games/on-sale"

    def __init__(self, page):
        self.page = page
        # Each product tile is an <li> whose data-testid is the product's SKU.
        # That attribute is meant for tests, so it's more stable than the generated class names.
        self.product_cards = page.locator("li[data-testid]")
        self.product_titles = self.product_cards.get_by_role("heading")
        # "Showing 20 of 446"
        self.results_summary = page.get_by_text(re.compile(r"^Showing \d+ of \d+$"))
        # The box has no visible label; its accessible name comes from the placeholder "Search".
        self.search_box = page.get_by_role("searchbox", name="Search")

    def open_all_games(self):
        open_url(self.page, self.ALL_GAMES_URL)

    def open_on_sale(self):
        open_url(self.page, self.ON_SALE_URL)

    def search(self, term):
        # Results update as you type (no Enter needed) and the term is added to the URL.
        self.search_box.fill(term)

    def first_card_with_add_to_cart(self, full_price_only=False):
        """Pick the first tile that has an "Add to cart" button, whatever product it is today.

        Not every tile has one (multi-edition games, Coming soon and free items don't).
        The button is hidden until hover, so we include hidden elements when searching.
        With full_price_only=True, discounted tiles are skipped: they carry a
        screen-reader label "original price:" next to the struck-through price.
        """
        hidden_button = self.page.get_by_role("button", name="Add to cart", include_hidden=True)
        cards = self.product_cards.filter(has=hidden_button)
        if full_price_only:
            cards = cards.filter(has_not_text="original price")

        # The buttons are added to the tiles a moment after the tiles appear,
        # so wait for a matching tile instead of counting straight away.
        cards.first.wait_for(state="attached")

        # Remember the card by its SKU, so we keep pointing at the same product
        # even if the list re-renders or changes order.
        sku = cards.first.get_attribute("data-testid")
        return ProductCard(self.page.get_by_test_id(sku))

    def add_first_available_product_to_cart(self, full_price_only=False):
        """Add the first product that has an Add to cart button, and return its name."""
        card = self.first_card_with_add_to_cart(full_price_only)
        product_name = card.title.inner_text()
        card.add_to_cart()
        return product_name

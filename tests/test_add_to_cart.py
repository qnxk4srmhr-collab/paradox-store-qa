from pages.catalog_page import CatalogPage
from pages.header import Header


def test_add01_adding_from_a_tile_updates_the_header_counter(page):
    """ADD-01 (required flow 2): add an On sale item from its tile; the header counter goes to 1."""
    catalog = CatalogPage(page)
    header = Header(page)
    catalog.open_on_sale()
    header.expect_cart_count(0)

    card = catalog.first_card_with_add_to_cart()
    card.add_to_cart()

    # No reload in between: the counter must update on its own.
    header.expect_cart_count(1)

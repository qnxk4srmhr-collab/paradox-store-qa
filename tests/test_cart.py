from playwright.sync_api import expect

from pages.cart_page import CartPage
from pages.catalog_page import CatalogPage
from pages.header import Header


def test_cart02_removing_the_only_item_shows_the_empty_cart(page):
    """CART-02 (required flow 4): remove the only item; the empty cart state is shown."""
    catalog = CatalogPage(page)
    cart = CartPage(page)
    header = Header(page)

    # Setup: exactly one item in the cart.
    catalog.open_on_sale()
    product_name = catalog.add_first_available_product_to_cart()
    header.expect_cart_count(1)  # also makes sure the add is saved before we leave the page

    cart.open()
    expect(cart.lines).to_have_count(1)
    cart.remove(product_name)

    expect(cart.empty_heading).to_be_visible()
    expect(cart.empty_message).to_be_visible()
    expect(cart.go_to_all_games_link).to_be_visible()
    expect(cart.lines).to_have_count(0)
    expect(cart.summary_heading).to_be_hidden()
    expect(cart.checkout_button).to_be_hidden()
    header.expect_cart_count(0)

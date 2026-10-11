from playwright.sync_api import expect

from pages.cart_page import CartPage
from pages.catalog_page import CatalogPage
from pages.header import Header
from utils.money import assert_same_amount


def test_cart01_summary_adds_up_and_checkout_is_available(page):
    """CART-01 (required flow 3): with a sale item and a full-price item, the summary adds up."""
    catalog = CatalogPage(page)
    cart = CartPage(page)
    header = Header(page)

    # Setup: one discounted item (from On sale) and one full-price item (from All games).
    catalog.open_on_sale()
    sale_item = catalog.add_first_available_product_to_cart()
    header.expect_cart_count(1)
    catalog.open_all_games()
    header.expect_cart_count(1)  # wait until the new page has loaded the existing cart
    full_price_item = catalog.add_first_available_product_to_cart(full_price_only=True)
    header.expect_cart_count(2)

    cart.open()
    sale_line = cart.line(sale_item)
    full_price_line = cart.line(full_price_item)
    expect(cart.lines).to_have_count(2)

    # The lines themselves look right.
    assert sale_line.current_price().cents < sale_line.original_price().cents, "Sale item isn't discounted"
    assert full_price_line.current_price() == full_price_line.original_price(), "Full-price item shows a discount"

    lines = [sale_line, full_price_line]
    subtotal = cart.subtotal()
    discount = cart.discount()
    total = cart.total()

    # Everything is in one currency, whichever one the store picked for this visitor.
    currencies = {subtotal.currency, discount.currency, total.currency}
    currencies |= {line.current_price().currency for line in lines}
    assert len(currencies) == 1, f"Mixed currencies in the cart: {currencies}"

    sum_of_original_prices = sum(line.original_price().cents for line in lines)
    sum_of_current_prices = sum(line.current_price().cents for line in lines)

    assert_same_amount(subtotal.cents, sum_of_original_prices, "Subtotal vs sum of original prices")
    assert discount.cents < 0, "Discount should be shown as a negative amount"
    assert_same_amount(-discount.cents, sum_of_original_prices - sum_of_current_prices, "Discount vs sum of line savings")
    assert_same_amount(total.cents, subtotal.cents + discount.cents, "Total vs subtotal minus discount")
    assert_same_amount(total.cents, sum_of_current_prices, "Total vs sum of current prices")

    # Checkout must be available, but we never click it on the live store.
    expect(cart.checkout_button).to_be_visible()
    expect(cart.checkout_button).to_be_enabled()


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

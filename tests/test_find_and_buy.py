import re

from playwright.sync_api import expect

from pages.buy_page import BuyPage
from pages.cart_page import CartPage
from pages.catalog_page import CatalogPage
from pages.header import Header
from pages.product_info_page import ProductInfoPage


def longest_word(title):
    """Pick a search word from a product title: its longest word (letters only)."""
    return max(re.findall(r"[A-Za-z]+", title), key=len)


def test_flow1_search_then_add_from_the_buy_page(page):
    """Required flow 1: CAT-01 (search) + PDP-01 (buy page) + ADD-02 (same name and price in the cart)."""
    catalog = CatalogPage(page)
    info_page = ProductInfoPage(page)
    buy_page = BuyPage(page)
    cart = CartPage(page)
    header = Header(page)

    # Take the search word from a product that's live today, so it always finds something.
    catalog.open_all_games()
    search_term = longest_word(catalog.first_card_with_add_to_cart().title.inner_text())

    # CAT-01: search narrows the list to matching products, and the search is in the URL.
    catalog.search(search_term)
    expect(page).to_have_url(re.compile(f"Search={search_term}"))
    expect(catalog.product_titles.first).to_be_visible()
    # Waits until no title is left without the term (has_not_text ignores upper/lower case).
    expect(catalog.product_titles.filter(has_not_text=search_term)).to_have_count(0)

    # Pick a result that can be bought on its own, and note what the listing says about it.
    result = catalog.first_card_with_add_to_cart()
    product_name = result.title.inner_text()
    listing_price = result.current_price()

    # Open its info page, then "Buy now" for this product.
    info_page.open(result.page_url())
    info_page.buy_now_link(result.sku()).click()
    expect(page).to_have_url(re.compile(r"/buy\b"))

    # PDP-01: the buy page shows the product with a price, a platform and an enabled Add to cart.
    item = buy_page.item(product_name)
    expect(item.price).to_be_visible()
    expect(item.platform).to_be_visible()
    expect(item.add_to_cart_button).to_be_enabled()
    buy_page_price = item.current_price()
    assert buy_page_price == listing_price, f"Buy page price {buy_page_price} differs from listing {listing_price}"

    # ADD-02: add it; the button changes and can't be used twice, and the header counts it.
    item.add_to_cart_button.click()
    expect(item.added_to_cart_button).to_be_disabled()
    header.expect_cart_count(1)

    # The cart has exactly this product, at the same price.
    cart.open()
    expect(cart.lines).to_have_count(1)
    cart_price = cart.line(product_name).current_price()
    assert cart_price == buy_page_price, f"Cart price {cart_price} differs from buy page {buy_page_price}"

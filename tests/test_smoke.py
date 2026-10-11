from playwright.sync_api import expect

from pages.catalog_page import CatalogPage
from pages.header import Header


def test_store_opens_with_an_empty_cart(page):
    """Quick check that the store is up and the setup works before the longer tests run."""
    catalog = CatalogPage(page)
    catalog.open_all_games()

    expect(catalog.results_summary).to_be_visible()
    # A new browser context has no saved order, so the cart starts empty.
    Header(page).expect_cart_count(0)

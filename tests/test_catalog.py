import re

from playwright.sync_api import expect

from pages.catalog_page import CatalogPage


def test_cat03_brand_filter_shows_only_that_brand_and_survives_a_reload(page):
    """CAT-03: ticking a brand shows only that brand's products, and the filter is kept in the URL."""
    catalog = CatalogPage(page)
    catalog.open_all_games()

    # Use the brand of a product that can be bought today, so the filter has real results.
    # Finding that tile also tells us the page is ready for the Filter click.
    brand = catalog.first_card_with_add_to_cart().brand()
    catalog.filter_by_brand(brand)

    expect(catalog.brand_checkbox(brand)).to_be_checked()
    expect(page).to_have_url(re.compile(r"Brand="))
    expect(catalog.product_cards.first).to_be_visible()
    # Waits until every tile on the page belongs to the chosen brand.
    expect(catalog.cards_not_of_brand(brand)).to_have_count(0)
    results_before = catalog.skus()

    # The filter lives in the URL, so a reload must show the same filtered results.
    page.reload()
    expect(page).to_have_url(re.compile(r"Brand="))
    expect(catalog.cards_not_of_brand(brand)).to_have_count(0)
    expect(catalog.product_cards).to_have_count(len(results_before))
    assert catalog.skus() == results_before, "Different products after reloading the filtered page"

from utils.money import MONEY_PATTERN, parse_money


class CartLine:
    """One product line in the cart.

    A discounted line shows two prices, the original (struck through) and then
    the current one. A full-price line shows a single price.
    """

    def __init__(self, root):
        self.prices = root.get_by_text(MONEY_PATTERN)

    def original_price(self):
        return parse_money(self.prices.first.inner_text())

    def current_price(self):
        return parse_money(self.prices.last.inner_text())


class CartPage:
    """The shopping cart page."""

    URL = "/our-games/cart"

    def __init__(self, page):
        self.page = page
        self.main = page.get_by_role("main")
        # One list item per product in the cart.
        self.lines = self.main.get_by_role("listitem")
        self.summary_heading = self.main.get_by_role("heading", name="Summary")
        # Only ever checked for visible and enabled. Never clicked: this is the live store.
        self.checkout_button = self.main.get_by_role("button", name="Proceed to checkout")

        # Empty cart state
        self.empty_heading = self.main.get_by_role("heading", name="Your cart is empty")
        self.empty_message = self.main.get_by_text("Have a look at our games to add items to your cart.")
        self.go_to_all_games_link = self.main.get_by_role("link", name="Go to all games")

    def open(self):
        self.page.goto(self.URL)

    def remove_button(self, product_name):
        # The product name arrives a moment after the line itself (the button briefly
        # reads "Remove undefined from cart"), so waiting for this exact name also
        # waits for the line to finish loading.
        return self.page.get_by_role("button", name=f"Remove {product_name} from cart", exact=True)

    def remove(self, product_name):
        self.remove_button(product_name).click()

    def line(self, product_name):
        """The cart line for this product, once it has fully loaded."""
        line = self.lines.filter(has=self.remove_button(product_name))
        line.wait_for()
        return CartLine(line)

    # Summary rows are plain text pairs, for example <span>Subtotal</span><span>69.98 EUR</span>,
    # so we find the label and read the element right after it.
    def _summary_amount(self, label):
        label_element = self.main.get_by_text(label, exact=True)
        return parse_money(label_element.locator("xpath=following-sibling::*[1]").inner_text())

    def subtotal(self):
        return self._summary_amount("Subtotal")

    def discount(self):
        """Shown as a negative amount, for example -14.99 EUR. Only present when there's a discount."""
        return self._summary_amount("Discount")

    def total(self):
        return self._summary_amount("Total")

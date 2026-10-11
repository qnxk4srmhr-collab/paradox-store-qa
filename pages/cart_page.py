class CartPage:
    """The shopping cart page."""

    URL = "/our-games/cart"

    def __init__(self, page):
        self.page = page
        main = page.get_by_role("main")
        # One list item per product in the cart.
        self.lines = main.get_by_role("listitem")
        self.summary_heading = main.get_by_role("heading", name="Summary")
        # Only ever checked for visible and enabled. Never clicked: this is the live store.
        self.checkout_button = main.get_by_role("button", name="Proceed to checkout")

        # Empty cart state
        self.empty_heading = main.get_by_role("heading", name="Your cart is empty")
        self.empty_message = main.get_by_text("Have a look at our games to add items to your cart.")
        self.go_to_all_games_link = main.get_by_role("link", name="Go to all games")

    def open(self):
        self.page.goto(self.URL)

    def remove_button(self, product_name):
        # The product name arrives a moment after the line itself (the button briefly
        # reads "Remove undefined from cart"), so waiting for this exact name also
        # waits for the line to finish loading.
        return self.page.get_by_role("button", name=f"Remove {product_name} from cart", exact=True)

    def remove(self, product_name):
        self.remove_button(product_name).click()

class ProductCard:
    """One product tile on a listing page (an <li> with data-testid="<SKU>")."""

    def __init__(self, root):
        self.root = root
        self.title = root.get_by_role("heading")
        # Every tile's button has the same name, so we only ever look inside this card.
        self.add_to_cart_button = root.get_by_role("button", name="Add to cart")

    def add_to_cart(self):
        # The button is hidden (display: none) until the mouse is over the card.
        self.root.hover()
        self.add_to_cart_button.click()

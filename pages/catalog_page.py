import re


class CatalogPage:
    """Product listing pages: All games and On sale."""

    ALL_GAMES_URL = "/our-games/all-games"

    def __init__(self, page):
        self.page = page
        # "Showing 20 of 446"
        self.results_summary = page.get_by_text(re.compile(r"^Showing \d+ of \d+$"))

    def open_all_games(self):
        self.page.goto(self.ALL_GAMES_URL)

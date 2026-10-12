from playwright.sync_api import expect

# Any date that makes the visitor an adult for every age rating.
ADULT_BIRTH_DAY, ADULT_BIRTH_MONTH, ADULT_BIRTH_YEAR = "1", "1", "1990"


def pass_age_gate_when_shown(page):
    """If an age-restricted product asks for a date of birth, enter an adult one.

    Only some products have the gate, and we don't choose products in advance,
    so like the cookie banner it's handled with a locator handler: before each
    click or assertion, Playwright checks for the gate and runs this first.
    """
    gate = page.get_by_role("heading", name="Enter your birth date")

    def enter_adult_birth_date():
        page.get_by_role("combobox", name="Day").select_option(ADULT_BIRTH_DAY)
        page.get_by_role("combobox", name="Month").select_option(ADULT_BIRTH_MONTH)
        page.get_by_role("combobox", name="Year").select_option(ADULT_BIRTH_YEAR)
        page.get_by_role("button", name="Submit").click()
        expect(gate).to_be_hidden()

    page.add_locator_handler(gate, enter_adult_birth_date)

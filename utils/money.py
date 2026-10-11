import re
from dataclasses import dataclass
from decimal import Decimal

# Prices as the store shows them: "19.99 EUR", "-14.99 EUR", "1,299.00 GBP".
MONEY_PATTERN = re.compile(r"^-?[\d,]+\.\d{2} [A-Z]{3}$")

# Totals may be rounded differently from the sum of rounded line prices,
# so amounts are allowed to differ by one cent.
TOLERANCE_CENTS = 1


@dataclass(frozen=True)
class Money:
    """An amount in whole cents, plus its currency code.

    Whole cents (integers) avoid floating point surprises like 0.1 + 0.2 = 0.30000000000000004.
    """

    cents: int
    currency: str


def parse_money(text):
    """Turn "19.99 EUR" into Money(cents=1999, currency="EUR")."""
    text = text.strip()
    if not MONEY_PATTERN.match(text):
        raise ValueError(f"Not a price: {text!r}")
    number, currency = text.split(" ")
    cents = int(Decimal(number.replace(",", "")) * 100)
    return Money(cents, currency)


def assert_same_amount(actual_cents, expected_cents, what):
    """Fail with a readable message if two amounts differ by more than the tolerance."""
    assert abs(actual_cents - expected_cents) <= TOLERANCE_CENTS, (
        f"{what}: expected {expected_cents / 100:.2f}, got {actual_cents / 100:.2f}"
    )

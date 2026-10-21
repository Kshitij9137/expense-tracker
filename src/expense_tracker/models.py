"""Data models and validation helpers.

Money is stored as integer cents to avoid floating point rounding errors
(for example 0.1 + 0.2 != 0.3 with floats).
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation


class ValidationError(ValueError):
    """Raised when user input is invalid."""


def to_cents(amount) -> int:
    """Convert a user-supplied amount (str/int/float) to integer cents."""
    try:
        value = Decimal(str(amount).strip())
    except (InvalidOperation, AttributeError):
        raise ValidationError(f"Invalid amount: {amount!r}")
    if not value.is_finite() or value <= 0:
        raise ValidationError("Amount must be a positive number")
    cents = (value * 100).quantize(Decimal("1"))
    return int(cents)


def format_money(cents: int) -> str:
    return f"{cents / 100:,.2f}"


def parse_date(value: str) -> str:
    """Validate a YYYY-MM-DD date string and return it normalised."""
    try:
        return date.fromisoformat(value).isoformat()
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid date {value!r}, expected YYYY-MM-DD")


def clean_category(value: str) -> str:
    category = (value or "").strip().lower()
    if not category:
        raise ValidationError("Category cannot be empty")
    if len(category) > 30:
        raise ValidationError("Category must be 30 characters or fewer")
    return category


@dataclass(frozen=True)
class Expense:
    id: int
    amount_cents: int
    category: str
    description: str
    spent_on: str

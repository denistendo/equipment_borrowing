from dataclasses import dataclass
from datetime import date, timedelta

from domain.exceptions import InvalidEquipmentCodeError


@dataclass(frozen=True)
class EquipmentCode:
    """BR1 - Value Object.

    Rule: An equipment code must contain between 3 and 20 non-empty characters.
    Violation: InvalidEquipmentCodeError is raised.
    No identity: two EquipmentCode('ABC') are interchangeable.
    """

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise InvalidEquipmentCodeError("Equipment code must be a string.")
        if not (3 <= len(self.value) <= 20):
            raise InvalidEquipmentCodeError(
                f"Equipment code must be 3-20 characters, got {len(self.value)}."
            )
        if not self.value.strip():
            raise InvalidEquipmentCodeError("Equipment code cannot be blank.")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class BorrowingId:
    """Identity value object for Aggregate A."""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("BorrowingId cannot be blank.")


@dataclass(frozen=True)
class EventDateRange:
    """Value Object: start and end of the borrowing occasion."""

    start_date: date
    end_date: date

    def __post_init__(self) -> None:
        if self.end_date < self.start_date:
            raise ValueError("Event end date cannot be before start date.")

    @property
    def duration_days(self) -> int:
        """Inclusive day count. 1 Jan -> 3 Jan = 3 days."""
        return (self.end_date - self.start_date).days + 1

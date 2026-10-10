from dataclasses import dataclass, field

from domain.value_objects import EquipmentCode


@dataclass
class Borrower:
    """Entity inside Aggregate A. Identity = borrower_id."""

    borrower_id: str
    name: str
    is_eligible: bool


@dataclass
class Event:
    """Entity inside Aggregate A. Identity = event_id.

    NOTE: This is the *borrowing occasion*, not a domain event.
    """

    event_id: str
    name: str

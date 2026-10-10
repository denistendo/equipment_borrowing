from dataclasses import dataclass, field
from enum import Enum

from domain.domain_event import EquipmentBorrowingApproved
from domain.entities import Borrower, Event
from domain.exceptions import TooManyEquipmentItemsError
from domain.value_objects import BorrowingId, EquipmentCode, EventDateRange


class BorrowingStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass
class EquipmentBorrowing:
    """Aggregate Root A.

    Identity: borrowing_id (BorrowingId).

    Invariant protected (BR3):
        A borrowing cannot contain more than 3 equipment items.
        Enforced by add_equipment_code().

    BR5:
        On approve(), raises EquipmentBorrowingApproved domain event
        so Aggregate B can reserve the equipment.
    """

    borrowing_id: BorrowingId
    borrower: Borrower
    event: Event
    event_date_range: EventDateRange
    equipment_codes: list[EquipmentCode] = field(default_factory=list)
    status: BorrowingStatus = BorrowingStatus.PENDING
    _pending_events: list = field(default_factory=list, repr=False)

    MAX_EQUIPMENT_ITEMS = 3

    # ---- BR3: collection invariant ----
    def add_equipment_code(self, code: EquipmentCode) -> None:
        if len(self.equipment_codes) >= self.MAX_EQUIPMENT_ITEMS:
            raise TooManyEquipmentItemsError(
                f"A borrowing cannot contain more than "
                f"{self.MAX_EQUIPMENT_ITEMS} equipment items."
            )
        if code in self.equipment_codes:
            raise TooManyEquipmentItemsError(f"Duplicate equipment code {code}.")
        self.equipment_codes.append(code)

    # ---- BR5: raise domain event on approval ----
    def approve(self) -> None:
        if self.status is not BorrowingStatus.PENDING:
            raise ValueError(f"Borrowing is not PENDING (current: {self.status}).")
        if not self.equipment_codes:
            raise ValueError("Cannot approve a borrowing with no equipment.")

        self.status = BorrowingStatus.APPROVED
        self._pending_events.append(
            EquipmentBorrowingApproved(
                borrowing_id=self.borrowing_id.value,
                equipment_codes=[c.value for c in self.equipment_codes],
            )
        )

    def reject(self) -> None:
        self.status = BorrowingStatus.REJECTED

    # ---- event collection (Application layer drains this) ----
    def pull_domain_events(self) -> list:
        events = list(self._pending_events)
        self._pending_events.clear()
        return events

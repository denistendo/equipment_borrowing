from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class EquipmentBorrowingApproved:
    """BR5 - Domain Event.

    Raised by EquipmentBorrowing.approve().
    Consumed by EquipmentBorrowingApprovedHandler, which asks
    each Equipment aggregate to reserve itself (BR2).
    """

    borrowing_id: str
    equipment_codes: list[str]
    occurred_at: datetime = field(default_factory=datetime.utcnow)

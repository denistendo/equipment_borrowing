from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class EquipmentBorrowingApproved:
    borrowing_id: str
    equipment_codes: list[str]
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
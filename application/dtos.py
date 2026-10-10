from dataclasses import dataclass, field
from datetime import date


@dataclass
class CreateBorrowingInput:
    borrowing_id: str
    borrower_id: str
    borrower_name: str
    borrower_is_eligible: bool
    event_id: str
    event_name: str
    start_date: date
    end_date: date
    equipment_codes: list[str] = field(default_factory=list)


@dataclass
class CreateBorrowingOutput:
    borrowing_id: str
    status: str
    message: str
    reserved_equipment: list[str] = field(default_factory=list)

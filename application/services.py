from application.dtos import CreateBorrowingInput, CreateBorrowingOutput
from application.handlers import EquipmentBorrowingApprovedHandler
from domain.aggregates.equipment_borrowing import (
    BorrowingStatus,
    EquipmentBorrowing,
)
from domain.domain_service import BorrowingEligibilityService
from domain.entities import Borrower, Event
from domain.exceptions import EquipmentNotFoundError
from domain.repository_interfaces import (
    EquipmentBorrowingRepository,
    EquipmentRepository,
)
from domain.value_objects import BorrowingId, EquipmentCode, EventDateRange


class CreateBorrowingService:
    """Main Application Service.

    Coordinates the use case. Does NOT contain business rules itself:
        - BR1 enforced by EquipmentCode
        - BR3 enforced by EquipmentBorrowing
        - BR4 enforced by BorrowingEligibilityService
        - BR6 enforced here by looking up the repository
        - BR5 raised by EquipmentBorrowing, handled by the handler
    """

    def __init__(
        self,
        equipment_repo: EquipmentRepository,
        borrowing_repo: EquipmentBorrowingRepository,
        eligibility_service: BorrowingEligibilityService,
        event_handler: EquipmentBorrowingApprovedHandler,
    ) -> None:
        # Dependency injection: all collaborators are supplied from outside.
        self._equipment_repo = equipment_repo
        self._borrowing_repo = borrowing_repo
        self._eligibility_service = eligibility_service
        self._event_handler = event_handler

    def execute(self, dto: CreateBorrowingInput) -> CreateBorrowingOutput:
        # ---- BR6: lookup every requested equipment first ----
        equipment_items = []
        for raw_code in dto.equipment_codes:
            code = EquipmentCode(raw_code)          # BR1 may fire here
            equipment = self._equipment_repo.find_by_code(code)
            if equipment is None:
                raise EquipmentNotFoundError(f"Equipment {raw_code} does not exist.")
            equipment_items.append(equipment)

        # ---- BR4: eligibility + duration ----
        borrower = Borrower(dto.borrower_id, dto.borrower_name, dto.borrower_is_eligible)
        period = EventDateRange(dto.start_date, dto.end_date)
        self._eligibility_service.ensure_eligible(borrower, period)

        # ---- Build Aggregate A ----
        borrowing = EquipmentBorrowing(
            borrowing_id=BorrowingId(dto.borrowing_id),
            borrower=borrower,
            event=Event(dto.event_id, dto.event_name),
            event_date_range=period,
        )
        for code in dto.equipment_codes:
            borrowing.add_equipment_code(EquipmentCode(code))   # BR3

        self._borrowing_repo.save(borrowing)

        # ---- Approve: raises BR5 event ----
        borrowing.approve()
        self._borrowing_repo.save(borrowing)

        # ---- Drain events and dispatch to the handler ----
        reserved: list[str] = []
        for event in borrowing.pull_domain_events():
            reserved = self._event_handler.handle(event)        # BR2 fires inside

        return CreateBorrowingOutput(
            borrowing_id=borrowing.borrowing_id.value,
            status=borrowing.status.value,
            message="Borrowing approved and equipment reserved.",
            reserved_equipment=reserved,
        )

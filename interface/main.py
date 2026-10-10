from datetime import date

from application.dtos import CreateBorrowingInput
from application.handlers import EquipmentBorrowingApprovedHandler
from application.services import CreateBorrowingService
from domain.aggregates.equipment import Equipment
from domain.domain_service import BorrowingEligibilityService
from domain.value_objects import EquipmentCode
from infrastructure.in_memory_repositories import (
    InMemoryEquipmentBorrowingRepository,
    InMemoryEquipmentRepository,
)


def build_service() -> CreateBorrowingService:
    """Composition root. Only this file knows the concrete implementations."""
    equipment_repo = InMemoryEquipmentRepository()
    borrowing_repo = InMemoryEquipmentBorrowingRepository()

    # seed equipment
    for code, kind in [("CAM01", "Camera"), ("TRP01", "Tripod"), ("MIC01", "Microphone")]:
        equipment_repo.add(Equipment(code=EquipmentCode(code), equipment_type=kind))

    handler = EquipmentBorrowingApprovedHandler(equipment_repo)
    return CreateBorrowingService(
        equipment_repo=equipment_repo,
        borrowing_repo=borrowing_repo,
        eligibility_service=BorrowingEligibilityService(),
        event_handler=handler,
    )


if __name__ == "__main__":
    service = build_service()
    dto = CreateBorrowingInput(
        borrowing_id="BR-001",
        borrower_id="S001",
        borrower_name="Alice",
        borrower_is_eligible=True,
        event_id="EV-001",
        event_name="Media Club Shoot",
        start_date=date(2025, 1, 10),
        end_date=date(2025, 1, 12),
        equipment_codes=["CAM01", "TRP01"],
    )
    result = service.execute(dto)
    print(result)

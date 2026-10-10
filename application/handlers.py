from domain.domain_event import EquipmentBorrowingApproved
from domain.repository_interfaces import EquipmentRepository
from domain.value_objects import EquipmentCode


class EquipmentBorrowingApprovedHandler:
    """BR5 - Follow-up handler.

    After Aggregate A approves a borrowing, this handler
    asks Aggregate B to reserve itself. Aggregate B still
    enforces BR2 independently.
    """

    def __init__(self, equipment_repository: EquipmentRepository) -> None:
        self._equipment_repository = equipment_repository

    def handle(self, event: EquipmentBorrowingApproved) -> list[str]:
        reserved: list[str] = []
        for raw_code in event.equipment_codes:
            code = EquipmentCode(raw_code)
            equipment = self._equipment_repository.find_by_code(code)
            if equipment is None:
                raise LookupError(f"Equipment {raw_code} not found at reserve time.")
            equipment.reserve()               # <- BR2 enforced HERE
            self._equipment_repository.save(equipment)
            reserved.append(raw_code)
        return reserved

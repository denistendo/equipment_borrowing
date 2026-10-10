from domain.aggregates.equipment import Equipment
from domain.aggregates.equipment_borrowing import EquipmentBorrowing
from domain.repository_interfaces import (
    EquipmentBorrowingRepository,
    EquipmentRepository,
)
from domain.value_objects import BorrowingId, EquipmentCode


class InMemoryEquipmentRepository(EquipmentRepository):
    def __init__(self) -> None:
        self._store: dict[str, Equipment] = {}

    def find_by_code(self, code: EquipmentCode) -> Equipment | None:
        return self._store.get(str(code))

    def save(self, equipment: Equipment) -> None:
        self._store[str(equipment.code)] = equipment

    # test convenience
    def add(self, equipment: Equipment) -> None:
        self.save(equipment)


class InMemoryEquipmentBorrowingRepository(EquipmentBorrowingRepository):
    def __init__(self) -> None:
        self._store: dict[str, EquipmentBorrowing] = {}

    def find_by_id(self, borrowing_id: BorrowingId) -> EquipmentBorrowing | None:
        return self._store.get(str(borrowing_id.value))

    def save(self, borrowing: EquipmentBorrowing) -> None:
        self._store[borrowing.borrowing_id.value] = borrowing

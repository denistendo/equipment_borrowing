from abc import ABC, abstractmethod

from domain.aggregates.equipment import Equipment
from domain.aggregates.equipment_borrowing import EquipmentBorrowing
from domain.value_objects import BorrowingId, EquipmentCode


class EquipmentRepository(ABC):
    @abstractmethod
    def find_by_code(self, code: EquipmentCode) -> Equipment | None: ...

    @abstractmethod
    def save(self, equipment: Equipment) -> None: ...


class EquipmentBorrowingRepository(ABC):
    @abstractmethod
    def find_by_id(self, borrowing_id: BorrowingId) -> EquipmentBorrowing | None: ...

    @abstractmethod
    def save(self, borrowing: EquipmentBorrowing) -> None: ...

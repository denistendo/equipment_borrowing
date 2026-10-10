from dataclasses import dataclass
from enum import Enum

from domain.exceptions import EquipmentNotAvailableError
from domain.value_objects import EquipmentCode


class EquipmentStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    BORROWED = "BORROWED"


@dataclass
class Equipment:
    """Aggregate Root B.

    Identity: equipment_code (an EquipmentCode value object).

    Invariant protected (BR2):
        Status can only transition AVAILABLE -> BORROWED.
        Any other transition raises EquipmentNotAvailableError.
    """

    code: EquipmentCode
    equipment_type: str
    status: EquipmentStatus = EquipmentStatus.AVAILABLE

    # ---- BR2: the only legal state transition ----
    def reserve(self) -> None:
        """Move AVAILABLE -> BORROWED. Enforces BR2."""
        if self.status is not EquipmentStatus.AVAILABLE:
            raise EquipmentNotAvailableError(
                f"Equipment {self.code} is not AVAILABLE (current: {self.status})."
            )
        self.status = EquipmentStatus.BORROWED

    def release(self) -> None:
        """Move BORROWED -> AVAILABLE (used in tests / clean-up)."""
        if self.status is not EquipmentStatus.BORROWED:
            raise EquipmentNotAvailableError(
                f"Equipment {self.code} is not BORROWED (current: {self.status})."
            )
        self.status = EquipmentStatus.AVAILABLE

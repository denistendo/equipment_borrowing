class DomainError(Exception):
    """Base class for all domain rule violations."""


class InvalidEquipmentCodeError(DomainError):
    """BR1: Equipment code must be 3-20 non-empty characters."""


class EquipmentNotAvailableError(DomainError):
    """BR2: Equipment can only move AVAILABLE -> BORROWED."""


class TooManyEquipmentItemsError(DomainError):
    """BR3: A borrowing cannot contain more than 3 equipment items."""


class BorrowerNotEligibleError(DomainError):
    """BR4: Borrower is not eligible."""


class BorrowingDurationExceededError(DomainError):
    """BR4: Borrowing duration exceeds 3 days."""


class EquipmentNotFoundError(DomainError):
    """BR6: Requested equipment does not exist."""

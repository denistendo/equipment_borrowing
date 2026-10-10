from domain.entities import Borrower
from domain.exceptions import (
    BorrowerNotEligibleError,
    BorrowingDurationExceededError,
)
from domain.value_objects import EventDateRange


class BorrowingEligibilityService:
    """BR4 - Domain Service.

    Rule: A borrower may borrow equipment only if the borrower is
          eligible AND the event duration does not exceed 3 days.
    Violation: BorrowerNotEligibleError or BorrowingDurationExceededError.

    Why a service? The rule crosses Borrower (an entity) and
    EventDateRange (a value object), so it does not naturally
    belong to either.
    """

    MAX_DURATION_DAYS = 3

    def ensure_eligible(self, borrower: Borrower, period: EventDateRange) -> None:
        if not borrower.is_eligible:
            raise BorrowerNotEligibleError(
                f"Borrower {borrower.borrower_id} is not eligible."
            )
        if period.duration_days > self.MAX_DURATION_DAYS:
            raise BorrowingDurationExceededError(
                f"Borrowing duration {period.duration_days} days exceeds "
                f"the {self.MAX_DURATION_DAYS}-day limit."
            )

"""
Automated tests T1 - T8 for the Event Equipment Borrowing domain.

Run from the project root with:
    python -m pytest tests/test_all.py -v
or:
    python -m unittest tests.test_all -v
"""

import sys
import unittest
from datetime import date
from pathlib import Path

# Make the project root importable when running this file directly.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from application.dtos import CreateBorrowingInput
from application.handlers import EquipmentBorrowingApprovedHandler
from application.services import CreateBorrowingService
from domain.aggregates.equipment import Equipment, EquipmentStatus
from domain.aggregates.equipment_borrowing import (
    BorrowingStatus,
    EquipmentBorrowing,
)
from domain.domain_service import BorrowingEligibilityService
from domain.entities import Borrower, Event
from domain.exceptions import (
    BorrowerNotEligibleError,
    BorrowingDurationExceededError,
    EquipmentNotAvailableError,
    EquipmentNotFoundError,
    InvalidEquipmentCodeError,
    TooManyEquipmentItemsError,
)
from domain.value_objects import BorrowingId, EquipmentCode, EventDateRange
from infrastructure.in_memory_repositories import (
    InMemoryEquipmentBorrowingRepository,
    InMemoryEquipmentRepository,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
def make_borrowing() -> EquipmentBorrowing:
    """A valid, empty, PENDING borrowing ready to receive equipment."""
    return EquipmentBorrowing(
        borrowing_id=BorrowingId("BR-TEST"),
        borrower=Borrower("S001", "Alice", True),
        event=Event("EV-001", "Media Club Shoot"),
        event_date_range=EventDateRange(date(2025, 1, 10), date(2025, 1, 12)),
    )


def make_service(seed_equipment: list[tuple[str, str]] | None = None):
    """Build a fully wired application service for tests."""
    seed_equipment = seed_equipment or [
        ("CAM01", "Camera"),
        ("TRP01", "Tripod"),
        ("MIC01", "Microphone"),
    ]
    equipment_repo = InMemoryEquipmentRepository()
    borrowing_repo = InMemoryEquipmentBorrowingRepository()

    for code, kind in seed_equipment:
        equipment_repo.add(Equipment(code=EquipmentCode(code), equipment_type=kind))

    handler = EquipmentBorrowingApprovedHandler(equipment_repo)
    service = CreateBorrowingService(
        equipment_repo=equipment_repo,
        borrowing_repo=borrowing_repo,
        eligibility_service=BorrowingEligibilityService(),
        event_handler=handler,
    )
    return service, equipment_repo, borrowing_repo


def make_input(**overrides) -> CreateBorrowingInput:
    """Default valid input; override any field per test."""
    defaults = dict(
        borrowing_id="BR-001",
        borrower_id="S001",
        borrower_name="Alice",
        borrower_is_eligible=True,
        event_id="EV-001",
        event_name="Media Club Shoot",
        start_date=date(2025, 1, 10),
        end_date=date(2025, 1, 12),
        equipment_codes=["CAM01"],
    )
    defaults.update(overrides)
    return CreateBorrowingInput(**defaults)


# ---------------------------------------------------------------------------
# T1 - BR1: Value rule (EquipmentCode must be 3-20 chars)
# ---------------------------------------------------------------------------
class T1_EquipmentCodeValueRule(unittest.TestCase):
    """T1 (BR1) - Value Object enforces 3-20 characters. Includes boundaries."""

    def test_T1_too_short_is_rejected(self):
        with self.assertRaises(InvalidEquipmentCodeError):
            EquipmentCode("AB")                      # boundary: 2 chars

    def test_T1_minimum_length_is_accepted(self):
        self.assertEqual(EquipmentCode("ABC").value, "ABC")   # boundary: 3 chars

    def test_T1_maximum_length_is_accepted(self):
        code = "A" * 20
        self.assertEqual(EquipmentCode(code).value, code)     # boundary: 20 chars

    def test_T1_too_long_is_rejected(self):
        with self.assertRaises(InvalidEquipmentCodeError):
            EquipmentCode("A" * 21)                  # boundary: 21 chars

    def test_T1_blank_is_rejected(self):
        with self.assertRaises(InvalidEquipmentCodeError):
            EquipmentCode("   ")


# ---------------------------------------------------------------------------
# T2 - BR2: Entity / Aggregate Root state transition
# ---------------------------------------------------------------------------
class T2_EquipmentStateTransition(unittest.TestCase):
    """T2 (BR2) - Equipment can only transition AVAILABLE -> BORROWED."""

    def test_T2_available_can_be_reserved(self):
        eq = Equipment(code=EquipmentCode("CAM01"), equipment_type="Camera")
        eq.reserve()
        self.assertEqual(eq.status, EquipmentStatus.BORROWED)

    def test_T2_already_borrowed_cannot_be_reserved_again(self):
        eq = Equipment(code=EquipmentCode("CAM01"), equipment_type="Camera")
        eq.reserve()
        with self.assertRaises(EquipmentNotAvailableError):
            eq.reserve()


# ---------------------------------------------------------------------------
# T3 - BR3: Aggregate invariant (max 3 equipment items)
# ---------------------------------------------------------------------------
class T3_MaxEquipmentItemsInvariant(unittest.TestCase):
    """T3 (BR3) - A borrowing cannot hold more than 3 items."""

    def test_T3_three_items_are_accepted(self):
        b = make_borrowing()
        b.add_equipment_code(EquipmentCode("AAA"))
        b.add_equipment_code(EquipmentCode("BBB"))
        b.add_equipment_code(EquipmentCode("CCC"))
        self.assertEqual(len(b.equipment_codes), 3)   # boundary: exactly 3

    def test_T3_fourth_item_is_rejected(self):
        b = make_borrowing()
        for code in ("AAA", "BBB", "CCC"):
            b.add_equipment_code(EquipmentCode(code))
        with self.assertRaises(TooManyEquipmentItemsError):
            b.add_equipment_code(EquipmentCode("DDD"))  # boundary: 4th


# ---------------------------------------------------------------------------
# T4 - BR4: Domain Service (eligibility + duration)
# ---------------------------------------------------------------------------
class T4_BorrowingEligibilityService(unittest.TestCase):
    """T4 (BR4) - Ineligible borrower and >3-day duration are rejected."""

    def setUp(self):
        self.service = BorrowingEligibilityService()

    def test_T4_eligible_borrower_within_duration_passes(self):
        borrower = Borrower("S001", "Alice", True)
        period = EventDateRange(date(2025, 1, 10), date(2025, 1, 12))  # 3 days
        self.service.ensure_eligible(borrower, period)   # boundary: exactly 3

    def test_T4_ineligible_borrower_is_rejected(self):
        borrower = Borrower("S002", "Bob", False)
        period = EventDateRange(date(2025, 1, 10), date(2025, 1, 11))
        with self.assertRaises(BorrowerNotEligibleError):
            self.service.ensure_eligible(borrower, period)

    def test_T4_duration_over_three_days_is_rejected(self):
        borrower = Borrower("S001", "Alice", True)
        period = EventDateRange(date(2025, 1, 10), date(2025, 1, 13))  # 4 days
        with self.assertRaises(BorrowingDurationExceededError):
            self.service.ensure_eligible(borrower, period)  # boundary: 4


# ---------------------------------------------------------------------------
# T5 - BR5: Follow-up rule (Domain Event raised by Aggregate A)
# ---------------------------------------------------------------------------
class T5_ApprovalRaisesDomainEvent(unittest.TestCase):
    """T5 (BR5) - approve() raises EquipmentBorrowingApproved."""

    def test_T5_approve_raises_event_with_correct_payload(self):
        b = make_borrowing()
        b.add_equipment_code(EquipmentCode("CAM01"))
        b.approve()

        events = b.pull_domain_events()
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event.borrowing_id, "BR-TEST")
        self.assertEqual(event.equipment_codes, ["CAM01"])
        self.assertEqual(b.status, BorrowingStatus.APPROVED)

    def test_T5_pull_domain_events_clears_pending(self):
        b = make_borrowing()
        b.add_equipment_code(EquipmentCode("CAM01"))
        b.approve()

        first = b.pull_domain_events()
        second = b.pull_domain_events()
        self.assertEqual(len(first), 1)
        self.assertEqual(second, [])


# ---------------------------------------------------------------------------
# T6 - BR6: Lookup rule (Application Service + Repository)
# ---------------------------------------------------------------------------
class T6_MissingEquipmentLookup(unittest.TestCase):
    """T6 (BR6) - Requested equipment must exist in the repository."""

    def test_T6_unknown_equipment_is_rejected(self):
        service, _, _ = make_service()
        dto = make_input(equipment_codes=["NOPE1"])
        with self.assertRaises(EquipmentNotFoundError):
            service.execute(dto)

    def test_T6_known_equipment_passes_lookup(self):
        service, _, _ = make_service()
        result = service.execute(make_input(equipment_codes=["CAM01"]))
        self.assertEqual(result.status, "APPROVED")


# ---------------------------------------------------------------------------
# T7 - Main use case (happy path): event handled, Aggregate B changes
# ---------------------------------------------------------------------------
class T7_MainUseCaseSuccess(unittest.TestCase):
    """T7 - Full flow: request -> service -> Aggregate A -> event -> handler -> Aggregate B."""

    def test_T7_borrowing_approved_and_equipment_reserved(self):
        service, equipment_repo, borrowing_repo = make_service()

        result = service.execute(
            make_input(equipment_codes=["CAM01", "TRP01"])
        )

        # Outcome
        self.assertEqual(result.status, "APPROVED")
        self.assertEqual(sorted(result.reserved_equipment), ["CAM01", "TRP01"])

        # Aggregate A persisted
        stored = borrowing_repo.find_by_id(BorrowingId("BR-001"))
        self.assertIsNotNone(stored)
        self.assertEqual(stored.status, BorrowingStatus.APPROVED)

        # Aggregate B changed as expected (event handler worked)
        self.assertEqual(
            equipment_repo.find_by_code(EquipmentCode("CAM01")).status,
            EquipmentStatus.BORROWED,
        )
        self.assertEqual(
            equipment_repo.find_by_code(EquipmentCode("TRP01")).status,
            EquipmentStatus.BORROWED,
        )
        # Untouched equipment stays AVAILABLE
        self.assertEqual(
            equipment_repo.find_by_code(EquipmentCode("MIC01")).status,
            EquipmentStatus.AVAILABLE,
        )


# ---------------------------------------------------------------------------
# T8 - Aggregate B rejects the follow-up action
# ---------------------------------------------------------------------------
class T8_AggregateBRejectsFollowUp(unittest.TestCase):
    """T8 - If equipment is already BORROWED, the handler's reserve() fails (BR2)."""

    def test_T8_handler_rejects_already_borrowed_equipment(self):
        service, equipment_repo, _ = make_service()

        # Pre-condition: CAM01 already BORROWED (via Aggregate B's own rule)
        cam = equipment_repo.find_by_code(EquipmentCode("CAM01"))
        cam.reserve()
        equipment_repo.save(cam)

        # Attempt a new borrowing that includes CAM01
        dto = make_input(equipment_codes=["CAM01"])
        with self.assertRaises(EquipmentNotAvailableError):
            service.execute(dto)

        # Final state: equipment still BORROWED (not double-booked)
        self.assertEqual(
            equipment_repo.find_by_code(EquipmentCode("CAM01")).status,
            EquipmentStatus.BORROWED,
        )

    def test_T8_partial_reservation_does_not_revert_first_item(self):
        """Documents current behaviour: items reserved before the failing one stay reserved."""
        service, equipment_repo, _ = make_service()

        # Make TRP01 already BORROWED; CAM01 is fine
        trp = equipment_repo.find_by_code(EquipmentCode("TRP01"))
        trp.reserve()
        equipment_repo.save(trp)

        dto = make_input(equipment_codes=["CAM01", "TRP01"])
        with self.assertRaises(EquipmentNotAvailableError):
            service.execute(dto)

        # CAM01 was reserved before TRP01 failed; TRP01 is still BORROWED
        self.assertEqual(
            equipment_repo.find_by_code(EquipmentCode("CAM01")).status,
            EquipmentStatus.BORROWED,
        )
        self.assertEqual(
            equipment_repo.find_by_code(EquipmentCode("TRP01")).status,
            EquipmentStatus.BORROWED,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

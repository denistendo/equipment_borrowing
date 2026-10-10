# Event Equipment Borrowing

A small Domain-Driven Design + Clean Architecture demo created for the
Advanced Programming coursework.

The domain: a borrower requests equipment for an event. When the
borrowing is approved, a domain event triggers the equipment to be
reserved in a separate aggregate.

## Business Rules

- BR1 (Value Rule)        : EquipmentCode must be 3-20 non-empty characters.
- BR2 (Identity/State)    : Equipment can only go AVAILABLE -> BORROWED.
- BR3 (Invariant)         : A borrowing holds at most 3 equipment items.
- BR4 (Cross-Concept)     : Borrower must be eligible AND duration <= 3 days.
- BR5 (Follow-up)         : On approval, EquipmentBorrowingApproved triggers
                            reservation of each equipment item.
- BR6 (Lookup)            : Every requested equipment must exist before the
                            borrowing can proceed.

## Project Structure

    domain/         Entities, Value Objects, Aggregates, Domain Service,
                    Domain Event, Repository interfaces, Exceptions.
    application/    DTOs, Application Service (use case), Event Handler.
    infrastructure/ In-memory repository implementations.
    interface/      Entry point (composition root).
    tests/          Automated tests T1 - T8.
    evidence/       TDD fail -> pass screenshots and text logs.

## How to Run the Demo

From the project root:

    python -m interface.main

Expected output:

    CreateBorrowingOutput(borrowing_id='BR-001', status='APPROVED',
        message='Borrowing approved and equipment reserved.',
        reserved_equipment=['CAM01', 'TRP01'])

## How to Run the Tests

From the project root:

    python -m unittest tests.test_all -v

Expected result: 19 tests, all OK.

## TDD Evidence

- evidence/tdd_red.png   (T2 failing before the BR2 guard was implemented)
- evidence/tdd_green.png (T2 passing after the guard was restored)
- evidence/tdd_red.txt   (text copy of the failing run)
- evidence/tdd_green.txt (text copy of the passing run)

## AI Tool Disclosure

An AI assistant was used to help draft the initial Clean Architecture
skeleton and to review the wording of the unit tests. All design
decisions, rule placement, and final code were reviewed and are
understood by the group. No part of this submission relies on
unexplained AI output.
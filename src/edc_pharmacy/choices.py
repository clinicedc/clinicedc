from clinicedc_constants import COMPLETE, NEW, NOT_APPLICABLE, OTHER, PARTIAL
from django.utils.translation import gettext as _

from .constants import (
    ALLOCATED,
    AVAILABLE,
    CANCELLED,
    DISPENSED,
    FILLED,
    TXN_ADJUSTED,
    TXN_ALLOCATED,
    TXN_ALLOCATION_ENDED,
    TXN_BIN_MOVED,
    TXN_DAMAGED,
    TXN_DISPENSED,
    TXN_EXPIRED,
    TXN_LOST,
    TXN_RECEIVED,
    TXN_REPACK_CONSUMED,
    TXN_REPACK_PRODUCED,
    TXN_RETURN_DISPATCHED,
    TXN_RETURN_DISPOSITION_DESTROYED,
    TXN_RETURN_DISPOSITION_QUARANTINED,
    TXN_RETURN_DISPOSITION_REPOOLED,
    TXN_RETURN_RECEIVED,
    TXN_RETURN_REQUESTED,
    TXN_REVERSAL,
    TXN_STORED,
    TXN_TRANSFER_DISPATCHED,
    TXN_TRANSFER_RECEIVED,
    TXN_VOIDED,
    ZERO_ITEM,
)

PRESCRIPTION_STATUS = (
    (NEW, "New"),
    (PARTIAL, "Partially filled"),
    (FILLED, "Filled"),
    (CANCELLED, "Cancelled"),
)


DISPENSE_STATUS = ((DISPENSED, "Dispensed"), (CANCELLED, "Cancelled"))


FREQUENCY = (
    ("hr", "per hour"),
    ("day", "per day"),
    ("single", "single dose"),
    (OTHER, "Other ..."),
    (NOT_APPLICABLE, "Not applicable"),
)

ORDER_CHOICES = ((NEW, _("New")), (PARTIAL, _("Partial")), (COMPLETE, _("Complete")))

STOCK_STATUS = (
    (AVAILABLE, "Available"),
    (ALLOCATED, "Allocated"),
    (ZERO_ITEM, "Zero"),
)


STOCK_UPDATE = (
    ("edc_pharmacy.receiveitem", "Receiving"),
    ("edc_pharmacy.repackrequest", "Repacking"),
)

STOCK_TRANSACTION_CHOICES = (
    # Intake
    (TXN_RECEIVED, "Received (label confirmed)"),
    # Transformation
    (TXN_REPACK_CONSUMED, "Repack — bulk consumed"),
    (TXN_REPACK_PRODUCED, "Repack — patient bottle produced"),
    # Subject binding
    (TXN_ALLOCATED, "Allocated to subject"),
    (TXN_ALLOCATION_ENDED, "Allocation ended"),
    # Forward movement
    (TXN_TRANSFER_DISPATCHED, "Transfer dispatched"),
    (TXN_TRANSFER_RECEIVED, "Transfer received at location"),
    (TXN_STORED, "Stored in bin"),
    (TXN_BIN_MOVED, "Moved to different bin"),
    (TXN_DISPENSED, "Dispensed to patient"),
    # Reverse movement
    (TXN_RETURN_REQUESTED, "Return requested"),
    (TXN_RETURN_DISPATCHED, "Return dispatched to central"),
    (TXN_RETURN_RECEIVED, "Return received at central"),
    (TXN_RETURN_DISPOSITION_REPOOLED, "Return disposition — re-pooled"),
    (TXN_RETURN_DISPOSITION_QUARANTINED, "Return disposition — quarantined"),
    (TXN_RETURN_DISPOSITION_DESTROYED, "Return disposition — destroyed"),
    # Exceptions
    (TXN_ADJUSTED, "Quantity adjusted"),
    (TXN_DAMAGED, "Damaged"),
    (TXN_LOST, "Lost"),
    (TXN_EXPIRED, "Expired"),
    (TXN_VOIDED, "Voided"),
    # Corrections
    (TXN_REVERSAL, "Reversal"),
)

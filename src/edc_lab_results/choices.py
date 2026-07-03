from .constants import (
    AMBIGUOUS_MULTI_PANEL,
    AMBIGUOUS_SAME_PANEL,
    ERROR,
    IMPORTED,
    LINKED,
    NO_MATCH,
    NO_PANEL_FOR_UTEST_ID,
    NO_UTEST_ID,
    OUT_OF_SCOPE,
    PENDING,
    SUBJECT_NOT_FOUND,
)

STATUS_CHOICES = [
    (PENDING, "Pending"),
    (IMPORTED, "Imported"),
    (ERROR, "Error"),
]

REQUISITION_MATCH_CATEGORY_CHOICES = [
    (LINKED, "Linked"),
    (AMBIGUOUS_MULTI_PANEL, "Ambiguous — utest_id spans multiple panels"),
    (AMBIGUOUS_SAME_PANEL, "Ambiguous — multiple requisitions, same panel"),
    (NO_MATCH, "No matching requisition"),
    (NO_PANEL_FOR_UTEST_ID, "Untracked — utest_id not on any panel"),
    (NO_UTEST_ID, "Unmapped — no EDC utest_id"),
    (SUBJECT_NOT_FOUND, "Subject not found"),
    (OUT_OF_SCOPE, "Out of scope — identifier not for this protocol/site"),
]

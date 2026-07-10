from .constants import (
    AMBIGUOUS_MULTI_PANEL,
    AMBIGUOUS_SAME_PANEL,
    ERROR,
    IMPORTED,
    NO_MATCH,
    NO_PANEL_FOR_UTEST_ID,
    NO_UTEST_ID,
    OUT_OF_SCOPE,
    PENDING,
    RESOLVED,
    SUBJECT_NOT_FOUND,
)

REVIEW_CATEGORIES = (
    SUBJECT_NOT_FOUND,
    NO_MATCH,
    AMBIGUOUS_MULTI_PANEL,
    AMBIGUOUS_SAME_PANEL,
)

REQUISITION_MATCH_CATEGORY_CHOICES = [
    (RESOLVED, "Resolved"),
    (AMBIGUOUS_MULTI_PANEL, "Ambiguous — utest_id spans multiple panels"),
    (AMBIGUOUS_SAME_PANEL, "Ambiguous — multiple requisitions, same panel"),
    (NO_MATCH, "No matching requisition"),
    (NO_PANEL_FOR_UTEST_ID, "Untracked — utest_id not on any panel"),
    (NO_UTEST_ID, "Unmapped — no EDC utest_id"),
    (SUBJECT_NOT_FOUND, "Subject not found"),
    (OUT_OF_SCOPE, "Out of scope — identifier not for this protocol/site"),
]

STATUS_CHOICES = [
    (PENDING, "Pending"),
    (IMPORTED, "Imported"),
    (ERROR, "Error"),
]

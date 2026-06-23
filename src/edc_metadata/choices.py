from .constants import CRF, KEYED, MISSED, NOT_REQUIRED, REQUIRED, REQUISITION

ENTRY_CATEGORY = (("CLINIC", "Clinic"), ("LAB", "Lab"), ("OTHER", "Other"))

METADATA_KIND = ((CRF, "CRF"), (REQUISITION, "Requisition"))

PRIORITY_TIER = ((1, "Tier 1 (highest)"), (2, "Tier 2"), (3, "Tier 3"))

ENTRY_STATUS = (
    (REQUIRED, "New"),
    (KEYED, "Keyed"),
    (MISSED, "Missed"),
    (NOT_REQUIRED, "Not required"),
)

ENTRY_WINDOW = (("VISIT", "Visit"), ("FORM", "Form"))

VISIT_INTERVAL_UNITS = (("H", "Hour"), ("D", "Day"), ("M", "Month"), ("Y", "Year"))

TAG_TYPE = (("REGISTRATION", "Registration"), ("OTHER", "Other"))

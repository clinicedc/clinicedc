from typing import Dict, Tuple

visit_schedule_fields: Tuple[str, ...] = (
    "visit_schedule_name",
    "schedule_name",
    "visit_code",
)

visit_schedule_fieldset_tuple: Tuple[str, Dict[str, Tuple[str, ...]]] = (
    "Visit Schedule",
    {"classes": ("collapse",), "fields": visit_schedule_fields},
)

visit_schedule_only_fields: Tuple[str, ...] = (
    "visit_schedule_name",
    "schedule_name",
)

visit_schedule_only_fieldset_tuple: Tuple[str, Dict[str, Tuple[str, ...]]] = (
    "Visit Schedule",
    {"classes": ("collapse",), "fields": visit_schedule_only_fields},
)

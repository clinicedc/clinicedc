visit_schedule_fields: tuple[str, ...] = (
    "visit_schedule_name",
    "schedule_name",
    "visit_code",
)

visit_schedule_fieldset_tuple: tuple[str, dict[str, tuple[str, ...]]] = (
    "Visit Schedule",
    {"classes": ("collapse",), "fields": visit_schedule_fields},
)

visit_schedule_only_fields: tuple[str, ...] = (
    "visit_schedule_name",
    "schedule_name",
)

visit_schedule_only_fieldset_tuple: tuple[str, dict[str, tuple[str, ...]]] = (
    "Visit Schedule",
    {"classes": ("collapse",), "fields": visit_schedule_only_fields},
)

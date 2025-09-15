requisition_fieldset: tuple[str, dict[str, tuple[str, ...]]] = (
    "Requisition",
    {
        "fields": (
            "is_drawn",
            "reason_not_drawn",
            "reason_not_drawn_other",
            "drawn_datetime",
            "item_type",
            "item_count",
            "estimated_volume",
            "comments",
        )
    },
)


requisition_status_fields: tuple[str, ...] = (
    "received",
    "received_datetime",
    "processed",
    "processed_datetime",
    "packed",
    "packed_datetime",
    "shipped",
    "shipped_datetime",
)

requisition_verify_fields: tuple[str, ...] = (
    "clinic_verified",
    "clinic_verified_datetime",
)

requisition_status_fieldset: tuple[str, dict[str, tuple[str, ...]]] = (
    "Status (For laboratory use only)",
    {"classes": ("collapse",), "fields": requisition_status_fields},
)


requisition_identifier_fields: tuple[str, ...] = (
    "requisition_identifier",
    "identifier_prefix",
    "primary_aliquot_identifier",
)

requisition_identifier_fieldset: tuple[str, dict[str, tuple[str, ...]]] = (
    "Identifiers",
    {"classes": ("collapse",), "fields": requisition_identifier_fields},
)

requisition_verify_fieldset: tuple[str, dict[str, tuple[str, ...]]] = (
    "Verification",
    {"classes": ("collapse",), "fields": requisition_verify_fields},
)

from typing import Dict, Tuple

requisition_fieldset: Tuple[str, Dict[str, Tuple[str, ...]]] = (
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


requisition_status_fields: Tuple[str, ...] = (
    "received",
    "received_datetime",
    "processed",
    "processed_datetime",
    "packed",
    "packed_datetime",
    "shipped",
    "shipped_datetime",
)

requisition_verify_fields: Tuple[str, ...] = ("clinic_verified", "clinic_verified_datetime")

requisition_status_fieldset: Tuple[str, Dict[str, Tuple[str, ...]]] = (
    "Status (For laboratory use only)",
    {"classes": ("collapse",), "fields": requisition_status_fields},
)


requisition_identifier_fields: Tuple[str, ...] = (
    "requisition_identifier",
    "identifier_prefix",
    "primary_aliquot_identifier",
)

requisition_identifier_fieldset: Tuple[str, Dict[str, Tuple[str, ...]]] = (
    "Identifiers",
    {"classes": ("collapse",), "fields": requisition_identifier_fields},
)

requisition_verify_fieldset: Tuple[str, Dict[str, Tuple[str, ...]]] = (
    "Verification",
    {"classes": ("collapse",), "fields": requisition_verify_fields},
)

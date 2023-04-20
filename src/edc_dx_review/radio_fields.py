from typing import Dict

from django.contrib import admin
from edc_dx import get_diagnosis_labels_prefixes


def get_clinical_review_cond_radio_fields() -> Dict[str, int]:
    radio_fields = {}
    for prefix in get_diagnosis_labels_prefixes():
        cond = prefix.lower()
        radio_fields.update(
            {
                f"{cond}_dx": admin.VERTICAL,
                f"{cond}_test": admin.VERTICAL,
            }
        )
    return radio_fields


def get_clinical_review_baseline_cond_radio_fields() -> Dict[str, int]:
    radio_fields = {}
    for prefix in get_diagnosis_labels_prefixes():
        cond = prefix.lower()
        radio_fields.update(
            {
                f"{cond}_dx": admin.VERTICAL,
                f"{cond}_dx_at_screening": admin.VERTICAL,
            }
        )
    return radio_fields

from edc_dx import get_diagnosis_labels


def get_clinical_review_baseline_cond_fieldset(
    cond: str, title: str = None
) -> tuple[str, dict]:
    if not title:
        title = cond.upper()
    return (
        title,
        {"fields": (f"{cond}_dx", f"{cond}_dx_at_screening")},
    )


def get_clinical_review_baseline_cond_fieldsets() -> tuple[tuple]:
    fieldsets = ()
    for prefix, label in get_diagnosis_labels().items():
        fieldsets = fieldsets + (
            get_clinical_review_baseline_cond_fieldset(cond=prefix.lower(), title=label),
        )
    return fieldsets


def get_clinical_review_cond_fieldset(cond: str, title: str = None) -> tuple[str, dict]:
    if not title:
        title = cond.upper()
    return (
        title,
        {
            "fields": (
                f"{cond}_test",
                f"{cond}_test_date",
                f"{cond}_reason",
                f"{cond}_reason_other",
                f"{cond}_dx",
            )
        },
    )


def get_clinical_review_cond_fieldsets() -> tuple[tuple]:
    fieldsets = ()
    for prefix, label in get_diagnosis_labels().items():
        fieldsets = fieldsets + (
            get_clinical_review_cond_fieldset(cond=prefix.lower(), title=label),
        )
    return fieldsets

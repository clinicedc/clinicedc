from __future__ import annotations

from django.utils.translation import gettext as _

from edc_model_admin.list_filters import (
    ListFieldWithOtherListFilter,
    PastDateListFilter,
)


class AeAwarenessListFilter(PastDateListFilter):
    title = _("Awareness date")

    parameter_name = "ae_awareness_date"
    field_name = "ae_awareness_date"


class DeathDateListFilter(PastDateListFilter):
    title = _("Death date")

    parameter_name = "death_datetime"
    field_name = "death_datetime"


class CauseOfDeathListFilter(ListFieldWithOtherListFilter):
    title = "Cause of death"
    parameter_name = "cause_of_death"
    other_parameter_name = "cause_of_death_other"


class AeClassificationListFilter(ListFieldWithOtherListFilter):
    title = "Classification"
    parameter_name = "ae_classification"
    other_parameter_name = "ae_classification_other"

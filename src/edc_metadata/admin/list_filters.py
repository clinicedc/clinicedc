from django.utils.translation import gettext as _
from edc_model_admin.list_filters import FutureDateListFilter


class CreatedListFilter(FutureDateListFilter):
    title = _("Created")

    parameter_name = "created"
    field_name = "created"


class DueDatetimeListFilter(FutureDateListFilter):
    title = _("Due")

    parameter_name = "due_datetime"
    field_name = "due_datetime"


class FillDatetimeListFilter(FutureDateListFilter):
    title = _("Keyed")

    parameter_name = "fill_datetime"
    field_name = "fill_datetime"

from django.utils.translation import gettext as _

from .past_date_list_filter import PastDateListFilter


class ReportDateListFilter(PastDateListFilter):
    title = _("Report date")

    parameter_name = "report_datetime"
    field_name = "report_datetime"

from django.utils.translation import gettext_lazy as _

crf_status_fieldset = (
    _("CRF Status"),
    {"classes": ("collapse",), "fields": ["crf_status", "crf_status_comments"]},
)

from django.contrib import admin
from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch
from django_audit_fields.admin import audit_fieldset_tuple

from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_model_admin.history import SimpleHistoryAdmin
from edc_sites.admin import SiteModelAdminMixin

from .admin_site import edc_refusal_admin
from .forms import SubjectRefusalForm
from .models import SubjectRefusal


class SubjectRefusalModelAdminMixin:
    fieldsets = (
        [
            None,
            {
                "fields": (
                    "screening_identifier",
                    "report_datetime",
                    "reason",
                    "other_reason",
                    "comment",
                )
            },
        ],
        audit_fieldset_tuple,
    )

    list_display = (
        "screening_identifier",
        "report_datetime",
        "reason",
        "user_created",
        "created",
    )

    list_filter = ("report_datetime", "reason")

    search_fields = ("screening_identifier",)

    radio_fields = {"reason": admin.VERTICAL}


@admin.register(SubjectRefusal, site=edc_refusal_admin)
class SubjectRefusalAdmin(
    SiteModelAdminMixin,
    SubjectRefusalModelAdminMixin,
    ModelAdminSubjectDashboardMixin,
    SimpleHistoryAdmin,
):
    form = SubjectRefusalForm

    post_url_on_delete_name = "screening_listboard_url"
    subject_listboard_url_name = "screening_listboard_url"
    subject_dashboard_url_name = "screening_listboard_url"

    def get_subject_dashboard_url_kwargs(self, obj):
        return dict(screening_identifier=obj.screening_identifier)

    def view_on_site(self, obj):
        try:
            url = reverse(
                self.get_subject_dashboard_url_name(),
                kwargs=self.get_subject_dashboard_url_kwargs(obj),
            )
        except NoReverseMatch as e:
            if callable(super().view_on_site):
                url = super().view_on_site(obj)
            else:
                raise NoReverseMatch(f"{e}. See subject_dashboard_url_name for {self!r}.")
        return url

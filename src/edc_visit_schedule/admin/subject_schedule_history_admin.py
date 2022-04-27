from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext as _
from edc_dashboard import url_names
from edc_model_admin import audit_fieldset_tuple
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin

from ..admin_site import edc_visit_schedule_admin
from ..forms import SubjectScheduleHistoryForm
from ..models import SubjectScheduleHistory


@admin.register(SubjectScheduleHistory, site=edc_visit_schedule_admin)
class SubjectScheduleHistoryAdmin(ModelAdminSubjectDashboardMixin, admin.ModelAdmin):

    form = SubjectScheduleHistoryForm

    date_hierarchy = "onschedule_datetime"

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "subject_identifier",
                    "visit_schedule_name",
                    "schedule_name",
                    "schedule_status",
                    "onschedule_datetime",
                    "offschedule_datetime",
                    "onschedule_model",
                    "offschedule_model",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "subject_identifier",
        "dashboard",
        "review",
        "visit_schedule_name",
        "schedule_name",
        "schedule_status",
        "onschedule_datetime",
        "offschedule_datetime",
    )

    list_filter = (
        "schedule_status",
        "onschedule_datetime",
        "offschedule_datetime",
        "visit_schedule_name",
        "schedule_name",
    )

    search_fields = ("subject_identifier",)

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj=obj)
        fields = (
            list(fields)
            + [
                "subject_identifier",
                "visit_schedule_name",
                "schedule_name",
                "schedule_status",
                "onschedule_datetime",
                "offschedule_datetime",
                "onschedule_model",
                "offschedule_model",
            ]
            + list(audit_fieldset_tuple[1].get("fields"))
        )
        return fields

    def dashboard(self, obj=None, label=None):
        try:
            url = reverse(
                self.get_subject_dashboard_url_name(),
                kwargs=self.get_subject_dashboard_url_kwargs(obj),
            )
        except NoReverseMatch:
            url = reverse(url_names.get("screening_listboard_url"), kwargs={})
            context = dict(
                title=_("Go to screening listboard"),
                url=f"{url}?q={obj.screening_identifier}",
                label=label,
            )
        else:
            context = dict(title=_("Go to subject dashboard"), url=url, label=label)
        return render_to_string("dashboard_button.html", context=context)

    def review(self, obj=None):
        try:
            url = (
                f"{reverse('edc_review_dashboard:subject_review_listboard_url')}?"
                f"q={obj.subject_identifier}"
            )
        except NoReverseMatch:
            context = {}
        else:
            context = dict(title=_("Go to subject review dashboard"), url=url)
        return render_to_string(
            "edc_review_dashboard/subject_review_button.html", context=context
        )

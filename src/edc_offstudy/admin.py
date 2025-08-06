from django.contrib import admin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin
from edc_model_admin.history import SimpleHistoryAdmin

from .admin_site import edc_offstudy_admin
from .models import SubjectOffstudy


@admin.register(SubjectOffstudy, site=edc_offstudy_admin)
class SubjectOffstudyAdmin(ModelAdminSubjectDashboardMixin, SimpleHistoryAdmin):
    fieldsets = (
        [
            None,
            {
                "fields": (
                    "subject_identifier",
                    "offstudy_datetime",
                )
            },
        ],
        [
            "Off-study reason",
            {
                "fields": (
                    "offstudy_reason",
                    "other_offstudy_reason",
                )
            },
        ],
        [
            "Comments",
            {"fields": ("comment",)},
        ],
    )

    list_filter = ("offstudy_datetime",)

    radio_fields = {
        "offstudy_reason": admin.VERTICAL,
    }

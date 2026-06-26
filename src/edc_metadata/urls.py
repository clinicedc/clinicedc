from django.urls import path

from .admin_site import edc_metadata_admin
from .views import (
    DeleteReviewFilterView,
    ExportOverviewView,
    HomeView,
    ManageMissingFlaggedReportView,
    ManageMissingFlagUnFlagView,
    ManageMissingView,
    SaveReviewFilterView,
)

app_name = "edc_metadata"

urlpatterns = [
    path("admin/", edc_metadata_admin.urls),
    path(
        "manage-missing/",
        ManageMissingView.as_view(),
        name="manage_missing_url",
    ),
    path(
        "manage-missing/flag-unflag/<str:subject_identifier>/<str:visit_schedule_name>/"
        "<str:schedule_name>/<str:visit_code>/",
        ManageMissingFlagUnFlagView.as_view(),
        name="manage_missing_by_subject_url",
    ),
    path(
        "manage-missing/bysubject/<str:subject_identifier>/",
        ManageMissingFlagUnFlagView.as_view(),
        name="manage_missing_by_subject_url",
    ),
    path(
        "manage-missing/flagged/",
        ManageMissingFlaggedReportView.as_view(),
        name="manage_missing_flagged_url",
    ),
    path(
        "manage-missing/filters/save/",
        SaveReviewFilterView.as_view(),
        name="manage_missing_save_filter_url",
    ),
    path(
        "manage-missing/filters/delete/",
        DeleteReviewFilterView.as_view(),
        name="manage_missing_delete_filter_url",
    ),
    path(
        "manage-missing/overview-export/",
        ExportOverviewView.as_view(),
        name="manage_missing_export_overview_url",
    ),
    path("", HomeView.as_view(), name="home_url"),
]

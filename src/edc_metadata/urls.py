from django.urls import path

from .admin_site import edc_metadata_admin
from .views import (
    DeleteReviewFilterView,
    ExportLeaderboardView,
    HomeView,
    ReviewOutstandingDetailView,
    ReviewOutstandingFlaggedView,
    ReviewOutstandingGridView,
    SaveReviewFilterView,
)

app_name = "edc_metadata"

urlpatterns = [
    path("admin/", edc_metadata_admin.urls),
    path("review-outstanding/", ReviewOutstandingGridView.as_view(), name="review_grid_url"),
    path(
        "review-outstanding/detail/<str:subject_identifier>/<str:visit_schedule_name>/"
        "<str:schedule_name>/<str:visit_code>/",
        ReviewOutstandingDetailView.as_view(),
        name="metadata_detail_url",
    ),
    path(
        "review-outstanding/unavailable/",
        ReviewOutstandingFlaggedView.as_view(),
        name="unavailable_report_url",
    ),
    path(
        "review-outstanding/filters/save/",
        SaveReviewFilterView.as_view(),
        name="save_filter_url",
    ),
    path(
        "review-outstanding/filters/delete/",
        DeleteReviewFilterView.as_view(),
        name="delete_filter_url",
    ),
    path(
        "review-outstanding/leaderboard-export/",
        ExportLeaderboardView.as_view(),
        name="export_leaderboard_url",
    ),
    path("", HomeView.as_view(), name="home_url"),
]

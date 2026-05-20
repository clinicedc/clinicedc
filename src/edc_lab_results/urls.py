from django.urls.conf import path

from .admin_site import edc_lab_results_admin
from .views import (
    HomeView,
    OrderDetailView,
    SubjectResultsView,
    UploadView,
    VisitsForSubjectView,
)

app_name = "edc_lab_results"

urlpatterns = [
    path("admin/", edc_lab_results_admin.urls),
    path(
        "results/",
        SubjectResultsView.as_view(),
        name="subject-results",
    ),
    path(
        "results/order/<str:order_no>/",
        OrderDetailView.as_view(),
        name="order-detail",
    ),
    path(
        "upload/",
        UploadView.as_view(),
        name="upload",
    ),
    path(
        "api/visits-for-subject/",
        VisitsForSubjectView.as_view(),
        name="visits-for-subject",
    ),
    path(
        "",
        HomeView.as_view(),
        name="home_url",
    ),
]

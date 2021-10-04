from django.contrib import admin
from django.urls import path
from edc_data_manager.views import HomeView
from edc_protocol import Protocol

from .views import SubjectReviewListboardView

app_name = "edc_review_dashboard"

urlpatterns = SubjectReviewListboardView.urls(
    namespace=app_name,
    label="subject_review_listboard",
    identifier_pattern=Protocol().subject_identifier_pattern,
)

urlpatterns += [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home_url"),
]

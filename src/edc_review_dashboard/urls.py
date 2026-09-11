from django.contrib import admin
from django.urls import path

from edc_data_manager.views import HomeView
from edc_protocol.trial_settings import trial_settings

from .views import SubjectReviewListboardView

app_name = "edc_review_dashboard"

urlpatterns = SubjectReviewListboardView.urls(
    namespace=app_name,
    url_names_key="subject_review_listboard_url",
    identifier_pattern=trial_settings.subject_identifier_pattern,
)

urlpatterns += [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home_url"),
]

# aliquot_listboard = ("edc_lab_dashboard:aliquot_listboard_url",)

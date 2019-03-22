from edc_dashboard.url_config import UrlConfig

from .views import SubjectReviewListboardView

app_name = "dashboard_app"

subject_review_listboard_url_config = UrlConfig(
    url_name='subject_review_listboard_url',
    view_class=SubjectReviewListboardView,
    label='subject_review_listboard',
    identifier_label='subject_identifier',
    identifier_pattern="\w+")

urlpatterns = subject_review_listboard_url_config.listboard_urls

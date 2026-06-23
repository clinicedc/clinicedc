from django.urls import path

from .admin_site import edc_metadata_admin
from .views import HomeView, MetadataReviewGridView

app_name = "edc_metadata"

urlpatterns = [
    path("admin/", edc_metadata_admin.urls),
    path("review/", MetadataReviewGridView.as_view(), name="review_grid_url"),
    path("", HomeView.as_view(), name="home_url"),
]

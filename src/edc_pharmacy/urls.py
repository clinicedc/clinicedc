from django.urls import path
from django.views.generic.base import RedirectView

from .admin_site import edc_pharmacy_admin
from .views import AllocateToSubjectView, ConfirmStockView

app_name = "edc_pharmacy"

urlpatterns = [
    path(
        "allocate/<uuid:stock_request_id>/$",
        AllocateToSubjectView.as_view(),
        name="allocate_url",
    ),
    path(
        "confirm_stock/<str:model>/<uuid:source_pk>/$",
        ConfirmStockView.as_view(),
        name="confirm_stock_url",
    ),
    path("admin/", edc_pharmacy_admin.urls),
    path("", RedirectView.as_view(url="admin/"), name="home_url"),
]

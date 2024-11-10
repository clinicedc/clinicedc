from django.urls import path, re_path
from django.views.generic.base import RedirectView

from .admin_site import edc_pharmacy_admin
from .views import ConfirmStockView, RelabelView

app_name = "edc_pharmacy"

urlpatterns = [
    re_path(
        "relabel/(?P<fulfillment_identifier>[0-9]{6,36})/$",
        RelabelView.as_view(),
        name="relabel_url",
    ),
    path(
        "confirm_stock/<str:model>/<uuid:source_pk>/$",
        ConfirmStockView.as_view(),
        name="confirm_stock_url",
    ),
    path("admin/", edc_pharmacy_admin.urls),
    path("", RedirectView.as_view(url="admin/"), name="home_url"),
]

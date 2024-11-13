from django.urls import path

from .admin_site import edc_pharmacy_admin
from .views import (
    AllocateToSubjectView,
    ConfirmStockView,
    HomeView,
    PrintLabelsView,
    TransferStockView,
)

app_name = "edc_pharmacy"


urlpatterns = [
    path(
        "allocate/<uuid:stock_request_id>/<uuid:assignment_id>",
        AllocateToSubjectView.as_view(),
        name="allocate_url",
    ),
    path(
        "allocate/<uuid:stock_request_id>/",
        AllocateToSubjectView.as_view(),
        name="allocate_url",
    ),
    path(
        "confirm_stock/<str:model>/<uuid:source_pk>/",
        ConfirmStockView.as_view(),
        name="confirm_stock_url",
    ),
    path(
        "transfer_stock/<uuid:stock_transfer>/",
        TransferStockView.as_view(),
        name="transfer_stock_url",
    ),
    path(
        "print_labels/<str:model>/<uuid:session_uuid>/",
        PrintLabelsView.as_view(),
        name="print_labels_url",
    ),
    path("admin/", edc_pharmacy_admin.urls),
    path("", HomeView.as_view(), name="home_url"),
]

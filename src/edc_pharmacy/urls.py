from django.urls import path

from .admin_site import edc_pharmacy_admin
from .views import (
    AllocateToSubjectView,
    ConfirmStockFromInstanceView,
    ConfirmStockFromQuerySetView,
    HomeView,
    PrepareAndReviewStockRequestView,
    PrintLabelsView,
    TransferStockView,
)

app_name = "edc_pharmacy"


urlpatterns = [
    path(
        "allocate/<uuid:stock_request>/<uuid:assignment>",
        AllocateToSubjectView.as_view(),
        name="allocate_url",
    ),
    path(
        "confirm_stock/<str:model>/<uuid:source_pk>/",
        ConfirmStockFromInstanceView.as_view(),
        name="confirm_stock_from_instance_url",
    ),
    path(
        "allocate/<uuid:stock_request>/",
        AllocateToSubjectView.as_view(),
        name="allocate_url",
    ),
    path(
        "confirm_stock_qs/<uuid:session_uuid>/",
        ConfirmStockFromQuerySetView.as_view(),
        name="confirm_stock_from_queryset_url",
    ),
    path(
        "transfer_stock/<uuid:stock_transfer>/",
        TransferStockView.as_view(),
        name="transfer_stock_url",
    ),
    path(
        "review_stock_request/<uuid:stock_request>/<uuid:session_uuid>/",
        PrepareAndReviewStockRequestView.as_view(),
        name="review_stock_request_url",
    ),
    path(
        "review_stock_request/<uuid:stock_request>/",
        PrepareAndReviewStockRequestView.as_view(),
        name="review_stock_request_url",
    ),
    path(
        "print_labels/<str:model>/<uuid:session_uuid>/",
        PrintLabelsView.as_view(),
        name="print_labels_url",
    ),
    path("admin/", edc_pharmacy_admin.urls),
    path("", HomeView.as_view(), name="home_url"),
]

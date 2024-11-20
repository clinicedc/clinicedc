from django.urls import path

from .admin_site import edc_pharmacy_admin
from .views import (
    AllocateToSubjectView,
    CeleryTaskStatusView,
    ConfirmStockFromQuerySetView,
    DispenseView,
    HomeView,
    PrepareAndReviewStockRequestView,
    PrintLabelsView,
    StockTransferConfirmationView,
    TransferStockView,
    print_stock_transfer_manifest_view,
)

app_name = "edc_pharmacy"


urlpatterns = [
    path(
        "dispense/<int:location_id>/<uuid:formulation_id>/"
        "<str:subject_identifier>/<int:container_count>/",
        DispenseView.as_view(),
        name="dispense_url",
    ),
    path(
        "stock-transfer-confirmation/<int:location_id>/<int:items_to_scan>/",
        StockTransferConfirmationView.as_view(),
        name="stock_transfer_confirmation_url",
    ),
    path(
        "review-stock-request/<uuid:stock_request>/<uuid:session_uuid>/",
        PrepareAndReviewStockRequestView.as_view(),
        name="review_stock_request_url",
    ),
    path(
        "allocate/<uuid:stock_request>/<uuid:assignment>/",
        AllocateToSubjectView.as_view(),
        name="allocate_url",
    ),
    path(
        "allocate/<uuid:stock_request>/<uuid:assignment>",
        AllocateToSubjectView.as_view(),
        name="allocate_url",
    ),
    # path(
    #     "confirm-stock/<str:model>/<uuid:source_pk>/",
    #     ConfirmStockFromInstanceView.as_view(),
    #     name="confirm_stock_from_instance_url",
    # ),
    path(
        "confirm-stock-qs/<uuid:session_uuid>/",
        ConfirmStockFromQuerySetView.as_view(),
        name="confirm_stock_from_queryset_url",
    ),
    path(
        "allocate/<uuid:stock_request>/",
        AllocateToSubjectView.as_view(),
        name="allocate_url",
    ),
    path(
        "transfer-stock/<uuid:stock_transfer>/",
        TransferStockView.as_view(),
        name="transfer_stock_url",
    ),
    path(
        "review-stock-request/<uuid:stock_request>/",
        PrepareAndReviewStockRequestView.as_view(),
        name="review_stock_request_url",
    ),
    path(
        "print-labels/<str:model>/<uuid:session_uuid>/",
        PrintLabelsView.as_view(),
        name="print_labels_url",
    ),
    path(
        "manifest/<uuid:stock_transfer>/",
        print_stock_transfer_manifest_view,
        name="generate_manifest",
    ),
    path(
        "task-status/<uuid:task_id>/",
        CeleryTaskStatusView.as_view(),
        name="celery_task_status_url",
    ),
    path(
        "stock-transfer-confirmation/",
        StockTransferConfirmationView.as_view(),
        name="stock_transfer_confirmation_url",
    ),
    path(
        "dispense/",
        DispenseView.as_view(),
        name="dispense_url",
    ),
    path("admin/", edc_pharmacy_admin.urls),
    path("", HomeView.as_view(), name="home_url"),
]

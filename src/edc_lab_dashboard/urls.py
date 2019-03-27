from django.urls.conf import path, re_path
from edc_dashboard.url_names import url_names

from .dashboard_urls import dashboard_urls
from .views import (
    HomeView,
    RequisitionListboardView,
    AliquotListboardView,
    ResultListboardView,
    ReceiveView,
    ProcessView,
    ManifestListboardView,
    ReceiveListboardView,
    PackListboardView,
    ManageBoxListboardView,
    VerifyBoxListboardView,
    ManageBoxItemView,
    VerifyBoxItemView,
    ProcessListboardView,
    PackView,
    ManageManifestView,
    ManageManifestListboardView,
    ManifestView,
    AliquotView,
    RequisitionView,
)


app_name = "edc_lab_dashboard"

urlpatterns = [
    # listboard urls
    re_path(
        "listboard/requisition/(?P<page>[0-9]+)/$",
        RequisitionListboardView.as_view(),
        name="requisition_listboard_url",
    ),
    path(
        "listboard/requisition/",
        RequisitionListboardView.as_view(),
        name="requisition_listboard_url",
    ),
    re_path(
        "listboard/receive/(?P<page>[0-9]+)/$",
        ReceiveListboardView.as_view(),
        name="receive_listboard_url",
    ),
    path(
        "listboard/receive/",
        ReceiveListboardView.as_view(),
        name="receive_listboard_url",
    ),
    re_path(
        "listboard/process/(?P<page>[0-9]+)/$",
        ProcessListboardView.as_view(),
        name="process_listboard_url",
    ),
    path(
        "listboard/process/",
        ProcessListboardView.as_view(),
        name="process_listboard_url",
    ),
    re_path(
        "listboard/pack/(?P<page>[0-9]+)/$",
        PackListboardView.as_view(),
        name="pack_listboard_url",
    ),
    path("listboard/pack/", PackListboardView.as_view(), name="pack_listboard_url"),
    re_path(
        "listboard/box/(?P<action_name>manage)/"
        "(?P<box_identifier>[A-Z0-9]+)/(?P<page>[0-9]+)/$",
        ManageBoxListboardView.as_view(),
        name="manage_box_listboard_url",
    ),
    re_path(
        "listboard/box/(?P<action_name>manage)/(?P<box_identifier>[A-Z0-9]+)/$",
        ManageBoxListboardView.as_view(),
        name="manage_box_listboard_url",
    ),
    re_path(
        "listboard/box/(?P<action_name>manage)/",
        ManageBoxListboardView.as_view(),
        name="manage_box_listboard_url",
    ),
    re_path(
        "listboard/box/(?P<action_name>verify)/"
        "(?P<box_identifier>[A-Z0-9]+)/"
        "(?P<position>[0-9]+)/(?P<page>[0-9]+)/$",
        VerifyBoxListboardView.as_view(),
        name="verify_box_listboard_url",
    ),
    re_path(
        "listboard/box/(?P<action_name>verify)/"
        "(?P<box_identifier>[A-Z0-9]+)/"
        "(?P<position>[0-9]+)/$",
        VerifyBoxListboardView.as_view(),
        name="verify_box_listboard_url",
    ),
    re_path(
        "listboard/box/(?P<action_name>verify)/" "(?P<position>[0-9]+)/$",
        VerifyBoxListboardView.as_view(),
        name="verify_box_listboard_url",
    ),
    re_path(
        "listboard/aliquot/(?P<page>[0-9]+)/$",
        AliquotListboardView.as_view(),
        name="aliquot_listboard_url",
    ),
    path(
        "listboard/aliquot/",
        AliquotListboardView.as_view(),
        name="aliquot_listboard_url",
    ),
    re_path(
        "listboard/manifest/(?P<action_name>manage)/"
        "(?P<manifest_identifier>[A-Z0-9]+)/(?P<page>[0-9]+)/$",
        ManageManifestListboardView.as_view(),
        name="manage_manifest_listboard_url",
    ),
    re_path(
        "listboard/manifest/(?P<action_name>manage)/(?P<manifest_identifier>[A-Z0-9]+)/$",
        ManageManifestListboardView.as_view(),
        name="manage_manifest_listboard_url",
    ),
    re_path(
        "listboard/manifest/(?P<action_name>manage)/$",
        ManageManifestListboardView.as_view(),
        name="manage_manifest_listboard_url",
    ),
    re_path(
        "listboard/manifest/(?P<page>[0-9]+)/$",
        ManifestListboardView.as_view(),
        name="manifest_listboard_url",
    ),
    path(
        "listboard/manifest/",
        ManifestListboardView.as_view(),
        name="manifest_listboard_url",
    ),
    re_path(
        "listboard/result/(?P<page>[0-9]+)/$",
        ResultListboardView.as_view(navbar_selected_item="result"),
        name="result_listboard_url",
    ),
    path(
        "listboard/result/",
        ResultListboardView.as_view(navbar_selected_item="result"),
        name="result_listboard_url",
    ),
    # action urls
    path("requisition/", RequisitionView.as_view(), name="requisition_form_action_url"),
    path("requisition/receive/", ReceiveView.as_view(), name="receive_form_action_url"),
    path("requisition/process/", ProcessView.as_view(), name="process_form_action_url"),
    path("requisition/pack/", PackView.as_view(), name="pack_form_action_url"),
    re_path(
        "box/(?P<box_identifier>[A-Z0-9]+)/(?P<action_name>manage)/$",
        ManageBoxItemView.as_view(),
        name="manage_box_item_form_action_url",
    ),
    re_path(
        "box/(?P<box_identifier>[A-Z0-9]+)/"
        "(?P<action_name>verify)/"
        "(?P<position>[0-9]+)/$",
        VerifyBoxItemView.as_view(),
        name="verify_box_item_form_action_url",
    ),
    path("manifest/", ManifestView.as_view(), name="manifest_form_action_url"),
    re_path(
        "manifest/(?P<manifest_identifier>[A-Z0-9]+)/(?P<action_name>manage)/$",
        ManageManifestView.as_view(),
        name="manage_manifest_item_form_action_url",
    ),
    path("aliquot/", AliquotView.as_view(), name="aliquot_form_action_url"),
    path("", HomeView.as_view(), name="home_url"),
]

url_names.register_from_dict(**dashboard_urls)

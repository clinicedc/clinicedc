from django.conf.urls import url

from .admin_site import edc_lab_admin
from .views import (
    HomeView, RequisitionListboardView, AliquotListboardView,
    ResultListboardView, ReceiveView, ProcessView,
    ManifestListboardView, ReceiveListboardView, PackListboardView,
    ManageBoxListboardView, VerifyBoxListboardView, ManageBoxItemView,
    VerifyBoxItemView, ProcessListboardView, PackView, ManifestView)

app_name = 'edc_lab'

urlpatterns = [
    url(r'^admin/', edc_lab_admin.urls),

    # listboard urls
    url(r'^listboard/requisition/$', RequisitionListboardView.as_view(),
        name='requisition_listboard_url'),
    url(r'^listboard/requisition/(?P<page>[0-9]+)/$', RequisitionListboardView.as_view(),
        name='requisition_listboard_url'),

    url(r'^listboard/receive/$', ReceiveListboardView.as_view(),
        name='receive_listboard_url'),
    url(r'^listboard/receive/(?P<page>[0-9]+)/$', ReceiveListboardView.as_view(),
        name='receive_listboard_url'),

    url(r'^listboard/process/$', ProcessListboardView.as_view(),
        name='process_listboard_url'),
    url(r'^listboard/process/(?P<page>[0-9]+)/$', ProcessListboardView.as_view(),
        name='process_listboard_url'),

    url(r'^listboard/pack/$', PackListboardView.as_view(),
        name='pack_listboard_url'),
    url(r'^listboard/pack/(?P<page>[0-9]+)/$', PackListboardView.as_view(),
        name='pack_listboard_url'),

    url(r'^listboard/box/(?P<action_name>manage)/(?P<box_identifier>[A-Z0-9]+)/(?P<page>[0-9]+)/$',
        ManageBoxListboardView.as_view(),
        name='manage_box_listboard_url'),
    url(r'^listboard/box/(?P<action_name>manage)/(?P<box_identifier>[A-Z0-9]+)/$',
        ManageBoxListboardView.as_view(),
        name='manage_box_listboard_url'),
    url(r'^listboard/box/(?P<action_name>manage)/$', ManageBoxListboardView.as_view(),
        name='manage_box_listboard_url'),

    url(r'^listboard/box/(?P<action_name>verify)/'
        '(?P<box_identifier>[A-Z0-9]+)/'
        '(?P<position>[0-9]+)/(?P<page>[0-9]+)/$',
        VerifyBoxListboardView.as_view(),
        name='verify_box_listboard_url'),
    url(r'^listboard/box/(?P<action_name>verify)/'
        '(?P<box_identifier>[A-Z0-9]+)/'
        '(?P<position>[0-9]+)/$',
        VerifyBoxListboardView.as_view(),
        name='verify_box_listboard_url'),
    url(r'^listboard/box/(?P<action_name>verify)/'
        '(?P<position>[0-9]+)/$',
        VerifyBoxListboardView.as_view(),
        name='verify_box_listboard_url'),

    url(r'^listboard/aliquot/$', AliquotListboardView.as_view(),
        name='aliquot_listboard_url'),
    url(r'^listboard/aliquot/(?P<page>[0-9]+)/$', AliquotListboardView.as_view(),
        name='aliquot_listboard_url'),

    url(r'^listboard/manifest/$', ManifestListboardView.as_view(),
        name='manifest_listboard_url'),
    url(r'^listboard/manifest/(?P<page>[0-9]+)/$', ManifestListboardView.as_view(),
        name='manifest_listboard_url'),

    url(r'^listboard/result/$', ResultListboardView.as_view(
        navbar_item_selected='result'),
        name='result_listboard_url'),
    url(r'^listboard/result/(?P<page>[0-9]+)/$', ResultListboardView.as_view(
        navbar_item_selected='result'),
        name='result_listboard_url'),

    # action urls
    url(r'^requisition/receive/$', ReceiveView.as_view(), name='receive_url'),
    url(r'^requisition/process/$', ProcessView.as_view(), name='process_url'),
    url(r'^requisition/pack/$', PackView.as_view(), name='pack_url'),
    url(r'^box/(?P<box_identifier>[A-Z0-9]+)/(?P<action_name>manage)/$',
        ManageBoxItemView.as_view(), name='manage_box_item_url'),
    url(r'^box/(?P<box_identifier>[A-Z0-9]+)/'
        '(?P<action_name>verify)/'
        '(?P<position>[0-9]+)/$',
        VerifyBoxItemView.as_view(), name='verify_box_item_url'),
    url(r'^requisition/manifest/$',
        ManifestView.as_view(), name='manifest_url'),

    url(r'^', HomeView.as_view(), name='home_url'),
]

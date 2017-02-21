from django.conf.urls import url

from .admin_site import edc_lab_admin
from .views import (
    HomeView, RequisitionListboardView, AliquotListboardView,
    ResultListboardView, ReceiveView, ProcessView, PackView,
    ManifestListboardView, ReceiveListboardView, PackListboardView,
    BoxListboardView, BoxItemView)

requisition_opts = dict(
    show_all=True,
    navbar_item_selected='requisition')

process_opts = dict(
    received=True,
    empty_queryset_message='All received specimens have been processed',
    action='process',
    action_url_name='edc-lab:process_url',
    listboard_url_name='edc-lab:process_listboard_url',
    search_form_action_url_name='edc-lab:process_listboard_url',
    navbar_item_selected='process')

aliquot_opts = dict(
    show_all=True,
    search_form_action_url_name='edc-lab:aliquot_listboard_url',
    navbar_item_selected='aliquot')

manifest_opts = dict(
    action='ship',
    action_url_name='edc-lab:ship_url',
    navbar_item_selected='manifest')

urlpatterns = [
    url(r'^admin/', edc_lab_admin.urls),

    url(r'^listboard/requisition/$', RequisitionListboardView.as_view(
        **requisition_opts),
        name='requisition_listboard_url'),
    url(r'^listboard/requisition/(?P<page>[0-9]+)/$', RequisitionListboardView.as_view(
        **requisition_opts),
        name='requisition_listboard_url'),

    url(r'^listboard/receive/$', ReceiveListboardView.as_view(),
        name='receive_listboard_url'),
    url(r'^listboard/receive/(?P<page>[0-9]+)/$', ReceiveListboardView.as_view(),
        name='receive_listboard_url'),

    url(r'^listboard/process/$', RequisitionListboardView.as_view(
        **process_opts),
        name='process_listboard_url'),
    url(r'^listboard/process/(?P<page>[0-9]+)/$', RequisitionListboardView.as_view(
        **process_opts),
        name='process_listboard_url'),

    url(r'^listboard/pack/$', PackListboardView.as_view(),
        name='pack_listboard_url'),
    url(r'^listboard/pack/(?P<page>[0-9]+)/$', PackListboardView.as_view(),
        name='pack_listboard_url'),

    url(r'^listboard/box/(?P<box_identifier>[A-Z0-9]+)/(?P<page>[0-9]+)/$', BoxListboardView.as_view(),
        name='box_listboard_url'),
    url(r'^listboard/box/(?P<box_identifier>[A-Z0-9]+)/$', BoxListboardView.as_view(),
        name='box_listboard_url'),
    url(r'^listboard/box/$', BoxListboardView.as_view(),
        name='box_listboard_url'),

    url(r'^listboard/aliquot/$', AliquotListboardView.as_view(
        **aliquot_opts),
        name='aliquot_listboard_url'),
    url(r'^listboard/aliquot/(?P<page>[0-9]+)/$', AliquotListboardView.as_view(
        **aliquot_opts),
        name='aliquot_listboard_url'),

    url(r'^listboard/manifest/$', ManifestListboardView.as_view(
        **manifest_opts),
        name='manifest_listboard_url'),
    url(r'^listboard/manifest/(?P<page>[0-9]+)/$', ManifestListboardView.as_view(
        **manifest_opts),
        name='manifest_listboard_url'),

    url(r'^listboard/result/$', ResultListboardView.as_view(
        navbar_item_selected='result'),
        name='result_listboard_url'),
    url(r'^listboard/result/(?P<page>[0-9]+)/$', ResultListboardView.as_view(
        navbar_item_selected='result'),
        name='result_listboard_url'),

    url(r'^requisition/receive/$', ReceiveView.as_view(), name='receive_url'),
    url(r'^requisition/process/$', ProcessView.as_view(), name='process_url'),
    url(r'^requisition/receive_and_process/$',
        ReceiveView.as_view(receive_and_process=True), name='receive_and_process_url'),
    url(r'^aliquot/pack/', PackView.as_view(), name='pack_aliquots_url'),
    url(r'^requisition/ship/$', ProcessView.as_view(), name='ship_url'),
    url(r'^box/(?P<box_identifier>[A-Z0-9]+)/additem/$',
        BoxItemView.as_view(), name='add_boxitem_url'),

    url(r'^', HomeView.as_view(), name='home_url'),
]

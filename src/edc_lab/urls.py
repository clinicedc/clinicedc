from django.conf.urls import url

from .admin_site import edc_lab_admin
from .views import HomeView
from edc_lab.views import (
    RequisitionListboardView, AliquotListboardView, ResultListboardView,
    ReceiveView, ProcessView, PackView, ManifestListboardView)

urlpatterns = [
    url(r'^admin/', edc_lab_admin.urls),
    url(r'^listboard/requisition/', RequisitionListboardView.as_view(
        show_all=True,
        navbar_item_selected='requisition'),
        name='requisition_listboard_url'),
    url(r'^listboard/receive/', RequisitionListboardView.as_view(
        empty_queryset_message='All specimens have been received',
        action='receive',
        action_url_name='edc-lab:receive_url',
        search_form_action_url_name='edc-lab:receive_listboard_url',
        navbar_item_selected='receive'),
        name='receive_listboard_url'),
    url(r'^listboard/process/', RequisitionListboardView.as_view(
        received=True,
        empty_queryset_message='All received specimens have been processed',
        action='process',
        action_url_name='edc-lab:process_url',
        search_form_action_url_name='edc-lab:process_listboard_url',
        navbar_item_selected='process'),
        name='process_listboard_url'),

    url(r'^listboard/pack/', AliquotListboardView.as_view(
        packed=False, shipped=False,
        search_form_action_url_name='edc-lab:pack_listboard_url',
        navbar_item_selected='pack'),
        name='pack_listboard_url'),
    url(r'^listboard/aliquot/', AliquotListboardView.as_view(
        show_all=True,
        search_form_action_url_name='edc-lab:aliquot_listboard_url',
        navbar_item_selected='aliquot'),
        name='aliquot_listboard_url'),

    url(r'^listboard/manifest/', ManifestListboardView.as_view(
        action='ship',
        action_url_name='edc-lab:ship_url',
        navbar_item_selected='manifest'),
        name='manifest_listboard_url'),
    url(r'^listboard/result/', ResultListboardView.as_view(
        navbar_item_selected='result'),
        name='result_listboard_url'),
    url(r'^requisition/receive/', ReceiveView.as_view(), name='receive_url'),
    url(r'^requisition/process/', ProcessView.as_view(), name='process_url'),
    url(r'^aliquot/pack/', PackView.as_view(),
        name='pack_aliquots_url'),
    url(r'^requisition/ship/', ProcessView.as_view(), name='ship_url'),
    url(r'^', HomeView.as_view(), name='home_url'),
]

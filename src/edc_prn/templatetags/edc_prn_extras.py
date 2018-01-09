from django import template
from django.core.exceptions import ObjectDoesNotExist

from ..site_prn_forms import site_prn_forms

register = template.Library()


@register.inclusion_tag('edc_prn/prn_list_items.html')
def prn_list_items(subject_identifier, **kwargs):
    prn_forms = []
    for prn in site_prn_forms:
        if prn.get_show_on_dashboard(subject_identifier=subject_identifier):
            prn_forms.append(prn)
    return dict(prn_forms=prn_forms, subject_identifier=subject_identifier)


@register.inclusion_tag('edc_prn/toggle_prn_popover.html')
def toggle_prn_crf_popover(appointment, subject_dashboard_url):
    prn_forms = []
    if appointment.visit.visit_code_sequence != 0:
        crfs_prn = appointment.visits.get(
            appointment.visit_code).crfs_unscheduled
    else:
        crfs_prn = appointment.visits.get(appointment.visit_code).crfs_prn

    for crf in crfs_prn:
        try:
            crf.model_cls.objects.get(
                **{crf.model_cls.visit_model_attr(): appointment.visit})
        except ObjectDoesNotExist:
            crf.add_url = crf.model_cls().get_absolute_url()
            crf.visit_model_attr = crf.model_cls.visit_model_attr()
            crf.subject_visit = str(appointment.visit.pk)
            prn_forms.append(crf)
    return dict(
        label='CRF',
        prn_forms=prn_forms,
        appointment_pk=str(appointment.pk),
        subject_identifier=appointment.subject_identifier,
        subject_dashboard_url=subject_dashboard_url)


@register.inclusion_tag('edc_prn/toggle_prn_popover.html')
def toggle_prn_requisition_popover(appointment, subject_dashboard_url):
    prn_forms = []
    if appointment.visit.visit_code_sequence != 0:
        requisitions_prn = appointment.visits.get(
            appointment.visit_code).requisitions_unscheduled
    else:
        requisitions_prn = appointment.visits.get(
            appointment.visit_code).requisitions_prn
    for requisition in requisitions_prn:
        try:
            requisition.model_cls.objects.get(
                **{requisition.model_cls.visit_model_attr(): appointment.visit,
                   'panel_name': requisition.panel.name})
        except ObjectDoesNotExist:
            requisition.add_url = requisition.model_cls().get_absolute_url()
            requisition.visit_model_attr = requisition.model_cls.visit_model_attr()
            requisition.subject_visit = str(appointment.visit.pk)
            prn_forms.append(requisition)
    return dict(
        label='Requisition',
        prn_forms=prn_forms,
        appointment_pk=str(appointment.pk),
        subject_identifier=appointment.subject_identifier,
        subject_dashboard_url=subject_dashboard_url)

from django import template
from django.core.exceptions import ObjectDoesNotExist
from edc_metadata.models import CrfMetadata, RequisitionMetadata
from edc_metadata.constants import REQUIRED, KEYED

from ..site_prn_forms import site_prn_forms

register = template.Library()

CRF = "CRF"
REQUISITION = "Requisition"


@register.inclusion_tag("edc_prn/list_prns.html")
def prn_list_items(subject_identifier, **kwargs):
    prn_forms = []
    for prn in site_prn_forms:
        if prn.get_show_on_dashboard(subject_identifier=subject_identifier):
            prn_forms.append(prn)
    return dict(prn_forms=prn_forms, subject_identifier=subject_identifier)


@register.inclusion_tag("edc_prn/add_prn_popover.html")
def add_prn_crf_popover(appointment, subject_dashboard_url):
    prn_forms = []
    for crf in appointment.visits.get(appointment.visit_code).crfs_prn:
        if not CrfMetadata.objects.filter(
            subject_identifier=appointment.subject_identifier,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            visit_code_sequence=appointment.visit_code_sequence,
            model=crf.model,
            entry_status__in=[REQUIRED, KEYED],
        ).exists():
            crf.add_url = crf.model_cls().get_absolute_url()
            crf.visit_model_attr = crf.model_cls.visit_model_attr()
            crf.subject_visit = str(appointment.visit.pk)
            prn_forms.append(crf)
    return dict(
        label=CRF,
        CRF=CRF,
        REQUISITION=REQUISITION,
        prn_forms=prn_forms,
        appointment_pk=str(appointment.pk),
        subject_identifier=appointment.subject_identifier,
        subject_dashboard_url=subject_dashboard_url,
    )


@register.inclusion_tag("edc_prn/add_prn_popover.html")
def add_prn_requisition_popover(appointment, subject_dashboard_url):
    prn_forms = []
    for requisition in appointment.visits.get(appointment.visit_code).requisitions_prn:
        try:
            RequisitionMetadata.objects.get(
                subject_identifier=appointment.subject_identifier,
                visit_schedule_name=appointment.visit_schedule_name,
                schedule_name=appointment.schedule_name,
                visit_code=appointment.visit_code,
                visit_code_sequence=appointment.visit_code_sequence,
                model=requisition.model,
                panel_name=requisition.panel.name,
                entry_status__in=[REQUIRED, KEYED],
            )
        except ObjectDoesNotExist:
            requisition.add_url = requisition.model_cls().get_absolute_url()
            requisition.visit_model_attr = requisition.model_cls.visit_model_attr()
            requisition.subject_visit = str(appointment.visit.pk)
            try:
                panel_id = requisition.model_cls.panel.field.remote_field.model.objects.get(
                    name=requisition.panel.name
                ).id
            except ObjectDoesNotExist:
                requisition.panel.id = None
                requisition.panel.pk = None
            else:
                requisition.panel.id = panel_id
                requisition.panel.pk = panel_id
            prn_forms.append(requisition)
    return dict(
        label=REQUISITION,
        CRF=CRF,
        REQUISITION=REQUISITION,
        prn_forms=prn_forms,
        appointment_pk=str(appointment.pk),
        subject_identifier=appointment.subject_identifier,
        subject_dashboard_url=subject_dashboard_url,
    )

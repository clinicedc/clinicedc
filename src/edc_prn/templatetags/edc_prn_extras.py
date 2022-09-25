from __future__ import annotations

from typing import TYPE_CHECKING

from django import template
from django.core.exceptions import ObjectDoesNotExist
from edc_metadata.constants import KEYED, REQUIRED
from edc_metadata.models import CrfMetadata, RequisitionMetadata

from ..site_prn_forms import site_prn_forms

if TYPE_CHECKING:
    from edc_appointment.models import Appointment
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
            subject_visit_id = getattr(appointment.related_visit, "pk", None)
            crf.add_url = crf.model_cls().get_absolute_url()
            crf.related_visit_model_attr = crf.model_cls.related_visit_model_attr()
            crf.related_visit = str(subject_visit_id) if subject_visit_id else None
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
def add_prn_requisition_popover(appointment: Appointment, subject_dashboard_url):
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
            requisition.related_visit_model_attr = (
                requisition.model_cls.related_visit_model_attr()
            )
            requisition.related_visit = str(getattr(appointment.related_visit, "id", ""))
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

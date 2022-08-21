from collections import namedtuple

from dateutil.relativedelta import relativedelta
from django import template
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.utils.html import format_html
from django.utils.translation import gettext as _
from edc_appointment.constants import (
    CANCELLED_APPT,
    COMPLETE_APPT,
    IN_PROGRESS_APPT,
    INCOMPLETE_APPT,
    NEW_APPT,
)
from edc_appointment.models import Appointment
from edc_constants.constants import COMPLETE
from edc_dashboard.utils import get_bootstrap_version
from edc_lab.models.manifest.consignee import Consignee
from edc_metadata import KEYED, REQUIRED
from edc_metadata.metadata_helper import MetadataHelper
from edc_utils import get_utcnow

register = template.Library()


class SubjectDashboardExtrasError(Exception):
    pass


@register.inclusion_tag(
    f"edc_subject_dashboard/bootstrap{get_bootstrap_version()}/forms_button.html"
)
def forms_button(wrapper=None):
    """wrapper is an AppointmentModelWrapper."""

    try:
        visit_pk = wrapper.wrapped_visit.object.id
    except AttributeError:
        visit_pk = None
    if visit_pk and wrapper.appt_status == IN_PROGRESS_APPT:
        btn_color = "btn-primary"
        title = ""
        fa_icon = "fas fa-list-alt"
        href = wrapper.forms_url
        label = _("Forms")
        label_fa_icon = "fas fa-share"
        visit_pk = str(visit_pk)
    else:
        btn_color = "btn-warning"
        title = _("Click to update the visit report")
        fa_icon = "fas fa-plus"
        href = wrapper.wrapped_visit.href
        label = _("Start visit")
        label_fa_icon = None
    btn_id = f"{label.lower()}_btn_{wrapper.visit_code}_{wrapper.visit_code_sequence}"
    return dict(
        btn_color=btn_color,
        btn_id=btn_id,
        fa_icon=fa_icon,
        href=href,
        label=label,
        label_fa_icon=label_fa_icon,
        title=title,
        visit_code=wrapper.visit_code,
        visit_code_sequence=wrapper.visit_code_sequence,
        visit_pk=visit_pk,
        document_status=wrapper.wrapped_visit.object.document_status,
        COMPLETE=COMPLETE,
    )


@register.inclusion_tag(
    f"edc_subject_dashboard/bootstrap{get_bootstrap_version()}/appointment_in_progress.html"
)
def appointment_in_progress(subject_identifier=None, visit_schedule=None, schedule=None):

    try:
        appointment = Appointment.objects.get(
            subject_identifier=subject_identifier,
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
            appt_status=IN_PROGRESS_APPT,
        )
    except ObjectDoesNotExist:
        visit_code = None
    except MultipleObjectsReturned:
        qs = Appointment.objects.filter(
            subject_identifier=subject_identifier,
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
            appt_status=IN_PROGRESS_APPT,
        )
        visit_code = ", ".join([obj.visit_code for obj in qs])
    else:
        visit_code = appointment.visit_code
    return dict(visit_code=visit_code)


@register.inclusion_tag(
    f"edc_subject_dashboard/bootstrap{get_bootstrap_version()}/"
    f"requisition_panel_actions.html",
    takes_context=True,
)
def requisition_panel_actions(context, requisitions=None):
    try:
        requisition_metadata = requisitions[0]
    except IndexError:
        context["verify_disabled"] = None
    else:
        app_label, model_name = requisition_metadata.model.split(".")
        context["verify_disabled"] = (
            None
            if context["user"].has_perm(f"{app_label}.change_{model_name}")
            else "disabled"
        )
    appointment = context.get("appointment")
    scanning = context.get("scanning")
    autofocus = "autofocus" if scanning else ""
    context["appointment"] = str(appointment.object.pk)
    context["autofocus"] = autofocus
    return context


@register.inclusion_tag(
    f"edc_subject_dashboard/bootstrap{get_bootstrap_version()}/"
    f"print_requisition_popover.html",
    takes_context=True,
)
def print_requisition_popover(context):
    C = namedtuple("Consignee", "pk name")
    consignees = []
    for consignee in Consignee.objects.all():
        consignees.append(C(str(consignee.pk), consignee.name))
    context["consignees"] = consignees
    return context


@register.inclusion_tag(
    f"edc_subject_dashboard/bootstrap{get_bootstrap_version()}/" f"appointment_status.html"
)
def appointment_status_icon(appt_status=None):
    return dict(
        appt_status=appt_status,
        NEW_APPT=NEW_APPT,
        IN_PROGRESS_APPT=IN_PROGRESS_APPT,
        INCOMPLETE_APPT=INCOMPLETE_APPT,
        COMPLETE_APPT=COMPLETE_APPT,
        CANCELLED_APPT=CANCELLED_APPT,
    )


@register.inclusion_tag(
    f"edc_subject_dashboard/bootstrap{get_bootstrap_version()}/dashboard/crf_totals.html"
)
def show_crf_totals(wrapped_appointment=None, request=None):
    helper = MetadataHelper(wrapped_appointment.object)
    crf_keyed = helper.get_crf_metadata_by(entry_status=KEYED).count()
    requisition_keyed = helper.get_requisition_metadata_by(entry_status=KEYED).count()
    crf_total = helper.get_crf_metadata_by(entry_status=[REQUIRED, KEYED]).count()
    requisition_total = helper.get_requisition_metadata_by(
        entry_status=[REQUIRED, KEYED]
    ).count()
    keyed = crf_keyed + requisition_keyed
    total = crf_total + requisition_total
    if wrapped_appointment.object.appt_datetime > get_utcnow():
        show_totals = False
    else:
        show_totals = False if keyed != 0 and keyed == total else True
    return dict(
        show_totals=show_totals,
        complete=keyed != 0 and keyed == total,
        request=request,
        keyed=keyed,
        total=total,
    )


@register.inclusion_tag(
    f"edc_subject_dashboard/bootstrap{get_bootstrap_version()}/dashboard/visit_button.html"
)
def show_dashboard_visit_button(wrapped_appointment=None, request=None):

    title = None
    label = None
    btn_class = None
    if wrapped_appointment.appt_status == NEW_APPT:
        label = _("Start")
        title = _("Start data collection for this timepoint.")
        if wrapped_appointment.object.appt_datetime <= get_utcnow():
            btn_class = "warning"
    elif wrapped_appointment.appt_status == INCOMPLETE_APPT:
        incomplete = _("Incomplete")
        label = format_html(
            '<i class="fas fa-pencil-alt fa-sm" aria-hidden="true"></i> {}', incomplete
        )
        title = _("Continue data collection for this timepoint.")
    elif wrapped_appointment.appt_status == CANCELLED_APPT:
        label = _("Cancelled")
        title = _("Cancelled.")
    elif wrapped_appointment.appt_status == COMPLETE_APPT:
        # this appt_status is handled by the subject visit button
        label = _("Done")
        label = format_html(
            '<i class="fas fa-pencil-alt fa-sm" aria-hidden="true"></i> {}', label
        )
        title = _("Done. Timepoint is complete")
        btn_class = "success"

    elif wrapped_appointment.appt_status == IN_PROGRESS_APPT:
        # this appt_status is handled by the subject visit button
        pass
    else:
        raise SubjectDashboardExtrasError(
            f"Unhandled appt_status. Got {wrapped_appointment.appt_status}"
        )
    return dict(
        wrapped_appointment=wrapped_appointment,
        title=title,
        label=label,
        btn_class=btn_class,
        request=request,
    )


@register.inclusion_tag(
    f"edc_subject_dashboard/bootstrap{get_bootstrap_version()}/"
    "dashboard/appointment_button.html"
)
def show_dashboard_appointment_button(
    wrapped_appointment=None, view_appointment=None, request=None
):
    anchor_id = (
        f"appointment_btn_{wrapped_appointment.visit_code }_"
        f"{ wrapped_appointment.visit_code_sequence }"
    )
    if (
        view_appointment
        and wrapped_appointment.object.site.id == request.site.id
        and wrapped_appointment.appt_status == IN_PROGRESS_APPT
    ):
        href = wrapped_appointment.href
    else:
        href = "#"
    disabled = "disabled" if href == "#" else ""
    if view_appointment and wrapped_appointment.object.site.id == request.site.id:
        title = "" if disabled else "Edit appointment"
    else:
        title = "No permission to edit"
    return dict(
        wrapped_appointment=wrapped_appointment,
        view_appointment=view_appointment,
        href=href,
        disabled=disabled,
        title=title,
        request=request,
        IN_PROGRESS_APPT=IN_PROGRESS_APPT,
        anchor_id=anchor_id,
    )


@register.inclusion_tag(
    f"edc_subject_dashboard/bootstrap{get_bootstrap_version()}/"
    "dashboard/unscheduled_appointment_button.html"
)
def show_dashboard_unscheduled_appointment_button(
    wrapped_appointment=None, view_appointment=None, request=None
):
    show_button = False
    if (
        wrapped_appointment
        and wrapped_appointment.object.relative_next
        and wrapped_appointment.appt_status in [INCOMPLETE_APPT, COMPLETE_APPT]
        and (
            wrapped_appointment.object.appt_datetime + relativedelta(days=1)
            != wrapped_appointment.object.relative_next.appt_datetime
        )
        # and (
        #     wrapped_appointment.object.relative_next.visit_code
        #     != wrapped_appointment.visit_code
        # )
    ):
        show_button = True
    anchor_id = (
        f"unscheduled_appt_btn_{wrapped_appointment.visit_code }_"
        f"{ wrapped_appointment.visit_code_sequence }"
    )

    if view_appointment and wrapped_appointment.object.site.id == request.site.id:
        href = wrapped_appointment.unscheduled_appointment_url
    else:
        href = "#"
    disabled = "disabled" if href == "#" else ""
    if view_appointment and wrapped_appointment.object.site.id == request.site.id:
        title = "" if disabled else "Edit appointment"
    else:
        title = "No permission to edit"
    return dict(
        show_button=show_button,
        anchor_id=anchor_id,
        wrapped_appointment=wrapped_appointment,
        view_appointment=view_appointment,
        href=href,
        disabled=disabled,
        title=title,
        request=request,
        INCOMPLETE_APPT=INCOMPLETE_APPT,
        COMPLETE_APPT=COMPLETE_APPT,
    )

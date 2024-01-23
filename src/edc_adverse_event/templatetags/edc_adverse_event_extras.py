from __future__ import annotations

import os
from textwrap import wrap
from typing import TYPE_CHECKING

from django import template
from django.conf import settings
from django.contrib.auth import get_permission_codename
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import select_template
from django.utils.html import format_html
from edc_action_item.utils import get_reference_obj
from edc_constants.constants import OPEN, OTHER, YES
from edc_dashboard.utils import get_bootstrap_version
from edc_utils import get_utcnow

from .. import get_ae_model
from ..auth_objects import TMG_ROLE
from ..constants import AE_WITHDRAWN
from ..utils import get_adverse_event_app_label

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from edc_action_item.models import ActionItem
    from edc_model.models import BaseUuidModel

    from ..model_mixins import (
        AeFollowupModelMixin,
        AeInitialModelMixin,
        DeathReportTmgModelMixin,
    )

    class DeathReportTmg(DeathReportTmgModelMixin, BaseUuidModel):
        ...

    class DeathReportTmgSecond(DeathReportTmgModelMixin, BaseUuidModel):
        ...

    class AeInitial(AeInitialModelMixin, BaseUuidModel):
        ...

    class AeFollowup(AeFollowupModelMixin, BaseUuidModel):
        ...


register = template.Library()


def wrapx(text, length):
    if length:
        return "<BR>".join(wrap(text, length))
    return text


def select_ae_template(relative_path):
    """Returns a template object."""
    local_path = f"{get_adverse_event_app_label()}/bootstrap{get_bootstrap_version()}/"
    default_path = f"edc_adverse_event/bootstrap{get_bootstrap_version()}/"
    return select_template(
        [
            os.path.join(local_path, relative_path),
            os.path.join(default_path, relative_path),
        ]
    )


def select_description_template(model):
    """Returns a template name."""
    return select_ae_template(f"{model}_description.html").template.name


@register.inclusion_tag(
    f"edc_adverse_event/bootstrap{get_bootstrap_version()}/"
    f"tmg/tmg_ae_listboard_result.html",
    takes_context=True,
)
def tmg_listboard_results(
    context, results: [ActionItem], empty_message: str | None = None
) -> dict:
    context["results"] = results
    context["empty_message"] = empty_message
    return context


@register.inclusion_tag(select_description_template("aeinitial"), takes_context=True)
def format_ae_description(context, ae_initial, wrap_length):
    context["utc_date"] = get_utcnow().date()
    context["SHORT_DATE_FORMAT"] = settings.SHORT_DATE_FORMAT
    context["OTHER"] = OTHER
    context["YES"] = YES
    context["ae_initial"] = ae_initial
    try:
        context["sae_reason"] = format_html(wrapx(ae_initial.sae_reason.name, wrap_length))
    except AttributeError:
        context["sae_reason"] = ""
    context["ae_description"] = format_html(wrapx(ae_initial.ae_description, wrap_length))
    return context


@register.inclusion_tag(select_description_template("aefollowup"), takes_context=True)
def format_ae_followup_description(context, ae_followup, wrap_length):
    context["AE_WITHDRAWN"] = AE_WITHDRAWN
    context["utc_date"] = get_utcnow().date()
    context["SHORT_DATE_FORMAT"] = settings.SHORT_DATE_FORMAT
    context["OTHER"] = OTHER
    context["YES"] = YES
    context["ae_followup"] = ae_followup
    context["ae_initial"] = ae_followup.ae_initial
    try:
        context["sae_reason"] = format_html(
            wrapx(ae_followup.ae_initial.sae_reason.name, wrap_length)
        )
    except AttributeError:
        context["sae_reason"] = ""
    context["relevant_history"] = format_html(wrapx(ae_followup.relevant_history, wrap_length))
    context["ae_description"] = format_html(
        wrapx(ae_followup.ae_initial.ae_description, wrap_length)
    )
    return context


@register.inclusion_tag(select_description_template("aesusar"), takes_context=True)
def format_ae_susar_description(context, ae_susar, wrap_length):
    context["utc_date"] = get_utcnow().date()
    context["SHORT_DATE_FORMAT"] = settings.SHORT_DATE_FORMAT
    context["OTHER"] = OTHER
    context["YES"] = YES
    context["ae_susar"] = ae_susar
    context["ae_initial"] = ae_susar.ae_initial
    context["sae_reason"] = format_html(
        "<BR>".join(wrap(ae_susar.ae_initial.sae_reason.name, wrap_length or 35))
    )
    context["ae_description"] = format_html(
        wrapx(ae_susar.ae_initial.ae_description, wrap_length)
    )
    return context


@register.inclusion_tag(
    f"edc_adverse_event/bootstrap{get_bootstrap_version()}/tmg/death_report_tmg_panel.html",
    takes_context=True,
)
def render_death_report_tmg_panel(context, action_item: ActionItem = None):
    return dict(action_item=action_item)


@register.simple_tag
def death_report_tmg_queryset(action_item: ActionItem = None) -> QuerySet[DeathReportTmg]:
    return get_ae_model("deathreporttmg").objects.filter(
        subject_identifier=action_item.subject_identifier
    )


@register.simple_tag
def death_report_tmg2_queryset(
    action_item: ActionItem = None,
) -> QuerySet[DeathReportTmgSecond]:
    return get_ae_model("deathreporttmgsecond").objects.filter(
        subject_identifier=action_item.subject_identifier
    )


@register.simple_tag
def death_report_queryset(
    subject_identifier: str = None,
) -> QuerySet[DeathReportTmgSecond]:
    return get_ae_model("deathreport").objects.filter(subject_identifier=subject_identifier)


@register.simple_tag
def ae_followup_queryset(ae_initial: AeInitial = None) -> QuerySet[AeFollowup]:
    return get_ae_model("aefollowup").objects.filter(ae_initial=ae_initial)


@register.inclusion_tag(
    f"edc_adverse_event/bootstrap{get_bootstrap_version()}/tmg/ae_tmg_panel.html",
    takes_context=True,
)
def render_tmg_panel(
    context,
    action_item: ActionItem = None,
    reference_obj: DeathReportTmg = None,
    change: bool | None = None,
    view_only: bool | None = None,
    by_user_created_only: bool | None = None,
    counter: int = None,
    report_status: str | None = None,
) -> dict:
    # must have either action item or reference_obj
    reference_obj = reference_obj or get_reference_obj(action_item)
    if not action_item and reference_obj:
        action_item = reference_obj.action_item
    may_access_tmg_obj = has_perms_for_obj(
        context,
        reference_obj=reference_obj,
        change=change,
        view_only=view_only,
        by_user_created_only=by_user_created_only,
    )
    disabled = "disabled" if not may_access_tmg_obj else ""
    if view_only:
        panel_color = "info"
    else:
        panel_color = "success" if reference_obj else "warning"
    return dict(
        reference_obj=reference_obj,
        action_item=action_item,
        may_access_tmg_obj=may_access_tmg_obj,
        counter=counter,
        panel_color=panel_color,
        disabled=disabled,
        view_only=view_only,
        report_status=report_status,
        OPEN=OPEN,
    )


@register.inclusion_tag(
    f"edc_adverse_event/bootstrap{get_bootstrap_version()}/tmg/ae_tmg_panel.html",
    takes_context=True,
)
def render_ae_initial_panel(
    context,
    action_item: ActionItem = None,
    counter: int = None,
) -> dict:
    may_access_tmg_obj = has_perms_for_obj(
        context,
        action_item=action_item,
        view_only=True,
    )
    return dict(
        action_item=action_item,
        may_access_tmg_obj=may_access_tmg_obj,
        counter=counter,
        panel_color="info",
    )


@register.simple_tag(takes_context=True)
def has_perms_for_obj(
    context,
    action_item: ActionItem | None = None,
    reference_obj: DeathReportTmg = None,
    change: bool | None = None,
    view_only: bool | None = None,
    by_user_created_only: bool | None = None,
) -> bool:
    has_perms = False

    reference_obj = reference_obj or get_reference_obj(action_item)
    if reference_obj:
        app_label = reference_obj._meta.app_label
        add_codename = get_permission_codename("add", reference_obj._meta)
        change_codename = get_permission_codename("change", reference_obj._meta)
        view_codename = get_permission_codename("view", reference_obj._meta)
        has_change_perms = context["request"].user.has_perms(
            [f"{app_label}.{add_codename}", f"{app_label}.{change_codename}"]
        )
        has_view_perms = context["request"].user.has_perm(f"{app_label}.{view_codename}")
        if change:
            has_perms = has_change_perms
        elif view_only:
            has_perms = not has_change_perms and has_view_perms
        if by_user_created_only:
            has_perms = (
                has_perms and reference_obj.user_created == context["request"].user.username
            )
    return has_perms


@register.simple_tag(takes_context=True)
def has_perms_for_tmg_role(context):
    has_perms = False
    try:
        has_perms = context["request"].user.userprofile.roles.get(name=TMG_ROLE)
    except ObjectDoesNotExist:
        pass
    return has_perms

from __future__ import annotations

import os
from textwrap import wrap
from typing import TYPE_CHECKING

from django import template
from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.messages import ERROR
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import select_template
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from edc_action_item.utils import get_reference_obj
from edc_constants.constants import CLOSED, OPEN, OTHER, YES
from edc_model_admin.utils import add_to_messages_once
from edc_utils import escape_braces

from ..constants import (
    AE_TMG_ACTION,
    AE_WITHDRAWN,
    DEATH_REPORT_TMG_ACTION,
    DEATH_REPORT_TMG_SECOND_ACTION,
    TMG_ROLE,
)
from ..utils import get_adverse_event_app_label, get_ae_model, has_valid_tmg_perms
from ..view_utils import TmgButton

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from edc_action_item.models import ActionItem
    from edc_model.models import BaseUuidModel

    from ..model_mixins import (
        AeFollowupModelMixin,
        AeInitialModelMixin,
        DeathReportModelMixin,
        DeathReportTmgModelMixin,
    )

    class DeathReportTmgModel(DeathReportTmgModelMixin, BaseUuidModel): ...

    class DeathReportTmgSecondModel(DeathReportTmgModelMixin, BaseUuidModel): ...

    class AeInitialModel(AeInitialModelMixin, BaseUuidModel): ...

    class AeFollowupModel(AeFollowupModelMixin, BaseUuidModel): ...

    class DeathReportModel(DeathReportModelMixin, BaseUuidModel): ...


register = template.Library()


def wrapx(text: str, length: int) -> str:
    if length:
        return "<BR>".join(wrap(text, length))
    return text


def select_ae_template(relative_path):
    """Returns a template object."""
    local_path = get_adverse_event_app_label()
    default_path = "edc_adverse_event"
    return select_template(
        [
            os.path.join(local_path, relative_path),
            os.path.join(default_path, relative_path),
        ]
    )


def select_description_template(model):
    """Returns a template name."""
    return select_ae_template(f"{model}_description.html").template.name


@register.inclusion_tag(select_description_template("aeinitial"), takes_context=True)
def format_ae_description(context, ae_initial, wrap_length):
    context["utc_date"] = timezone.now().date()
    context["SHORT_DATE_FORMAT"] = settings.SHORT_DATE_FORMAT
    context["OTHER"] = OTHER
    context["YES"] = YES
    context["ae_initial"] = ae_initial
    try:
        context["sae_reason"] = format_html(
            "{}",
            mark_safe(wrapx(escape_braces(ae_initial.sae_reason.name), wrap_length)),  # nosec B703, B308
        )
    except AttributeError:
        context["sae_reason"] = ""
    context["ae_description"] = format_html(
        "{}",
        mark_safe(wrapx(escape_braces(ae_initial.ae_description), wrap_length)),  # nosec B703, B308
    )
    return context


@register.inclusion_tag(select_description_template("aefollowup"), takes_context=True)
def format_ae_followup_description(context, ae_followup, wrap_length):
    context["AE_WITHDRAWN"] = AE_WITHDRAWN
    context["utc_date"] = timezone.now().date()
    context["SHORT_DATE_FORMAT"] = settings.SHORT_DATE_FORMAT
    context["OTHER"] = OTHER
    context["YES"] = YES
    context["ae_followup"] = ae_followup
    context["ae_initial"] = ae_followup.ae_initial
    try:
        context["sae_reason"] = format_html(
            "{}",
            mark_safe(
                wrapx(escape_braces(ae_followup.ae_initial.sae_reason.name), wrap_length)
            ),  # nosec B703, B308
        )
    except AttributeError:
        context["sae_reason"] = ""
    context["relevant_history"] = format_html(
        "{}",
        mark_safe(wrapx(escape_braces(ae_followup.relevant_history), wrap_length)),  # nosec B703, B308
    )
    context["ae_description"] = format_html(
        "{}",
        mark_safe(wrapx(escape_braces(ae_followup.ae_initial.ae_description), wrap_length)),  # nosec B703, B308
    )
    return context


@register.inclusion_tag(select_description_template("aesusar"), takes_context=True)
def format_ae_susar_description(context, ae_susar, wrap_length):
    context["utc_date"] = timezone.now().date()
    context["SHORT_DATE_FORMAT"] = settings.SHORT_DATE_FORMAT
    context["OTHER"] = OTHER
    context["YES"] = YES
    context["ae_susar"] = ae_susar
    context["ae_initial"] = ae_susar.ae_initial
    context["sae_reason"] = format_html(
        "{}",
        mark_safe(
            "<BR>".join(
                wrap(
                    escape_braces(ae_susar.ae_initial.sae_reason.name),
                    wrap_length or 35,
                )
            )
        ),  # nosec B703, B308
    )
    context["ae_description"] = format_html(
        "{}",
        mark_safe(wrapx(escape_braces(ae_susar.ae_initial.ae_description), wrap_length)),  # nosec B703, B308
    )
    return context


@register.inclusion_tag(
    "edc_adverse_event/tmg/tmg_ae_listboard_result.html",
    takes_context=True,
)
def tmg_listboard_results(
    context, results: [ActionItem], empty_qs_message: str | None = None
) -> dict:
    context["results"] = results
    context["empty_message"] = empty_qs_message
    return context


@register.inclusion_tag(
    "edc_adverse_event/tmg/death_report_tmg_panel.html",
    takes_context=True,
)
def render_death_report_tmg_panel(context, action_item: ActionItem = None):
    return dict(action_item=action_item)


@register.simple_tag
def ae_tmg_queryset(subject_identifier: str = None) -> QuerySet[DeathReportTmgModel]:
    return get_ae_model("aetmg").objects.filter(subject_identifier=subject_identifier)


@register.simple_tag
def death_report_tmg_queryset(
    subject_identifier: str = None,
) -> QuerySet[DeathReportTmgModel]:
    return get_ae_model("deathreporttmg").objects.filter(subject_identifier=subject_identifier)


@register.simple_tag
def death_report_tmg2_queryset(
    subject_identifier: str = None,
) -> QuerySet[DeathReportTmgSecondModel]:
    return get_ae_model("deathreporttmgsecond").objects.filter(
        subject_identifier=subject_identifier
    )


@register.simple_tag
def death_report_queryset(
    subject_identifier: str = None,
) -> QuerySet[DeathReportTmgSecondModel]:
    return get_ae_model("deathreport").objects.filter(subject_identifier=subject_identifier)


@register.simple_tag
def ae_followup_queryset(
    ae_initial: AeInitialModel = None,
) -> QuerySet[AeFollowupModel] | None:
    if ae_initial:
        return get_ae_model("aefollowup").objects.filter(ae_initial_id=ae_initial.id)
    return None


@register.simple_tag
def ae_tmg_action_item(subject_identifier: str = None) -> ActionItem:
    try:
        obj = django_apps.get_model("edc_action_item.actionitem").objects.get(
            subject_identifier=subject_identifier, action_type__name=AE_TMG_ACTION
        )
    except ObjectDoesNotExist:
        obj = None
    return obj


@register.simple_tag
def death_report_tmg_action_item(subject_identifier: str = None) -> ActionItem:
    try:
        obj = django_apps.get_model("edc_action_item.actionitem").objects.get(
            subject_identifier=subject_identifier,
            action_type__name=DEATH_REPORT_TMG_ACTION,
        )
    except ObjectDoesNotExist:
        obj = None
    return obj


@register.simple_tag
def death_report_tmg_second_action_item(subject_identifier: str = None) -> ActionItem:
    try:
        obj = django_apps.get_model("edc_action_item.actionitem").objects.get(
            subject_identifier=subject_identifier,
            action_type__name=DEATH_REPORT_TMG_SECOND_ACTION,
        )
    except ObjectDoesNotExist:
        obj = None
    return obj


@register.inclusion_tag(
    "edc_adverse_event/tmg/ae_tmg_panel.html",
    takes_context=True,
)
def render_tmg_panel(
    context,
    action_item: ActionItem = None,
    reference_obj: DeathReportTmgModel = None,
    view_only: bool | None = None,
    by_user_created_only: bool | None = None,
    counter: int = None,
    report_status: str | None = None,
    next_url_name: str | None = None,
) -> dict:
    reference_obj = reference_obj or get_reference_obj(action_item)
    if not action_item and reference_obj:
        action_item = reference_obj.action_item
    disable_all = True if not has_valid_tmg_perms(request=context["request"]) else False
    if action_item:
        params = dict(
            user=context["request"].user,
            subject_identifier=action_item.subject_identifier,
            model_obj=reference_obj,
            model_cls=action_item.action_cls.reference_model_cls(),
            request=context["request"],
            only_user_created_may_access=by_user_created_only,
            forloop_counter=counter,
            current_site=context["request"].site,
            disable_all=disable_all,
            action_item=action_item,
        )
        if next_url_name:
            params.update(next_url_name=next_url_name.split(":")[1])
        btn = TmgButton(**params)
        if view_only:
            panel_color = "info"
        elif not reference_obj:
            panel_color = "warning"
        else:
            panel_color = "success"
        # panel_label
        display_name = action_item.display_name.replace("Submit", "").replace("pending", "")
        identifier = action_item.identifier or "New"
        panel_label = _(f"{display_name} {identifier}")
        return dict(
            btn=btn,
            panel_color=panel_color,
            reference_obj=reference_obj,
            action_item=action_item,
            OPEN=OPEN,
            CLOSED=CLOSED,
            report_status=report_status,
            panel_label=panel_label,
        )
    return {}


@register.simple_tag(takes_context=True)
def has_perms_for_tmg_role(context):
    has_perms = False
    try:
        has_perms = context["request"].user.userprofile.roles.get(name=TMG_ROLE)
    except ObjectDoesNotExist:
        add_to_messages_once(
            context["request"],
            ERROR,
            _(
                "Access disabled. User has not been granted a TMG role. "
                "Contact your administrator."
            ),
        )

    return has_perms


@register.simple_tag()
def get_empty_qs_message(status: str, search_term: str):
    msg = f"There are no {status} reports."
    if search_term:
        msg = f"{msg[:-1]} for your search criteria"
    return _(msg)


@register.inclusion_tag(
    "edc_adverse_event/tmg/tmg_button_group.html",
    takes_context=True,
)
def render_tmg_button_group(context, subject_identifier: str):
    if context["request"].user.userprofile.roles.filter(name=TMG_ROLE).exists():
        return dict(subject_identifier=subject_identifier)
    return {}

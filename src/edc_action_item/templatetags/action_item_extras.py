from __future__ import annotations

from typing import TYPE_CHECKING, Type

from django import template
from edc_auth.utils import get_user
from edc_constants.constants import CANCELLED, CLOSED, HIGH_PRIORITY, NEW, OPEN
from edc_utils import formatted_date
from edc_utils.date import to_local

from ..models import ActionItem
from ..site_action_items import site_action_items
from ..utils import (
    get_parent_reference_obj,
    get_reference_obj,
    get_related_reference_obj,
)
from ..view_utils import ActionItemButton, ActionItemPopoverListItem

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from edc_appointment.models import Appointment

    from ..action import Action


register = template.Library()


@register.inclusion_tag(
    "edc_action_item/action_item_button.html",
    takes_context=True,
)
def render_action_item_button(
    context,
    action_item: ActionItem | None = None,
    name: str | None = None,
    label: str | None = None,
    color: str | None = None,
    appointment: Appointment = None,
) -> dict[str, ActionItemButton]:
    if action_item:
        action_cls = action_item.action_cls
    else:
        action_cls = site_action_items.get(name)
    btn = ActionItemButton(
        subject_identifier=context["subject_identifier"],
        action_cls=action_cls,
        model_obj=action_item,
        model_cls=ActionItem,
        request=context["request"],
        user=context["request"].user,
        current_site=context["request"].site,
        appointment=appointment or context.get("appointment"),
        fixed_label=label,
        fixed_color=color,
    )
    return dict(btn=btn)


@register.inclusion_tag(
    "edc_action_item/add_action_item_popover.html",
    takes_context=True,
)
def add_action_item_popover(
    context,
    subject_identifier: str = None,
    subject_dashboard_url: str = None,
    color: str = None,
) -> dict[str, str | Action | WSGIRequest | Appointment]:
    """
    `Add action linked PRN forms`
    """
    action_item_add_url: str = "edc_action_item_admin:edc_action_item_actionitem_add"
    add_actions: dict[str, Type[Action]] = site_action_items.get_add_actions_to_show()
    if add_actions:
        d = {k: v.display_name for k, v in add_actions.items()}
        add_actions = {}
        for k in sorted(d, key=d.get):
            add_actions.update({k: d[k]})
    return dict(
        action_item_add_url=action_item_add_url,
        subject_identifier=subject_identifier,
        subject_dashboard_url=subject_dashboard_url,
        add_actions=add_actions,
        request=context["request"],
        appointment=context.get("appointment"),
        color=color,
    )


@register.inclusion_tag(
    "edc_action_item/action_item_with_popover.html",
    takes_context=True,
)
def action_item_with_popover(context, action_item: ActionItem, tabindex):
    date_last_updated = None
    user_last_updated = None
    if reference_obj := get_reference_obj(action_item):
        date_last_updated = formatted_date(
            to_local(reference_obj.modified or reference_obj.created)
        )
        if get_user(reference_obj.user_modified or reference_obj.user_created):
            user_last_updated = reference_obj.user_modified or reference_obj.user_created
        else:
            user_last_updated = None

    return dict(
        action_item=action_item,
        action_identifier=action_item.action_identifier,
        subject_identifier=context.get("subject_identifier"),
        action_item_model_name="edc_action_item.actionitem",
        next_url_name="subject_dashboard_url",
        request=context["request"],
        appointment=context.get("appointment"),
        report_datetime=formatted_date(to_local(action_item.report_datetime)),
        date_last_updated=date_last_updated,
        user_last_updated=user_last_updated,
        CANCELLED=CANCELLED,
        CLOSED=CLOSED,
        HIGH_PRIORITY=HIGH_PRIORITY,
        NEW=NEW,
        OPEN=OPEN,
        tabindex=tabindex,
        popover_title=ActionItem._meta.verbose_name,
        # priority=
    )


@register.inclusion_tag(
    "edc_subject_dashboard/buttons/popover_list_item.html",
    takes_context=True,
)
def render_popover_list_item(
    context,
    action_item: ActionItem = None,
    action_item_type: str = None,
    appointment: Appointment | None = None,
) -> dict:
    """Renders one ListItem"""
    opts = dict(
        action_item=action_item,
        category=action_item_type,
        subject_identifier=context.get("subject_identifier"),
        next_url_name=context.get("next_url_name"),
        user=context["request"].user,
        current_site=context["request"].site,
        request=context["request"],
        appointment=appointment,
    )
    btn = ActionItemPopoverListItem(**opts)
    return dict(btn=btn)


@register.inclusion_tag(
    "edc_action_item/action_item_reason.html",
)
def render_action_item_reason(action_item):
    action_item_reasons = []
    objects = [
        get_reference_obj(action_item),
        get_parent_reference_obj(action_item),
        get_related_reference_obj(action_item),
    ]
    for obj in objects:
        try:
            action_item_reasons.append(obj.get_action_item_reason())
        except AttributeError as e:
            if "get_action_item_reason" not in str(e):
                raise
    if action_item_reasons:
        action_item_reasons = list(set(action_item_reasons))
    return {"action_item_reasons": action_item_reasons}

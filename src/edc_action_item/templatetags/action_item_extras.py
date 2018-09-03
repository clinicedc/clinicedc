from django import template
from django.conf import settings
from edc_constants.constants import NEW, OPEN, CLOSED, CANCELLED

from ..choices import ACTION_STATUS
from ..constants import HIGH_PRIORITY
from ..helpers import ActionItemHelper
from ..site_action_items import site_action_items

register = template.Library()


@register.inclusion_tag(f'edc_action_item/bootstrap{settings.EDC_BOOTSTRAP}/'
                        'add_action_item_popover.html')
def add_action_item_popover(subject_identifier, subject_dashboard_url):
    action_item_add_url = (
        'edc_action_item_admin:edc_action_item_actionitem_add')
    show_link_to_add_actions = site_action_items.get_show_link_to_add_actions()
    return dict(
        action_item_add_url=action_item_add_url,
        subject_identifier=subject_identifier,
        subject_dashboard_url=subject_dashboard_url,
        show_link_to_add_actions=show_link_to_add_actions)


@register.inclusion_tag(f'edc_action_item/bootstrap{settings.EDC_BOOTSTRAP}/'
                        'action_item_with_popover.html')
def action_item_with_popover(action_item_model_wrapper, tabindex):
    helper = ActionItemHelper(
        model_wrapper=action_item_model_wrapper)
    context = helper.get_context()
    context.update(
        CANCELLED=[c[1] for c in ACTION_STATUS if c[0] == CANCELLED][0],
        CLOSED=[c[1] for c in ACTION_STATUS if c[0] == CLOSED][0],
        HIGH_PRIORITY=HIGH_PRIORITY,
        NEW=[c[1] for c in ACTION_STATUS if c[0] == NEW][0],
        OPEN=[c[1] for c in ACTION_STATUS if c[0] == OPEN][0],
        tabindex=tabindex
    )
    return context

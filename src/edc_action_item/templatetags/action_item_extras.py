from django import template
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_base.utils import convert_php_dateformat
from urllib.parse import urlparse, parse_qsl

from ..constants import HIGH_PRIORITY
from ..site_action_items import site_action_items

register = template.Library()


@register.inclusion_tag('edc_action_item/action_item_control.html')
def action_item_control(subject_identifier, subject_dashboard_url):
    action_item_add_url = (
        'edc_action_item_admin:edc_action_item_actionitem_add')
    show_link_to_add_actions = site_action_items.get_show_link_to_add_actions()
    return dict(
        action_item_add_url=action_item_add_url,
        subject_identifier=subject_identifier,
        subject_dashboard_url=subject_dashboard_url,
        show_link_to_add_actions=show_link_to_add_actions)


@register.inclusion_tag('edc_action_item/action_item_with_popover.html')
def action_item_with_popover(action_item_model_wrapper, tabindex):
    strike_thru = None
    action_item = action_item_model_wrapper.object
    date_format = convert_php_dateformat(settings.SHORT_DATE_FORMAT)
    last_updated = action_item.last_updated
    if last_updated:
        last_updated = last_updated.strftime(date_format)
        user_last_updated = action_item.user_last_updated
        text = (
            f'Last updated on {last_updated} by {user_last_updated}.')
    else:
        text = 'This action item has not been updated.'
    model_url = None
    model_cls = None
    if action_item.action_type.model:
        # this reference model and url
        model_cls = django_apps.get_model(action_item.action_type.model)
        query_dict = dict(
            parse_qsl(urlparse(action_item_model_wrapper.href).query))
        parent_model_url = None
        parent_model_name = None
        action_item_reason = None
        parent_action_identifier = None
        try:
            model_url = model_cls.action_cls.reference_model_url(
                action_item=action_item,
                action_identifier=action_item.action_identifier,
                **query_dict)
        except ObjectDoesNotExist:
            # object wont exist if an action item was deleted
            # that was created by another action item.
            strike_thru = True
        else:
            if action_item.parent_action_item:
                # parent action item
                parent_model_cls = django_apps.get_model(
                    action_item.parent_action_item.action_type.model)
                # parent reference model and url
                try:
                    parent_obj = parent_model_cls.objects.get(
                        tracking_identifier=action_item.parent_reference_identifier)
                except ObjectDoesNotExist:
                    pass
                else:
                    parent_model_url = model_cls.action_cls.reference_model_url(
                        model_obj=parent_obj,
                        action_item=action_item,
                        action_identifier=action_item.action_identifier,
                        **query_dict)

                    parent_model_name = (
                        f'{parent_model_cls._meta.verbose_name} {parent_obj.identifier}')
                    action_item_reason = parent_obj.action_item_reason
                parent_action_identifier = action_item.parent_action_item.action_identifier

    return dict(
        HIGH_PRIORITY=HIGH_PRIORITY,
        action_identifier=action_item.action_identifier,
        action_instructions=action_item.instructions,
        action_item_reason=action_item_reason,
        action_item_color=model_cls.action_cls.color_style,
        display_name=action_item.action_type.display_name,
        href=action_item_model_wrapper.href,
        last_updated_text=text,
        model_name=model_cls._meta.verbose_name,
        model_url=model_url,
        name=action_item.action_type.name,
        parent_action_identifier=parent_action_identifier,
        parent_action_item=action_item.parent_action_item,
        parent_model_name=parent_model_name,
        parent_model_url=parent_model_url,
        priority=action_item.priority or '',
        report_datetime=action_item.report_datetime,
        status=action_item.get_status_display(),
        tabindex=tabindex,
        strike_thru=strike_thru)

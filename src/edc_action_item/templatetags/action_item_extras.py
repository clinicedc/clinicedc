from django import template
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_base.utils import convert_php_dateformat
from edc_constants.constants import OPEN
from urllib.parse import urlparse, parse_qsl

from ..constants import HIGH_PRIORITY
from ..choices import ACTION_STATUS
from ..site_action_items import site_action_items

register = template.Library()


@register.inclusion_tag('edc_action_item/add_action_item_popover.html')
def add_action_item_popover(subject_identifier, subject_dashboard_url):
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
    reference_model_cls = None
    if action_item.action_type.model:
        # this reference model and url
        reference_model_cls = django_apps.get_model(
            action_item.action_type.model)
        query_dict = dict(
            parse_qsl(urlparse(action_item_model_wrapper.href).query))
        parent_model_url = None
        parent_model_name = None
        action_item_reason = None
        parent_action_identifier = None
        # reference_model and url
        try:
            reference_model_obj = reference_model_cls.objects.get(
                action_identifier=action_item.action_identifier)
        except ObjectDoesNotExist:
            reference_model_obj = None
        try:
            model_url = reference_model_cls.action_cls.reference_model_url(
                action_item=action_item,
                action_identifier=action_item.action_identifier,
                model_obj=reference_model_obj,
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
                    try:
                        subject_visit = parent_obj.visit
                    except (AttributeError, ObjectDoesNotExist):
                        pass
                    else:
                        # parent model is a CRF, add visit to querystring
                        query_dict.update({
                            parent_obj.visit_model_attr(): str(subject_visit.pk)})
                    parent_model_url = reference_model_cls.action_cls.reference_model_url(
                        model_obj=parent_obj,
                        action_item=action_item,
                        action_identifier=action_item.action_identifier,
                        **query_dict)

                    parent_model_name = (
                        f'{parent_model_cls._meta.verbose_name} {parent_obj.identifier}')
                    action_item_reason = parent_obj.action_item_reason
                parent_action_identifier = action_item.parent_action_item.action_identifier

    open_display = [c[1] for c in ACTION_STATUS if c[0] == OPEN][0]

    return dict(
        HIGH_PRIORITY=HIGH_PRIORITY,
        OPEN=open_display,
        action_identifier=action_item.action_identifier,
        action_instructions=action_item.instructions,
        action_item_reason=action_item_reason,
        action_item_color=reference_model_cls.action_cls.color_style,
        display_name=action_item.action_type.display_name,
        href=action_item_model_wrapper.href,
        last_updated_text=text,
        model_name=reference_model_cls._meta.verbose_name,
        model_url=model_url,
        name=action_item.action_type.name,
        parent_action_identifier=parent_action_identifier,
        parent_action_item=action_item.parent_action_item,
        parent_model_name=parent_model_name,
        parent_model_url=parent_model_url,
        priority=action_item.priority or '',
        reference_model_obj=reference_model_obj,
        report_datetime=action_item.report_datetime,
        status=action_item.get_status_display(),
        tabindex=tabindex,
        strike_thru=strike_thru)

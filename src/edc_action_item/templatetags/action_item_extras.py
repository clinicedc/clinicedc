from django import template
from django.apps import apps as django_apps
from django.conf import settings
from edc_base.utils import convert_php_dateformat
from edc_constants.constants import YES

from ..constants import HIGH_PRIORITY

register = template.Library()


@register.inclusion_tag('edc_action_item/action_item_with_popover.html')
def action_item_with_popover(action_item_model_wrapper):
    action_item = action_item_model_wrapper.object
    date_format = convert_php_dateformat(settings.SHORT_DATE_FORMAT)
    last_updated = action_item.last_updated
    if last_updated:
        last_updated = last_updated.strftime(date_format)
        user_last_updated = action_item.user_last_updated
        text = (
            f'Last updated on { last_updated } by { user_last_updated}.')
    else:
        text = 'This action item has not been updated.'
    model_url = None
    if action_item.action_type.prn_form_action == YES:
        model_cls = django_apps.get_model(action_item.action_type.model)
        model_url = (model_cls().get_absolute_url()
                     + '?' + action_item_model_wrapper.href.split('?')[1])
    return dict(
        display_name=action_item.action_type.display_name,
        reason=action_item.reason,
        status=action_item.get_status_display(),
        report_datetime=action_item.report_datetime,
        last_updated_text=text,
        action_identifier=action_item.action_identifier,
        href=action_item_model_wrapper.href,
        model_url=model_url,
        model_name=model_cls._meta.verbose_name,
        priority=action_item.priority or '',
        HIGH_PRIORITY=HIGH_PRIORITY)

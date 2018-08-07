from django import template
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_base import convert_php_dateformat
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
    href = action_item_model_wrapper.href
    date_format = convert_php_dateformat(settings.SHORT_DATE_FORMAT)

    if action_item.last_updated:
        # could also use action_item.linked_to_reference?
        last_updated = action_item.last_updated.strftime(date_format)
        user_last_updated = action_item.user_last_updated
        last_updated_text = (
            f'Last updated on {last_updated} by {user_last_updated}.')
    else:
        last_updated_text = 'This action item has not been updated.'

    query_dict = dict(parse_qsl(urlparse(href).query))
    related_reference_url = None
    related_reference_model_name = None
    related_reference_identifier = None
    parent_reference_url = None
    parent_reference_identifier = None
    parent_reference_model_name = None
    action_item_reason = None

    # action class
    action_cls = site_action_items.get(
        action_item.reference_model_cls.action_name)

    # reference_model instance
    try:
        reference_obj = action_item.reference_model_cls.objects.get(
            action_identifier=action_item.action_identifier)
    except ObjectDoesNotExist:
        reference_obj = None

    # reference model url
    try:
        reference_url = action_cls.reference_url(
            action_item=action_item,
            action_identifier=action_item.action_identifier,
            reference_obj=reference_obj,
            **query_dict)
    except ObjectDoesNotExist:
        reference_url = None
        # object wont exist if action item was deleted
        # that was created by another action item.
        strike_thru = True

    if action_item.parent_reference_identifier:
        # parent reference model and url
        try:
            parent_reference_obj = action_item.parent_reference_obj
        except ObjectDoesNotExist:
            pass
        else:
            try:
                subject_visit = parent_reference_obj.visit
            except (AttributeError, ObjectDoesNotExist):
                pass
            else:
                # parent reference model is a CRF, add visit to querystring
                query_dict.update({
                    parent_reference_obj.visit_model_attr(): str(subject_visit.pk),
                    'appointment': str(subject_visit.appointment.pk)})
            parent_reference_url = (
                action_cls.reference_url(
                    reference_obj=parent_reference_obj,
                    action_item=action_item,
                    action_identifier=action_item.action_identifier,
                    **query_dict))

            parent_reference_model_name = (
                f'{action_item.parent_reference_model_cls._meta.verbose_name} '
                f'{str(parent_reference_obj)}')
            action_item_reason = parent_reference_obj.action_item_reason
        parent_reference_identifier = action_item.parent_action_item.action_identifier

    if action_item.related_reference_identifier:
        try:
            related_reference_obj = action_item.related_reference_obj
        except ObjectDoesNotExist:
            pass
        else:
            try:
                subject_visit = related_reference_obj.visit
            except (AttributeError, ObjectDoesNotExist):
                pass
            else:
                # related reference model is a CRF, add visit to querystring
                query_dict.update({
                    related_reference_obj.visit_model_attr(): str(subject_visit.pk),
                    'appointment': str(subject_visit.appointment.pk)})
            related_reference_url = (
                action_cls.reference_url(
                    reference_obj=related_reference_obj,
                    action_item=action_item,
                    action_identifier=action_item.action_identifier,
                    **query_dict))

            related_reference_model_name = (
                f'{action_item.related_reference_obj._meta.verbose_name} '
                f'{str(related_reference_obj)}')
        related_reference_identifier = action_item.related_reference_identifier

    open_display = [c[1] for c in ACTION_STATUS if c[0] == OPEN][0]

    context = dict(
        HIGH_PRIORITY=HIGH_PRIORITY,
        OPEN=open_display,
        action_instructions=action_item.instructions,
        action_item_reason=action_item_reason,
        report_datetime=action_item.report_datetime,
        display_name=action_item.action_type.display_name,
        action_identifier=action_item.action_identifier,

        parent_reference_identifier=parent_reference_identifier,
        parent_action_item=action_item.parent_action_item,

        href=href,
        last_updated_text=last_updated_text,
        name=action_item.action_type.name,

        reference_model_name=action_item.reference_model_cls()._meta.verbose_name,
        reference_url=reference_url,
        reference_obj=reference_obj,
        action_item_color=action_cls.color_style,

        parent_reference_model_name=parent_reference_model_name,
        parent_reference_url=parent_reference_url,

        related_reference_url=related_reference_url,
        related_reference_model_name=related_reference_model_name,
        related_reference_identifier=related_reference_identifier,

        priority=action_item.priority or '',
        status=action_item.get_status_display(),
        tabindex=tabindex,
        strike_thru=strike_thru)

    return context

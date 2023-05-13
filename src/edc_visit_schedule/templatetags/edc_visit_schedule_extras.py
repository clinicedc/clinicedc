from urllib.parse import unquote, urlencode

from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import format_html
from edc_dashboard.utils import get_bootstrap_version

from ..models import SubjectScheduleHistory

register = template.Library()


@register.inclusion_tag(
    f"edc_visit_schedule/bootstrap{get_bootstrap_version()}/"
    f"subject_schedule_footer_row.html"
)
def subject_schedule_footer_row(
    subject_identifier, visit_schedule, schedule, subject_dashboard_url
):
    context = dict(
        visit_schedule=visit_schedule,
        verbose_name=schedule.offschedule_model_cls._meta.verbose_name,
        schedule=schedule,
    )

    try:
        history_obj = SubjectScheduleHistory.objects.get(
            visit_schedule_name=visit_schedule.name,
            schedule_name=schedule.name,
            subject_identifier=subject_identifier,
            # offschedule_datetime__isnull=False,
        )
    except ObjectDoesNotExist:
        history_obj = None
    context.update(history_obj=history_obj)
    if not history_obj:
        # subject was NEVER on this schedule
        context = dict(
            offschedule_datetime=None,
            onschedule_datetime=None,
            href=None,
        )
    elif not history_obj.offschedule_datetime:
        # subject is still ON this schedule
        onschedule_model_obj = schedule.onschedule_model_cls.objects.get(
            subject_identifier=subject_identifier
        )
        options = dict(subject_identifier=subject_identifier)
        query = unquote(urlencode(options))
        href = (
            f"{schedule.offschedule_model_cls().get_absolute_url()}?next="
            f"{subject_dashboard_url},subject_identifier"
        )
        href = "&".join([href, query])
        context.update(
            offschedule_datetime=None,
            onschedule_datetime=onschedule_model_obj.onschedule_datetime,
            href=format_html(href),
        )
    elif history_obj.offschedule_datetime:
        # subject is OFF this schedule (offschedule_model_obj)
        onschedule_model_obj = schedule.onschedule_model_cls.objects.get(
            subject_identifier=subject_identifier
        )
        offschedule_model_obj = schedule.offschedule_model_cls.objects.get(
            subject_identifier=subject_identifier
        )
        options = dict(subject_identifier=subject_identifier)
        query = unquote(urlencode(options))
        href = (
            f"{offschedule_model_obj.get_absolute_url()}?next="
            f"{subject_dashboard_url},subject_identifier"
        )
        href = "&".join([href, query])
        context.update(
            offschedule_datetime=history_obj.offschedule_datetime,
            onschedule_datetime=onschedule_model_obj.onschedule_datetime,
            href=format_html(href),
        )
    return context

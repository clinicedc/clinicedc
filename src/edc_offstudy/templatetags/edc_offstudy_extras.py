from django import template
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.utils.safestring import mark_safe
from urllib.parse import urlencode, unquote

register = template.Library()


@register.inclusion_tag("edc_offstudy/visit_schedule_row.html")
def offstudy_visit_schedule_row(
    subject_identifier, visit_schedule, subject_dashboard_url
):

    context = {}
    offstudy_model = visit_schedule.offstudy_model
    offstudy_model_cls = django_apps.get_model(offstudy_model)
    try:
        obj = offstudy_model_cls.objects.get(subject_identifier=subject_identifier)
    except ObjectDoesNotExist:
        pass
    else:
        options = dict(subject_identifier=subject_identifier)
        query = unquote(urlencode(options))
        href = (
            f"{obj.get_absolute_url()}?next={subject_dashboard_url},subject_identifier"
        )
        href = "&".join([href, query])
        context = dict(
            offstudy_datetime=obj.offstudy_datetime,
            visit_schedule=visit_schedule,
            href=mark_safe(href),
            verbose_name=obj._meta.verbose_name,
        )
    return context

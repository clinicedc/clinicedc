from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.urls.base import reverse
from django.utils.safestring import mark_safe
from edc_utils import get_utcnow, formatted_datetime
from uuid import uuid4

from ..models import QueryRule
from ..rule import update_query_rules

DATA_MANAGER_ENABLED = getattr(settings, "DATA_MANAGER_ENABLED", True)


def toggle_active_flag(modeladmin, request, queryset):
    for obj in queryset:
        obj.active = False if obj.active else True
        obj.save()


toggle_active_flag.short_description = (
    f"Toggle Active/Inactive {QueryRule._meta.verbose_name_plural}"
)


def copy_query_rule_action(modeladmin, request, queryset):
    if queryset.count() == 1:
        obj = queryset[0]
        options = {
            k: v
            for k, v in obj.__dict__.items()
            if not k.startswith("_") and k not in ["id"]
        }
        options["title"] = f"{options['title']} (Copy)"
        options["active"] = False
        options["reference"] = uuid4()
        try:
            queryset.model.objects.get(title=options["title"])
        except ObjectDoesNotExist:
            new_obj = queryset.model.objects.create(**options)
            for o in obj.visit_schedule.all().order_by("timepoint"):
                new_obj.visit_schedule.add(o)
            for o in obj.data_dictionaries.all().order_by("number"):
                new_obj.data_dictionaries.add(o)
            msg = f'Query rule has been copied. New title is "{options["title"]}"'
            messages.add_message(request, messages.SUCCESS, msg)
        else:
            msg = f'Query rule already exists. Got "{options["title"]}"'
            messages.add_message(request, messages.ERROR, msg)
    else:
        messages.add_message(
            request,
            messages.ERROR,
            "Selecting multiple query rules is not allowed. Select just one.",
        )


copy_query_rule_action.short_description = f"Copy {QueryRule._meta.verbose_name}"


def update_query_rules_action(modeladmin, request, queryset):

    if not DATA_MANAGER_ENABLED:
        msg = mark_safe(
            "Data manager features are currently disabled. "
            "See settings.DATA_MANAGER_ENABLED."
        )
        messages.add_message(request, messages.ERROR, msg)
    elif queryset:
        if settings.CELERY_ENABLED:
            update_query_rules.delay(pks=[o.pk for o in queryset])
            dte = get_utcnow()
            taskresult_url = reverse(
                "admin:django_celery_results_taskresult_changelist"
            )
            msg = mark_safe(
                f"Updating data queries in the background. "
                f"Started at {formatted_datetime(dte)}. "
                f"An updated digest will be email upon completion. "
                f'You may also check in <a href="{taskresult_url}?'
                f'task_name=update_query_rules">task results</A>. '
            )
        else:
            results = update_query_rules(pks=[o.pk for o in queryset])
            msg = mark_safe(
                f"Done updating data queries. Created {results.get('created')}, "
                f"resolved {results.get('resolved')}."
            )
        messages.add_message(request, messages.SUCCESS, msg)


update_query_rules_action.short_description = (
    f"Run selected {QueryRule._meta.verbose_name_plural}"
)

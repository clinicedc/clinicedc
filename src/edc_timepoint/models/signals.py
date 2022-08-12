from django.apps import apps as django_apps
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from ..constants import OPEN_TIMEPOINT


@receiver(post_save, weak=False, dispatch_uid="update_timepoint_on_post_save")
def update_timepoint_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Update the TimePointStatus mixin datetime field."""
    if not raw:
        try:
            if instance.enabled_as_timepoint:
                app_config = django_apps.get_app_config("edc_timepoint")
                if "historical" not in sender._meta.label_lower:
                    timepoint = app_config.timepoints.get(sender._meta.label_lower)
                    datetime_value = getattr(instance, timepoint.datetime_field)
                    if (
                        instance.timepoint_opened_datetime is None
                        or instance.timepoint_opened_datetime != datetime_value
                    ):
                        instance.timepoint_opened_datetime = datetime_value
                        instance.timepoint_status = OPEN_TIMEPOINT
                        instance.save(
                            update_fields=[
                                "timepoint_opened_datetime",
                                "timepoint_status",
                            ]
                        )
        except AttributeError as e:
            if "enabled_as_timepoint" not in str(e):
                raise AttributeError(str(e))

from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver


@receiver(post_save, weak=False, dispatch_uid="update_timepoint_on_post_save")
def update_timepoint_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Update the TimePointStatus mixin datetime field."""
    if not raw:
        try:
            instance.update_timepoint()
        except AttributeError as e:
            if "update_timepoint" not in str(e):
                raise
            pass

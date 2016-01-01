from django.db.models.signals import post_save
from django.dispatch import receiver

from .visit_model_mixin import VisitModelMixin


@receiver(post_save, weak=False, dispatch_uid="base_visit_tracking_check_in_progress_on_post_save")
def base_visit_tracking_check_in_progress_on_post_save(sender, instance, raw, created, using, **kwargs):
    """Calls post_save method on the visit tracking instance."""
    if not raw:
        if isinstance(instance, VisitModelMixin):
            instance.post_save_check_in_progress()

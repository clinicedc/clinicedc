from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(
    post_save,
    weak=False,
    dispatch_uid="update_crf_status_post_save",
)
def update_crf_status_post_save(sender, instance, raw, created, using, **kwargs):
    if not raw and not kwargs.get("update_fields"):
        if ".historical" not in instance._meta.label_lower:
            try:
                instance.update_crf_status_for_instance
            except AttributeError as e:
                if "update_crf_status_for_instance" not in str(e):
                    raise AttributeError(str(e))
            else:
                instance.update_crf_status_for_instance()

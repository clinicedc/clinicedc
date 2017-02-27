from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .box import Box
from .manifest_item import ManifestItem
from edc_lab.constants import VERIFIED


@receiver(post_delete, weak=False, sender=ManifestItem,
          dispatch_uid="manifest_item_on_post_delete")
def manifest_item_on_post_delete(sender, instance, using, **kwargs):
    try:
        box = Box.objects.get(box_identifier=instance.identifier)
    except Box.DoesNotExist as e:
        print(e)
        pass
    else:
        box.status = VERIFIED
        box.save()

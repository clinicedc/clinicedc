from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist

from ..constants import VERIFIED
from ..models import BoxItem
from .box import Box
from .manifest import ManifestItem


@receiver(post_delete, weak=False, sender=ManifestItem,
          dispatch_uid="manifest_item_on_post_delete")
def manifest_item_on_post_delete(sender, instance, using, **kwargs):
    try:
        box = Box.objects.get(box_identifier=instance.identifier)
    except ObjectDoesNotExist:
        pass
    else:
        box.status = VERIFIED
        box.save()


@receiver(post_delete, weak=False, sender=BoxItem,
          dispatch_uid="box_item_on_post_delete")
def box_item_on_post_delete(sender, instance, using, **kwargs):
    instance.box.save()

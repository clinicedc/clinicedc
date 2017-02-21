from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import BoxItem


@receiver(post_save, weak=False, sender=BoxItem,
          dispatch_uid='box_item_on_post_save')
def box_item_on_post_save(sender, instance, raw, created, using, **kwargs):
    if not raw:
        if not instance.position:
            print('hello')
            instance.position = instance.box.boxitem_set.all().count() + 1

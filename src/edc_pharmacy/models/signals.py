from django.db.models.signals import post_save
from django.dispatch import receiver

from .dispensed_item import DispensedItem


@receiver(post_save, sender=DispensedItem,
          dispatch_uid='dispense_item_on_post_save')
def dispense_item_on_post_save(sender, instance, raw, created, **kwargs):
    if not raw:
        instance.prescription_item.save()

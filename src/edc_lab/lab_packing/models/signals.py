from django.db.models.signals import post_save
from django.dispatch import receiver

from edc_lab.lab_packing.helpers import PackingListHelper

from ..models import BasePackingList


@receiver(post_save, weak=False, dispatch_uid='packing_list_on_post_save')
def packing_list_on_post_save(sender, instance, raw, created, using, update_fields, **kwargs):
    if not raw:
        if issubclass(sender, BasePackingList):
            packing_list_helper = PackingListHelper(instance)
            packing_list_helper.update()

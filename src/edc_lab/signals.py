from django.db.models.signals import post_save
from django.dispatch import receiver

# from .packing.helpers import PackingListHelper
#
# from .packing.model_mixins import PackingListModelMixin


# @receiver(post_save, weak=False, dispatch_uid='packing_list_on_post_save')
# def packing_list_on_post_save(sender, instance, raw, created, using, update_fields, **kwargs):
#     if not raw:
#         if issubclass(sender, PackingListModelMixin):
#             packing_list_helper = PackingListHelper(instance)
#             packing_list_helper.update()


@receiver(post_save, weak=False, dispatch_uid='requisition_identifier_on_post_save')
def requisition_identifier_on_post_save(sender, instance, raw, created, using, update_fields, **kwargs):
    if not raw:
        try:
            instance.update_requisition_identifier(sender)
        except AttributeError as e:
            if 'update_requisition_identifier' not in str(e):
                raise AttributeError(e)

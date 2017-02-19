# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
#
#
# @receiver(post_save, weak=False,
#           dispatch_uid='aliquot_on_post_save')
# def aliquot_on_post_save(sender, instance, raw, created, using, **kwargs):
#     if not raw:
#         try:
#             instance.creates_primary_aliquot_on_receive()
#         except AttributeError as e:
#             if 'create_primary_aliquot' not in str(e):
#                 raise

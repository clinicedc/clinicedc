from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models.signals import post_save
from django.dispatch import receiver

from .action_handler import ActionHandler
from .models import ActionItem, ActionItemUpdate
from edc_action_item.reference_model_updater import ReferenceModelUpdater


@receiver(post_save, weak=False, sender=ActionItem, dispatch_uid='action_item_on_post_save')
def action_item_on_post_save(sender, instance, raw, created, update_fields, **kwargs):
    """Updates the reference model instance with the action_identifier,
    if this is an action type connected to a model.
    """
    if not raw and not update_fields:
        if instance.reference_model:
            updater = ReferenceModelUpdater(action_item=instance)
            updater.update()


@receiver(post_save, weak=False, dispatch_uid='update_or_create_action_item_on_post_save')
def update_or_create_action_item_on_post_save(sender, instance, raw,
                                              created, update_fields, **kwargs):
    """Updates or creates an action item for a model using
    the ActionItemModelMixin.
    """
    if not raw and not update_fields:

        try:
            instance.action_identifier
        except AttributeError:
            pass
        else:
            if ('historical' not in instance._meta.label_lower
                    and not isinstance(instance, (ActionItem, ActionItemUpdate))):

                # update action item with tracking_identifier from this
                # instance if action item already exists
                try:
                    action_item = ActionItem.objects.get(
                        action_identifier=instance.action_identifier)
                except ObjectDoesNotExist:
                    try:
                        action_item = ActionItem.objects.get(
                            subject_identifier=instance.subject_identifier,
                            reference_model=sender._meta.label_lower,
                            reference_identifier=None)
                    except ObjectDoesNotExist:
                        action_item = None
                    except MultipleObjectsReturned:
                        action_item = ActionItem.objects.filter(
                            subject_identifier=instance.subject_identifier,
                            reference_model=sender._meta.label_lower,
                            reference_identifier=None).order_by('created').first()

                if action_item:
                    action_item.reference_identifier = instance.tracking_identifier
                    action_item.save(update_fields=['reference_identifier'])

                # create a new action item(s) if required
                handler = ActionHandler(model_obj=instance)
                handler.create()
                handler.close()

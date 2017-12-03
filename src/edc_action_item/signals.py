from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver

from .action_item_handler import ActionItemHandler
from .models import ActionItem, ActionItemUpdate


@receiver(post_save, weak=False, sender=ActionItem, dispatch_uid='action_item_on_post_save')
def action_item_on_post_save(sender, instance, raw, created, update_fields, **kwargs):
    """Updates the reference model instance with the action_identifier,
    if this is an action type connected to a model.
    """
    if not raw and not update_fields:
        if instance.reference_model:
            model_cls = django_apps.get_model(
                instance.reference_model or None)
            # get reference model instance or the first one without
            # an action identifier
            try:
                model_obj = model_cls.objects.get(
                    tracking_identifier=instance.reference_identifier,
                    action_identifier__isnull=False)
            except ObjectDoesNotExist:
                model_obj = model_cls.objects.filter(
                    subject_identifier=instance.subject_identifier,
                    action_identifier__isnull=True).order_by('created').first()
            # update the reference model to link to the action item
            if model_obj:
                model_obj.action_identifier = instance.action_identifier
                model_obj.save(update_fields=['action_identifier'])


@receiver(post_save, weak=False, dispatch_uid='update_or_create_action_item_on_post_save')
def update_or_create_action_item_on_post_save(sender, instance, raw, created, update_fields, **kwargs):
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
                if action_item:
                    action_item.reference_identifier = instance.tracking_identifier
                    action_item.save(update_fields=['reference_identifier'])

                # create a new action item(s) if required
                handler = ActionItemHandler(
                    model_obj=instance, model_cls=sender)
                handler.create()
                handler.close()

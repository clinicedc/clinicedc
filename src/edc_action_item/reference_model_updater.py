from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist, FieldError


class ActionItemFieldError(Exception):
    pass


class ReferenceModelUpdater:

    def __init__(self, action_item=None):
        self.action_item = action_item

    @property
    def reference_model_cls(self):
        return django_apps.get_model(self.action_item.reference_model)

    def get_first(self):
        """Returns the first reference model instance that has
        a null action_identifier for this subject.

        Either subject identifier is a field on reference model
        or reference model has a FK to the visit model.
        """
        try:
            reference_model_obj = self.reference_model_cls.objects.filter(
                subject_identifier=self.action_item.subject_identifier,
                action_identifier__isnull=True).order_by('created').first()
        except FieldError:
            visit_model_attr = self.reference_model_cls.visit_model_attr()
            opts = {f'{visit_model_attr}__subject_identifier':
                    self.action_item.subject_identifier}
            reference_model_obj = self.reference_model_cls.objects.filter(
                action_identifier__isnull=True, **opts).order_by('created').first()
        return reference_model_obj

    def update(self):
        """Gets the reference model instance or the first one without
        an action identifier and updates it with this action_identifier.
        """

        try:
            reference_model_obj = self.reference_model_cls.objects.get(
                tracking_identifier=self.action_item.reference_identifier,
                action_identifier__isnull=False)
        except ObjectDoesNotExist:
            reference_model_obj = self.get_first()
        except FieldError:
            raise ActionItemFieldError(
                f'Unable to update action_identifier. Field action_identifier '
                f'is missing on model {repr(self.reference_model_cls)}. '
                f'Got {self.action_item.action_identifier}.')
        # update the reference model to link to the action item
        if reference_model_obj:
            reference_model_obj.action_identifier = self.action_item.action_identifier
            reference_model_obj.save(update_fields=['action_identifier'])

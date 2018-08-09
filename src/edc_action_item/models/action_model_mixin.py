from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from edc_constants.constants import OPEN

from ..action import ActionItemGetter
from ..site_action_items import site_action_items


class ActionClassNotDefined(Exception):
    pass


class ActionModelMixin(models.Model):

    action_name = None

    action_item_model = 'edc_action_item.actionitem'

    subject_dashboard_url = 'subject_dashboard_url'

    action_identifier = models.CharField(
        max_length=25,
        null=True)

    subject_identifier = models.CharField(
        max_length=50)

    parent_reference_identifier = models.CharField(
        max_length=30,
        null=True)

    related_reference_identifier = models.CharField(
        max_length=30,
        null=True)

    def __str__(self):
        return f'{self.action_identifier[-9:]}'

    def save(self, *args, **kwargs):
        if not self.action_cls():
            raise ActionClassNotDefined(
                f'Action class name not defined. See {repr(self)}')

        if (not self.related_reference_identifier
                and self.action_cls().related_reference_fk_attr):
            self.related_reference_identifier = getattr(
                self, self.action_cls().related_reference_fk_attr).action_identifier

        if self.action_identifier:
            # get the existing ActionItem linked to this model
            ActionItemGetter(
                self.action_cls(),
                subject_identifier=self.subject_identifier,
                action_identifier=self.action_identifier,
                parent_reference_identifier=self.parent_reference_identifier,
                related_reference_identifier=self.related_reference_identifier,
                allow_create=False)
        else:
            # get an existing unlinked ActionItem or create a new one
            allow_create = (
                False if self.related_reference_identifier
                or self.parent_reference_identifier else True)
            getter = ActionItemGetter(
                self.action_cls(),
                subject_identifier=self.subject_identifier,
                parent_reference_identifier=self.parent_reference_identifier,
                related_reference_identifier=self.related_reference_identifier,
                allow_create=allow_create)

            # link action_item to this model instance
            self.action_identifier = getter.action_identifier
            self.parent_reference_identifier = getter.action_item.parent_reference_identifier
            getter.action_item.linked_to_reference = True
            getter.action_item.status = OPEN
            getter.action_item.save()
        # also see signals.py
        super().save(*args, **kwargs)

    @classmethod
    def action_cls(cls):
        return site_action_items.get(cls.action_name)

    @property
    def action_item(self):
        """Returns the ActionItem instance associated with
        this model or None.
        """
        ActionItem = django_apps.get_model(self.action_item_model)
        try:
            action_item = ActionItem.objects.get(
                action_identifier=self.action_identifier)
        except ObjectDoesNotExist:
            action_item = None
        return action_item

    @property
    def action_item_reason(self):
        return None

    @property
    def identifier(self):
        """Returns a shortened action_identifier.
        """
        return self.action_identifier[-9:]

    class Meta:
        abstract = True

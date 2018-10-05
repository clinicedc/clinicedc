from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.deletion import PROTECT
from edc_constants.constants import OPEN

from ..action import ActionItemGetter, RelatedReferenceObjectDoesNotExist
from ..create_action_item import create_action_item
from ..site_action_items import site_action_items
from .action_item import ActionItem


class ActionClassNotDefined(Exception):
    pass


class ActionModelMixin(models.Model):

    action_name = None

    action_item_model = 'edc_action_item.actionitem'

    subject_dashboard_url = 'subject_dashboard_url'

    action_identifier = models.CharField(
        max_length=25,
        unique=True)

    subject_identifier = models.CharField(
        max_length=50)

    parent_action_identifier = models.CharField(
        max_length=30,
        null=True,
        help_text=('action identifier that links to parent '
                   'reference model instance.'))

    related_action_identifier = models.CharField(
        max_length=30,
        null=True,
        help_text=('action identifier that links to related '
                   'reference model instance.'))

    action_item = models.ForeignKey(
        ActionItem,
        null=True,
        on_delete=PROTECT)

    def __str__(self):
        return f'{self.action_identifier[-9:]}'

    def save(self, *args, **kwargs):
        if not self.get_action_cls():
            raise ActionClassNotDefined(
                f'Action class name not defined. See {repr(self)}')

        if (self.get_action_cls().related_reference_model
                and not self.related_action_identifier):
            self.related_action_identifier = getattr(
                self, self.get_action_cls().related_reference_fk_attr
            ).action_identifier

        if not self.action_identifier:
            # this is a new instance
            # associate a new or existing ActionItem
            # with this reference model instance
            action_cls = site_action_items.get(self.action_name)
            try:
                # try to get an existing action_item
                getter = ActionItemGetter(
                    action_cls,
                    subject_identifier=self.subject_identifier,
                    parent_action_identifier=self.parent_action_identifier,
                    related_action_identifier=self.related_action_identifier)
            except ObjectDoesNotExist as e:
                if action_cls.related_reference_fk_attr:
                    # action item must exist!
                    raise RelatedReferenceObjectDoesNotExist(e)
                # create an new action_item
                self.action_item = create_action_item(
                    action_cls,
                    subject_identifier=self.subject_identifier,
                    action_identifier=self.action_identifier)
            else:
                self.action_item = getter.action_item
            self.action_identifier = self.action_item.action_identifier
            self.parent_action_identifier = self.action_item.parent_action_identifier
            self.related_action_identifier = self.action_item.related_action_identifier
            self.action_item.linked_to_reference = True
            self.action_item.status = OPEN
            self.action_item.save()
            # also see signals.py
        else:
            if not self.action_item:
                self.action_item = ActionItem.objects.get(
                    action_identifier=self.action_identifier)
            self.action_item.status = OPEN
            self.action_item.save()
        super().save(*args, **kwargs)

    @classmethod
    def get_action_cls(cls):
        return site_action_items.get(cls.action_name)

    @property
    def action(self):
        return self.get_action_cls()(action_item=self.action_item)

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

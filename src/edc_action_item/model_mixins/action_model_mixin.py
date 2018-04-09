from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from edc_identifier.model_mixins import TrackingIdentifier

from ..action import ActionItemGetter
from ..models import ActionItem
from ..site_action_items import site_action_items


class ActionClassNotDefined(Exception):
    pass


class ActionModelMixin(models.Model):

    action_name = None

    subject_dashboard_url = 'subject_dashboard_url'

    tracking_identifier_cls = TrackingIdentifier

    tracking_identifier_prefix = ''

    action_identifier = models.CharField(
        max_length=25,
        null=True)

    subject_identifier = models.CharField(
        max_length=50)

    tracking_identifier = models.CharField(
        max_length=30,
        null=True)

    related_tracking_identifier = models.CharField(
        max_length=30,
        null=True)

    parent_tracking_identifier = models.CharField(
        max_length=30,
        null=True)

    def save(self, *args, **kwargs):
        if not self.action_cls:
            raise ActionClassNotDefined(
                f'Action class name not defined. See {repr(self)}')

        if not self.id and not self.tracking_identifier:
            self.tracking_identifier = self.tracking_identifier_cls(
                identifier_prefix=self.tracking_identifier_prefix,
                identifier_type=self._meta.label_lower).identifier

        if (not self.related_tracking_identifier
                and self.action_cls.related_reference_model_fk_attr):
            self.related_tracking_identifier = getattr(
                self, self.action_cls.related_reference_model_fk_attr).tracking_identifier

        if self.action_identifier:
            ActionItemGetter(
                self.action_cls, action_identifier=self.action_identifier)
        else:
            getter = ActionItemGetter(
                self.action_cls,
                subject_identifier=self.subject_identifier,
                reference_identifier=self.tracking_identifier,
                related_reference_identifier=self.related_tracking_identifier,
                parent_reference_identifier=self.parent_tracking_identifier,
                allow_create=True)
            self.action_identifier = getter.action_identifier
        super().save(*args, **kwargs)

    @property
    def action_cls(self):
        return site_action_items.get(self.action_name)

    @property
    def action_item(self):
        """Returns the ActionItem instance associated with
        this model or None.
        """
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
        """Returns a shortened tracking identifier.
        """
        return self.tracking_identifier[-9:]

    class Meta:
        abstract = True

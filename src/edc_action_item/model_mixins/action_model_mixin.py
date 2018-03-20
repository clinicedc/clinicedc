from django.core.exceptions import ObjectDoesNotExist, FieldError
from django.db import models

from ..models import ActionItem
from edc_action_item.action.action_item_getter import ActionItemGetter
from edc_identifier.model_mixins.tracking_identifier_model_mixin import TrackingIdentifier


class ActionClassNotDefined(Exception):
    pass


class ActionModelMixin(models.Model):

    action_cls = None
    subject_dashboard_url = 'subject_dashboard_url'
    tracking_identifier_cls = TrackingIdentifier
    tracking_identifier_prefix = ''

    action_identifier = models.CharField(
        max_length=25,
        unique=True)

    subject_identifier = models.CharField(
        max_length=50)

    tracking_identifier = models.CharField(
        max_length=30,
        unique=True)

    parent_tracking_identifier = models.CharField(
        max_length=30,
        null=True)

    def save(self, *args, **kwargs):

        if not self.action_cls:
            raise ActionClassNotDefined(
                f'Action class not defined. See {repr(self)}')

        if not self.id and not self.tracking_identifier:
            self.tracking_identifier = self.tracking_identifier_cls(
                identifier_prefix=self.tracking_identifier_prefix,
                identifier_type=self._meta.label_lower).identifier

        if (not self.parent_tracking_identifier
                and self.action_cls.parent_reference_model_fk_attr):
            self.parent_tracking_identifier = getattr(
                self, self.action_cls.parent_reference_model_fk_attr).tracking_identifier

        if self.action_identifier:
            ActionItemGetter(
                self.action_cls, action_identifier=self.action_identifier)
        else:
            getter = ActionItemGetter(
                self.action_cls,
                subject_identifier=self.subject_identifier,
                reference_identifier=self.tracking_identifier,
                parent_reference_identifier=self.parent_tracking_identifier,
                allow_create=True)
            self.action_identifier = getter.model_obj.action_identifier
        super().save(*args, **kwargs)

    @property
    def action_item(self):
        try:
            return ActionItem.objects.get(
                action_identifier=self.action_identifier)
        except ObjectDoesNotExist:
            return None

    @property
    def action_item_reason(self):
        return None

    class Meta:
        abstract = True

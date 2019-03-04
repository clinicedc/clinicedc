from django.db import models
from django.db.models.deletion import PROTECT
from edc_model.models import HistoricalRecords

from ..site_action_items import site_action_items
from .action_item import ActionItem


class ActionClassNotDefined(Exception):
    pass


class ActionItemError(Exception):
    pass


class ActionItemModelManager(models.Manager):
    def get_by_natural_key(self, action_identifier):
        return self.get(action_identifier=action_identifier)


class ActionModelMixin(models.Model):

    action_name = None

    action_item_model = "edc_action_item.actionitem"

    subject_dashboard_url = "subject_dashboard_url"

    action_identifier = models.CharField(max_length=50, unique=True)

    subject_identifier = models.CharField(max_length=50)

    action_item = models.ForeignKey(ActionItem, null=True, on_delete=PROTECT)

    parent_action_item = models.ForeignKey(
        ActionItem, related_name="+", null=True, on_delete=PROTECT
    )

    related_action_item = models.ForeignKey(
        ActionItem, related_name="+", null=True, on_delete=PROTECT
    )

    # remove
    parent_action_identifier = models.CharField(
        max_length=30,
        null=True,
        help_text=(
            "action identifier that links to parent " "reference model instance."
        ),
    )

    # remove
    related_action_identifier = models.CharField(
        max_length=30,
        null=True,
        help_text=(
            "action identifier that links to related " "reference model instance."
        ),
    )

    objects = ActionItemModelManager()

    history = HistoricalRecords(inherit=True)

    def __str__(self):
        return f"{self.action_identifier[-9:]}"

    def save(self, *args, **kwargs):
        if not self.get_action_cls():
            raise ActionClassNotDefined(
                f"Action class name not defined. See {repr(self)}"
            )

        if not self.subject_identifier:
            raise ActionItemError(
                f"Missing subject identifier. See {self.__class__}"
                f" {self.action_identifier}."
            )

        if (
            self.get_action_cls().related_reference_model
            and not self.related_action_item
        ):
            self.related_action_item = getattr(
                self, self.get_action_cls().related_reference_fk_attr
            ).action_item

        if not self.id:
            # this is a new instance
            # associate a new or existing ActionItem
            # with this reference model instance
            action_cls = site_action_items.get(self.action_name)
            action = action_cls(
                subject_identifier=self.subject_identifier,
                action_identifier=self.action_identifier,
                related_action_item=self.related_action_item,
            )
            self.action_item = action.action_item
            self.action_item.linked_to_reference = True
            self.action_identifier = self.action_item.action_identifier
        elif self.id and not self.action_item:
            self.action_item = ActionItem.objects.get(
                action_identifier=self.action_identifier
            )
        self.parent_action_item = self.action_item.parent_action_item
        # also see signals.py
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.action_identifier,)

    natural_key.dependencies = ["edc_action_item.actionitem"]

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

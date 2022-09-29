from typing import Any

from django.db import models
from django.db.models.deletion import PROTECT
from edc_model.models import HistoricalRecords

from ..managers import ActionIdentifierModelManager
from ..site_action_items import site_action_items
from .action_item import ActionItem


class ActionClassNotDefined(Exception):
    pass


class ActionItemError(Exception):
    pass


class ActionNoManagersModelMixin(models.Model):

    action_name: str = None

    action_item_model: str = "edc_action_item.actionitem"

    subject_dashboard_url: str = "subject_dashboard_url"

    action_identifier = models.CharField(max_length=50, unique=True, null=True, blank=True)

    action_item = models.ForeignKey(ActionItem, null=True, blank=True, on_delete=PROTECT)

    parent_action_item = models.ForeignKey(
        ActionItem, related_name="+", null=True, blank=True, on_delete=PROTECT
    )

    related_action_item = models.ForeignKey(
        ActionItem, related_name="+", null=True, blank=True, on_delete=PROTECT
    )

    # remove
    parent_action_identifier = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        help_text="action identifier that links to parent reference model instance.",
    )

    # remove
    related_action_identifier = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        help_text="action identifier that links to related reference model instance.",
    )

    action_item_reason = models.TextField(null=True, editable=False)

    def __str__(self):
        return f"{self.action_identifier[-9:]}"

    def save(self: Any, *args, **kwargs):
        # ensure action class is defined
        if not self.get_action_cls():
            raise ActionClassNotDefined(f"Action class name not defined. See {repr(self)}")

        # ensure subject_identifier
        if not self.subject_identifier:
            raise ActionItemError(
                f"Subject identifier may not be None. See {self.__class__}"
                f" action_identifier=`{self.action_identifier}`."
            )

        # ensure related_action_item is set if there is a
        # related reference model.
        if self.get_action_cls().related_reference_model and not self.related_action_item:
            self.related_action_item = getattr(
                self, self.get_action_cls().related_reference_fk_attr
            ).action_item

        if not self.id:
            # this is a new instance
            # associate a new or existing ActionItem
            # with this reference model instance
            action_cls = self.get_action_cls()
            action = action_cls(
                subject_identifier=self.subject_identifier,
                action_identifier=self.action_identifier,
                related_action_item=self.related_action_item,
            )
            self.action_item = action.action_item
            self.action_item.linked_to_reference = True
            self.action_identifier = self.action_item.action_identifier
        elif self.id and not self.action_item:
            self.action_item = ActionItem.objects.get(action_identifier=self.action_identifier)
        self.parent_action_item = self.action_item.parent_action_item

        # also see signals.py
        super().save(*args, **kwargs)  # type: ignore

    def natural_key(self: Any) -> tuple:
        return (self.action_identifier,)  # noqa

    # noinspection PyTypeHints
    natural_key.dependencies = ["edc_action_item.actionitem"]  # type:ignore

    @classmethod
    def get_action_cls(cls):
        return site_action_items.get(cls.action_name)

    @property
    def action(self: Any):
        return self.get_action_cls()(
            subject_identifier=self.subject_identifier,
            action_item=self.action_item,
            readonly=True,
        )

    def get_action_item_reason(self):
        return self.action_item_reason or self.action_name

    @property
    def identifier(self):
        """Returns a shortened action_identifier"""
        return self.action_identifier[-9:]

    class Meta:
        abstract = True


class ActionModelMixin(ActionNoManagersModelMixin):

    objects = ActionIdentifierModelManager()

    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True

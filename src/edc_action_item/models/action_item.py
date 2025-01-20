from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Type

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.deletion import PROTECT
from edc_constants.constants import CANCELLED, NEW
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_notification.model_mixins import NotificationModelMixin
from edc_sites.managers import CurrentSiteManager as BaseCurrentSiteManager
from edc_sites.model_mixins import SiteModelMixin
from edc_utils import get_utcnow

from ..choices import ACTION_STATUS, PRIORITY
from ..exceptions import ActionItemStatusError, SubjectDoesNotExist
from ..identifiers import ActionIdentifier
from ..site_action_items import site_action_items
from .action_type import ActionType

if TYPE_CHECKING:
    from edc_crf.model_mixins import CrfModelMixin

    from ..action import Action

    class PrnModel(BaseUuidModel):
        subject_identifier: str
        ...

    class CrfModel(CrfModelMixin): ...


class CurrentSiteManager(BaseCurrentSiteManager):
    use_in_migrations = True

    def get_by_natural_key(self, action_identifier):
        return self.get(action_identifier=action_identifier)


class ActionItemManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, action_identifier):
        return self.get(action_identifier=action_identifier)


class ActionItem(
    NonUniqueSubjectIdentifierFieldMixin,
    SiteModelMixin,
    NotificationModelMixin,
    BaseUuidModel,
):
    subject_identifier_model = "edc_registration.registeredsubject"

    action_identifier = models.CharField(max_length=50, unique=True)

    report_datetime = models.DateTimeField(default=get_utcnow)

    action_type = models.ForeignKey(
        ActionType, on_delete=PROTECT, related_name="action_type", verbose_name="Action"
    )

    linked_to_reference = models.BooleanField(
        default=False,
        editable=False,
        help_text=(
            "True if this action is linked to it's reference_model."
            "Initially False if this action is created before reference_model."
            "Always True when reference_model creates the action."
            'Set to True when reference_model is created and "links" to this action.'
            "(Note: reference_model looks for actions where "
            "linked_to_reference is False before attempting to "
            "create a new ActionItem)."
        ),
    )

    # related_reference_model = models.CharField(max_length=100, null=True, editable=False)

    related_action_identifier = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text=(
            "May be left blank. e.g. action identifier from "
            "source model that opened the item."
        ),
    )

    parent_action_identifier = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text=(
            "May be left blank. e.g. action identifier from "
            "reference model that opened the item (parent)."
        ),
    )

    priority = models.CharField(
        max_length=25,
        choices=PRIORITY,
        null=True,
        blank=True,
        help_text="Leave blank to use default for this action type.",
    )

    parent_action_item = models.ForeignKey(
        "self",
        on_delete=PROTECT,
        related_name="+",
        null=True,
        blank=True,
        editable=False,
    )

    related_action_item = models.ForeignKey(
        "self",
        on_delete=PROTECT,
        related_name="+",
        null=True,
        blank=True,
        editable=False,
    )

    status = models.CharField(max_length=25, default=NEW, choices=ACTION_STATUS)

    instructions = models.TextField(
        null=True, blank=True, help_text="populated by action class"
    )

    auto_created = models.BooleanField(default=False)

    auto_created_comment = models.CharField(max_length=25, null=True, blank=True)

    objects = ActionItemManager()

    on_site = CurrentSiteManager()

    history = HistoricalRecords()

    def __str__(self) -> str:
        return (
            f"{self.action_type.display_name} {self.action_identifier[-9:]} "
            f"for {self.subject_identifier} ({self.get_status_display()})"
        )

    def save(self, *args, **kwargs):
        """See also signals and action_cls."""
        if not self.id:
            # a new persisted action item always has
            # a unique action identifier
            self.action_identifier = (
                self.action_identifier
                or ActionIdentifier(
                    subject_identifier=self.subject_identifier,
                    site_id=self.site_id,
                    source_model=self._meta.label_lower,
                    name=self.action_type.name,
                ).identifier
            )
            # subject_identifier
            subject_identifier_model_cls = django_apps.get_model(self.subject_identifier_model)
            try:
                subject_identifier_model_cls.objects.get(
                    subject_identifier=self.subject_identifier
                )
            except ObjectDoesNotExist:
                raise SubjectDoesNotExist(
                    f"Attempt to create {self.__class__.__name__} failed. "
                    f"Invalid subject identifier. Subject does not exist "
                    f"in '{self.subject_identifier_model}'. "
                    f"Got '{self.subject_identifier}'."
                )
            self.priority = self.priority or self.action_type.priority
        else:
            if (
                self.status in [NEW, CANCELLED]
                and django_apps.get_model(self.reference_model)
                .objects.filter(action_identifier=self.action_identifier)
                .exists()
            ):
                raise ActionItemStatusError(
                    "Invalid action item status. Reference model exists. "
                    f"Got `{self.get_status_display()}`. Perhaps catch this in the form"
                )
        super().save(*args, **kwargs)

    def natural_key(self) -> tuple[str]:
        return (self.action_identifier,)  # noqa

    @property
    def last_updated(self) -> datetime | str:
        return None if self.status == NEW else self.modified

    @property
    def user_last_updated(self) -> str | None:
        return None if self.status == NEW else self.user_modified or self.user_created

    @property
    def action_cls(self) -> Type[Action]:
        """Returns the action_cls."""
        return site_action_items.get(self.action_type.name)

    @property
    def action(self) -> Action:
        """Returns the instantiated action_cls."""
        return self.action_cls(
            subject_identifier=self.subject_identifier,
            action_identifier=self.action_identifier,
            readonly=True,
        )

    @property
    def reference_model(self) -> str:
        return self.action_type.reference_model

    @property
    def reference_model_cls(self) -> Type[PrnModel | CrfModel]:
        return django_apps.get_model(self.action_type.reference_model)

    @property
    def reference_obj(self) -> PrnModel | CrfModel:
        return self.reference_model_cls.objects.get(action_identifier=self.action_identifier)

    @property
    def parent_reference_obj(self) -> PrnModel | CrfModel:
        if not self.parent_action_item:
            raise ObjectDoesNotExist(
                f"Parent ActionItem does not exist for {self.action_identifier}."
            )
        return self.parent_action_item.reference_obj

    @property
    def related_reference_model(self) -> str:
        return self.action_type.related_reference_model

    @property
    def related_reference_obj(self) -> PrnModel | CrfModel:
        if not self.related_action_item:
            raise ObjectDoesNotExist(
                f"Related ActionItem does not exist for {self.action_identifier}."
            )
        return self.related_action_item.reference_obj

    @property
    def identifier(self) -> str:
        """Returns a shortened action identifier."""
        return self.action_identifier[-9:]

    @property
    def display_name(self) -> str:
        return self.action_type.display_name

    @property
    def label_color(self) -> str:
        return self.action_cls.color_style

    class Meta(
        BaseUuidModel.Meta,
        NonUniqueSubjectIdentifierFieldMixin.Meta,
    ):
        verbose_name = "Action Item"
        verbose_name_plural = "Action Items"
        indexes = (
            BaseUuidModel.Meta.indexes
            + NonUniqueSubjectIdentifierFieldMixin.Meta.indexes
            + [
                models.Index(
                    fields=[
                        "subject_identifier",
                        "action_identifier",
                        "action_type",
                        "site_id",
                        "status",
                        "report_datetime",
                    ],
                ),
            ]
        )

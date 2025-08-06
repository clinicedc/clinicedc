from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Type
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from edc_view_utils import ADD, PrnButton

if TYPE_CHECKING:
    from edc_appointment.models import Appointment
    from edc_crf.model_mixins import CrfModelMixin
    from edc_model.models import BaseUuidModel

    from edc_action_item.models import ActionItem

    class PrnModel(BaseUuidModel):
        subject_identifier: str
        ...

    class CrfModel(CrfModelMixin): ...


@dataclass
class ActionItemPopoverListItem(PrnButton):
    action_item: ActionItem = None
    category: str = None
    appointment: Appointment | None = None
    model_obj: PrnModel | CrfModel | None = field(default=None, init=False)
    model_cls: Type[PrnModel | CrfModel | None] = field(default=None, init=False)

    def __post_init__(self):
        if self.category == "reference":
            self.model_obj = self.reference_obj
            self.model_cls = self.action_item.reference_model_cls
        elif self.category == "parent":
            self.model_obj = self.parent_reference_obj
            self.model_cls = self.action_item.parent_action_item.reference_model_cls
        elif self.category == "related":
            self.model_obj = self.related_reference_obj
            self.model_cls = self.action_item.related_action_item.reference_model_cls

    @property
    def reference_obj(self) -> PrnModel | CrfModel | None:
        try:
            obj = self.action_item.reference_obj
        except ObjectDoesNotExist:
            obj = None
        return obj

    @property
    def parent_reference_obj(self) -> PrnModel | CrfModel | None:
        obj = None
        if self.action_item.parent_action_item:
            try:
                obj = self.action_item.parent_action_item.reference_obj
            except ObjectDoesNotExist:
                pass
        return obj

    @property
    def related_reference_obj(self) -> PrnModel | CrfModel | None:
        obj = None
        if self.action_item.related_action_item:
            try:
                obj = self.action_item.related_action_item.reference_obj
            except ObjectDoesNotExist:
                pass
        return obj

    def label(self) -> str:
        """Fix label to the model's verbose_name."""
        if self.action == ADD:
            # prefix with word Add
            return _("Add %(verbose_name)s") % dict(
                verbose_name=self.model_cls._meta.verbose_name
            )
        return self.model_cls._meta.verbose_name

    @property
    def reverse_kwargs(self) -> dict[str, str]:
        kwargs = dict(
            subject_identifier=self.subject_identifier or self.model_obj.subject_identifier,
        )
        if self.appointment:
            # add appointment to return back to current timepoint
            # instead of schedule of all timepoints
            kwargs.update({"appointment": self.appointment.id})
        return kwargs

    @property
    def extra_kwargs(self) -> dict[str, str | int | UUID]:
        kwargs = dict(
            action_identifier=self.action_item.action_identifier,
        )
        if self.action == ADD:
            # Add field to prefill form
            for obj in [self.parent_reference_obj, self.related_reference_obj]:
                for fld in self.model_cls._meta.get_fields(include_hidden=True):
                    if fld.related_model == obj.__class__:
                        kwargs.update({fld.name: obj.id})
        return kwargs

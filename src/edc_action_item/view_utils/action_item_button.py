from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Type
from uuid import UUID

from django.contrib.sites.models import Site
from edc_view_utils import ModelButton

from ..models import ActionType

if TYPE_CHECKING:
    from edc_appointment.models import Appointment

    from edc_action_item import Action
    from edc_action_item.models import ActionItem


@dataclass(kw_only=True)
class ActionItemButton(ModelButton):
    action_cls: Type[Action] = None
    model_obj: ActionItem | None = None
    model_cls: Type[ActionItem] = field(default=None)
    appointment: Appointment = None
    next_url_name: str = field(default="subject_dashboard_url")

    @property
    def label(self) -> str | None:
        if self.fixed_label:
            return self.fixed_label
        return self.action_cls.reference_model_cls()._meta.verbose_name

    @property
    def site(self) -> Site | None:
        """If model_obj is None, then Site should come from the
        request object.
        """
        return (
            getattr(self.model_obj, "site", None)
            or getattr(self.appointment, "site", None)
            or getattr(self.request, "site", None)
        )

    def get_subject_identifier(self):
        if self.appointment:
            return self.appointment.subject_identifier
        return self.subject_identifier

    @property
    def url(self) -> str:
        url = super().url
        return url

    @property
    def reverse_kwargs(self) -> dict[str, str | UUID]:
        if self.appointment:
            return dict(
                subject_identifier=self.appointment.subject_identifier,
                appointment=self.appointment.id,
            )
        return dict(
            subject_identifier=self.subject_identifier,
        )

    @property
    def extra_kwargs(self) -> dict[str, UUID]:
        return dict(
            action_type=ActionType.objects.get(name=self.action_cls.name).id,
            priority=self.action_cls.priority,
            subject_identifier=self.get_subject_identifier(),
            appointment=getattr(self.appointment, "id", None),
            related_action_item_id=getattr(self.model_obj, "related_action_item_id", ""),
            parent_action_item_id=getattr(self.model_obj, "parent_action_item_id", ""),
        )

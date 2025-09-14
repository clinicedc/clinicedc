from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

__all__ = ["CrfButton"]

from edc_view_utils import DashboardModelButton


@dataclass
class CrfButton(DashboardModelButton):
    colors: tuple[str, str, str] = field(default=("warning", "success", "success"))

    @property
    def extra_kwargs(self) -> dict[str, str | int | UUID]:
        return {self.model_cls().related_visit_model_attr(): self.appointment.related_visit.id}

    @property
    def disabled(self) -> str:
        disabled = "disabled"
        if (not self.model_obj and self.perms.add) or self.perms.change:
            disabled = ""
        elif self.perms.view:
            if self.model_obj:
                disabled = ""
        return disabled

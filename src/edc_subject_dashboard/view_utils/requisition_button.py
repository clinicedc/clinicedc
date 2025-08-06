from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from django.apps import apps as django_apps

from .crf_button import CrfButton

if TYPE_CHECKING:
    from edc_lab.models import Panel

__all__ = ["RequisitionButton"]


@dataclass
class RequisitionButton(CrfButton):
    @property
    def btn_id(self) -> str:
        btn_id = super().btn_id
        if self.model_obj:
            btn_id = f"{btn_id}-{self.panel.name}"
        return btn_id

    @property
    def extra_kwargs(self) -> dict[str, str | int | UUID]:
        extra_kwargs = super().extra_kwargs
        extra_kwargs.update(panel=self.panel.id)
        return extra_kwargs

    @property
    def panel(self) -> Panel:
        if self.model_obj:
            panel = self.model_obj.panel
        else:
            panel_model_cls = django_apps.get_model("edc_lab.panel")
            panel = panel_model_cls.objects.get(name=self.metadata_model_obj.panel_name)
        return panel

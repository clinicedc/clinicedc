from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from edc_lab.models import Panel

from .crf_button import CrfButton

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
            panel = Panel.objects.get(name=self.metadata_model_obj.panel_name)
        return panel

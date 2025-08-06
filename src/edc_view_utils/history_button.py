from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from django.utils.translation import gettext as _

from edc_model.utils import get_history_url

if TYPE_CHECKING:
    from edc_metadata.models import CrfMetadata

__all__ = ["HistoryButton"]


@dataclass
class HistoryButton:
    model_obj: InitVar[CrfMetadata] = None
    color: str = field(default="default")
    url: str = field(default=None, init=False)
    disabled: str = field(default="disabled", init=False)
    btn_id: str = field(init=False)

    def __post_init__(self, model_obj: CrfMetadata):
        if model_obj.model_instance:
            self.url = get_history_url(model_obj.model_instance)
            if self.url:
                self.disabled = ""
                self.btn_id = (
                    f"{model_obj.model_cls._meta.label_lower.split('.')[1]}-history-"
                    f"{model_obj.model_instance.id.hex}"
                )
        else:
            self.btn_id = (
                f"{model_obj.model_cls._meta.label_lower.split('.')[1]}-history-"
                f"{uuid4().hex}"
            )

    @property
    def label(self) -> str:
        return _("Audit")

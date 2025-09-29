from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import UUID

from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import gettext as _

from edc_view_utils import DashboardModelButton

if TYPE_CHECKING:
    from edc_model.models import BaseUuidModel
    from edc_screening.model_mixins import ScreeningModelMixin

    class ScreeningModel(ScreeningModelMixin, BaseUuidModel): ...


__all__ = ["SubjectScreeningButton"]


@dataclass
class SubjectScreeningButton(DashboardModelButton):
    model_obj: ScreeningModel | None = None
    metadata_model_obj: models.Model = field(init=False)

    def __post_init__(self):
        self.model_cls = self.model_obj.__class__

    @property
    def color(self) -> str:
        return "success"

    @property
    def fa_icon(self) -> str:
        if self.perms.view_only:
            fa_icon = "fa-eye"
        else:
            fa_icon = "fa-eye" if self.model_obj.consented else "fa-pencil"
        return fa_icon

    @property
    def label(self) -> str:
        return ""

    @property
    def site(self) -> Site:
        return self.model_obj.site

    @property
    def reverse_kwargs(self) -> dict[str, str | UUID]:
        return dict(screening_identifier=self.model_obj.screening_identifier)

    @property
    def title(self) -> str:
        title = _("View") if self.perms.view_only or self.model_obj.consented else _("Edit")
        verbose_name = self.model_cls._meta.verbose_name.lower()
        return f"{title} {verbose_name}"

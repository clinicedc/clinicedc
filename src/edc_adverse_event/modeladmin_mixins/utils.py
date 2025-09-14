from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import TYPE_CHECKING

from django.conf import settings
from django.urls import reverse

from edc_model.models import BaseUuidModel
from edc_utils import convert_php_dateformat

if TYPE_CHECKING:
    from django.contrib import admin

    from .modeladmin_mixins import AdverseEventModelAdminMixin

    class ModelAdmin(AdverseEventModelAdminMixin, admin.ModelAdmin): ...

    class Model(BaseUuidModel):
        report_datetime: datetime
        ...


@dataclass(order=True)
class ColumnItem:
    """Prepare a label and url for use in list_display.

    Used my AE modeladmin"""

    modeladmin: ModelAdmin = field(compare=False)
    obj: Model = field(compare=False)
    search: str = field(compare=False)
    date_field: str | None = field(default="report_datetime", compare=False)
    verbose_name: str = field(init=False, repr=False, compare=False)
    formatted_date: str = field(init=False, repr=False, compare=False)
    model_cls: type[Model] = field(init=False, repr=False, compare=False)
    date_value: date = field(init=False, repr=False, compare=True)

    def __post_init__(self):
        try:
            self.date_value = getattr(self.obj, self.date_field).date()
        except AttributeError:
            self.date_value = getattr(self.obj, self.date_field)
        self.verbose_name = self.obj._meta.verbose_name
        self.formatted_date = self.date_value.strftime(
            convert_php_dateformat(settings.SHORT_DATE_FORMAT)
        )
        self.model_cls = self.obj.__class__

    @property
    def anchor(self) -> str:
        return (
            f'<a title="go to {self.verbose_name} for '
            f'{self.formatted_date}" href="{self.url}?q={self.search}">'
            f"<span nowrap>{self.verbose_name}</span></a>"
        )

    @property
    def url(self) -> str:
        url_name = "_".join(self.obj._meta.label_lower.split("."))
        namespace = self.modeladmin.admin_site.name
        return reverse(f"{namespace}:{url_name}_changelist")

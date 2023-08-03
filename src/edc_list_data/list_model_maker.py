from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from .row import Row

if TYPE_CHECKING:
    from django.apps import AppConfig


class ListModelMakerError(Exception):
    pass


class ListModelMaker:
    def __init__(
        self,
        display_index: int,
        row: tuple[str, str] | Row,
        model_name: str,
        apps: AppConfig | None = None,
    ):
        self.model_name = model_name
        self.apps = apps or django_apps
        self.display_index = display_index
        self.extra_value: str | None = None

        try:
            self.name, self.display_name = row
        except ValueError as e:
            raise ListModelMakerError(e)
        except TypeError as e:
            if "Row" not in str(e):
                raise
            try:
                self.name, self.display_name = row.data
                self.extra_value = row.extra
            except ValueError as e:
                raise ListModelMakerError(e)

    def create_or_update(self):
        try:
            obj = self.model_cls.objects.get(name=self.name)
        except ObjectDoesNotExist:
            obj = self.model_cls.objects.create(
                name=self.name,
                display_name=self.display_name,
                display_index=self.display_index,
                extra_value=self.extra_value,
            )
        else:
            obj.display_name = self.display_name
            obj.display_index = self.display_index
            obj.extra_value = self.extra_value
            obj.save()
        return obj

    @property
    def model_cls(self):
        return self.apps.get_model(self.model_name)

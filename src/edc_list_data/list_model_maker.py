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
        self.extra_value: str | None = None
        self.custom_name: str | None = None

        self.display_index = display_index
        self.model_name = model_name
        self.apps = apps or django_apps

        try:
            self.name, self.display_name = row
        except ValueError as e:
            raise ListModelMakerError(e) from e
        except TypeError as e:
            if "Row" not in str(e):
                raise
            self.name = row.name
            self.display_name = row.display_name
            self.extra_value = row.extra
            self.custom_name = row.custom_name

    def create_or_update(self):
        opts = dict(
            display_index=self.display_index,
            display_name=self.display_name,
            extra_value=self.extra_value or "",
        )
        if "custom_name" in [f.name for f in self.model_cls._meta.get_fields()]:
            opts.update(custom_name=self.custom_name)
        try:
            obj = self.model_cls.objects.get(name=self.name)
        except ObjectDoesNotExist:
            obj = self.model_cls.objects.create(name=self.name, **opts)
        else:
            for k, v in opts.items():
                setattr(obj, k, v)
            obj.save()
        return obj

    @property
    def model_cls(self):
        return self.apps.get_model(self.model_name)

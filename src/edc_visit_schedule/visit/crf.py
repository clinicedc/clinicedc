from __future__ import annotations

from django.apps import apps as django_apps
from django.db import models


class CrfLookupError(Exception):
    pass


class CrfModelNotProxyModelError(Exception):
    pass


class Crf:
    def __init__(
        self,
        show_order: int = None,
        model: str = None,
        required: bool = None,
        additional: bool = None,
        site_ids: list[int] = None,
        shares_proxy_root: bool = None,
    ) -> None:
        self.additional = additional
        self.model = model.lower()
        self.required = True if required is None else required
        self.show_order = show_order
        self.site_ids = site_ids or []
        self.shares_proxy_root = shares_proxy_root or False

        if self.shares_proxy_root and not self.model_cls._meta.proxy:
            raise CrfModelNotProxyModelError(
                "Invalid use of `shares_proxy_root=True`. "
                f"CRF model is not a proxy model. Got {self.full_name}."
            )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.show_order}, {self.model}, {self.required})"

    def __str__(self) -> str:
        required = "Required" if self.required else ""
        return f"{self.model} {required}"

    @property
    def name(self) -> str:
        return f"{self.model}.{'required' if self.required else 'not_required'}"

    def validate(self) -> None:
        """Raises an exception if the model class lookup fails."""
        try:
            self.get_model_cls()
        except LookupError as e:
            raise CrfLookupError(e) from e

    def get_model_cls(self) -> type[models.Model]:
        return self.model_cls

    @property
    def model_cls(self) -> type[models.Model]:
        return django_apps.get_model(self.model)

    @property
    def verbose_name(self) -> str:
        return self.model_cls._meta.verbose_name

    @property
    def full_name(self):
        return self.model

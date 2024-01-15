from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Type
from uuid import uuid4

from .perms import Perms

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django.contrib.sites.models import Site
    from edc_model.models import BaseUuidModel

    class Model(BaseUuidModel):
        ...


ADD: int = 0
CHANGE = 1
VIEW = 2

__all__ = ["ModelButton", "ADD", "CHANGE", "VIEW"]


@dataclass
class ModelButton:
    user: User = None
    model_obj: Model = None
    current_site: Site = None
    labels: tuple[str, str, str] = field(default=("Add", "Change", "View"))
    fa_icons: tuple[str, str, str] = field(default=("fas fa-plus", "fas fa-pen", "fas fa-eye"))
    btn_colors: tuple[str, str, str] = field(
        default=("btn-warning", "btn-success", "btn-default")
    )
    titles: tuple[str, str, str] = field(default=("Add", "Change", "View only"))
    model_cls: Type[Model] = field(default=None, init=False)
    _action: int = field(default=None, init=False)
    _perms: Perms = None

    @property
    def site(self) -> Site | None:
        """Returns the site for the model being changed."""
        return getattr(self.model_obj, "site", None)

    @property
    def fa_icon(self) -> str:
        return self.fa_icons[self.action]

    @property
    def label(self) -> str:
        return self.labels[self.action]

    @property
    def btn_color(self) -> str:
        return self.btn_colors[self.action]

    @property
    def title(self) -> str:
        return self.titles[self.action]

    @property
    def action(self):
        if not self._action:
            self._action = VIEW
            if not self.model_obj:
                self._action = ADD
            elif self.model_obj:
                if self.perms.change:
                    self._action = CHANGE
        return self._action

    @property
    def perms(self) -> Perms:
        if not self._perms:
            self._perms = Perms(
                model_cls=self.model_cls,
                user=self.user,
                current_site=self.current_site,
                site=self.site,
            )
        return self._perms

    @property
    def url(self) -> str:
        if self.action == ADD:
            url = self.model_cls().get_absolute_url()
        else:
            url = self.model_obj.get_absolute_url()
        return url

    @property
    def disabled(self) -> str:
        disabled = "disabled"
        if not self.model_obj and self.perms.add:
            disabled = ""
        else:
            if self.perms.change or self.perms.view:
                disabled = ""
        return disabled

    @property
    def btn_id(self) -> str:
        btn_id = f"{self.model_cls._meta.label_lower.split('.')[1]}-{uuid4().hex}"
        if self.model_obj:
            btn_id = (
                f"{self.model_cls._meta.label_lower.split('.')[1]}-" f"{self.model_obj.id.hex}"
            )
        return btn_id

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from django.core.handlers.wsgi import WSGIRequest
from django.utils.translation import gettext as _

from .next_querystring import NextQuerystring
from .perms import Perms

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django.contrib.sites.models import Site

    from edc_model.models import BaseUuidModel

    class Model(BaseUuidModel):
        subject_identifier: str
        ...

    class WSGIRequestObject(WSGIRequest):
        site: Site


ADD: int = 0
CHANGE = 1
VIEW = 2

__all__ = ["ADD", "CHANGE", "VIEW", "ModelButton"]


class ModelButtonError(Exception):
    pass


@dataclass(kw_only=True)
class ModelButton:
    user: User = None
    model_obj: Model = None
    model_cls: type[Model] = field(default=None)
    current_site: Site = None
    subject_identifier: str | None = None
    request: WSGIRequestObject | None = None
    fixed_label: str | None = None
    labels: tuple[str, str, str] = field(default=("Add", "Change", "View"))
    fa_icons: tuple[str, str, str] = field(default=("fas fa-plus", "fas fa-pen", "fas fa-eye"))
    fixed_color: str | None = None
    colors: tuple[str, str, str] = field(default=("warning", "success", "default"))
    titles: tuple[str, str, str] = field(default=("Add", "Change", "View only"))
    next_url_name: str = field(default=None)
    _action: int = field(default=None, init=False)
    _perms: Perms = field(default=None, init=False)

    def __post_init__(self):
        if self.model_obj:
            self.model_cls = self.model_obj._meta.model
        if not self.model_cls:
            raise ModelButtonError(f"Model class is required if instance=None. See {self}.")

    @property
    def fa_icon(self) -> str:
        return self.fa_icons[self.action]

    @property
    def label(self) -> str:
        if self.fixed_label:
            return _(self.fixed_label)
        return _(self.labels[self.action])

    @property
    def color(self) -> str:
        if self.fixed_color:
            return self.fixed_color
        return self.colors[self.action]

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
    def disabled(self) -> str:
        disabled = "disabled"
        if (not self.model_obj and self.perms.add) or (
            self.model_obj and (self.perms.change or self.perms.view)
        ):
            disabled = ""
        return disabled

    @property
    def btn_id(self) -> str:
        btn_id = f"{self.model_cls._meta.label_lower.split('.')[1]}-{uuid4().hex}"
        if self.model_obj:
            btn_id = (
                f"{self.model_cls._meta.label_lower.split('.')[1]}-{self.model_obj.id.hex}"
            )
        return btn_id

    @property
    def site(self) -> Site | None:
        """If model_obj is None, then Site should come from the
        request object (if add).
        """
        return getattr(self.model_obj, "site", None) or getattr(self.request, "site", None)

    @property
    def url(self) -> str:
        if self.action == ADD:
            url = "?".join([f"{self.model_cls().get_absolute_url()}", self.querystring])
        else:
            url = "?".join([f"{self.model_obj.get_absolute_url()}", self.querystring])
        return url

    @property
    def querystring(self) -> str:
        nq = NextQuerystring(
            next_url_name=self.next_url_name,
            reverse_kwargs=self.reverse_kwargs,
            extra_kwargs=self.extra_kwargs,
        )
        return nq.querystring

    @property
    def reverse_kwargs(self) -> dict[str, str]:
        return dict(
            subject_identifier=self.subject_identifier or self.model_obj.subject_identifier,
        )

    @property
    def extra_kwargs(self) -> dict[str, str | int]:
        return {}

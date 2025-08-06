from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps

if TYPE_CHECKING:
    from django.contrib.sites.models import Site


class SiteFormValidatorMixin:

    @property
    def site_model_cls(self) -> Site:
        return django_apps.get_model("sites.site")

    @property
    def site(self) -> Site:
        return (
            self.cleaned_data.get("site")
            or getattr(self.instance, "site", None)
            or self.site_model_cls.objects.get_current()
        )

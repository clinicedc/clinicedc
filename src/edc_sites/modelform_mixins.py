from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms
from django.apps import apps as django_apps

if TYPE_CHECKING:
    from django.contrib.sites.models import Site

__all__ = ["SiteModelFormMixin"]


class SiteModelFormMixin:
    """Validate the current site against a form question.

    This should be used sparingly. A good place is on the screening and/or consent form.

    Declare the modeladmin class with `SiteModelAdminMixin` to have
    the current site set on the form from the request object.

    Declare a `site` field with widget on the ModeForm:

    site = SiteField()

    You will also need to re-declare the `site` model field as `editable`.
    """

    def clean(self) -> dict:
        cleaned_data = super().clean()
        self.validate_with_current_site()
        return cleaned_data

    @property
    def site_model_cls(self) -> type[Site]:
        return django_apps.get_model("sites.site")

    @property
    def site(self) -> Site:
        if related_visit := getattr(self, "related_visit", None):
            return related_visit.site
        return (
            self.cleaned_data.get("site")
            or self.instance.site
            or self.site_model_cls.objects.get_current()
        )

    def validate_with_current_site(self) -> None:
        current_site = getattr(self, "current_site", None)
        if current_site and self.site and current_site.id != self.site.id:
            raise forms.ValidationError(
                {
                    "site": (
                        "Invalid. Please check you are logged into the correct site "
                        "before continuing"
                    )
                }
            )

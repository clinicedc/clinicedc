from __future__ import annotations

import collections

from django.contrib import admin
from django.core.exceptions import FieldError

from ..get_country import get_current_country
from ..get_language_choices_for_site import get_language_choices_for_site


class SiteModeAdminMixinError(Exception):
    pass


class SiteModelAdminMixin:
    language_db_field_name = "language"

    limit_related_to_current_country: list[str] = None
    limit_related_to_current_site: list[str] = None

    @admin.display(description="Site", ordering="site__id")
    def site_code(self, obj=None):
        return obj.site.id

    def get_queryset(self, request):
        """Limit modeladmin queryset for the current site only"""
        qs = super().get_queryset(request)
        if getattr(request, "site", None):
            try:
                qs = qs.filter(site_id=request.site.id)
            except FieldError:
                raise SiteModeAdminMixinError(
                    f"Model missing field `site`. Model `{self.model}`. Did you mean to use "
                    f"the SiteModelAdminMixin? See `{self}`."
                )
        return qs

    def get_form(self, request, obj=None, change=False, **kwargs):
        """Add current_site attr to form instance"""
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        form.current_site = getattr(request, "site", None)
        return form

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        """Use site id to select languages to show in choices."""
        if db_field.name == self.language_db_field_name:
            try:
                language_choices = get_language_choices_for_site(request.site, other=True)
            except AttributeError as e:
                if "WSGIRequest" not in str(e):
                    raise
            else:
                if language_choices:
                    kwargs["choices"] = language_choices
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter a ForeignKey field`s queryset by the current site
        or country.

        Note, a queryset set by the ModelForm class will overwrite
        the field's queryset added here.
        """
        self.raise_on_dups_in_field_lists(
            self.limit_related_to_current_country,
            self.limit_related_to_current_site,
        )
        if db_field.name in (self.limit_related_to_current_country or []):
            self.raise_on_queryset_exists(db_field, kwargs)
            country = get_current_country(request=request)
            model_cls = getattr(self.model, db_field.name).field.related_model
            kwargs["queryset"] = model_cls.objects.filter(siteprofile__country=country)
        elif db_field.name in (self.limit_related_to_current_site or []) and getattr(
            request, "site", None
        ):
            self.raise_on_queryset_exists(db_field, kwargs)
            model_cls = getattr(self.model, db_field.name).field.related_model
            kwargs["queryset"] = model_cls.objects.filter(id=request.site.id)
        elif db_field.name in (self.limit_related_to_current_site or []):
            self.raise_on_queryset_exists(db_field, kwargs)
            model_cls = getattr(self.model, db_field.name).field.related_model
            kwargs["queryset"] = model_cls.on_site.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Filter a ManyToMany field`s queryset by the current site.

        Note, a queryset set by the ModelForm class will overwrite
        the field's queryset added here.
        """
        self.raise_on_dups_in_field_lists(
            self.limit_related_to_current_country,
            self.limit_related_to_current_site,
        )
        if db_field.name in (self.limit_related_to_current_site or []):
            self.raise_on_queryset_exists(db_field, kwargs)
            model_cls = getattr(self.model, db_field.name).remote_field.model
            kwargs["queryset"] = model_cls.on_site.all()
        elif db_field.name in (self.limit_related_to_current_country or []):
            country = get_current_country(request=request)
            model_cls = getattr(self.model, db_field.name).remote_field.model
            kwargs["queryset"] = model_cls.objects.filter(siteprofile__country=country)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def raise_on_queryset_exists(self, db_field, kwargs):
        """Raise an exception if the `queryset` key exists in the
        kwargs dict.

        If `queryset` exists, remove the field name from the class attr:
            limit_fk_field_to_...
            limit_m2m_field_to_...
        """
        if "queryset" in kwargs:
            raise SiteModeAdminMixinError(
                f"Key `queryset` unexpectedly exists. Got field `{db_field.name}` "
                f"from {self}."
                f". Did you manually set key `queryset` for field `{db_field.name}`?"
            )

    @staticmethod
    def raise_on_dups_in_field_lists(*field_lists: list[str]):
        orig = []
        for field_list in field_lists:
            orig.extend(field_list or [])
        if dups := [item for item, count in collections.Counter(orig).items() if count > 1]:
            raise SiteModeAdminMixinError(
                f"Related field appears in more than one list. Got {dups}."
            )

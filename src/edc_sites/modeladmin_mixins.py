import collections

from django.contrib import admin
from django.core.exceptions import FieldError

from .get_country import get_current_country
from .get_language_choices_for_site import get_language_choices_for_site


class SiteModeAdminMixinError(Exception):
    pass


class SiteModelAdminMixin:
    """Adds the current site to the form from the request object.

    Use together with the `SiteModelFormMixin`.



    """

    language_db_field_name = "language"
    limit_fk_field_to_current_country: list[str] = None
    limit_fk_field_to_current_site: list[str] = None
    limit_m2m_field_to_current_site: list[str] = None

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
                pass
        return qs

    def get_form(self, request, obj=None, change=False, **kwargs):
        """Add current_site attr to form instance"""
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        form.current_site = getattr(request, "site", None)
        return form

    def formfield_for_choice_field(self, db_field, request, **kwargs):
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
        """Add a queryset to kwargs if a condition is a matched.

        Note, a queryset set at the form level will replace any
        queryset added to kwargs here.
        """
        self.raise_on_duplicates_in_fk_fields_lists()
        if db_field.name in (self.limit_fk_field_to_current_country or []):
            country = get_current_country(request)
            model_cls = getattr(self.model, db_field.name).field.related_model
            kwargs["queryset"] = model_cls.objects.filter(siteprofile__country=country)
        elif db_field.name in (self.limit_fk_field_to_current_site or []) and getattr(
            request, "site", None
        ):
            model_cls = getattr(self.model, db_field.name).field.related_model
            kwargs["queryset"] = model_cls.objects.filter(id=request.site.id)
        elif db_field.name in (self.limit_fk_field_to_current_site or []):
            model_cls = getattr(self.model, db_field.name).field.related_model
            kwargs["queryset"] = model_cls.on_site.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in (self.limit_m2m_field_to_current_site or []):
            model_cls = getattr(self.model, db_field.name).remote_field.model
            kwargs["queryset"] = model_cls.on_site.all()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def raise_on_duplicates_in_fk_fields_lists(self):
        orig = (self.limit_fk_field_to_current_country or []) + (
            self.limit_fk_field_to_current_site or []
        )
        if dups := [item for item, count in collections.Counter(orig).items() if count > 1]:
            raise SiteModeAdminMixinError(
                f"FK field name appears in more than one list. Got {dups}."
            )

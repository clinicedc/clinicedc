from typing import Tuple

from django.core.handlers.wsgi import WSGIRequest

from ..utils import get_remove_patient_names_from_countries


class PiiNamesModelAdminMixin:
    """Will remove name fields from the modeladmin if the country is listed
    in EDC_CONSENT_REMOVE_PATIENT_NAMES_FROM_COUNTRIES.

    Should be first in the MRO"""

    name_fields: list[str] = ["first_name", "last_name"]
    name_display_field: str = "first_name"
    all_sites: dict = {}

    def get_fieldsets(self, request: WSGIRequest, obj=None) -> tuple:
        fieldsets = super().get_fieldsets(request, obj=obj)
        return self.fieldsets_without_names(fieldsets, request)

    def get_fields(self, request: WSGIRequest, obj=None) -> Tuple[str, ...]:
        fields = super().get_fields(request, obj=obj)
        return self.fields_without_names(fields, request)

    def get_search_fields(self, request: WSGIRequest) -> Tuple[str, ...]:
        search_fields = super().get_search_fields(request)
        return self.fields_without_names(search_fields, request)

    def get_list_display(self, request) -> tuple:
        fields = super().get_list_display(request)
        return self.fields_without_names(fields, request)

    def fieldsets_without_names(self, fieldsets: tuple, request: WSGIRequest) -> tuple:
        for country in get_remove_patient_names_from_countries():
            site = getattr(request, "site", None)
            if site and site.id in [s.site_id for s in self.all_sites.get(country)]:
                for fieldset in fieldsets:
                    fields = fieldset[1].get("fields")
                    fieldset[1]["fields"] = [f for f in fields if f not in self.name_fields]
        return fieldsets

    def fields_without_names(self, fields: tuple, request: WSGIRequest) -> Tuple[str, ...]:
        for country in get_remove_patient_names_from_countries():
            site = getattr(request, "site", None)
            if site and site.id in [s.site_id for s in self.all_sites.get(country)]:
                fields = tuple([f for f in fields if f not in self.name_fields])
        return fields

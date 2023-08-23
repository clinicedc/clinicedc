import re
from copy import copy, deepcopy
from typing import Tuple

from django.core.handlers.wsgi import WSGIRequest
from edc_constants.constants import UUID_PATTERN
from edc_sites.validate_site_id import validated_site_id

from ..utils import get_site_ids_with_pii_perms


class PiiNamesModelAdminMixin:
    """Will remove name fields from the modeladmin if the country is listed
    in EDC_CONSENT_REMOVE_PATIENT_NAMES_FROM_COUNTRIES.

    Should be first in the MRO

    See also `edc_model_admin.ModelAdminProtectPiiMixin`
    """

    _original_fieldsets = None
    _original_fields = None
    _original_search_fields = None
    _original_list_display = None

    name_fields: list[str] = ["first_name", "last_name"]
    name_display_field: str = "first_name"
    all_sites: dict = {}

    def get_fieldsets(self, request: WSGIRequest, obj=None) -> tuple:
        fieldsets = super().get_fieldsets(request, obj=obj)
        if not self._original_fieldsets:
            self._original_fieldsets = deepcopy(fieldsets)
        return self.filter_fieldsets_for_pii_permissions(fieldsets, request)

    def get_fields(self, request: WSGIRequest, obj=None) -> Tuple[str, ...]:
        fields = super().get_fields(request, obj=obj)
        if not self._original_fields:
            self._original_fields = copy(fields)
        return self.filter_fields_for_pii_permissions(fields, request)

    def get_search_fields(self, request: WSGIRequest) -> Tuple[str, ...]:
        search_fields = super().get_search_fields(request)
        if not self._original_search_fields:
            self._original_search_fields = copy(search_fields)
        return self.filter_search_fields_for_pii_permissions(search_fields, request)

    def get_list_display(self, request) -> tuple:
        fields = super().get_list_display(request)
        if not self._original_list_display:
            self._original_list_display = copy(fields)
        return self.filter_list_display_for_pii_permissions(fields, request)

    def filter_fieldsets_for_pii_permissions(
        self, fieldsets: tuple, request: WSGIRequest
    ) -> tuple:
        site_id = validated_site_id(all_sites=self.all_sites, request=request)
        if site_id and site_id not in get_site_ids_with_pii_perms(self.all_sites):
            for index, fieldset in enumerate(self._original_fieldsets):
                fields = tuple(fieldset[1].get("fields"))
                filtered_fields = tuple([f for f in fields if f not in self.name_fields])
                if fields != filtered_fields:
                    fieldsets[index][1]["fields"] = filtered_fields
        return fieldsets

    def filter_fields_for_pii_permissions(
        self, fields: tuple, request: WSGIRequest
    ) -> Tuple[str, ...]:
        site_id = validated_site_id(all_sites=self.all_sites, request=request)
        if site_id and site_id not in get_site_ids_with_pii_perms(self.all_sites):
            filtered_fields = tuple(
                [f for f in self._original_fields if f not in self.name_fields]
            )
            if tuple(fields) != filtered_fields:
                fields = filtered_fields
        return fields

    def filter_list_display_for_pii_permissions(self, fields, request):
        site_id = validated_site_id(all_sites=self.all_sites, request=request)
        if site_id and site_id not in get_site_ids_with_pii_perms(self.all_sites):
            filtered_fields = tuple(
                [f for f in self._original_list_display if f not in self.name_fields]
            )
            if tuple(fields) != filtered_fields:
                fields = filtered_fields
        return fields

    def filter_search_fields_for_pii_permissions(self, fields, request):
        site_id = validated_site_id(all_sites=self.all_sites, request=request)
        if site_id and site_id not in get_site_ids_with_pii_perms(self.all_sites):
            filtered_fields = tuple(
                [f for f in self._original_search_fields if f not in self.name_fields]
            )
            if tuple(fields) != filtered_fields:
                fields = filtered_fields
        return fields

    def get_changeform_initial_data(self, request) -> dict:
        dct = super().get_changeform_initial_data(request)
        for field in self.name_fields:
            if re.match(UUID_PATTERN, dct.get(field, "")):
                dct.update({field: None})
        return dct

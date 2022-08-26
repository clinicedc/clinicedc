from typing import Tuple

from .fieldsets import action_fields


class ActionItemModelAdminMixin:
    def get_readonly_fields(self, request, obj=None) -> Tuple[str, ...]:
        """
        Returns a list of readonly field names.

        Note: "action_identifier" is remove.
            You are expected to use ActionItemFormMixin with the form.
        """
        fields = super().get_readonly_fields(request, obj=obj)
        fields += action_fields
        return tuple(f for f in fields if f != "action_identifier")

    def get_search_fields(self, request) -> Tuple[str, ...]:
        search_fields = super().get_search_fields(request)
        custom_fields = ("action_identifier",)
        if "subject_identifier" in self.model._meta.fields:
            custom_fields = ("subject_identifier",) + custom_fields
        return tuple(set(custom_fields + search_fields))

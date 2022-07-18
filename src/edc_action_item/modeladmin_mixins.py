from copy import copy

from .fieldsets import action_fields


class ActionItemModelAdminMixin:
    def get_readonly_fields(self, request, obj=None) -> tuple:
        """
        Returns a list of readonly field names.

        Note: "action_identifier" is remove.
            You are expected to use ActionItemFormMixin with the form.
        """
        fields = super().get_readonly_fields(request, obj=obj)
        action_flds = copy(list(action_fields))
        action_flds.remove("action_identifier")
        return tuple(fields) + tuple(action_flds)

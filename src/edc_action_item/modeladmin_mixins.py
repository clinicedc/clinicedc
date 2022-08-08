from .fieldsets import action_fields


class ActionItemModelAdminMixin:
    def get_readonly_fields(self, request, obj=None) -> tuple:
        """
        Returns a list of readonly field names.

        Note: "action_identifier" is remove.
            You are expected to use ActionItemFormMixin with the form.
        """
        fields = super().get_readonly_fields(request, obj=obj)
        fields += action_fields
        return tuple(f for f in fields if f != "action_identifier")

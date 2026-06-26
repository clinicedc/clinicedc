from django.apps import apps as django_apps
from django.contrib import admin


class MissingModelAdminMixin:
    def has_add_permission(self, request) -> bool:  # noqa: ARG002
        return False

    @admin.display(description="Visit", ordering="visit_code")
    def visit_as_string(self, obj=None) -> str | None:
        if obj:
            return f"{obj.visit_code}.{obj.visit_code_sequence}"
        return None

    @admin.display(description="Model", ordering="model")
    def model_verbose_name(self, obj=None) -> str | None:
        if obj:
            return django_apps.get_model(obj.model)._meta.verbose_name
        return None

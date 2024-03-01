from django_audit_fields import audit_fieldset_tuple

from ..fieldsets import REQUIRES_CONSENT_FIELDS, requires_consent_fieldset_tuple


class RequiresConsentModelAdminMixin:

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj=obj)
        fieldsets = list(fieldsets)
        for index, fieldset in enumerate(fieldsets):
            if fieldset == audit_fieldset_tuple:
                fieldsets.insert(index, requires_consent_fieldset_tuple)
                break
        return tuple(fieldsets)

    def get_readonly_fields(self, request, obj=None) -> tuple[str, ...]:
        readonly_fields = super().get_readonly_fields(request, obj=obj)
        return tuple(set(readonly_fields + REQUIRES_CONSENT_FIELDS))

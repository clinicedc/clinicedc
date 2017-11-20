from django.contrib import admin

from .model_admin_audit_fields_mixin import audit_fieldset_tuple, audit_fields


class AddressModelAdminMixin(admin.ModelAdmin):

    fieldsets = (
        (None, {
            'fields': (
                'contact_name',
                'name',
                'address',
                'postal_code',
                'city',
                'country',
                'telephone',
                'mobile',
                'fax',
                'email'
            )}),
        audit_fieldset_tuple)

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj=obj) + audit_fields

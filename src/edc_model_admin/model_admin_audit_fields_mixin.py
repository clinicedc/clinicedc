from edc_base.utils import get_utcnow

audit_fields = ('user_created', 'user_modified',
                'created', 'modified', 'hostname_created', 'hostname_modified')

audit_fieldset_tuple = (
    'Audit', {
        'classes': ('collapse',),
        'fields': audit_fields})


class ModelAdminAuditFieldsMixin:

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user_created = request.user.username
            obj.created = get_utcnow()
        else:
            obj.user_modified = request.user.username
            obj.modified = get_utcnow()
        super().save_model(request, obj, form, change)

    def get_list_filter(self, request):
        columns = ['created', 'modified', 'user_created',
                   'user_modified', 'hostname_created', 'hostname_modified']
        self.list_filter = list(self.list_filter or [])
        self.list_filter = self.list_filter + \
            [item for item in columns if item not in self.list_filter]
        return tuple(self.list_filter)

    def get_readonly_fields(self, request, obj=None):
        # FIXME: somewhere the readonly_fields is being changed to a list
        readonly_fields = super().get_readonly_fields(request, obj=obj)
        if readonly_fields:
            readonly_fields = tuple(readonly_fields)
        return readonly_fields + audit_fields

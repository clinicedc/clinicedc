from import_export.admin import ExportMixin

from edc_data_manager.auth_objects import DATA_MANAGER_ROLE


class ExportMixinModelAdminMixin(ExportMixin):
    export_roles = (DATA_MANAGER_ROLE,)

    def has_export_permission(self, request):
        try:
            roles = request.user.userprofile.roles
        except AttributeError:
            return False
        return roles.filter(name__in=self.export_roles).exists()

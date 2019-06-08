from django.contrib import admin
from django.contrib.admin.decorators import register
from edc_auth.admin import UserAdmin as BaseUserAdmin
from edc_metadata.models import CrfMetadata
from edc_permissions.constants.group_names import DATA_MANAGER
from edc_registration.admin import RegisteredSubjectAdmin as BaseRegisteredSubjectAdmin
from edc_visit_schedule.admin import VisitScheduleAdmin as BaseVisitScheduleAdmin

from ..admin_site import edc_data_manager_admin
from ..models import QueryUser, DataManagerUser, QueryVisitSchedule, QuerySubject


@register(QuerySubject, site=edc_data_manager_admin)
class QuerySubjectAdmin(BaseRegisteredSubjectAdmin):
    ordering = ("subject_identifier",)
    search_fields = ("subject_identifier",)


@register(DataManagerUser, site=edc_data_manager_admin)
class DataManagerUserAdmin(BaseUserAdmin):
    ordering = ("first_name", "last_name")
    search_fields = ("first_name", "last_name", "username", "email")

    inlines = []

    def get_queryset(self, request):
        return super().get_queryset(request).filter(groups__name=DATA_MANAGER)


@register(QueryUser, site=edc_data_manager_admin)
class QueryUserAdmin(BaseUserAdmin):
    ordering = ("first_name", "last_name")
    search_fields = ("first_name", "last_name", "username", "email")

    inlines = []

    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            userprofile__sites__id=request.site.id
        ).exclude(groups__name=DATA_MANAGER)


@register(CrfMetadata, site=edc_data_manager_admin)
class CrfMetadataAdmin(admin.ModelAdmin):
    ordering = ("model",)
    search_fields = ("model",)


@register(QueryVisitSchedule, site=edc_data_manager_admin)
class QueryVisitScheduleAdmin(BaseVisitScheduleAdmin):
    pass

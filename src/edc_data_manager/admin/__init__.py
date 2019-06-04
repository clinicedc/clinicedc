from django.contrib import admin
from django.contrib.admin.decorators import register
from django.contrib.auth.models import User
from edc_metadata.models import CrfMetadata
from edc_registration.models import RegisteredSubject

from ..admin_site import edc_data_manager_admin
from .data_dictionary_admin import DataDictionaryAdmin
from .data_manager_query_admin import DataManagerQueryAdmin
from .query_admin import QueryAdmin
from .visit_schedule_admin import VisitScheduleAdmin


@register(RegisteredSubject, site=edc_data_manager_admin)
class RegisteredSubjectAdmin(admin.ModelAdmin):
    ordering = ("subject_identifier",)
    search_fields = ("subject_identifier",)


@register(User, site=edc_data_manager_admin)
class UserAdmin(admin.ModelAdmin):
    ordering = ("first_name", "last_name")
    search_fields = ("first_name", "last_name", "username")


@register(CrfMetadata, site=edc_data_manager_admin)
class CrfMetadataAdmin(admin.ModelAdmin):
    ordering = ("model",)
    search_fields = ("model",)

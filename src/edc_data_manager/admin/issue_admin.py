from django.contrib import admin
from edc_form_runners.admin import IssueAdmin as BaseIssueAdmin

from edc_data_manager.admin_site import edc_data_manager_admin

from ..models import Issue


@admin.register(Issue, site=edc_data_manager_admin)
class IssueAdmin(BaseIssueAdmin):
    pass

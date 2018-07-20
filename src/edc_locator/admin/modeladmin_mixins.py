from django_revision.modeladmin_mixin import ModelAdminRevisionMixin
from edc_model_admin import (
    ModelAdminNextUrlRedirectMixin, ModelAdminFormInstructionsMixin,
    ModelAdminFormAutoNumberMixin, ModelAdminAuditFieldsMixin,
    ModelAdminReadOnlyMixin, ModelAdminInstitutionMixin,
    ModelAdminRedirectOnDeleteMixin)
from django.urls.base import reverse
from django.conf import settings
from edc_subject_dashboard import ModelAdminSubjectDashboardMixin


class ModelAdminMixin(ModelAdminNextUrlRedirectMixin, ModelAdminFormInstructionsMixin,
                      ModelAdminFormAutoNumberMixin, ModelAdminRevisionMixin,
                      ModelAdminAuditFieldsMixin, ModelAdminReadOnlyMixin,
                      ModelAdminInstitutionMixin, ModelAdminRedirectOnDeleteMixin,
                      ModelAdminSubjectDashboardMixin):

    list_per_page = 10
    date_hierarchy = 'modified'
    empty_value_display = '-'
    subject_dashboard_url = 'subject_dashboard_url'

    post_url_on_delete_name = settings.DASHBOARD_URL_NAMES.get(
        subject_dashboard_url)

    def post_url_on_delete_kwargs(self, request, obj):
        return dict(subject_identifier=obj.subject_identifier)

    def redirect_url(self, request, obj, post_url_continue=None):
        if obj:
            return reverse(settings.DASHBOARD_URL_NAMES.get(
                self.subject_dashboard_url),
                kwargs=dict(subject_identifier=obj.subject_identifier))
        else:
            return super().redirect_url(request, obj, post_url_continue)

from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse, NoReverseMatch
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin
from edc_model_admin import (
    ModelAdminNextUrlRedirectMixin,
    ModelAdminFormInstructionsMixin,
    ModelAdminFormAutoNumberMixin,
    ModelAdminAuditFieldsMixin,
    ModelAdminInstitutionMixin,
    ModelAdminRedirectOnDeleteMixin,
    ModelAdminReplaceLabelTextMixin,
    TemplatesModelAdminMixin,
)
from edc_notification import NotificationModelAdminMixin


class ModelAdminSubjectDashboardMixin(
    TemplatesModelAdminMixin,
    ModelAdminNextUrlRedirectMixin,
    NotificationModelAdminMixin,
    ModelAdminFormInstructionsMixin,
    ModelAdminFormAutoNumberMixin,
    ModelAdminRevisionMixin,
    ModelAdminAuditFieldsMixin,
    ModelAdminInstitutionMixin,
    ModelAdminRedirectOnDeleteMixin,
    ModelAdminReplaceLabelTextMixin,
):

    date_hierarchy = "modified"
    empty_value_display = "-"
    list_per_page = 10
    subject_dashboard_url_name = "subject_dashboard_url"
    show_cancel = False

    def get_subject_dashboard_url_name(self):
        return settings.DASHBOARD_URL_NAMES.get(self.subject_dashboard_url_name)

    def get_subject_dashboard_url_kwargs(self, obj):
        return dict(subject_identifier=obj.subject_identifier)

    def get_post_url_on_delete_name(self, *args):
        return self.get_subject_dashboard_url_name()

    def post_url_on_delete_kwargs(self, request, obj):
        return self.get_subject_dashboard_url_kwargs(obj)

    def dashboard(self, obj=None):
        url = reverse(
            self.get_subject_dashboard_url_name(),
            kwargs=self.get_subject_dashboard_url_kwargs(obj),
        )
        context = dict(
            dashboard="dashboard", title="Go to subject's dashboard", url=url
        )
        return render_to_string("dashboard_button.html", context=context)

    def view_on_site(self, obj):
        try:
            url = reverse(
                self.get_subject_dashboard_url_name(),
                kwargs=self.get_subject_dashboard_url_kwargs(obj),
            )
        except NoReverseMatch:
            url = super().view_on_site(obj)
        return url

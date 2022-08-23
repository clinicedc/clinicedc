from django.apps import apps as django_apps
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields.admin import ModelAdminAuditFieldsMixin
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin
from edc_appointment.models import Appointment
from edc_dashboard import url_names
from edc_model_admin.mixins import (
    ModelAdminFormAutoNumberMixin,
    ModelAdminFormInstructionsMixin,
    ModelAdminInstitutionMixin,
    ModelAdminNextUrlRedirectMixin,
    TemplatesModelAdminMixin,
)


class ModelAdminMixin(
    TemplatesModelAdminMixin,
    ModelAdminNextUrlRedirectMixin,
    ModelAdminFormInstructionsMixin,
    ModelAdminFormAutoNumberMixin,
    ModelAdminRevisionMixin,
    ModelAdminAuditFieldsMixin,
    ModelAdminInstitutionMixin,
):
    subject_dashboard_url_name = "subject_dashboard_url"
    subject_listboard_url_name = "subject_listboard_url"

    def get_subject_dashboard_url_name(self):
        return url_names.get(self.subject_dashboard_url_name)

    def get_subject_dashboard_url_kwargs(self, obj):
        appointment = Appointment.objects.get(
            subject_identifier=obj.subject_identifier,
            visit_code=obj.visit_code,
            visit_code_sequence=obj.visit_code_sequence,
        )
        return dict(
            subject_identifier=obj.subject_identifier,
            appointment=appointment.id,
        )

    def dashboard(self, obj=None, label=None):
        opts = self.get_subject_dashboard_url_kwargs(obj)
        appointment_model_cls = django_apps.get_model("edc_appointment.appointment")
        if not appointment_model_cls.objects.get(id=opts.get("appointment")).visit:
            opts.pop("appointment")
        url = reverse(
            self.get_subject_dashboard_url_name(),
            kwargs=opts,
        )
        context = dict(title="Go to subject's dashboard", url=url, label=label)
        return render_to_string("dashboard_button.html", context=context)

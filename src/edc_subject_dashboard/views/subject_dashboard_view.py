from django.core.exceptions import ImproperlyConfigured
from django.views.generic.base import ContextMixin
from edc_action_item.view_mixins import ActionItemViewMixin
from edc_appointment.view_mixins import AppointmentViewMixin
from edc_consent.view_mixins import ConsentViewMixin
from edc_dashboard.views import DashboardView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_locator.view_mixins import SubjectLocatorViewMixin
from edc_metadata.view_mixins import MetaDataViewMixin
from edc_navbar.view_mixin import NavbarViewMixin
from edc_visit_schedule.view_mixins import VisitScheduleViewMixin

from edc_subject_model_wrappers import (
    AppointmentModelWrapper,
    SubjectConsentModelWrapper,
    SubjectLocatorModelWrapper,
    SubjectVisitModelWrapper,
)
from ..view_mixins import RegisteredSubjectViewMixin, SubjectVisitViewMixin


class VerifyRequisitionMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scanning = self.kwargs.get("scanning")
        context.update(scanning=scanning)
        return context


class SubjectDashboardView(
    EdcViewMixin,
    NavbarViewMixin,
    MetaDataViewMixin,
    ConsentViewMixin,
    SubjectLocatorViewMixin,
    AppointmentViewMixin,
    ActionItemViewMixin,
    SubjectVisitViewMixin,
    VisitScheduleViewMixin,
    RegisteredSubjectViewMixin,
    VerifyRequisitionMixin,
    DashboardView,
):

    navbar_name = None  # e.g. "ambition_dashboard"
    navbar_selected_item = "consented_subject"

    dashboard_url = "subject_dashboard_url"
    dashboard_template = "subject_dashboard_template"

    appointment_model = "edc_appointment.appointment"
    appointment_model_wrapper_cls = AppointmentModelWrapper

    consent_model = None
    consent_model_wrapper_cls = SubjectConsentModelWrapper

    subject_locator_model = "edc_locator.subjectlocator"
    subject_locator_model_wrapper_cls = SubjectLocatorModelWrapper

    visit_model = None
    visit_model_wrapper_cls = SubjectVisitModelWrapper

    def __init__(self, **kwargs):
        if not self.navbar_name:
            raise ImproperlyConfigured(
                f"'navbar_name' cannot be None. See {repr(self)}.")
        self.appointment_model_wrapper_cls.visit_model_wrapper_cls = (
            self.visit_model_wrapper_cls)
        if self.visit_model:
            self.visit_model_wrapper_cls.model = self.visit_model
        else:
            self.visit_model = self.visit_model_wrapper_cls.model
        if self.consent_model:
            self.consent_model_wrapper_cls.model = self.consent_model
        else:
            self.consent_model = self.consent_model_wrapper_cls.model
        super().__init__(**kwargs)

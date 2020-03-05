from django import forms
from django.conf import settings
from edc_consent.modelform_mixins import RequiresConsentModelFormMixin
from edc_form_validators import FormValidatorMixin
from edc_sites.forms import SiteModelFormMixin
from edc_visit_schedule.modelform_mixins import SubjectScheduleModelFormMixin
from edc_visit_tracking.modelform_mixins import VisitTrackingModelFormMixin


class CrfModelFormMixin(
    SiteModelFormMixin,
    RequiresConsentModelFormMixin,
    SubjectScheduleModelFormMixin,
    VisitTrackingModelFormMixin,
    FormValidatorMixin,
):
    pass


class InlineCrfModelFormMixin(FormValidatorMixin, forms.ModelForm):
    visit_model = settings.SUBJECT_VISIT_MODEL

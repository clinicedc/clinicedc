from django import forms
from edc_form_validators import FormValidatorMixin
from edc_sites.forms import SiteModelFormMixin
from edc_visit_schedule.modelform_mixins import SubjectScheduleCrfModelFormMixin

from .visit_tracking_modelform_mixin import VisitTrackingModelFormMixin


class SubjectModelFormMixin(
    SiteModelFormMixin,
    FormValidatorMixin,
    SubjectScheduleCrfModelFormMixin,
    VisitTrackingModelFormMixin,
    forms.ModelForm,
):

    visit_model = None  # SubjectVisit


class InlineSubjectModelFormMixin(FormValidatorMixin, forms.ModelForm):

    visit_model = None  # SubjectVisit

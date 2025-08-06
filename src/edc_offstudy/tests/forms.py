from django import forms
from edc_model_form.mixins import BaseModelFormMixin
from edc_visit_schedule.modelform_mixins import VisitScheduleCrfModelFormMixin
from edc_visit_tracking.modelform_mixins import VisitTrackingCrfModelFormMixin

from ..modelform_mixins import (
    OffstudyCrfModelFormMixin,
    OffstudyModelFormMixin,
    OffstudyNonCrfModelFormMixin,
)
from ..models import SubjectOffstudy
from .models import CrfOne, NonCrfOne


class SubjectOffstudyForm(OffstudyModelFormMixin, BaseModelFormMixin, forms.ModelForm):
    class Meta:
        model = SubjectOffstudy
        fields = "__all__"


class CrfOneForm(
    OffstudyCrfModelFormMixin,
    VisitScheduleCrfModelFormMixin,
    VisitTrackingCrfModelFormMixin,
    BaseModelFormMixin,
    forms.ModelForm,
):
    report_datetime_field_attr = "report_datetime"

    class Meta:
        model = CrfOne
        fields = "__all__"


class NonCrfOneForm(OffstudyNonCrfModelFormMixin, BaseModelFormMixin, forms.ModelForm):
    report_datetime_field_attr = "report_datetime"

    class Meta:
        model = NonCrfOne
        fields = "__all__"

from django import forms

from edc_appointment.form_validator_mixins import NextAppointmentCrfFormValidatorMixin
from edc_appointment.modelform_mixins import NextAppointmentCrfModelFormMixin
from edc_consent.form_validators import SubjectConsentFormValidatorMixin
from edc_consent.modelform_mixins import ConsentModelFormMixin
from edc_crf.crf_form_validator import CrfFormValidator
from edc_crf.crf_form_validator_mixins import BaseFormValidatorMixin
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_form_validators import FormValidator, FormValidatorMixin

from .models import CrfThree, NextAppointmentCrf, SubjectConsentV1


class NextAppointmentCrfFormValidator(
    NextAppointmentCrfFormValidatorMixin, CrfFormValidator
):
    pass


class SubjectConsentFormValidator(
    SubjectConsentFormValidatorMixin, BaseFormValidatorMixin, FormValidator
):
    pass


class SubjectConsentForm(ConsentModelFormMixin, FormValidatorMixin, forms.ModelForm):
    form_validator_cls = SubjectConsentFormValidator

    screening_identifier = forms.CharField(
        label="Screening identifier",
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    class Meta:
        model = SubjectConsentV1
        fields = "__all__"


class CrfThreeForm(
    NextAppointmentCrfModelFormMixin, CrfModelFormMixin, forms.ModelForm
):
    form_validator_cls = NextAppointmentCrfFormValidator

    appt_date_fld = "appt_date"
    visit_code_fld = "f1"

    def validate_against_consent(self) -> None:
        pass

    class Meta:
        model = CrfThree
        fields = "__all__"
        labels = {"appt_date": "Next scheduled appointment date"}


class NextAppointmentCrfForm(
    NextAppointmentCrfModelFormMixin, CrfModelFormMixin, forms.ModelForm
):
    form_validator_cls = NextAppointmentCrfFormValidator

    def validate_against_consent(self) -> None:
        pass

    class Meta:
        model = NextAppointmentCrf
        fields = "__all__"

from django import forms

from edc_action_item.forms import ActionItemFormMixin
from edc_appointment.form_validator_mixins import NextAppointmentCrfFormValidatorMixin
from edc_appointment.modelform_mixins import NextAppointmentCrfModelFormMixin
from edc_consent.form_validators import SubjectConsentFormValidatorMixin
from edc_consent.modelform_mixins import ConsentModelFormMixin
from edc_crf.crf_form_validator import CrfFormValidator
from edc_crf.crf_form_validator_mixins import BaseFormValidatorMixin
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_form_validators import FormValidator, FormValidatorMixin
from edc_model_form.mixins import BaseModelFormMixin
from edc_pharmacy.form_validators import (
    StudyMedicationFormValidator as BaseStudyMedicationFormValidator,
)
from edc_sites.modelform_mixins import SiteModelFormMixin
from edc_visit_schedule.modelform_mixins import OffScheduleModelFormMixin
from edc_visit_tracking.form_validators import VisitMissedFormValidator
from edc_visit_tracking.models import SubjectVisitMissed

from .models import (
    CrfThree,
    NextAppointmentCrf,
    OffSchedule,
    StudyMedication,
    SubjectConsentV1,
    TestModel3,
    TestModel5,
)


class OffScheduleFormValidator(FormValidator):
    pass


class NextAppointmentCrfFormValidator(
    NextAppointmentCrfFormValidatorMixin, CrfFormValidator
):
    pass


class SubjectConsentFormValidator(
    SubjectConsentFormValidatorMixin, BaseFormValidatorMixin, FormValidator
):
    pass


class StudyMedicationFormValidator(BaseStudyMedicationFormValidator):
    def validate_demographics(self) -> None:
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


class OffScheduleForm(
    OffScheduleModelFormMixin,
    SiteModelFormMixin,
    FormValidatorMixin,
    ActionItemFormMixin,
    BaseModelFormMixin,
    forms.ModelForm,
):
    form_validator_cls = OffScheduleFormValidator
    report_datetime_field_attr = "offschedule_datetime"

    class Meta:
        model = OffSchedule
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


class TestModel3Form(forms.ModelForm):
    class Meta:
        model = TestModel3
        fields = "__all__"


class TestModel5Form(forms.ModelForm):
    class Meta:
        model = TestModel5
        fields = "__all__"


class SubjectVisitMissedForm(CrfModelFormMixin, forms.ModelForm):
    form_validator_cls = VisitMissedFormValidator

    def validate_against_consent(self):
        pass

    class Meta:
        model = SubjectVisitMissed
        fields = "__all__"


class StudyMedicationForm(CrfModelFormMixin, forms.ModelForm):
    form_validator_cls = StudyMedicationFormValidator

    def validate_against_consent(self):
        pass

    class Meta:
        model = StudyMedication
        fields = "__all__"

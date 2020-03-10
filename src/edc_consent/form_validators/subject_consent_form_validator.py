from dateutil.relativedelta import relativedelta
from django import forms
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_screening.utils import get_subject_screening_model
from edc_utils.date import to_utc
from edc_utils.text import convert_php_dateformat
from pytz import timezone


class SubjectConsentFormValidatorMixin:

    subject_screening_model = get_subject_screening_model()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._subject_screening = None
        self._consent_datetime = None
        self.dob = self.cleaned_data.get("dob")
        self.gender = self.cleaned_data.get("gender")
        self.guardian_name = self.cleaned_data.get("guardian_name")
        self.screening_identifier = self.cleaned_data.get("screening_identifier")
        self.tz = timezone(settings.TIME_ZONE)

    def clean(self):

        self.validate_consent_datetime()

        self.validate_age()

        self.validate_gender()

        self.validate_identity()

    @property
    def subject_screening_model_cls(self):
        return django_apps.get_model(self.subject_screening_model)

    @property
    def consent_datetime(self):
        if not self._consent_datetime:
            if "consent_datetime" in self.cleaned_data:
                if self.add_form and not self.cleaned_data.get("consent_datetime"):
                    raise forms.ValidationError(
                        {"consent_datetime": "This field is required."}
                    )
                self._consent_datetime = to_utc(
                    self.cleaned_data.get("consent_datetime")
                )
            else:
                self._consent_datetime = self.instance.consent_datetime
        return self._consent_datetime

    @property
    def subject_screening(self):
        if not self._subject_screening:
            try:
                self._subject_screening = self.subject_screening_model_cls.objects.get(
                    screening_identifier=self.screening_identifier
                )
            except ObjectDoesNotExist:
                raise forms.ValidationError(
                    'Complete the "Subject Screening" form before proceeding.',
                    code="missing_subject_screening",
                )
        return self._subject_screening

    def validate_age(self):
        """Validate age matches that on the screening form.
        """
        screening_age_in_years = relativedelta(
            self.subject_screening.report_datetime.date(), self.dob
        ).years
        if screening_age_in_years != self.subject_screening.age_in_years:
            raise forms.ValidationError(
                {
                    "dob": "Age mismatch. The date of birth entered does "
                    f"not match the age at screening. "
                    f"Expected {self.subject_screening.age_in_years}. "
                    f"Got {screening_age_in_years}."
                }
            )

    def validate_gender(self):
        """Validate gender matches that on the screening form.
        """
        if self.gender != self.subject_screening.gender:
            raise forms.ValidationError(
                {
                    "gender": "Gender mismatch. The gender entered does "
                    f"not match that reported at screening. "
                    f"Expected '{self.subject_screening.get_gender_display()}'. "
                }
            )

    def validate_consent_datetime(self):
        """Validate consent datetime with the eligibility datetime.

        Eligibility datetime must come first.

        Watchout for timezone.
        """
        if (
            self.consent_datetime - self.subject_screening.eligibility_datetime
        ).total_seconds() < 0:
            local_dt = self.subject_screening.eligibility_datetime.astimezone(self.tz)
            formatted = local_dt.strftime(
                convert_php_dateformat(settings.SHORT_DATETIME_FORMAT)
            )
            raise forms.ValidationError(
                {
                    "consent_datetime": (
                        f"Cannot be before the date and time eligibility "
                        f"was confirmed. Eligibility was confirmed at "
                        f"{formatted}."
                    )
                },
            )

    def validate_identity(self):
        pass

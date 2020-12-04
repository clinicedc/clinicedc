from django import forms
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import LOST_TO_FOLLOWUP, NO, YES
from edc_form_validators import FormValidator
from edc_utils import convert_php_dateformat
from edc_visit_tracking.constants import MISSED_VISIT
from edc_visit_tracking.models import get_subject_visit_model


class LossToFollowupFormValidator(FormValidator):
    def clean(self):
        self.check_if_last_visit_was_missed()
        self.required_if(YES, field="phone", field_required="phone_attempts")
        self.required_if(YES, field="home_visit", field_required="home_visit_detail")
        if (
            self.cleaned_data.get("phone_attempts") == 0
            and self.cleaned_data.get("home_visit") == NO
        ):
            raise forms.ValidationError(
                "No contact attempted. An attempt must be made to contact "
                "the patient by phone or home visit before declaring as lost "
                "to follow up."
            )
        self.validate_other_specify(
            field="loss_category", other_specify_field="loss_category_other"
        )

    def check_if_last_visit_was_missed(self):
        last_obj = (
            get_subject_visit_model()
            .objects.filter(
                appointment__subject_identifier=self.cleaned_data.get(
                    "subject_identifier"
                ),
            )
            .last()
        )
        if last_obj.reason != MISSED_VISIT:
            raise forms.ValidationError(
                f"Wait! Last visit was not reported as `missed`. Got {last_obj}"
            )
        return True


class LtfuFormValidatorMixin:
    """Used in off schedule form or any form that
    needs to confirm the LTFU form was submitted
    first.
    """

    loss_to_followup_model = None  # "inte_prn.losstofollowup"
    loss_to_followup_date_field = None  # "ltfu_date"
    loss_to_followup_reason = LOST_TO_FOLLOWUP

    @property
    def loss_to_followup_model_cls(self):
        return django_apps.get_model(self.loss_to_followup_model)

    def validate_loss_to_followup(self):
        if self.loss_to_followup_model and (
            self.cleaned_data.get("subject_identifier") or self.instance
        ):
            subject_identifier = (
                self.cleaned_data.get("subject_identifier")
                or self.instance.subject_identifier
            )

            try:
                ltfu = django_apps.get_model(self.loss_to_followup_model).objects.get(
                    subject_identifier=subject_identifier
                )
            except ObjectDoesNotExist:
                if (
                    self.cleaned_data.get(self.offschedule_reason_field)
                    and self.cleaned_data.get(self.offschedule_reason_field).name
                    == self.loss_to_followup_reason
                ):
                    msg = (
                        "Patient is lost to followup, please complete "
                        f"`{self.loss_to_followup_model_cls._meta.verbose_name}` "
                        "form first."
                    )
                    raise forms.ValidationError({self.offschedule_reason_field: msg})
            else:
                if self.cleaned_data.get(self.loss_to_followup_date_field) and (
                    ltfu.ltfu_date
                    != self.cleaned_data.get(self.loss_to_followup_date_field)
                ):
                    expected = ltfu.ltfu_date.strftime(
                        convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                    )
                    got = self.cleaned_data.get(
                        self.loss_to_followup_date_field
                    ).strftime(convert_php_dateformat(settings.SHORT_DATE_FORMAT))
                    raise forms.ValidationError(
                        {
                            self.loss_to_followup_date_field: (
                                "Date does not match "
                                f"`{self.loss_to_followup_model_cls._meta.verbose_name}` "
                                f"form. Expected {expected}. Got {got}."
                            )
                        }
                    )

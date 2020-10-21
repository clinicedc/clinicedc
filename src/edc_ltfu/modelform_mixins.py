from django import forms
from edc_constants.constants import NO, YES
from edc_form_validators import FormValidator
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

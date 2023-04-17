from edc_constants.constants import OTHER, YES
from edc_dx import get_diagnosis_labels
from edc_dx.form_validators import DiagnosisFormValidatorMixin
from edc_visit_schedule.utils import raise_if_baseline


class ClinicalReviewFollowupFormValidatorMixin(DiagnosisFormValidatorMixin):
    def _clean(self):
        raise_if_baseline(self.cleaned_data.get("subject_visit"))
        for prefix, label in get_diagnosis_labels().items():
            cond = prefix.lower()
            self.applicable_if_not_diagnosed(
                prefix=cond,
                field_applicable=f"{cond}_test",
                label=label,
            )
            self.required_if(YES, field=f"{cond}_test", field_required=f"{cond}_test_date")
            self.m2m_required_if(YES, field=f"{cond}_test", m2m_field=f"{cond}_reason")
            self.m2m_other_specify(
                OTHER,
                m2m_field=f"{cond}_reason",
                field_other=f"{cond}_reason_other",
            )
            self.applicable_if(YES, field=f"{cond}_test", field_applicable=f"{cond}_dx")
        super()._clean()

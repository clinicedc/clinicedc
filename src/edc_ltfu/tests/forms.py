from django.forms import ModelForm
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_visit_tracking.form_validators import VisitMissedFormValidator

from edc_metadata.tests.models import SubjectVisitMissed


class SubjectVisitMissedForm(CrfModelFormMixin, ModelForm):

    form_validator_cls = VisitMissedFormValidator

    def validate_against_consent(self):
        pass

    class Meta:
        model = SubjectVisitMissed
        fields = "__all__"

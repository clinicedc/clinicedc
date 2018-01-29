from django import forms

from ..crf_date_validator import CrfDateValidator
from ..crf_date_validator import CrfReportDateAllowanceError, CrfReportDateBeforeStudyStart
from ..crf_date_validator import CrfReportDateIsFuture


class VisitTrackingModelFormMixin:

    visit_attr = None

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('report_datetime'):
            try:
                CrfDateValidator(
                    report_datetime=cleaned_data.get('report_datetime'),
                    visit_report_datetime=cleaned_data.get(
                        self._meta.model.visit_model_attr()).report_datetime)
            except (CrfReportDateAllowanceError, CrfReportDateBeforeStudyStart,
                    CrfReportDateIsFuture) as e:
                raise forms.ValidationError(e)
        return cleaned_data

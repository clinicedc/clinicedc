from django import forms

from edc_appointment.constants import (
    NEW_APPT, INCOMPLETE_APPT, IN_PROGRESS_APPT, CANCELLED_APPT,
    COMPLETE_APPT)
from edc_metadata.constants import REQUIRED
from edc_metadata.models import CrfMetadata, RequisitionMetadata


class AppointmentFormMixin:

    def clean(self):
        cleaned_data = super().clean()
        appt_status = cleaned_data.get('appt_status')
        if appt_status in [NEW_APPT, CANCELLED_APPT] and self.crf_metadata_exists:
            raise forms.ValidationError({
                'appt_status': 'Invalid. Not all required CRFs have been keyed'})
        elif appt_status in [NEW_APPT, CANCELLED_APPT] and self.requisition_metadata_exists:
            raise forms.ValidationError({
                'appt_status': 'Invalid. Not all required requisitions have been keyed'})
        elif (appt_status not in [INCOMPLETE_APPT, IN_PROGRESS_APPT]
              and self.crf_metadata_exists):
            raise forms.ValidationError({
                'appt_status': 'Invalid. Not all required CRFs have been keyed'})
        elif (appt_status not in [INCOMPLETE_APPT, IN_PROGRESS_APPT]
              and self.requisition_metadata_exists):
            raise forms.ValidationError({
                'appt_status': 'Invalid. Not all required requisitions have been keyed'})
        elif appt_status == IN_PROGRESS_APPT and self.appointment_in_progress_exists:
            raise forms.ValidationError({
                'appt_status': 'Invalid. Another appointment in this schedule is in progress.'})
        elif (appt_status not in [COMPLETE_APPT, NEW_APPT]
              and not self.crf_metadata_exists):
            raise forms.ValidationError({
                'appt_status': 'Invalid. All required CRFs have been keyed'})
        elif (appt_status not in [COMPLETE_APPT, NEW_APPT]
              and not self.requisition_metadata_exists):
            raise forms.ValidationError({
                'appt_status': 'Invalid. All required requisitions have been keyed'})
        return cleaned_data

    @property
    def appointment_in_progress_exists(self):
        return self._meta.model.objects.filter(
            subject_identifier=self.instance.subject_identifier,
            visit_schedule_name=self.instance.visit_schedule_name,
            schedule_name=self.instance.schedule_name,
            appt_status=IN_PROGRESS_APPT).exists()

    @property
    def crf_metadata_exists(self):
        return CrfMetadata.objects.filter(
            subject_identifier=self.instance.subject_identifier,
            visit_schedule_name=self.instance.visit_schedule_name,
            schedule_name=self.instance.schedule_name,
            visit_code=self.instance.visit_code,
            entry_status=REQUIRED).exists()

    @property
    def requisition_metadata_exists(self):
        return RequisitionMetadata.objects.filter(
            subject_identifier=self.instance.subject_identifier,
            visit_schedule_name=self.instance.visit_schedule_name,
            schedule_name=self.instance.schedule_name,
            visit_code=self.instance.visit_code,
            entry_status=REQUIRED).exists()

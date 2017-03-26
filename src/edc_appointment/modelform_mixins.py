import arrow

from django import forms

from edc_base.utils import get_utcnow
from edc_metadata.constants import REQUIRED
from edc_metadata.models import CrfMetadata, RequisitionMetadata

from .constants import (
    NEW_APPT, INCOMPLETE_APPT, IN_PROGRESS_APPT, CANCELLED_APPT,
    COMPLETE_APPT)


class AppointmentFormMixin:

    def clean(self):
        cleaned_data = super().clean()

        self.validate_not_future_appt_datetime()

        appt_status = cleaned_data.get('appt_status')
        if self.instance.previous and self.instance.previous.appt_status == NEW_APPT:
            raise forms.ValidationError(
                'Appointments should be updated in sequence. A previous '
                'appointment needs be updated before continuing. '
                'See appointment for {}'.format(self.instance.previous.visit_code))
        elif appt_status in [NEW_APPT, CANCELLED_APPT] and self.crf_metadata_required_exists:
            raise forms.ValidationError({
                'appt_status': 'Invalid. CRF data has already been entered.'})
        elif appt_status in [NEW_APPT, CANCELLED_APPT] and self.requisition_metadata_required_exists:
            raise forms.ValidationError({
                'appt_status': 'Invalid. requisition data has already been entered.'})
        elif (appt_status not in [INCOMPLETE_APPT, IN_PROGRESS_APPT]
              and self.crf_metadata_required_exists):
            raise forms.ValidationError({
                'appt_status': 'Invalid. Not all required CRFs have been keyed'})
        elif (appt_status not in [INCOMPLETE_APPT, IN_PROGRESS_APPT]
              and self.requisition_metadata_required_exists):
            raise forms.ValidationError({
                'appt_status': 'Invalid. Not all required requisitions have been keyed'})
        elif (appt_status not in [INCOMPLETE_APPT, IN_PROGRESS_APPT]
              and self.required_additional_forms_exist):
            raise forms.ValidationError({
                'appt_status': 'Invalid. Not all required \'additional\' forms have been keyed'})
        elif appt_status == IN_PROGRESS_APPT and self.appointment_in_progress_exists:
            raise forms.ValidationError({
                'appt_status': 'Invalid. Another appointment in this schedule is in progress.'})
        elif (appt_status not in [COMPLETE_APPT, NEW_APPT]
              and self.crf_metadata_exists
              and self.requisition_metadata_exists
              and not self.crf_metadata_required_exists
              and not self.requisition_metadata_required_exists
              and not self.required_additional_forms_exist):
            if not self.crf_metadata_required_exists:
                raise forms.ValidationError({
                    'appt_status': 'Invalid. All required CRFs have been keyed'})
            elif not self.requisition_metadata_required_exists:
                raise forms.ValidationError({
                    'appt_status': 'Invalid. All required requisitions have been keyed'})
            elif not self.required_additional_forms_exist:
                raise forms.ValidationError({
                    'appt_status': 'Invalid. All required \'additional\' forms have been keyed'})
        return cleaned_data

    @property
    def appointment_in_progress_exists(self):
        """Returns True if another appointment in this schedule is currently
        set to "in_progress".
        """
        return self._meta.model.objects.filter(
            subject_identifier=self.instance.subject_identifier,
            visit_schedule_name=self.instance.visit_schedule_name,
            schedule_name=self.instance.schedule_name,
            appt_status=IN_PROGRESS_APPT).exclude(id=self.instance.id).exists()

    @property
    def required_additional_forms_exist(self):
        """Returns True if any additional required forms are yet to be keyed.
        """
        return False

    @property
    def crf_metadata_exists(self):
        """Returns True if CRF metadata exists for this visit code.
        """
        return CrfMetadata.objects.filter(
            subject_identifier=self.instance.subject_identifier,
            visit_schedule_name=self.instance.visit_schedule_name,
            schedule_name=self.instance.schedule_name,
            visit_code=self.instance.visit_code).exists()

    @property
    def crf_metadata_required_exists(self):
        """Returns True if any required CRFs for this visit code have
        not yet been keyed.
        """
        return CrfMetadata.objects.filter(
            subject_identifier=self.instance.subject_identifier,
            visit_schedule_name=self.instance.visit_schedule_name,
            schedule_name=self.instance.schedule_name,
            visit_code=self.instance.visit_code,
            entry_status=REQUIRED).exists()

    @property
    def requisition_metadata_exists(self):
        """Returns True if requisition metadata exists for this visit code.
        """
        return RequisitionMetadata.objects.filter(
            subject_identifier=self.instance.subject_identifier,
            visit_schedule_name=self.instance.visit_schedule_name,
            schedule_name=self.instance.schedule_name,
            visit_code=self.instance.visit_code).exists()

    @property
    def requisition_metadata_required_exists(self):
        """Returns True if any required requisitions for this visit code
        have not yet been keyed.
        """
        return RequisitionMetadata.objects.filter(
            subject_identifier=self.instance.subject_identifier,
            visit_schedule_name=self.instance.visit_schedule_name,
            schedule_name=self.instance.schedule_name,
            visit_code=self.instance.visit_code,
            entry_status=REQUIRED).exists()

    def validate_not_future_appt_datetime(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('appt_status') != NEW_APPT:
            appt_datetime = cleaned_data.get('appt_datetime')
            rappt_datetime = arrow.Arrow.fromdatetime(
                appt_datetime, appt_datetime.tzinfo)
            if rappt_datetime.to('UTC').date() > get_utcnow().date():
                raise forms.ValidationError({
                    'appt_datetime': 'Cannot be a future date.'})

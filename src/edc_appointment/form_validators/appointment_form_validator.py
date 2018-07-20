from arrow.arrow import Arrow
from django import forms
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_base import get_utcnow
from edc_form_validators.form_validator import FormValidator
from edc_metadata.form_validators import MetaDataFormValidatorMixin

from ..constants import NEW_APPT, IN_PROGRESS_APPT, CANCELLED_APPT
from ..constants import UNSCHEDULED_APPT, INCOMPLETE_APPT, COMPLETE_APPT


class AppointmentFormValidator(MetaDataFormValidatorMixin, FormValidator):
    """Note, the appointment is only changed, never added,
    through this form.
    """

    appointment_model = 'edc_appointment.appointment'

    def clean(self):

        self.validate_sequence()
        self.validate_not_future_appt_datetime()
        self.validate_appt_new_or_cancelled()
        self.validate_appt_inprogress_or_incomplete()
        self.validate_appt_inprogress()
        self.validate_appt_new_or_complete()
        self.validate_facility_name()
        self.validate_appt_reason()

    @property
    def appointment_model_cls(self):
        return django_apps.get_model(self.appointment_model)

    @property
    def required_additional_forms_exist(self):
        """Returns True if any additional required forms are
        yet to be keyed.
        """
        return False

    def validate_sequence(self):
        """Enforce appointment and visit entry sequence.
        """
        if self.cleaned_data.get('appt_status') == IN_PROGRESS_APPT:
            # visit report sequence
            try:
                self.instance.previous.visit
            except ObjectDoesNotExist:
                last_visit = self.appointment_model_cls.visit_model_cls().objects.filter(
                    appointment__subject_identifier=self.instance.subject_identifier,
                    visit_schedule_name=self.instance.visit_schedule_name,
                    schedule_name=self.instance.schedule_name,
                ).order_by('appointment__appt_datetime').last()
                if last_visit:
                    raise forms.ValidationError(
                        f'A previous visit report is required. Enter the visit report for '
                        f'appointment {last_visit.appointment.next.visit_code} before '
                        'starting with this appointment.')
            except AttributeError:
                pass

            # appointment sequence
            try:
                self.instance.previous.visit
            except ObjectDoesNotExist:
                first_new_appt = self.appointment_model_cls.objects.filter(
                    subject_identifier=self.instance.subject_identifier,
                    visit_schedule_name=self.instance.visit_schedule_name,
                    schedule_name=self.instance.schedule_name,
                    appt_status=NEW_APPT
                ).order_by('appt_datetime').first()
                if first_new_appt:
                    raise forms.ValidationError(
                        'A previous appointment requires updating. '
                        f'Update appointment for {first_new_appt.visit_code} first.')
            except AttributeError:
                pass

    def validate_not_future_appt_datetime(self):
        appt_datetime = self.cleaned_data.get('appt_datetime')
        if appt_datetime and appt_datetime != NEW_APPT:
            rappt_datetime = Arrow.fromdatetime(
                appt_datetime, appt_datetime.tzinfo)
            if rappt_datetime.to('UTC').date() > get_utcnow().date():
                raise forms.ValidationError({
                    'appt_datetime': 'Cannot be a future date.'})

    def validate_appt_new_or_cancelled(self):
        """Don't allow new or cancelled if form data exists.
        """
        appt_status = self.cleaned_data.get('appt_status')
        if (appt_status in [NEW_APPT, CANCELLED_APPT]
                and self.crf_metadata_required_exists):
            raise forms.ValidationError({
                'appt_status': 'Invalid. CRF data has already been entered.'})
        elif (appt_status in [NEW_APPT, CANCELLED_APPT]
              and self.requisition_metadata_required_exists):
            raise forms.ValidationError({
                'appt_status': 'Invalid. requisition data has already been entered.'})

    def validate_appt_inprogress_or_incomplete(self):
        appt_status = self.cleaned_data.get('appt_status')
        if (appt_status not in [INCOMPLETE_APPT, IN_PROGRESS_APPT]
                and self.crf_metadata_required_exists):
            raise forms.ValidationError({
                'appt_status': 'Invalid. Not all required CRFs have been keyed'})
        elif (appt_status not in [INCOMPLETE_APPT, IN_PROGRESS_APPT]
              and self.requisition_metadata_required_exists):
            raise forms.ValidationError({
                'appt_status':
                'Invalid. Not all required requisitions have been keyed'})
        elif (appt_status not in [INCOMPLETE_APPT, IN_PROGRESS_APPT]
              and self.required_additional_forms_exist):
            raise forms.ValidationError({
                'appt_status':
                'Invalid. Not all required \'additional\' forms have been keyed'})

    def validate_appt_inprogress(self):
        appt_status = self.cleaned_data.get('appt_status')
        if appt_status == IN_PROGRESS_APPT and self.appointment_in_progress_exists:
            raise forms.ValidationError({
                'appt_status':
                'Invalid. Another appointment in this schedule is in progress.'})

    def validate_appt_new_or_complete(self):
        appt_status = self.cleaned_data.get('appt_status')
        if (appt_status not in [COMPLETE_APPT, NEW_APPT]
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
                    'appt_status':
                    'Invalid. All required requisitions have been keyed'})
            elif not self.required_additional_forms_exist:
                raise forms.ValidationError({
                    'appt_status':
                    'Invalid. All required \'additional\' forms have been keyed'})

    @property
    def appointment_in_progress_exists(self):
        """Returns True if another appointment in this schedule
        is currently set to "in_progress".
        """
        return self.appointment_model_cls.objects.filter(
            subject_identifier=self.instance.subject_identifier,
            visit_schedule_name=self.instance.visit_schedule_name,
            schedule_name=self.instance.schedule_name,
            appt_status=IN_PROGRESS_APPT).exclude(
                id=self.instance.id).exists()

    def validate_facility_name(self):
        """Raises if facility_name not found in edc_facility.AppConfig.
        """
        if self.cleaned_data.get('facility_name'):
            app_config = django_apps.get_app_config('edc_facility')
            if self.cleaned_data.get('facility_name') not in app_config.facilities:
                raise forms.ValidationError(
                    f'Facility \'{self.facility_name}\' does not exist.')

    def validate_appt_reason(self):
        """Raises if visit_code_sequence is not 0 and appt_reason
        is not UNSCHEDULED_APPT.
        """
        appt_reason = self.cleaned_data.get('appt_reason')
        if (appt_reason and self.instance.visit_code_sequence
                and appt_reason != UNSCHEDULED_APPT):
            raise forms.ValidationError({
                'appt_reason': f'Expected {UNSCHEDULED_APPT.title()}'})
        elif (appt_reason
                and not self.instance.visit_code_sequence
                and appt_reason == UNSCHEDULED_APPT):
            raise forms.ValidationError({
                'appt_reason': f'Cannot be {UNSCHEDULED_APPT.title()}'})

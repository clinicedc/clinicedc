import arrow

from django import forms
from django.apps import apps as django_apps
from edc_base.utils import get_utcnow
from edc_metadata.constants import REQUIRED
from edc_metadata.models import CrfMetadata, RequisitionMetadata

from .constants import (
    NEW_APPT, INCOMPLETE_APPT, IN_PROGRESS_APPT, CANCELLED_APPT,
    COMPLETE_APPT, UNSCHEDULED_APPT)
from django.core.exceptions import ObjectDoesNotExist


# class AppointmentFormMixin:
#
#     def clean(self):
#         cleaned_data = super().clean()

#         try:
#             self.instance.previous.visit
#         except ObjectDoesNotExist:
#             raise forms.ValidationError(
#                 f'Previous visit report required. Enter the visit report for '
#                 f'{self.instance.previous.visit_code} first.')
#
#         self.validate_not_future_appt_datetime()
#
#         appt_status = cleaned_data.get('appt_status')
#         if self.instance.previous and self.instance.previous.appt_status == NEW_APPT:
#             raise forms.ValidationError(
#                 'Appointments should be updated in sequence. A previous '
#                 'appointment needs be updated before continuing. '
#                 f'See appointment for {self.instance.previous.visit_code}')

#         self.validate_appt_new_or_cancelled(appt_status=appt_status)
#         self.validate_appt_inprogress_or_incomplete(appt_status=appt_status)
#         self.validate_appt_inprogress(appt_status=appt_status)
#         self.validate_appt_new_or_complete(appt_status=appt_status)
#         self.validate_facility_name()
#         self.validate_appt_reason()
#         return cleaned_data
#
#     def validate_appt_reason(self):
#         """Raises if visit_code_sequence is not 0 and appt_reason
#         is not UNSCHEDULED_APPT.
#         """
#         cleaned_data = self.cleaned_data
#         if (cleaned_data.get('appt_reason')
#                 and self.instance.visit_code_sequence
#                 and cleaned_data.get('appt_reason') != UNSCHEDULED_APPT):
#             raise forms.ValidationError({
#                 'appt_reason': f'Expected {UNSCHEDULED_APPT.title()}'})
#         elif (cleaned_data.get('appt_reason')
#                 and not self.instance.visit_code_sequence
#                 and cleaned_data.get('appt_reason') == UNSCHEDULED_APPT):
#             raise forms.ValidationError({
#                 'appt_reason': f'Cannot be {UNSCHEDULED_APPT.title()}'})
#
#     def validate_facility_name(self):
#         """Raises if facility_name not found in edc_facility.AppConfig.
#         """
#         cleaned_data = self.cleaned_data
#         if cleaned_data.get('facility_name'):
#             app_config = django_apps.get_app_config('edc_facility')
#             if cleaned_data.get('facility_name') not in app_config.facilities:
#                 raise forms.ValidationError(
#                     f'Facility \'{self.facility_name}\' does not exist.')
#
#     def validate_appt_inprogress_or_incomplete(self, appt_status=None):
#         if (appt_status not in [INCOMPLETE_APPT, IN_PROGRESS_APPT]
#                 and self.crf_metadata_required_exists):
#             raise forms.ValidationError({
#                 'appt_status': 'Invalid. Not all required CRFs have been keyed'})
#         elif (appt_status not in [INCOMPLETE_APPT, IN_PROGRESS_APPT]
#               and self.requisition_metadata_required_exists):
#             raise forms.ValidationError({
#                 'appt_status': 'Invalid. Not all required requisitions have been keyed'})
#         elif (appt_status not in [INCOMPLETE_APPT, IN_PROGRESS_APPT]
#               and self.required_additional_forms_exist):
#             raise forms.ValidationError({
#                 'appt_status': 'Invalid. Not all required \'additional\' forms have been keyed'})
#
#     def validate_appt_inprogress(self, appt_status=None):
#         if appt_status == IN_PROGRESS_APPT and self.appointment_in_progress_exists:
#             raise forms.ValidationError({
#                 'appt_status': 'Invalid. Another appointment in this schedule is in progress.'})
#
#     def validate_appt_new_or_complete(self, appt_status=None):
#         if (appt_status not in [COMPLETE_APPT, NEW_APPT]
#                 and self.crf_metadata_exists
#                 and self.requisition_metadata_exists
#                 and not self.crf_metadata_required_exists
#                 and not self.requisition_metadata_required_exists
#                 and not self.required_additional_forms_exist):
#             if not self.crf_metadata_required_exists:
#                 raise forms.ValidationError({
#                     'appt_status': 'Invalid. All required CRFs have been keyed'})
#             elif not self.requisition_metadata_required_exists:
#                 raise forms.ValidationError({
#                     'appt_status': 'Invalid. All required requisitions have been keyed'})
#             elif not self.required_additional_forms_exist:
#                 raise forms.ValidationError({
#                     'appt_status': 'Invalid. All required \'additional\' forms have been keyed'})
#
#     @property
#     def appointment_in_progress_exists(self):
#         """Returns True if another appointment in this schedule is currently
#         set to "in_progress".
#         """
#         return self._meta.model.objects.filter(
#             subject_identifier=self.instance.subject_identifier,
#             visit_schedule_name=self.instance.visit_schedule_name,
#             schedule_name=self.instance.schedule_name,
#             appt_status=IN_PROGRESS_APPT).exclude(id=self.instance.id).exists()
#
#     @property
#     def required_additional_forms_exist(self):
#         """Returns True if any additional required forms are yet to be keyed.
#         """
#         return False


# class AppointmentMetaDataFormValidatorMixin:
#
#     @property
#     def crf_metadata_exists(self):
#         """Returns True if CRF metadata exists for this visit code.
#         """
#         return CrfMetadata.objects.filter(
#             subject_identifier=self.instance.subject_identifier,
#             visit_schedule_name=self.instance.visit_schedule_name,
#             schedule_name=self.instance.schedule_name,
#             visit_code=self.instance.visit_code).exists()
#
#     @property
#     def crf_metadata_required_exists(self):
#         """Returns True if any required CRFs for this visit code have
#         not yet been keyed.
#         """
#         return CrfMetadata.objects.filter(
#             subject_identifier=self.instance.subject_identifier,
#             visit_schedule_name=self.instance.visit_schedule_name,
#             schedule_name=self.instance.schedule_name,
#             visit_code=self.instance.visit_code,
#             entry_status=REQUIRED).exists()
#
#     @property
#     def requisition_metadata_exists(self):
#         """Returns True if requisition metadata exists for this visit code.
#         """
#         return RequisitionMetadata.objects.filter(
#             subject_identifier=self.instance.subject_identifier,
#             visit_schedule_name=self.instance.visit_schedule_name,
#             schedule_name=self.instance.schedule_name,
#             visit_code=self.instance.visit_code).exists()
#
#     @property
#     def requisition_metadata_required_exists(self):
#         """Returns True if any required requisitions for this visit code
#         have not yet been keyed.
#         """
#         return RequisitionMetadata.objects.filter(
#             subject_identifier=self.instance.subject_identifier,
#             visit_schedule_name=self.instance.visit_schedule_name,
#             schedule_name=self.instance.schedule_name,
#             visit_code=self.instance.visit_code,
#             entry_status=REQUIRED).exists()

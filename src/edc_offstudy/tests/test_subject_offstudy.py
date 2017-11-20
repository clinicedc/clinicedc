from datetime import timedelta
from edc_consent.site_consents import site_consents
from edc_constants.constants import DEAD
from edc_visit_schedule import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from dateutil.relativedelta import relativedelta
from django.test import TestCase
from edc_base.utils import get_utcnow
from edc_consent.consent import Consent
from model_mommy import mommy

from edc_offstudy.tests.visit_schedule import visit_schedule1

from ..model_mixins import OffstudyError
from .dates_test_mixin import DatesTestMixin
from .models import Enrollment, SubjectConsent, SubjectOffstudy


class TestOffstudy(DatesTestMixin, TestCase):

    def setUp(self):
        site_consents.reset_registry()

        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)

        self.consent_factory(
            start=self.study_open_datetime,
            end=self.study_open_datetime + timedelta(days=50),
            version='1.0')
        self.dob = self.study_open_datetime - relativedelta(years=25)
        self.visit_schedule_name = 'visit_schedule1'
        self.schedule_name = 'schedule1'
        self.subject_consent = mommy.make_recipe(
            'edc_offstudy.tests.subjectconsent',
            subject_identifier='111111111',
            consent_datetime=self.study_open_datetime)
        Enrollment.objects.create(
            subject_identifier=self.subject_consent.subject_identifier)
        enrollment = Enrollment.objects.get(
            subject_identifier=self.subject_consent.subject_identifier)
        self.schedule = enrollment.schedule

    def consent_factory(self, **kwargs):
        options = dict(
            start=kwargs.get('start', self.study_open_datetime),
            end=kwargs.get('end', self.study_close_datetime),
            gender=kwargs.get('gender', ['M', 'F']),
            updates_versions=kwargs.get('updates_versions', []),
            version=kwargs.get('version', '1'),
            age_min=kwargs.get('age_min', 16),
            age_max=kwargs.get('age_max', 64),
            age_is_adult=kwargs.get('age_is_adult', 18),
        )
        model = kwargs.get('model', 'edc_offstudy.subjectconsent')
        consent = Consent(model, **options)
        site_consents.register(consent)
        return consent

    def test_off_study_date_after_consent(self):
        """Assert can go off study a week after consent."""
        try:
            SubjectOffstudy.objects.create(
                subject_identifier=self.subject_consent.subject_identifier,
                offstudy_datetime=get_utcnow() - relativedelta(weeks=3),
                reason=DEAD
            )
        except OffstudyError as e:
            self.fail(str(e))

#     def test_off_study_date_before_consent(self):
#         """Assert cannot go off study a week before consent."""
#         try:
#             SubjectOffstudy.objects.create(
#                 subject_identifier=self.subject_consent.subject_identifier,
#                 offstudy_datetime=get_utcnow() - relativedelta(weeks=5),
#                 reason=DEAD
#             )
#             self.fail('OffstudyError not raised')
#         except OffstudyError:
#             pass
#
#     def test_off_study_date_before_subject_visit(self):
#         """Assert cannot enter off study if visits already exist after offstudy date."""
#         for appointment in Appointment.objects.exclude(
#                 subject_identifier=self.subject_identifier).order_by('appt_datetime'):
#             SubjectVisitFactory(
#                 appointment=appointment,
#                 visit_schedule_name=appointment.visit_schedule_name,
#                 schedule_name=appointment.schedule_name,
#                 visit_code=appointment.visit_code,
#                 report_datetime=appointment.appt_datetime,
#                 study_status=SCHEDULED)
#         for appointment in Appointment.objects.filter(subject_identifier=self.subject_identifier):
#             SubjectVisitFactory(
#                 appointment=appointment,
#                 visit_schedule_name=appointment.visit_schedule_name,
#                 schedule_name=appointment.schedule_name,
#                 visit_code=appointment.visit_code,
#                 report_datetime=get_utcnow(),
#                 study_status=SCHEDULED)
#         appointment = Appointment.objects.filter(
#             subject_identifier=self.subject_identifier).first()
#         self.subject_visit = SubjectVisit.objects.get(appointment=appointment)
#         try:
#             SubjectOffstudy.objects.create(
#                 subject_identifier=self.subject_consent.subject_identifier,
#                 offstudy_datetime=get_utcnow() - relativedelta(weeks=3),
#                 reason=DEAD
#             )
#             self.fail('OffstudyError not raised')
#         except OffstudyError:
#             pass
#
#     def test_off_study_date_after_subject_visit(self):
#         """Assert can enter off study if visits do not exist after offstudy date."""
#         for appointment in Appointment.objects.exclude(
#                 subject_identifier=self.subject_identifier).order_by('appt_datetime'):
#             SubjectVisitFactory(
#                 appointment=appointment,
#                 visit_schedule_name=appointment.visit_schedule_name,
#                 schedule_name=appointment.schedule_name,
#                 visit_code=appointment.visit_code,
#                 report_datetime=appointment.appt_datetime,
#                 study_status=SCHEDULED)
#         for appointment in Appointment.objects.filter(
#                 subject_identifier=self.subject_identifier).order_by('appt_datetime')[0:2]:
#             SubjectVisitFactory(
#                 appointment=appointment,
#                 visit_schedule_name=appointment.visit_schedule_name,
#                 schedule_name=appointment.schedule_name,
#                 visit_code=appointment.visit_code,
#                 report_datetime=appointment.appt_datetime,
#                 study_status=SCHEDULED)
#         try:
#             SubjectOffstudy.objects.create(
#                 subject_identifier=self.subject_consent.subject_identifier,
#                 offstudy_datetime=get_utcnow(),
#                 reason=DEAD
#             )
#         except OffstudyError:
#             self.fail('OffstudyError unexpectedly raised')
#
#     def test_off_study_date_deletes_unused_appointments(self):
#         """Assert deletes any unused appointments after offstudy date."""
#         n = 0
#         # create some appointments for other subjects
#         for appointment in Appointment.objects.exclude(
#                 subject_identifier=self.subject_identifier).order_by('appt_datetime'):
#             SubjectVisitFactory(
#                 appointment=appointment,
#                 visit_schedule_name=appointment.visit_schedule_name,
#                 schedule_name=appointment.schedule_name,
#                 visit_code=appointment.visit_code,
#                 report_datetime=appointment.appt_datetime,
#                 study_status=SCHEDULED)
#             n += 1
#         self.assertEquals(Appointment.objects.all().count(), 4 + n)
#         self.assertEquals(Appointment.objects.filter(
#             subject_identifier=self.subject_identifier).count(), 4)
#         appointments = Appointment.objects.filter(
#             subject_identifier=self.subject_identifier)
#         # report visit on day of first appointment (1/4) for our subject
#         self.subject_visit = SubjectVisitFactory(
#             appointment=appointments[0],
#             visit_schedule_name=appointment.visit_schedule_name,
#             schedule_name=appointment.schedule_name,
#             visit_code=appointment.visit_code,
#             report_datetime=appointments[0].appt_datetime,
#             study_status=SCHEDULED)
#         # report off study day after first visit for our subject
#         SubjectOffstudy.objects.create(
#             subject_identifier=self.subject_consent.subject_identifier,
#             offstudy_datetime=appointments[0].appt_datetime +
#             relativedelta(days=1),
#             reason=DEAD)
#         # assert other appointments for other subjects are not deleted
#         self.assertEquals(
#             Appointment.objects.exclude(subject_identifier=self.subject_identifier).count(), n)
#         # assert appointments scheduled after the first appointment are deleted
#         self.assertEquals(
#             Appointment.objects.filter(subject_identifier=self.subject_identifier).count(), 1)
#
#     def test_off_study_date_deletes_unused_appointments2(self):
#         """Assert only deletes appointments without subject visit and on/after the offstudy date."""
#         # count appointments for our subject, 1-4
#         self.assertEquals(
#             Appointment.objects.filter(subject_identifier=self.subject_identifier).count(), 4)
#         appointments = Appointment.objects.filter(
#             subject_identifier=self.subject_identifier).order_by('appt_datetime')
#         appointment_datetimes = [
#             appointment.appt_datetime for appointment in appointments]
#         # report visits for first and second appointment, 1, 2
#         for index, appointment in enumerate(appointments[0:2]):
#             self.subject_visit = SubjectVisitFactory(
#                 appointment=appointment,
#                 visit_schedule_name=appointment.visit_schedule_name,
#                 schedule_name=appointment.schedule_name,
#                 visit_code=appointment.visit_code,
#                 report_datetime=appointment_datetimes[index],
#                 study_status=SCHEDULED)
#         # report off study on same date as third visit
#         SubjectOffstudy.objects.create(
#             subject_identifier=self.subject_consent.subject_identifier,
#             offstudy_datetime=appointment_datetimes[2],
#             reason=DEAD)
#         # assert deletes 3rd and fourth appointment only.
#         self.assertEquals(
#             Appointment.objects.filter(subject_identifier=self.subject_identifier).count(), 2)
#
#     def test_off_study_date_deletes_unused_appointments3(self):
#         """Assert does not delete unused appointments if offstudy date is greater than
#         all unused appointments."""
#         # count appointments for our subject, 1-4
#         self.assertEquals(
#             Appointment.objects.filter(subject_identifier=self.subject_identifier).count(), 4)
#         appointments = Appointment.objects.filter(
#             subject_identifier=self.subject_identifier).order_by('appt_datetime')
#         appointment_datetimes = [
#             appointment.appt_datetime for appointment in appointments]
#         # report visits for first and second appointment, 1, 2
#         for index, appointment in enumerate(appointments[0:2]):
#             SubjectVisitFactory(
#                 appointment=appointment,
#                 visit_schedule_name=appointment.visit_schedule_name,
#                 schedule_name=appointment.schedule_name,
#                 visit_code=appointment.visit_code,
#                 report_datetime=appointment_datetimes[index],
#                 study_status=SCHEDULED)
#         # report off study on same date as second visit
#         SubjectOffstudy.objects.create(
#             subject_identifier=self.subject_consent.subject_identifier,
#             offstudy_datetime=appointment_datetimes[3] + relativedelta(days=1),
#             reason=DEAD)
#         # assert deletes 3rd and fourth appointment only.
#         self.assertEquals(
#             Appointment.objects.filter(subject_identifier=self.subject_identifier).count(), 4)
#
#     def test_off_study_blocks_subject_visit(self):
#         """Assert cannot enter subject visit after off study date because appointment no longer exists."""
#         # count appointments for our subject, 1-4
#         self.assertEquals(
#             Appointment.objects.filter(subject_identifier=self.subject_identifier).count(), 4)
#         appointments = Appointment.objects.filter(
#             subject_identifier=self.subject_identifier).order_by('appt_datetime')
#         appointment_datetimes = [
#             appointment.appt_datetime for appointment in appointments]
#         # report visits for first and second appointment, 1, 2
#         for index, appointment in enumerate(appointments[0:2]):
#             SubjectVisitFactory(
#                 appointment=appointment,
#                 visit_schedule_name=appointment.visit_schedule_name,
#                 schedule_name=appointment.schedule_name,
#                 visit_code=appointment.visit_code,
#                 report_datetime=appointment_datetimes[index],
#                 study_status=SCHEDULED)
#         # report off study on same date as second visit
#         SubjectOffstudy.objects.create(
#             subject_identifier=self.subject_consent.subject_identifier,
#             offstudy_datetime=appointment_datetimes[1],
#             reason=DEAD)
#         self.assertEquals(
#             Appointment.objects.filter(subject_identifier=self.subject_identifier).count(), 2)
#         # assert cannot add subject visit with report date before offstudy
#         # because appointment no longer exists
#         self.assertRaises(
#             IntegrityError, SubjectVisitFactory,
#             appointment=appointments[2],
#             visit_schedule_name=appointments[2].visit_schedule_name,
#             schedule_name=appointments[2].schedule_name,
#             visit_code=appointments[2].visit_code,
#             report_datetime=appointment_datetimes[1] - relativedelta(hours=2),
#             study_status=SCHEDULED)

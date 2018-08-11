from dateutil.relativedelta import relativedelta
from django.test import TestCase, tag
from edc_appointment.constants import IN_PROGRESS_APPT
from edc_appointment.models import Appointment
from edc_appointment.tests.visit_schedule import visit_schedule1, visit_schedule2
from edc_appointment.tests.models import OnScheduleOne, SubjectConsent, SubjectVisit
from edc_appointment.tests.models import OnScheduleTwo

from edc_base import get_utcnow, get_dob
from edc_consent.site_consents import site_consents
from edc_constants.constants import DEAD
from edc_facility.import_holidays import import_holidays
from edc_registration.models import RegisteredSubject
from edc_visit_schedule.site_visit_schedules import site_visit_schedules,\
    SiteVisitScheduleError
from edc_visit_tracking.constants import SCHEDULED

from ..model_mixins import OffstudyNonCrfModelMixinError
from ..models import SubjectOffstudy
from ..offstudy import OFFSTUDY_DATETIME_BEFORE_DOB, INVALID_DOB
from ..offstudy import Offstudy, OffstudyError, NOT_CONSENTED
from ..offstudy import SUBJECT_NOT_REGISTERED, INVALID_OFFSTUDY_DATETIME_CONSENT
from ..offstudy_crf import SubjectOffstudyError
from .consents import v1_consent
from .forms import SubjectOffstudyForm, CrfOneForm, NonCrfOneForm
from .models import BadSubjectOffstudy, CrfOne, NonCrfOne, BadNonCrfOne, SubjectOffstudy2


class TestOffstudy(TestCase):

    @classmethod
    def setUpClass(cls):
        site_consents.register(v1_consent)
        import_holidays()
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.visit_schedule_name = 'visit_schedule1'
        self.schedule_name = 'schedule'

        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule1)
        site_visit_schedules.register(visit_schedule2)

        self.subject_identifier = '111111111'
        self.subject_identifiers = [
            self.subject_identifier, '222222222', '333333333', '444444444']
        self.consent_datetime = get_utcnow() - relativedelta(weeks=4)
        dob = get_dob(age_in_years=25, now=self.consent_datetime)
        for subject_identifier in self.subject_identifiers:
            subject_consent = SubjectConsent.objects.create(
                subject_identifier=subject_identifier,
                identity=subject_identifier,
                confirm_identity=subject_identifier,
                consent_datetime=self.consent_datetime,
                dob=dob)
            OnScheduleOne.objects.create(
                subject_identifier=subject_consent.subject_identifier,
                onschedule_datetime=self.consent_datetime)
        self.subject_consent = SubjectConsent.objects.get(
            subject_identifier=self.subject_identifier,
            dob=dob)

    def test_offstudy_cls_consented(self):
        try:
            Offstudy(
                subject_identifier=self.subject_identifier,
                offstudy_datetime=get_utcnow(),
                consent_model='edc_appointment.subjectconsent',
                offstudy_model='edc_offstudy.subjectoffstudy')
        except OffstudyError:
            self.fail('OffstudyError unexpectedly raised.')

    def test_offstudy_cls_date_equals_consent(self):
        try:
            Offstudy(
                subject_identifier=self.subject_identifier,
                offstudy_datetime=self.consent_datetime,
                consent_model='edc_appointment.subjectconsent',
                offstudy_model='edc_offstudy.subjectoffstudy')
        except OffstudyError:
            self.fail('OffstudyError unexpectedly raised.')

    def test_offstudy_cls_raises(self):
        subject_identifier = '12345'
        self.assertRaises(
            OffstudyError,
            Offstudy,
            subject_identifier=subject_identifier,
            offstudy_datetime=self.consent_datetime -
            relativedelta(days=1),
            consent_model='edc_appointment.subjectconsent',
            offstudy_model='edc_offstudy.subjectoffstudy')

    def test_offstudy_cls_subject_not_registered(self):
        subject_identifier = '12345'
        with self.assertRaises(OffstudyError) as cm:
            Offstudy(
                subject_identifier=subject_identifier,
                offstudy_datetime=self.consent_datetime -
                relativedelta(days=1),
                consent_model='edc_appointment.subjectconsent',
                offstudy_model='edc_offstudy.subjectoffstudy')
        self.assertEqual(
            cm.exception.code,
            SUBJECT_NOT_REGISTERED)

    def test_offstudy_cls_subject_registered_but_no_dob(self):
        subject_identifier = '12345'
        RegisteredSubject.objects.create(
            subject_identifier=subject_identifier)
        with self.assertRaises(OffstudyError) as cm:
            Offstudy(
                subject_identifier=subject_identifier,
                offstudy_datetime=self.consent_datetime -
                relativedelta(days=1),
                consent_model='edc_appointment.subjectconsent',
                offstudy_model='edc_offstudy.subjectoffstudy')
        self.assertEqual(
            cm.exception.code,
            INVALID_DOB)

    def test_offstudy_cls_subject_registered_but_dob_after_offstudy_datetime(self):
        subject_identifier = '12345'
        RegisteredSubject.objects.create(
            subject_identifier=subject_identifier,
            dob=self.consent_datetime)
        with self.assertRaises(OffstudyError) as cm:
            Offstudy(
                subject_identifier=subject_identifier,
                offstudy_datetime=self.consent_datetime -
                relativedelta(days=1),
                consent_model='edc_appointment.subjectconsent',
                offstudy_model='edc_offstudy.subjectoffstudy')
        self.assertEqual(
            cm.exception.code,
            OFFSTUDY_DATETIME_BEFORE_DOB)

    def test_offstudy_cls_subject_registered_but_no_consent(self):
        subject_identifier = '12345'
        RegisteredSubject.objects.create(
            subject_identifier=subject_identifier,
            dob=get_utcnow() - relativedelta(years=25))
        with self.assertRaises(OffstudyError) as cm:
            Offstudy(
                subject_identifier=subject_identifier,
                offstudy_datetime=self.consent_datetime -
                relativedelta(days=1),
                consent_model='edc_appointment.subjectconsent',
                offstudy_model='edc_offstudy.subjectoffstudy')
        self.assertEqual(cm.exception.code, NOT_CONSENTED)

    def test_offstudy_cls_offstudy_datetime_before_consent(self):
        with self.assertRaises(OffstudyError) as cm:
            Offstudy(
                subject_identifier=self.subject_identifier,
                offstudy_datetime=self.consent_datetime -
                relativedelta(days=1),
                # consent_model='edc_appointment.subjectconsent',
                offstudy_model='edc_offstudy.subjectoffstudy')
        self.assertEqual(cm.exception.code, INVALID_OFFSTUDY_DATETIME_CONSENT)

    def test_offstudy_with_model_mixin(self):
        off_study = BadSubjectOffstudy()
        self.assertRaises(SiteVisitScheduleError, off_study.save)

    def test_appointments_created(self):
        """Asserts creates 4 appointments per subject
        since there are 4 visits in the schedule.
        """
        for subject_identifier in self.subject_identifiers:
            self.assertEqual(Appointment.objects.filter(
                subject_identifier=subject_identifier).count(), 4)

    def test_off_study_date_after_consent(self):
        """Assert can go off study a week after consent.
        """
        try:
            SubjectOffstudy.objects.create(
                subject_identifier=self.subject_consent.subject_identifier,
                offstudy_datetime=get_utcnow() - relativedelta(weeks=3),
                offstudy_reason=DEAD)
        except OffstudyError:
            self.fail('OffstudyError unexpectedly raised.')

    def test_off_study_date_before_consent(self):
        """Assert cannot go off study a week before consent.
        """
        self.assertRaises(
            OffstudyError,
            SubjectOffstudy.objects.create,
            subject_identifier=self.subject_consent.subject_identifier,
            offstudy_datetime=get_utcnow() - relativedelta(weeks=5),
            offstudy_reason=DEAD)

    def test_off_study_date_before_subject_visit(self):
        """Assert cannot enter off study if visits already
        exist after offstudy date.
        """
        for appointment in Appointment.objects.exclude(
                subject_identifier=self.subject_identifier).order_by('appt_datetime'):
            SubjectVisit.objects.create(
                appointment=appointment,
                visit_schedule_name=appointment.visit_schedule_name,
                schedule_name=appointment.schedule_name,
                visit_code=appointment.visit_code,
                report_datetime=appointment.appt_datetime,
                study_status=SCHEDULED)
        for appointment in Appointment.objects.filter(subject_identifier=self.subject_identifier):
            SubjectVisit.objects.create(
                appointment=appointment,
                visit_schedule_name=appointment.visit_schedule_name,
                schedule_name=appointment.schedule_name,
                visit_code=appointment.visit_code,
                report_datetime=get_utcnow(),
                study_status=SCHEDULED)
        appointment = Appointment.objects.filter(
            subject_identifier=self.subject_identifier).first()
        self.subject_visit = SubjectVisit.objects.get(appointment=appointment)
        self.assertRaises(
            OffstudyError,
            SubjectOffstudy.objects.create,
            subject_identifier=self.subject_consent.subject_identifier,
            offstudy_datetime=get_utcnow() - relativedelta(weeks=3),
            offstudy_reason=DEAD)

    def test_off_study_date_after_subject_visit(self):
        """Assert can enter off study if visits do not exist
        after off-study date.
        """
        for appointment in Appointment.objects.exclude(
                subject_identifier=self.subject_identifier).order_by('appt_datetime'):
            SubjectVisit.objects.create(
                appointment=appointment,
                visit_schedule_name=appointment.visit_schedule_name,
                schedule_name=appointment.schedule_name,
                visit_code=appointment.visit_code,
                report_datetime=appointment.appt_datetime,
                study_status=SCHEDULED)
        for appointment in Appointment.objects.filter(
                subject_identifier=self.subject_identifier).order_by('appt_datetime')[0:2]:
            SubjectVisit.objects.create(
                appointment=appointment,
                visit_schedule_name=appointment.visit_schedule_name,
                schedule_name=appointment.schedule_name,
                visit_code=appointment.visit_code,
                report_datetime=appointment.appt_datetime,
                study_status=SCHEDULED)
        try:
            SubjectOffstudy.objects.create(
                subject_identifier=self.subject_consent.subject_identifier,
                offstudy_datetime=get_utcnow(),
                offstudy_reason=DEAD)
        except OffstudyError:
            self.fail('OffstudyError unexpectedly raised')

    def test_off_study_date_deletes_unused_appointments(self):
        """Assert deletes any unused appointments after offstudy date.
        """
        n = 0
        # create some appointments for other subjects
        for appointment in Appointment.objects.exclude(
                subject_identifier=self.subject_identifier).order_by('appt_datetime'):
            SubjectVisit.objects.create(
                appointment=appointment,
                visit_schedule_name=appointment.visit_schedule_name,
                schedule_name=appointment.schedule_name,
                visit_code=appointment.visit_code,
                report_datetime=appointment.appt_datetime,
                study_status=SCHEDULED)
            n += 1
        self.assertEquals(Appointment.objects.all().count(), 4 + n)
        self.assertEquals(Appointment.objects.filter(
            subject_identifier=self.subject_identifier).count(), 4)
        appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier)
        # report visit on day of first appointment (1/4) for our subject
        self.subject_visit = SubjectVisit.objects.create(
            appointment=appointments[0],
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            report_datetime=appointments[0].appt_datetime,
            study_status=SCHEDULED)
        # report off study day after first visit for our subject
        SubjectOffstudy.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            offstudy_datetime=appointments[0].appt_datetime +
            relativedelta(days=1),
            offstudy_reason=DEAD)
        # assert other appointments for other subjects are not deleted
        self.assertEquals(
            Appointment.objects.exclude(subject_identifier=self.subject_identifier).count(), n)
        # assert appointments scheduled after the first appointment are deleted
        self.assertEquals(
            Appointment.objects.filter(subject_identifier=self.subject_identifier).count(), 1)

    def test_off_study_date_deletes_unused_appointments2(self):
        """Assert only deletes appointments without subject
        visit and on/after the offstudy date.
        """
        # count appointments for our subject, 1-4
        self.assertEquals(
            Appointment.objects.filter(subject_identifier=self.subject_identifier).count(), 4)
        appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier).order_by('appt_datetime')
        appointment_datetimes = [
            appointment.appt_datetime for appointment in appointments]
        # report visits for first and second appointment, 1, 2
        for index, appointment in enumerate(appointments[0:2]):
            self.subject_visit = SubjectVisit.objects.create(
                appointment=appointment,
                visit_schedule_name=appointment.visit_schedule_name,
                schedule_name=appointment.schedule_name,
                visit_code=appointment.visit_code,
                report_datetime=appointment_datetimes[index],
                study_status=SCHEDULED)
        # report off study on same date as third visit
        SubjectOffstudy.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            offstudy_datetime=appointment_datetimes[2],
            offstudy_reason=DEAD)
        # assert deletes 3rd and fourth appointment only.
        self.assertEquals(
            Appointment.objects.filter(subject_identifier=self.subject_identifier).count(), 2)

    def test_off_study_date_deletes_unused_appointments3(self):
        """Assert does not delete unused appointments if
        offstudy date is greater than all unused appointments.
        """
        # count appointments for our subject, 1-4
        self.assertEquals(
            Appointment.objects.filter(subject_identifier=self.subject_identifier).count(), 4)
        appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier).order_by('appt_datetime')
        appointment_datetimes = [
            appointment.appt_datetime for appointment in appointments]
        # report visits for first and second appointment, 1, 2
        for index, appointment in enumerate(appointments[0:2]):
            SubjectVisit.objects.create(
                appointment=appointment,
                visit_schedule_name=appointment.visit_schedule_name,
                schedule_name=appointment.schedule_name,
                visit_code=appointment.visit_code,
                report_datetime=appointment_datetimes[index],
                study_status=SCHEDULED)
        # report off study on same date as second visit
        SubjectOffstudy.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            offstudy_datetime=appointment_datetimes[3] + relativedelta(days=1),
            offstudy_reason=DEAD)
        # assert deletes 3rd and fourth appointment only.
        self.assertEquals(
            Appointment.objects.filter(subject_identifier=self.subject_identifier).count(), 4)

    def test_off_study_blocks_subject_visit(self):
        """Assert cannot enter subject visit after off study
        date because appointment no longer exists.
        """
        # count appointments for our subject, 1-4
        self.assertEquals(
            Appointment.objects.filter(subject_identifier=self.subject_identifier).count(), 4)
        appointments = Appointment.objects.filter(
            subject_identifier=self.subject_identifier).order_by('appt_datetime')
        appointment_datetimes = [
            appointment.appt_datetime for appointment in appointments]
        # report visits for first and second appointment, 1, 2
        for index, appointment in enumerate(appointments[0:2]):
            SubjectVisit.objects.create(
                appointment=appointment,
                visit_schedule_name=appointment.visit_schedule_name,
                schedule_name=appointment.schedule_name,
                visit_code=appointment.visit_code,
                report_datetime=appointment_datetimes[index],
                study_status=SCHEDULED)
        # report off study on same date as second visit
        SubjectOffstudy.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            offstudy_datetime=appointment_datetimes[1],
            offstudy_reason=DEAD)
        self.assertEquals(
            Appointment.objects.filter(subject_identifier=self.subject_identifier).count(), 2)
        # assert only first two appointments exist
        self.assertEquals(
            Appointment.objects.filter(subject_identifier=self.subject_identifier).count(), 2)
        visit_codes = [a.visit_code for a in Appointment.objects.filter(
            subject_identifier=self.subject_identifier)]
        visit_codes.sort()
        self.assertEqual(visit_codes, ['1000', '2000'])

    def test_crf_model_mixin(self):

        # get subject's appointments
        appointments = [appt for appt in Appointment.objects.filter(
            subject_identifier=self.subject_identifier).order_by('appt_datetime')]

        # get first appointment
        appointment = appointments[0]
        # get first visit
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            report_datetime=appointment.appt_datetime,
            study_status=SCHEDULED)
        # get crf_one for this visit
        crf_one = CrfOne(
            subject_visit=subject_visit,
            report_datetime=appointment.appt_datetime)
        crf_one.save()

        # get second appointment
        appointment = appointments[1]

        # create second visit
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            report_datetime=appointment.appt_datetime,
            study_status=SCHEDULED)

        # create complete off-study form for 1 hour after
        # first visit date
        SubjectOffstudy.objects.create(
            offstudy_datetime=appointment.appt_datetime +
            relativedelta(hours=1),
            subject_identifier=self.subject_identifier)
        # show CRF saves OK
        crf_one = CrfOne(
            report_datetime=appointment.appt_datetime,
            subject_visit=subject_visit)
        crf_one.save()

        # get second appointment
        appointment = appointments[2]
        # resave since instance was deleted when SubjectOffstudy model
        # was created above
        appointment.save()
        # create a second visit
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            report_datetime=appointment.appt_datetime,
            study_status=SCHEDULED)
        crf_one = CrfOne(
            subject_visit=subject_visit,
            report_datetime=appointment.appt_datetime)
        self.assertRaises(
            SubjectOffstudyError,
            crf_one.save)

    def test_non_crf_model_mixin(self):
        non_crf_one = NonCrfOne.objects.create(
            subject_identifier=self.subject_identifier)

        SubjectOffstudy.objects.create(
            offstudy_datetime=get_utcnow() + relativedelta(hours=1),
            subject_identifier=self.subject_identifier)

        non_crf_one.delete()
        non_crf_one = NonCrfOne.objects.create(
            subject_identifier=self.subject_identifier)

        self.assertRaises(NotImplementedError, getattr, non_crf_one, 'visit')
        self.assertRaises(
            NotImplementedError, getattr, non_crf_one, 'schedule')
        self.assertRaises(NotImplementedError, getattr, non_crf_one, 'visits')

    def test_bad_non_crf_model_mixin(self):
        self.assertRaises(
            OffstudyNonCrfModelMixinError,
            BadNonCrfOne.objects.create,
            subject_identifier=self.subject_identifier)

    def test_modelform_mixin_ok(self):
        data = dict(
            subject_identifier=self.subject_identifier,
            offstudy_datetime=get_utcnow(),
            offstudy_reason=DEAD)
        form = SubjectOffstudyForm(data=data)
        self.assertTrue(form.is_valid())

    def test_modelform_mixin_not_ok(self):
        """Asserts that Offstudy class is called.

        Other tests above apply.
        """
        data = dict(
            subject_identifier='12345',
            offstudy_datetime=get_utcnow(),
            offstudy_reason=DEAD)
        form = SubjectOffstudyForm(data=data)
        form.is_valid()
        self.assertIn('Unknown subject. Got 12345.',
                      form.errors.get('__all__'))

    def test_crf_modelform_mixin_ok(self):
        appointments = [appt for appt in Appointment.objects.filter(
            subject_identifier=self.subject_identifier).order_by('appt_datetime')]
        appointment = appointments[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            report_datetime=appointment.appt_datetime,
            study_status=SCHEDULED)
        data = dict(
            subject_visit=str(subject_visit.id),
            report_datetime=appointment.appt_datetime)
        form = CrfOneForm(data=data)
        self.assertTrue(form.is_valid())

    def test_crf_modelform_mixin_not_ok(self):
        """Asserts that Offstudy class is called.

        Other tests above apply.
        """
        appointments = [appt for appt in Appointment.objects.filter(
            subject_identifier=self.subject_identifier).order_by('appt_datetime')]
        appointments[0].appt_status = IN_PROGRESS_APPT
        appointments[0].save()
        SubjectVisit.objects.create(
            appointment=appointments[0],
            visit_schedule_name=appointments[0].visit_schedule_name,
            schedule_name=appointments[0].schedule_name,
            visit_code=appointments[0].visit_code,
            report_datetime=appointments[0].appt_datetime,
            study_status=SCHEDULED)

        SubjectOffstudy.objects.create(
            offstudy_datetime=appointments[0].appt_datetime,
            subject_identifier=self.subject_identifier)

        appointments[1].save()
        subject_visit = SubjectVisit.objects.create(
            appointment=appointments[1],
            visit_schedule_name=appointments[1].visit_schedule_name,
            schedule_name=appointments[1].schedule_name,
            visit_code=appointments[1].visit_code,
            report_datetime=appointments[1].appt_datetime,
            study_status=SCHEDULED)

        data = dict(
            subject_visit=str(subject_visit.id),
            report_datetime=appointments[1].appt_datetime)
        form = CrfOneForm(data=data)
        form.is_valid()
        self.assertIn('report_datetime', form.errors)

    def test_non_crf_modelform_mixin_ok(self):
        data = dict(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow())
        form = NonCrfOneForm(data=data)
        self.assertTrue(form.is_valid())

    def test_non_crf_modelform_mixin_not_ok(self):
        """Asserts that Offstudy class is called.

        Other tests above apply.
        """
        SubjectOffstudy.objects.create(
            offstudy_datetime=get_utcnow() - relativedelta(days=1),
            subject_identifier=self.subject_identifier)
        data = dict(
            subject_identifier=self.subject_identifier,
            report_datetime=get_utcnow())
        form = NonCrfOneForm(data=data)
        form.is_valid()
        self.assertIn('report_datetime', form.errors)

    @tag('1')
    def test_crf_model_mixin_for_visit_schedule_2(self):

        appointments = [appt for appt in Appointment.objects.filter(
            subject_identifier=self.subject_identifier).order_by('appt_datetime')]

        appointment = appointments[0]
        self.assertEqual(
            [a.visit_code for a in appointments],
            ['1000', '2000', '3000', '4000'])

        # create visit for fist appointment, 1000
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            report_datetime=appointment.appt_datetime,
            study_status=SCHEDULED)
        crf_one = CrfOne(
            subject_visit=subject_visit,
            report_datetime=appointment.appt_datetime)
        crf_one.save()

        # create visit for first appointment, 2000
        appointment = appointments[1]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            report_datetime=appointment.appt_datetime,
            study_status=SCHEDULED)

        # enter offstudy
        SubjectOffstudy.objects.create(
            offstudy_datetime=appointment.appt_datetime +
            relativedelta(hours=1),
            subject_identifier=self.subject_identifier)
        crf_one = CrfOne(
            report_datetime=appointment.appt_datetime,
            subject_visit=subject_visit)
        crf_one.save()

        # show appt was deleted
        self.assertEqual(
            ['1000', '2000'],
            [appt.visit_code for appt in Appointment.objects.filter(
                subject_identifier=self.subject_identifier).order_by('appt_datetime')])

        # now create an error condition
        appointment = appointments[2]
        # resave since instance was deleted when SubjectOffstudy model
        # was created above
        appointment.save()

        # create visit for first appointment, 3000
        # knowing Offstudy for has been saved
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            report_datetime=appointment.appt_datetime,
            study_status=SCHEDULED)
        crf_one = CrfOne(
            subject_visit=subject_visit,
            report_datetime=appointment.appt_datetime)
        self.assertRaises(
            SubjectOffstudyError,
            crf_one.save)
        # clean up
        subject_visit.delete()
        appointment.delete()

        appointments = [appt.visit_code for appt in Appointment.objects.filter(
            subject_identifier=self.subject_identifier).order_by('appt_datetime')]
        self.assertEqual(appointments, ['1000', '2000'])

        # enroll to visit_schedule2
        # to create more appointments
        OnScheduleTwo.objects.create(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=self.consent_datetime)
        # show adds the visits for visit_schedule2
        appointments = [appt.visit_code for appt in Appointment.objects.filter(
            subject_identifier=self.subject_identifier).order_by('appt_datetime')]
        self.assertEqual(
            appointments, ['1000', '2000', '5000', '6000', '7000', '8000'])

        # show adds the visits for visit_schedule2
        appointments = [appt.visit_schedule_name for appt in Appointment.objects.filter(
            subject_identifier=self.subject_identifier).order_by('appt_datetime')]
        self.assertEqual(
            appointments, [
                'visit_schedule1', 'visit_schedule1',
                'visit_schedule2', 'visit_schedule2', 'visit_schedule2', 'visit_schedule2'])
        # show adding off study 2 removes visits from schedule2 only
        SubjectOffstudy2.objects.create(
            offstudy_datetime=appointment.appt_datetime +
            relativedelta(hours=1),
            subject_identifier=self.subject_identifier)
        appointments = [appt.visit_code for appt in Appointment.objects.filter(
            subject_identifier=self.subject_identifier).order_by('appt_datetime')]
        # note deletes appointments AFTER the date
        # see edc_appointment for setting
        self.assertEqual(appointments, ['1000', '2000', '5000'])

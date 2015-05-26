from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from django.test import TestCase

from edc.core.bhp_content_type_map.classes import ContentTypeMapHelper
from edc.core.bhp_content_type_map.models import ContentTypeMap
from edc.core.bhp_variables.tests.factories import StudySiteFactory
from edc.subject.appointment.models import Appointment
from edc.subject.consent.models import AttachedModel
from edc.subject.consent.tests.factories import ConsentCatalogueFactory
from edc.subject.registration.tests.factories import RegisteredSubjectFactory
from edc.subject.visit_schedule.models import VisitDefinition
from edc.subject.visit_schedule.tests.factories import VisitDefinitionFactory
from edc.testing.models import TestOffStudy
from edc.testing.models import TestSubjectVisit


class OffStudyMethodsTests(TestCase):

    def setUp(self):

        from edc.testing.tests.factories import TestConsentFactory
        self.test_consent_factory = TestConsentFactory
        self.create_study_variables()

        study_site = StudySiteFactory(site_code='10', site_name='TESTSITE')
        content_type_map_helper = ContentTypeMapHelper()
        content_type_map_helper.populate()
        content_type_map_helper.sync()
        content_type_map = ContentTypeMap.objects.get(model__iexact='TestConsent')
        consent_catalogue = ConsentCatalogueFactory(
            name='test',
            content_type_map=content_type_map,
            consent_type='study',
            version=1,
            start_datetime=datetime.today() - relativedelta(months=7),
            end_datetime=datetime(datetime.today().year + 5, 1, 1),
            add_for_app='visit_tracking')
        consent_catalogue.add_for_app = 'consent'
        consent_catalogue.add_for_app = 'off_study'
        consent_catalogue.save()
        # assert OffStudy model is in AttachedModel
        self.assertTrue(AttachedModel.objects.get(content_type_map=ContentTypeMap.objects.get(model__iexact=TestSubjectVisit._meta.object_name)))
        # create a subject
        self.registered_subject = RegisteredSubjectFactory()
        # consent the subject
        self.subject_consent = self.test_consent_factory(
            first_name='TEST',
            last_name='TESTER',
            initials='TT',
            identity='111111111',
            confirm_identity='111111111',
            identity_type='omang',
            dob=datetime(1990, 01, 01),
            is_dob_estimated='No',
            gender='M',
            subject_type='subject',
            consent_datetime=datetime.today(),
            study_site=study_site,
            may_store_samples='Yes',
            )
        # create some visit definitions
        visit_tracking_content_type_map = ContentTypeMap.objects.get(content_type__model='testvisit')
        VisitDefinitionFactory(code='1000', visit_tracking_content_type_map=visit_tracking_content_type_map)
        VisitDefinitionFactory(code='1300', visit_tracking_content_type_map=visit_tracking_content_type_map)
        VisitDefinitionFactory(code='1600', visit_tracking_content_type_map=visit_tracking_content_type_map)
        VisitDefinitionFactory(code='1800', visit_tracking_content_type_map=visit_tracking_content_type_map)

    def create_appointments(self, now, appts):
        from edc.subject.appointment.tests.factories import AppointmentFactory
        for visit_code, dte in appts.iteritems():
            appointment = AppointmentFactory(registered_subject=self.registered_subject, appt_datetime=dte, visit_definition=VisitDefinition.objects.get(code=visit_code))
            # appt_datetime may be change by get_best_apptdatetime, so update dict
            appts.update({visit_code: appointment.appt_datetime})
        return appts

    def test_post_save(self):
        now = datetime.today()
        test_off_study = TestOffStudy.objects.create(registered_subject=self.registered_subject, offstudy_date=date(now.year, now.month, now.day))
        # assert that off_study form can determine the visit model class
        self.assertIsNotNone(test_off_study.get_visit_model_cls())
        test_off_study.delete()
        # create some appointments
        appts = {'1000': now - relativedelta(months=6), '1300': now - relativedelta(months=3), '1600': now, '1800': now + relativedelta(months=3)}
        appts = self.create_appointments(now, appts)
        # assert 4 appointments wre created
        self.assertEqual(Appointment.objects.all().count(), 4)
        for appt_datetime in appts.itervalues():
            self.assertTrue(Appointment.objects.filter(appt_datetime=appt_datetime).exists())
        # create off study with date before last appointment
        TestOffStudy.objects.create(registered_subject=self.registered_subject, offstudy_date=date(now.year, now.month, now.day))
        # signal on off_study should delete the last two 4 appointments
        self.assertEqual(Appointment.objects.all().count(), 2)
        self.assertEqual([appt for appt in Appointment.objects.filter(visit_definition__code__in=['1600', '1800'])], [])
        # clear appointment
        Appointment.objects.all().delete()
        TestOffStudy.objects.all().delete()
        appts = {'1000': now - relativedelta(months=6), '1300': now - relativedelta(months=3), '1600': now, '1800': now + relativedelta(months=3)}
        appts = self.create_appointments(now, appts)
        self.assertEqual(Appointment.objects.all().count(), 4)
        for appt_datetime in appts.itervalues():
            self.assertTrue(Appointment.objects.filter(appt_datetime=appt_datetime).exists())
        # add a visit tracking form to now
        appointment = Appointment.objects.get(visit_definition__code='1600')
        TestSubjectVisit.objects.create(appointment=appointment, report_datetime=now, reason='off_study', info_source='participant')
        TestOffStudy.objects.create(registered_subject=self.registered_subject, offstudy_date=date(now.year, now.month, now.day))
        # signal on off_study should delete the last two 4 appointments
        self.assertEqual(Appointment.objects.all().count(), 3)
        self.assertEqual([appt for appt in Appointment.objects.filter(visit_definition__code__in=['1800'])], [])

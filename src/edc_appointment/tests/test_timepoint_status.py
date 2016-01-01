from datetime import date
from dateutil.relativedelta import relativedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

from edc_appointment.models import Appointment, TimePointStatus
from edc_constants.constants import YES, CLOSED, IN_PROGRESS, COMPLETE_APPT, INCOMPLETE, NEW_APPT, MALE
from edc_testing.models import TestPanel, TestAliquotType, TestVisit
from edc_testing.tests.factories import TestConsentWithMixinFactory

from .base_test_case import BaseTestCase
from .test_models import TestCrfModel1, TestCrfModel2, TestCrfModel3, TestRequisitionModel


class TestTimePointStatus(BaseTestCase):

    def setUp(self):
        super(TestTimePointStatus, self).setUp()
        self.consent = TestConsentWithMixinFactory(
            registered_subject=self.registered_subject,
            consent_datetime=timezone.now(),
            gender=MALE,
            is_literate=YES,
            dob=date.today() - relativedelta(years=35),
            identity='111111111',
            confirm_identity='111111111',
            subject_identifier='999-100000-1',
            study_site=self.study_site)
        self.assertGreater(Appointment.objects.filter(
            registered_subject=self.consent.registered_subject).count(),
            0)
        self.appointments = Appointment.objects.filter(
            registered_subject=self.consent.registered_subject).order_by('visit_definition__time_point')

    def test_created(self):
        """Assert that time completion model is created for each appointment created."""
        for appointment in Appointment.objects.filter(registered_subject=self.consent.registered_subject):
            self.assertIsInstance(appointment.timepoint_status, TimePointStatus)

    def test_close1(self):
        """Assert cannot set TimePointStatus to closed if appointment is NEW."""
        for appointment in self.appointments:
            self.assertEqual(appointment.appt_status, NEW_APPT)
            appointment.timepoint_status.status = CLOSED
            self.assertRaisesMessage(ValidationError,
                                     ('Cannot close timepoint. Appointment '
                                      'status is {0}.').format(appointment.appt_status.upper()),
                                     appointment.timepoint_status.save)

    def test_close2(self):
        """Assert cannot set TimePointStatus to closed if appointment is in_progress."""
        for appointment in self.appointments:
            appointment.appt_status = IN_PROGRESS
            appointment.save()
            appointment = Appointment.objects.get(pk=appointment.pk)
            self.assertEqual(appointment.appt_status, NEW_APPT)  # fips to new
            appointment.timepoint_status.status = CLOSED
            self.assertRaisesMessage(ValidationError,
                                     ('Cannot close timepoint. Appointment '
                                      'status is {0}.').format(appointment.appt_status.upper()),
                                     appointment.timepoint_status.save)

    def test_close3(self):
        """Assert cannot set TimePointStatus to closed if appointment is done."""
        for appointment in self.appointments:
            appointment.appt_status = IN_PROGRESS
            appointment.save()
            test_visit = TestVisit.objects.create(
                appointment=appointment,
                report_datetime=timezone.now())
            TestCrfModel1.objects.create(test_visit=test_visit)
            TestCrfModel2.objects.create(test_visit=test_visit)
            TestCrfModel3.objects.create(test_visit=test_visit)
            panel = TestPanel.objects.get(name='Research Blood Draw')
            aliquot_type = TestAliquotType.objects.get(alpha_code='WB')
            TestRequisitionModel.objects.create(
                test_visit=test_visit,
                panel=panel,
                aliquot_type=aliquot_type,
                site=self.study_site)
            panel = TestPanel.objects.get(name='Viral Load')
            TestRequisitionModel.objects.create(
                test_visit=test_visit, panel=panel,
                aliquot_type=aliquot_type,
                site=self.study_site)
            panel = TestPanel.objects.get(name='Microtube')
            TestRequisitionModel.objects.create(
                test_visit=test_visit,
                panel=panel,
                aliquot_type=aliquot_type,
                site=self.study_site)
            appointment.appt_status = COMPLETE_APPT
            appointment.save()
            self.assertEqual(appointment.appt_status, COMPLETE_APPT)
            appointment.timepoint_status.status = CLOSED
            appointment.timepoint_status.save()

    def test_close4(self):
        """Assert can set TimePointStatus to closed if appointment is incomplete."""
        for appointment in self.appointments:
            appointment.appt_status = IN_PROGRESS
            appointment.save()
            test_visit = TestVisit.objects.create(
                appointment=appointment,
                report_datetime=timezone.now())
            TestCrfModel1.objects.create(test_visit=test_visit)
            TestCrfModel2.objects.create(test_visit=test_visit)
            TestCrfModel3.objects.create(test_visit=test_visit)
            appointment.appt_status = COMPLETE_APPT
            appointment.save()
            appointment = Appointment.objects.get(pk=appointment.pk)
            self.assertEqual(appointment.appt_status, INCOMPLETE)
            appointment.timepoint_status.status = CLOSED
            appointment.timepoint_status.save()

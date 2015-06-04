from django.core.exceptions import ValidationError
from django.test import TestCase

from edc_constants.constants import CLOSED, NEW, COMPLETE
from edc.testing.classes import TestAppConfiguration, TestVisitSchedule, TestLabProfile
from edc.testing.models import TestPanel
from edc.testing.tests.factories import (TestVisitFactory, TestScheduledModel1Factory,
                                         TestScheduledModel2Factory, TestScheduledModel3Factory,
                                         TestRequisitionFactory, TestConsentWithMixinFactory)

from edc.testing.models.test_aliquot_type import TestAliquotType

from ..constants import IN_PROGRESS, INCOMPLETE, CANCELLED
from ..models import Appointment, TimePointStatus


class TestTimePointStatus(TestCase):

    study_site = None

    def startup(self):
        try:
            site_lab_profiles.register(TestLabProfile())
        except AlreadyRegisteredLabProfile:
            pass
        TestAppConfiguration()
        site_lab_tracker.autodiscover()
        TestVisitSchedule().build()
        self.study_site = StudySite.objects.all()[0]

    def test_created(self):
        """Assert that time completion model is created for each appointment created."""
        self.startup()
        TestConsentWithMixinFactory(study_site=self.study_site)
        for appointment in Appointment.objects.all():
            self.assertEqual(TimePointStatus.objects.filter(appointment=appointment).count(), 1)

    def test_close1(self):
        """Assert cannot set TimePointStatus to closed if appointment is NEW."""
        self.startup()
        TestConsentWithMixinFactory(study_site=self.study_site)
        appointment = Appointment.objects.all()[0]
        self.assertEqual(appointment.appt_status, NEW)
        time_point_status = TimePointStatus.objects.get(appointment=appointment)
        time_point_status.status = CLOSED
        self.assertRaisesMessage(ValidationError,
                                 ('Cannot close timepoint. Appointment '
                                  'status is {0}.').format(appointment.appt_status.upper()),
                                 time_point_status.save)

    def test_close2(self):
        """Assert cannot set TimePointStatus to closed if appointment is in_progress."""
        self.startup()
        TestConsentWithMixinFactory(study_site=self.study_site)
        appointment = Appointment.objects.all()[0]
        appointment.appt_status = IN_PROGRESS
        appointment.save()
        appointment = Appointment.objects.get(pk=appointment.pk)
        self.assertEqual(appointment.appt_status, NEW)  # new??
        time_point_status = TimePointStatus.objects.get(appointment=appointment)
        time_point_status.status = CLOSED
        self.assertRaisesMessage(ValidationError,
                                 ('Cannot close timepoint. Appointment '
                                  'status is {0}.').format(appointment.appt_status.upper()),
                                 time_point_status.save)

    def test_close3(self):
        """Assert cannot set TimePointStatus to closed if appointment is done."""
        self.startup()
        TestConsentWithMixinFactory(study_site=self.study_site)
        appointment = Appointment.objects.all()[0]
        appointment.appt_status = IN_PROGRESS
        appointment.save()
        test_visit = TestVisitFactory(appointment=appointment)
        TestScheduledModel1Factory(test_visit=test_visit)
        TestScheduledModel2Factory(test_visit=test_visit)
        TestScheduledModel3Factory(test_visit=test_visit)
        panel = TestPanel.objects.get(name='Research Blood Draw')
        aliquot_type = TestAliquotType.objects.get(alpha_code='WB')
        TestRequisitionFactory(test_visit=test_visit, panel=panel, aliquot_type=aliquot_type, site=self.study_site)
        panel = TestPanel.objects.get(name='Viral Load')
        TestRequisitionFactory(test_visit=test_visit, panel=panel, aliquot_type=aliquot_type, site=self.study_site)
        panel = TestPanel.objects.get(name='Microtube')
        TestRequisitionFactory(test_visit=test_visit, panel=panel, aliquot_type=aliquot_type, site=self.study_site)
        appointment.appt_status = COMPLETE
        appointment.save()
        appointment = Appointment.objects.get(pk=appointment.pk)
        self.assertEqual(appointment.appt_status, COMPLETE)
        time_point_status = TimePointStatus.objects.get(appointment=appointment)
        time_point_status.status = CLOSED
        time_point_status.save()

    def test_close4(self):
        """Assert can set TimePointStatus to closed if appointment is incomplete."""
        self.startup()
        TestConsentWithMixinFactory(study_site=self.study_site)
        appointment = Appointment.objects.all()[0]
        appointment.appt_status = IN_PROGRESS
        appointment.save()
        test_visit = TestVisitFactory(appointment=appointment)
        TestScheduledModel1Factory(test_visit=test_visit)
        TestScheduledModel2Factory(test_visit=test_visit)
        appointment.appt_status = COMPLETE
        appointment.save()
        appointment = Appointment.objects.get(pk=appointment.pk)
        self.assertEqual(appointment.appt_status, INCOMPLETE)
        time_point_status = TimePointStatus.objects.get(appointment=appointment)
        time_point_status.status = CLOSED
        time_point_status.save()

from datetime import datetime
from django.test import TestCase

from edc.core.bhp_content_type_map.classes import ContentTypeMapHelper
from edc.core.bhp_content_type_map.models import ContentTypeMap
from edc.subject.lab_tracker.classes import site_lab_tracker
from edc_consent.tests.factories import StudySiteFactory
from edc_registration.tests.factories import RegisteredSubjectFactory
from edc_visit_schedule.tests.factories import VisitDefinitionFactory

from ..models import Appointment, PreAppointmentContact


class AuditTrailTests(TestCase):

    def test_audit_trail(self):
        site_lab_tracker.autodiscover()
        StudySiteFactory()
        content_type_map_helper = ContentTypeMapHelper()
        content_type_map_helper.populate()
        content_type_map_helper.sync()
        visit_tracking_content_type_map = ContentTypeMap.objects.get(content_type__model='testvisit')

        visit_definition = VisitDefinitionFactory(
            code='1000', title='Test', visit_tracking_content_type_map=visit_tracking_content_type_map)
        registered_subject = RegisteredSubjectFactory(subject_identifier='12345')
        appointment = Appointment.objects.create(
            appt_datetime=datetime.today(),
            best_appt_datetime=datetime.today(),
            appt_status='new',
            visit_definition=visit_definition,
            registered_subject=registered_subject)
        PreAppointmentContact.objects.create(
            appointment=appointment, contact_datetime=datetime.today(), is_contacted='Yes', is_confirmed=False)

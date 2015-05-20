from datetime import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from edc.core.bhp_variables.tests.factories import StudySiteFactory
from edc.core.bhp_content_type_map.models import ContentTypeMap
from edc.core.bhp_content_type_map.classes import ContentTypeMapHelper
from edc.core.bhp_variables.tests.factories import StudySpecificFactory
from edc.subject.lab_tracker.classes import site_lab_tracker
from edc.subject.visit_schedule.tests.factories import VisitDefinitionFactory
from edc.subject.registration.tests.factories import RegisteredSubjectFactory
from edc_appointment import AppointmentFactory


class BaseAppointmentTests(TestCase):

    def __init__(self, *args, **kwargs):
        self.visit_definition = None
        self.registered_subject = None
        self.appointment = None
        self.admin_user = None
        super(BaseAppointmentTests, self).__init__(*args, **kwargs)

    def setup(self):
        site_lab_tracker.autodiscover()
        StudySpecificFactory()
        StudySiteFactory()
        content_type_map_helper = ContentTypeMapHelper()
        content_type_map_helper.populate()
        content_type_map_helper.sync()
        visit_tracking_content_type_map = ContentTypeMap.objects.get(content_type__model__iexact='TestVisit')
        self.visit_definition = VisitDefinitionFactory(code='9999', title='Test', visit_tracking_content_type_map=visit_tracking_content_type_map)
        self.registered_subject = RegisteredSubjectFactory(subject_identifier='062-7982139-3', subject_type='maternal')
        study_site = StudySiteFactory(site_code='99', site_name='test site')
        self.appointment = AppointmentFactory(
            appt_datetime=datetime.today(),
            best_appt_datetime=datetime.today(),
            appt_status='new',
            study_site=study_site,
            visit_definition=self.visit_definition,
            registered_subject=self.registered_subject,
            )
        # create a admin_user
        self.admin_user = User.objects.create(username='admin', password='1234')
        self.admin_user.set_password('1234')
        self.admin_user.is_staff = True
        self.admin_user.is_active = True
        self.admin_user.is_superuser = True
        self.admin_user.save()

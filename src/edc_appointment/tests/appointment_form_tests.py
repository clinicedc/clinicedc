from edc.subject.visit_schedule.tests.factories import VisitDefinitionFactory
from edc.core.bhp_content_type_map.models import ContentTypeMap
from ..forms import AppointmentForm
from .base_appointment_tests import BaseAppointmentTests
from edc_constants.constants import NEW_APPT


class AppointmentFormTests(BaseAppointmentTests):

    def test_appointment_form(self):
        # create an appointment
        self.setup()
        # confirm visit_instance is 0 for first appointment
        self.assertEqual(self.appointment.visit_instance, '0')
        visit_tracking_content_type_map = ContentTypeMap.objects.get(content_type__model__iexact='TestVisit')
        visit_definition = VisitDefinitionFactory(id='2', code='9998', title='Test 9998', visit_tracking_content_type_map=visit_tracking_content_type_map)

        appointment_form = AppointmentForm(data={'registered_subject': self.appointment.registered_subject,
                                                 'visit_definition': visit_definition,
                                                 'study_site': self.appointment.study_site,
                                                 'appt_status': NEW_APPT,
                                                 'appt_datetime': self.appointment.appt_datetime,
                                                 'appt_type': self.appointment.appt_type,
                                                 'visit_instance': '1'})
        self.client.login(username=self.admin_user.username, password='1234')
        response = self.client.post('/admin/bhp_appointment/appointment/', {
            'registered_subject': self.appointment.registered_subject,
            'visit_definition': visit_definition,
            'study_site': self.appointment.study_site,
            'appt_status': NEW_APPT,
            #'appt_datetime': self.appointment.appt_datetime,
            'appt_type': self.appointment.appt_type,
            'visit_instance': '1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cannot create continuation appointment for visit None. Cannot find the original appointment (visit instance equal to 0).')
        self.assertEqual(appointment_form.data.get('appt_status'), NEW_APPT)

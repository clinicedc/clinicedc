import factory

from django.utils import timezone

from edc.core.bhp_variables.tests.factories import StudySiteFactory
from edc.subject.registration.tests.factories import RegisteredSubjectFactory
from edc_appointment.models import Appointment
from edc_visit_schedule.tests.factories import VisitDefinitionFactory


class AppointmentFactory(factory.DjangoModelFactory):

    class Meta:
        model = Appointment

    registered_subject = factory.SubFactory(RegisteredSubjectFactory)
    appt_datetime = timezone.now()
    best_appt_datetime = timezone.now()
    appt_close_datetime = timezone.now()
    study_site = factory.SubFactory(StudySiteFactory)
    visit_definition = factory.SubFactory(VisitDefinitionFactory)
    visit_instance = '0'

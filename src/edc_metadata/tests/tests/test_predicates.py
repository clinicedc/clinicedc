from django.test import TestCase
from edc_appointment.models import Appointment
from edc_constants.constants import FEMALE, MALE
from edc_facility.import_holidays import import_holidays
from edc_reference.reference.reference_getter import ReferenceGetter
from edc_reference.site_reference import site_reference_configs
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from faker import Faker

from ...metadata_rules import PF, P
from ..models import CrfOne, SubjectConsent, SubjectVisit
from ..reference_configs import register_to_site_reference_configs
from ..visit_schedule import visit_schedule

fake = Faker()


class TestPredicates(TestCase):
    @classmethod
    def setUpClass(cls):
        import_holidays()
        return super().setUpClass()

    def setUp(self):
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)

        register_to_site_reference_configs()
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_metadata.subjectvisit"}
        )
        _, self.schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_metadata.onschedule"
        )

    def enroll(self, gender=None):
        subject_identifier = fake.credit_card_number()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=subject_identifier,
            consent_datetime=get_utcnow(),
            gender=gender,
        )
        self.registered_subject = RegisteredSubject.objects.get(
            subject_identifier=subject_identifier
        )
        self.schedule.put_on_schedule(
            subject_identifier=subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )
        self.appointment = Appointment.objects.get(
            subject_identifier=subject_identifier,
            visit_code=self.schedule.visits.first.code,
        )
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            reason=SCHEDULED,
            subject_identifier=subject_identifier,
        )
        return subject_visit

    def test_p_male(self):
        visit = self.enroll(gender=MALE)
        opts = dict(
            source_model="edc_metadata.crfone",
            registered_subject=self.registered_subject,
            visit=visit,
            reference_getter_cls=ReferenceGetter,
        )
        self.assertTrue(P("gender", "eq", MALE)(**opts))
        self.assertFalse(P("gender", "eq", FEMALE)(**opts))

    def test_p_female(self):
        visit = self.enroll(gender=FEMALE)
        opts = dict(
            source_model="edc_metadata.crfone",
            registered_subject=self.registered_subject,
            visit=visit,
            reference_getter_cls=ReferenceGetter,
        )
        self.assertTrue(P("gender", "eq", FEMALE)(**opts))
        self.assertFalse(P("gender", "eq", MALE)(**opts))

    def test_p_reason(self):
        visit = self.enroll(gender=FEMALE)
        opts = dict(
            source_model="edc_metadata.crfone",
            registered_subject=self.registered_subject,
            visit=visit,
            reference_getter_cls=ReferenceGetter,
        )
        self.assertTrue(P("reason", "eq", SCHEDULED)(**opts))

    # def test_p_with_field_on_source_not_keyed(self):
    #     """Assert raises NoValueError if CrfOne has not been keyed."""
    #     visit = self.enroll(gender=FEMALE)
    #     opts = dict(
    #         source_model="edc_metadata.crfone",
    #         registered_subject=self.registered_subject,
    #         visit=visit,
    #         reference_getter_cls=ReferenceGetter,
    #     )
    #     self.assertRaises(NoValueError, P("f1", "eq", "car"), **opts)

    def test_p_with_field_on_source_keyed_value_none(self):
        visit = self.enroll(gender=FEMALE)
        opts = dict(
            source_model="edc_metadata.crfone",
            registered_subject=self.registered_subject,
            visit=visit,
            reference_getter_cls=ReferenceGetter,
        )
        CrfOne.objects.create(subject_visit=visit)
        self.assertFalse(P("f1", "eq", "car")(**opts))

    def test_p_with_field_on_source_keyed_with_value(self):
        visit = self.enroll(gender=FEMALE)
        opts = dict(
            source_model="edc_metadata.crfone",
            registered_subject=self.registered_subject,
            visit=visit,
            reference_getter_cls=ReferenceGetter,
        )
        CrfOne.objects.create(subject_visit=visit, f1="bicycle")
        self.assertFalse(P("f1", "eq", "car")(**opts))

    def test_p_with_field_on_source_keyed_with_matching_value(self):
        visit = self.enroll(gender=FEMALE)
        opts = dict(
            source_model="edc_metadata.crfone",
            registered_subject=self.registered_subject,
            visit=visit,
            reference_getter_cls=ReferenceGetter,
        )
        CrfOne.objects.create(subject_visit=visit, f1="car")
        self.assertTrue(P("f1", "eq", "car")(**opts))

    def test_p_with_field_on_source_keyed_with_multiple_values_in(self):
        visit = self.enroll(gender=FEMALE)
        opts = dict(
            source_model="edc_metadata.crfone",
            registered_subject=self.registered_subject,
            visit=visit,
            reference_getter_cls=ReferenceGetter,
        )
        CrfOne.objects.create(subject_visit=visit, f1="car")
        self.assertTrue(P("f1", "in", ["car", "bicycle"])(**opts))

    def test_p_with_field_on_source_keyed_with_multiple_values_not_in(self):
        visit = self.enroll(gender=FEMALE)
        opts = dict(
            source_model="edc_metadata.crfone",
            registered_subject=self.registered_subject,
            visit=visit,
            reference_getter_cls=ReferenceGetter,
        )
        CrfOne.objects.create(subject_visit=visit, f1="truck")
        self.assertFalse(P("f1", "in", ["car", "bicycle"])(**opts))

    def test_pf(self):
        visit = self.enroll(gender=FEMALE)
        opts = dict(
            source_model="edc_metadata.crfone",
            registered_subject=self.registered_subject,
            visit=visit,
            reference_getter_cls=ReferenceGetter,
        )
        CrfOne.objects.create(subject_visit=visit, f1="car")
        self.assertTrue(PF("f1", func=lambda x: x == "car")(**opts))
        self.assertFalse(PF("f1", func=lambda x: x == "bicycle")(**opts))

    def test_pf_2(self):
        def func(f1, f2):
            return f1 == "car" and f2 == "bicycle"

        visit = self.enroll(gender=FEMALE)
        opts = dict(
            source_model="edc_metadata.crfone",
            registered_subject=self.registered_subject,
            visit=visit,
            reference_getter_cls=ReferenceGetter,
        )
        CrfOne.objects.create(subject_visit=visit, f1="car", f2="bicycle")
        self.assertTrue(PF("f1", "f2", func=func)(**opts))

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from edc_action_item import site_action_items
from edc_auth.site_auths import site_auths
from edc_consent import site_consents
from edc_facility import import_holidays
from edc_reference import site_reference_configs
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.tests.helper import Helper
from visit_schedule_app.consents import v1_consent
from visit_schedule_app.models import SubjectConsent
from visit_schedule_app.visit_schedule import visit_schedule

from edc_unblinding.action_items import UnblindingRequestAction, UnblindingReviewAction
from edc_unblinding.auth_objects import (
    UNBLINDING_REQUESTORS_ROLE,
    UNBLINDING_REVIEWERS_ROLE,
)
from edc_unblinding.models import UnblindingRequest, UnblindingRequestorUser


@override_settings(
    SUBJECT_CONSENT_MODEL="visit_schedule_app.subjectconsent",
    SUBJECT_SCREENING_MODEL="visit_schedule_app.subjectscreening",
)
class EdcunblindingTestCase(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpClass(cls):
        site_action_items.register(action_cls=UnblindingRequestAction)
        site_action_items.register(action_cls=UnblindingReviewAction)
        return super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        import_holidays()
        get_user_model().objects.create(username="frazey", is_staff=True, is_active=True)

    def setUp(self):
        self.user = get_user_model().objects.get(username="frazey")
        self.subject_identifier = "12345"
        site_consents.registry = {}
        site_consents.register(v1_consent)
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier,
            subject_consent_model_cls=SubjectConsent,
            onschedule_model_name="visit_schedule_app.onschedule",
        )
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule)
        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_visit_tracking.subjectvisit"}
        )
        self.subject_consent = self.helper.consent_and_put_on_schedule()

    def test_ok(self):
        opts = dict(
            subject_identifier=self.subject_consent.subject_identifier,
            requestor=UnblindingRequestorUser.objects.all()[0],
        )
        model = UnblindingRequest(**opts)
        model.save()

    def test_auth(self):
        self.assertIn(UNBLINDING_REQUESTORS_ROLE, site_auths.roles)
        self.assertIn(UNBLINDING_REVIEWERS_ROLE, site_auths.roles)

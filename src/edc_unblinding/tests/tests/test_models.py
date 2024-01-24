from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from edc_action_item import site_action_items
from edc_action_item.site_action_items import AlreadyRegistered
from edc_auth.site_auths import site_auths
from edc_consent.site_consents import site_consents
from edc_facility import import_holidays
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.tests.helper import Helper
from visit_schedule_app.consents import consent_v1
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
    SITE_ID=10,
)
class UnblindingTestCase(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpTestData(cls):
        import_holidays()
        get_user_model().objects.create(username="frazey", is_staff=True, is_active=True)

    def setUp(self):
        try:
            site_action_items.register(action_cls=UnblindingRequestAction)
        except AlreadyRegistered:
            pass
        try:
            site_action_items.register(action_cls=UnblindingReviewAction)
        except AlreadyRegistered:
            pass
        self.user = get_user_model().objects.get(username="frazey")
        self.subject_identifier = "12345"
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule)
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier,
        )
        self.subject_consent = self.helper.consent_and_put_on_schedule(
            visit_schedule_name="visit_schedule", schedule_name="schedule"
        )

    def test_ok(self):
        opts = dict(
            subject_identifier=self.subject_consent.subject_identifier,
            requestor=UnblindingRequestorUser.objects.all()[0],
        )
        obj = UnblindingRequest(**opts)
        obj.save()

    def test_auth(self):
        self.assertIn(UNBLINDING_REQUESTORS_ROLE, site_auths.roles)
        self.assertIn(UNBLINDING_REVIEWERS_ROLE, site_auths.roles)

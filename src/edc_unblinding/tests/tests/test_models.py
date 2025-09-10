from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings, tag

from edc_action_item.site_action_items import AlreadyRegistered, site_action_items
from edc_auth.site_auths import site_auths
from edc_consent.site_consents import site_consents
from edc_facility.import_holidays import import_holidays
from edc_unblinding.action_items import UnblindingRequestAction, UnblindingReviewAction
from edc_unblinding.auth_objects import (
    UNBLINDING_REQUESTORS_ROLE,
    UNBLINDING_REVIEWERS_ROLE,
)
from edc_unblinding.models import UnblindingRequest, UnblindingRequestorUser
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from tests.action_items import register_actions
from tests.consents import consent_v1
from tests.helper import Helper
from tests.visit_schedules.visit_schedule import get_visit_schedule


@tag("unblinding")
@override_settings(SITE_ID=10)
class UnblindingTestCase(TestCase):
    helper_cls = Helper

    @classmethod
    def setUpTestData(cls):
        import_holidays()
        register_actions()
        get_user_model().objects.create(
            username="frazey", is_staff=True, is_active=True
        )

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
        site_consents.registry = {}
        site_consents.register(consent_v1)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(get_visit_schedule(consent_v1))
        self.helper = self.helper_cls()
        self.subject_consent = self.helper.consent_and_put_on_schedule(
            consent_definition=consent_v1
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

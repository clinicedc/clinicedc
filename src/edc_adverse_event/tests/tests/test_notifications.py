from django.core import mail
from django.test import TestCase, override_settings, tag
from model_bakery import baker

from edc_adverse_event.notifications import (
    AeInitialG3EventNotification,
    AeInitialG4EventNotification,
)
from edc_constants.constants import GRADE3, GRADE4, GRADE5, NO, YES
from edc_facility.import_holidays import import_holidays
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites
from clinicedc_tests.sites import all_sites

from ...action_items import (
    AeFollowupAction,
    AeInitialAction,
    AeSusarAction,
    AeTmgAction,
    DeathReportAction,
    DeathReportTmgAction,
)
from .mixins import DeathReportTestMixin


@tag("adverse_event")
@override_settings(EDC_LIST_DATA_ENABLE_AUTODISCOVER=False, SITE_ID=30)
class TestNotifications(DeathReportTestMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    def test_notifies_initial_ae_g3_not_sae(self):
        baker.make_recipe(
            "clinicedc_tests.aeinitial",
            subject_identifier=self.subject_identifier,
            ae_grade=GRADE3,
            sae=NO,
        )

        self.assertEqual(len(mail.outbox), 3)

        # AeInitial Action notification
        self.assertEqual(
            1,
            len(
                [
                    m.__dict__.get("subject")
                    for m in mail.outbox
                    if AeInitialAction.notification_display_name
                    in m.__dict__.get("subject")
                ]
            ),
        )

        # AeInitialG3EventNotification
        self.assertEqual(
            1,
            len(
                [
                    m.__dict__.get("subject")
                    for m in mail.outbox
                    if AeInitialG3EventNotification.display_name
                    in m.__dict__.get("subject")
                ]
            ),
        )

        # AeFollowupAction
        self.assertEqual(
            1,
            len(
                [
                    m.__dict__.get("subject")
                    for m in mail.outbox
                    if AeFollowupAction.notification_display_name
                    in m.__dict__.get("subject")
                ]
            ),
        )

    def test_notifies_initial_ae_g3_is_sae(self):
        baker.make_recipe(
            "clinicedc_tests.aeinitial",
            subject_identifier=self.subject_identifier,
            ae_grade=GRADE3,
            sae=YES,
        )

        self.assertEqual(len(mail.outbox), 4)

        # AeInitial Action notification
        self.assertEqual(
            1,
            len(
                [
                    m.__dict__.get("subject")
                    for m in mail.outbox
                    if AeInitialAction.notification_display_name
                    in m.__dict__.get("subject")
                ]
            ),
        )

        # AeInitialG3EventNotification
        self.assertEqual(
            1,
            len(
                [
                    m.__dict__.get("subject")
                    for m in mail.outbox
                    if AeInitialG3EventNotification.display_name
                    in m.__dict__.get("subject")
                ]
            ),
        )

        # AeFollowupAction
        self.assertEqual(
            1,
            len(
                [
                    m.__dict__.get("subject")
                    for m in mail.outbox
                    if AeFollowupAction.notification_display_name
                    in m.__dict__.get("subject")
                ]
            ),
        )

        # AeTmgAction
        self.assertEqual(
            1,
            len(
                [
                    m.__dict__.get("subject")
                    for m in mail.outbox
                    if AeTmgAction.notification_display_name
                    in m.__dict__.get("subject")
                ]
            ),
        )

    def test_notifies_initial_ae_g4_is_sae(self):
        baker.make_recipe(
            "clinicedc_tests.aeinitial",
            subject_identifier=self.subject_identifier,
            ae_grade=GRADE4,
            sae=YES,
        )

        self.assertEqual(len(mail.outbox), 4)

        # AeInitialG4EventNotification
        self.assertEqual(
            1,
            len(
                [
                    m.__dict__.get("subject")
                    for m in mail.outbox
                    if AeInitialG4EventNotification.display_name
                    in m.__dict__.get("subject")
                ]
            ),
        )

    def test_notifies_initial_ae_death(self):
        baker.make_recipe(
            "clinicedc_tests.aeinitial",
            subject_identifier=self.subject_identifier,
            ae_grade=GRADE5,
            sae=YES,
        )

        self.assertEqual(len(mail.outbox), 3)

        # AeInitial Action notification
        self.assertEqual(
            1,
            len(
                [
                    m.__dict__.get("subject")
                    for m in mail.outbox
                    if AeInitialAction.notification_display_name
                    in m.__dict__.get("subject")
                ]
            ),
        )

        # DeathReportAction
        self.assertEqual(
            1,
            len(
                [
                    m.__dict__.get("subject")
                    for m in mail.outbox
                    if DeathReportAction.notification_display_name
                    in m.__dict__.get("subject")
                ]
            ),
        )

        # AeTmgAction
        self.assertEqual(
            1,
            len(
                [
                    m.__dict__.get("subject")
                    for m in mail.outbox
                    if AeTmgAction.notification_display_name
                    in m.__dict__.get("subject")
                ]
            ),
        )

    def test_notifies_initial_ae_death_with_tmg(self):
        self.get_death_report()

        self.assertIn(
            f"TEST/UAT --EDC TEST PROJECT: Death Report for {self.subject_identifier}",
            [m.subject for m in mail.outbox],
        )
        self.assertIn(
            "TEST/UAT --EDC TEST PROJECT: "
            f"TMG Death Report (1st) for {self.subject_identifier}",
            [m.subject for m in mail.outbox],
        )
        self.assertIn(
            "TEST/UAT --EDC TEST PROJECT:  "
            f"a death has been reported for {self.subject_identifier}",
            [m.subject for m in mail.outbox],
        )

        self.assertEqual(len(mail.outbox), 6)

        # AeInitial Action notification
        self.assertEqual(
            1,
            len(
                [
                    m.__dict__.get("subject")
                    for m in mail.outbox
                    if AeInitialAction.notification_display_name
                    in m.__dict__.get("subject")
                ]
            ),
        )

        # DeathReportAction
        self.assertIn(
            DeathReportAction.notification_display_name,
            "|".join([m.__dict__.get("subject") for m in mail.outbox]),
        )

        # DeathReportTmgAction
        self.assertEqual(
            1,
            len(
                [
                    m.__dict__.get("subject")
                    for m in mail.outbox
                    if DeathReportTmgAction.notification_display_name
                    in m.__dict__.get("subject")
                ]
            ),
        )

    def test_notifies_initial_ae_susar(self):
        baker.make_recipe(
            "clinicedc_tests.aeinitial",
            subject_identifier=self.subject_identifier,
            ae_grade=GRADE4,
            sae=YES,
            susar=YES,
            susar_reported=NO,
        )
        self.assertEqual(len(mail.outbox), 5)

        # AeSusarAction
        self.assertEqual(
            1,
            len(
                [
                    m.__dict__.get("subject")
                    for m in mail.outbox
                    if AeSusarAction.notification_display_name
                    in m.__dict__.get("subject")
                ]
            ),
        )

from django.core import mail
from django.test import TestCase
from edc_constants.constants import NO, YES
from edc_facility.import_holidays import import_holidays
from edc_list_data.site_list_data import site_list_data
from edc_reportable.constants import GRADE3, GRADE4, GRADE5
from model_bakery import baker

from ...action_items import (
    AeFollowupAction,
    AeInitialAction,
    AeSusarAction,
    AeTmgAction,
    DeathReportAction,
    DeathReportTmgAction,
)
from ...notifications import AeInitialG3EventNotification, AeInitialG4EventNotification
from .mixins import DeathReportTestMixin


class TestNotifications(DeathReportTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        site_list_data.autodiscover()
        import_holidays()

    def test_notifies_initial_ae_g3_not_sae(self):
        baker.make_recipe(
            "adverse_event_app.aeinitial",
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
                    if AeInitialAction.notification_display_name in m.__dict__.get("subject")
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
                    if AeInitialG3EventNotification.display_name in m.__dict__.get("subject")
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
                    if AeFollowupAction.notification_display_name in m.__dict__.get("subject")
                ]
            ),
        )

    def test_notifies_initial_ae_g3_is_sae(self):
        baker.make_recipe(
            "adverse_event_app.aeinitial",
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
                    if AeInitialAction.notification_display_name in m.__dict__.get("subject")
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
                    if AeInitialG3EventNotification.display_name in m.__dict__.get("subject")
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
                    if AeFollowupAction.notification_display_name in m.__dict__.get("subject")
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
                    if AeTmgAction.notification_display_name in m.__dict__.get("subject")
                ]
            ),
        )

    def test_notifies_initial_ae_g4_is_sae(self):
        baker.make_recipe(
            "adverse_event_app.aeinitial",
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
                    if AeInitialG4EventNotification.display_name in m.__dict__.get("subject")
                ]
            ),
        )

    def test_notifies_initial_ae_death(self):
        baker.make_recipe(
            "adverse_event_app.aeinitial",
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
                    if AeInitialAction.notification_display_name in m.__dict__.get("subject")
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
                    if DeathReportAction.notification_display_name in m.__dict__.get("subject")
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
                    if AeTmgAction.notification_display_name in m.__dict__.get("subject")
                ]
            ),
        )

    def test_notifies_initial_ae_death_with_tmg(self):

        self.get_death_report()

        self.assertEqual(len(mail.outbox), 7)

        # AeInitial Action notification
        self.assertEqual(
            1,
            len(
                [
                    m.__dict__.get("subject")
                    for m in mail.outbox
                    if AeInitialAction.notification_display_name in m.__dict__.get("subject")
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
            "adverse_event_app.aeinitial",
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
                    if AeSusarAction.notification_display_name in m.__dict__.get("subject")
                ]
            ),
        )

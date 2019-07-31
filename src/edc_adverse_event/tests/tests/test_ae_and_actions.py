from unittest import mock

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.test import TestCase, tag
from edc_action_item.get_action_type import get_action_type
from edc_action_item.models import SubjectDoesNotExist
from edc_action_item.models.action_item import ActionItem
from edc_constants.constants import CLOSED, NO, NEW, YES, LOST_TO_FOLLOWUP
from edc_constants.constants import DEAD
from edc_list_data.site_list_data import site_list_data
from edc_registration.models import RegisteredSubject
from edc_reportable import GRADE3, GRADE4, GRADE5
from edc_utils import get_utcnow
from model_mommy import mommy

from ...action_items import AeFollowupAction, AeInitialAction
from ...models import AeInitial, AeFollowup, AeSusar


class TestAeAndActions(TestCase):
    @classmethod
    def setUpClass(cls):
        site_list_data.autodiscover()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.subject_identifier = "12345"
        RegisteredSubject.objects.create(subject_identifier=self.subject_identifier)

    def test_subject_identifier(self):
        mommy.make_recipe(
            "ambition_ae.aeinitial", subject_identifier=self.subject_identifier
        )

        self.assertRaises(
            SubjectDoesNotExist,
            mommy.make_recipe,
            "ambition_ae.aeinitial",
            subject_identifier="blahblah",
        )

    def test_entire_flow(self):
        for _ in range(0, 5):
            ae_initial = mommy.make_recipe(
                "ambition_ae.aeinitial", subject_identifier=self.subject_identifier
            )
            mommy.make_recipe(
                "ambition_ae.aetmg",
                ae_initial=ae_initial,
                subject_identifier=self.subject_identifier,
            )
            mommy.make_recipe(
                "ambition_ae.aefollowup",
                ae_initial=ae_initial,
                subject_identifier=self.subject_identifier,
            )
            mommy.make_recipe(
                "ambition_ae.aefollowup",
                ae_initial=ae_initial,
                subject_identifier=self.subject_identifier,
            )
            mommy.make_recipe(
                "ambition_ae.aefollowup",
                ae_initial=ae_initial,
                subject_identifier=self.subject_identifier,
            )
            mommy.make_recipe(
                "ambition_ae.aefollowup",
                ae_initial=ae_initial,
                subject_identifier=self.subject_identifier,
                followup=NO,
            )

    def test_fk1(self):
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial", subject_identifier=self.subject_identifier
        )
        mommy.make_recipe(
            "ambition_ae.aefollowup",
            ae_initial=ae_initial,
            subject_identifier=self.subject_identifier,
        )
        mommy.make_recipe(
            "ambition_ae.aefollowup",
            ae_initial=ae_initial,
            subject_identifier=self.subject_identifier,
        )
        mommy.make_recipe(
            "ambition_ae.aefollowup",
            ae_initial=ae_initial,
            subject_identifier=self.subject_identifier,
        )
        mommy.make_recipe(
            "ambition_ae.aefollowup",
            ae_initial=ae_initial,
            subject_identifier=self.subject_identifier,
        )
        mommy.make_recipe(
            "ambition_ae.aetmg",
            ae_initial=ae_initial,
            subject_identifier=self.subject_identifier,
        )

    def test_fk2(self):
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial", subject_identifier=self.subject_identifier
        )
        mommy.make_recipe(
            "ambition_ae.aefollowup",
            ae_initial=ae_initial,
            subject_identifier=self.subject_identifier,
        )
        mommy.make_recipe(
            "ambition_ae.aefollowup",
            ae_initial=ae_initial,
            subject_identifier=self.subject_identifier,
        )
        mommy.make_recipe(
            "ambition_ae.aefollowup",
            ae_initial=ae_initial,
            subject_identifier=self.subject_identifier,
            followup=NO,
        )
        mommy.make_recipe(
            "ambition_ae.aetmg",
            ae_initial=ae_initial,
            subject_identifier=self.subject_identifier,
        )

    def test_ae_initial_action(self):
        """Asserts an AeInitial creates one and only one
        AeFollowupAction.
        """
        # create ae initial action
        action_type = get_action_type(AeInitialAction)
        action_item = ActionItem.objects.create(
            subject_identifier=self.subject_identifier, action_type=action_type
        )
        # create ae initial
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial",
            action_identifier=action_item.action_identifier,
            subject_identifier=self.subject_identifier,
        )
        action_item = ActionItem.objects.get(
            subject_identifier=self.subject_identifier, action_type=action_type
        )
        action_item = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            action_type=action_type,
            status=CLOSED,
        )

        # assert ae initial action created ONE ae followup
        action_type = get_action_type(AeFollowupAction)
        self.assertEqual(
            ActionItem.objects.filter(
                subject_identifier=self.subject_identifier, action_type=action_type
            ).count(),
            1,
        )

        # assert ae initial action created ONE ae followup
        # with correct parent action identifier
        action_item = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            parent_action_item=action_item,
            action_type=action_type,
            status=NEW,
        )

        # resave ae initial and show does not create another followup
        ae_initial.save()
        ae_initial.save()
        ae_initial.save()
        self.assertEqual(
            ActionItem.objects.filter(
                subject_identifier=self.subject_identifier, action_type=action_type
            ).count(),
            1,
        )

    def test_ae_initial_action2(self):
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial", subject_identifier=self.subject_identifier
        )
        action_item = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            action_identifier=ae_initial.action_identifier,
            reference_model="ambition_ae.aeinitial",
        )
        self.assertEqual(action_item.status, CLOSED)

    def test_ae_initial_creates_action(self):
        # create reference model first which creates action_item
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial", subject_identifier=self.subject_identifier
        )
        try:
            ActionItem.objects.get(
                subject_identifier=self.subject_identifier,
                action_identifier=ae_initial.action_identifier,
                reference_model="ambition_ae.aeinitial",
            )
        except ObjectDoesNotExist:
            self.fail(f"action item unexpectedly does not exist.")
        except MultipleObjectsReturned:
            self.fail(f"action item unexpectedly returned multiple objects.")
        self.assertEqual(
            ActionItem.objects.filter(
                subject_identifier=self.subject_identifier,
                action_identifier=ae_initial.action_identifier,
                reference_model="ambition_ae.aeinitial",
            ).count(),
            1,
        )
        self.assertEqual(
            ActionItem.objects.filter(
                subject_identifier=self.subject_identifier,
                parent_action_item=ae_initial.action_item,
                related_action_item=ae_initial.action_item,
                reference_model="ambition_ae.aefollowup",
            ).count(),
            1,
        )

    def test_ae_initial_does_not_recreate_action_on_resave(self):
        # create reference model first which creates action_item
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial", subject_identifier=self.subject_identifier
        )
        ae_initial = AeInitial.objects.get(pk=ae_initial.pk)
        ae_initial.save()
        self.assertEqual(
            ActionItem.objects.filter(
                subject_identifier=self.subject_identifier,
                action_identifier=ae_initial.action_identifier,
                reference_model="ambition_ae.aeinitial",
            ).count(),
            1,
        )

    def test_ae_initial_updates_existing_action_item(self):
        action_type = get_action_type(AeInitialAction)
        action_item = ActionItem.objects.create(
            subject_identifier=self.subject_identifier,
            action_type=action_type,
            reference_model="ambition_ae.aeinitial",
        )

        # then create reference model
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial",
            subject_identifier=self.subject_identifier,
            action_identifier=action_item.action_identifier,
        )

        action_item = ActionItem.objects.get(pk=action_item.pk)
        self.assertEqual(action_item.reference_model, ae_initial._meta.label_lower)
        self.assertEqual(action_item.action_identifier, ae_initial.action_identifier)

    def test_ae_initial_creates_next_action_on_close(self):
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial", subject_identifier=self.subject_identifier
        )
        ae_initial = AeInitial.objects.get(pk=ae_initial.pk)
        self.assertTrue(
            ActionItem.objects.get(
                subject_identifier=self.subject_identifier,
                action_identifier=ae_initial.action_identifier,
                parent_action_item=None,
                reference_model="ambition_ae.aeinitial",
                status=CLOSED,
            )
        )
        self.assertTrue(
            ActionItem.objects.get(
                subject_identifier=self.subject_identifier,
                parent_action_item=ae_initial.action_item,
                related_action_item=ae_initial.action_item,
                reference_model="ambition_ae.aefollowup",
                status=NEW,
            )
        )
        self.assertTrue(
            ActionItem.objects.get(
                subject_identifier=self.subject_identifier,
                parent_action_item=ae_initial.action_item,
                related_action_item=ae_initial.action_item,
                reference_model="ambition_ae.aetmg",
                status=NEW,
            )
        )

    def test_next_action1(self):
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial", subject_identifier=self.subject_identifier
        )
        # action item has no parent, is updated
        ActionItem.objects.get(
            parent_action_item=None,
            action_identifier=ae_initial.action_identifier,
            reference_model="ambition_ae.aeinitial",
        )

        # action item a parent, is not updated
        ActionItem.objects.get(
            parent_action_item=ae_initial.action_item,
            related_action_item=ae_initial.action_item,
            reference_model="ambition_ae.aefollowup",
        )

        # action item a parent, is not updated
        ActionItem.objects.get(
            parent_action_item=ae_initial.action_item,
            related_action_item=ae_initial.action_item,
            reference_model="ambition_ae.aetmg",
        )

    def test_next_action2(self):
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial", subject_identifier=self.subject_identifier
        )
        ae_followup = mommy.make_recipe(
            "ambition_ae.aefollowup",
            ae_initial=ae_initial,
            subject_identifier=self.subject_identifier,
        )
        ae_followup = AeFollowup.objects.get(pk=ae_followup.pk)

        ActionItem.objects.get(
            parent_action_item=ae_initial.action_item,
            related_action_item=ae_initial.action_item,
            action_identifier=ae_followup.action_identifier,
            reference_model="ambition_ae.aefollowup",
            linked_to_reference=True,
            status=CLOSED,
        )
        ActionItem.objects.get(
            parent_action_item=ae_followup.action_item,
            related_action_item=ae_initial.action_item,
            reference_model="ambition_ae.aefollowup",
            linked_to_reference=False,
            status=NEW,
        )

    def test_next_action3(self):
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial", subject_identifier=self.subject_identifier
        )
        ae_followup1 = mommy.make_recipe(
            "ambition_ae.aefollowup",
            ae_initial=ae_initial,
            subject_identifier=self.subject_identifier,
        )
        ae_followup1 = AeFollowup.objects.get(pk=ae_followup1.pk)
        ae_followup2 = mommy.make_recipe(
            "ambition_ae.aefollowup",
            ae_initial=ae_initial,
            subject_identifier=self.subject_identifier,
        )
        ae_followup2 = AeFollowup.objects.get(pk=ae_followup2.pk)
        ActionItem.objects.get(
            parent_action_item=ae_initial.action_item,
            related_action_item=ae_initial.action_item,
            action_identifier=ae_followup1.action_identifier,
            reference_model="ambition_ae.aefollowup",
            linked_to_reference=True,
            status=CLOSED,
        )
        ActionItem.objects.get(
            parent_action_item=ae_followup1.action_item,
            related_action_item=ae_initial.action_item,
            action_identifier=ae_followup2.action_identifier,
            reference_model="ambition_ae.aefollowup",
            linked_to_reference=True,
            status=CLOSED,
        )
        ActionItem.objects.get(
            parent_action_item=ae_followup2.action_item,
            related_action_item=ae_initial.action_item,
            reference_model="ambition_ae.aefollowup",
            linked_to_reference=False,
            status=NEW,
        )

    def test_next_action4(self):
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial", subject_identifier=self.subject_identifier
        )
        ae_followup1 = mommy.make_recipe(
            "ambition_ae.aefollowup",
            ae_initial=ae_initial,
            subject_identifier=self.subject_identifier,
        )
        ae_followup1 = AeFollowup.objects.get(pk=ae_followup1.pk)
        # set followup = NO so next action item is not created
        ae_followup2 = mommy.make_recipe(
            "ambition_ae.aefollowup",
            ae_initial=ae_initial,
            subject_identifier=self.subject_identifier,
            followup=NO,
        )
        ae_followup2 = AeFollowup.objects.get(pk=ae_followup2.pk)

        ActionItem.objects.get(
            parent_action_item=ae_initial.action_item,
            related_action_item=ae_initial.action_item,
            action_identifier=ae_followup1.action_identifier,
            reference_model="ambition_ae.aefollowup",
            linked_to_reference=True,
            status=CLOSED,
        )

        ActionItem.objects.get(
            parent_action_item=ae_followup1.action_item,
            related_action_item=ae_initial.action_item,
            action_identifier=ae_followup2.action_identifier,
            reference_model="ambition_ae.aefollowup",
            linked_to_reference=True,
            status=CLOSED,
        )

        self.assertRaises(
            ObjectDoesNotExist,
            ActionItem.objects.get,
            parent_action_item=ae_followup2.action_item,
            related_action_item=ae_initial.action_item,
            reference_model="ambition_ae.aefollowup",
            linked_to_reference=False,
            status=NEW,
        )

    def test_ae_followup_multiple_instances(self):
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial", subject_identifier=self.subject_identifier
        )
        ae_initial = AeInitial.objects.get(pk=ae_initial.pk)

        ae_followup = mommy.make_recipe(
            "ambition_ae.aefollowup",
            ae_initial=ae_initial,
            subject_identifier=self.subject_identifier,
        )
        ae_followup = AeFollowup.objects.get(pk=ae_followup.pk)

        ae_followup = mommy.make_recipe(
            "ambition_ae.aefollowup",
            ae_initial=ae_initial,
            subject_identifier=self.subject_identifier,
        )
        ae_followup = AeFollowup.objects.get(pk=ae_followup.pk)

    def test_ae_followup_outcome_ltfu_creates_action(self):

        with mock.patch("ambition_ae.action_items.get_offschedule_models") as mocked:
            mocked.return_value = ["ambition_prn.studyterminationconclusion"]

            ae_initial = mommy.make_recipe(
                "ambition_ae.aeinitial", subject_identifier=self.subject_identifier
            )

            ae_followup = mommy.make_recipe(
                "ambition_ae.aefollowup",
                ae_initial=ae_initial,
                subject_identifier=self.subject_identifier,
                report_datetime=get_utcnow(),
                outcome=LOST_TO_FOLLOWUP,
            )

            try:
                ActionItem.objects.get(
                    parent_action_item=ae_followup.action_item,
                    reference_model="ambition_prn.studyterminationconclusion",
                )
            except ObjectDoesNotExist:
                self.fail("ObjectDoesNotExist unexpectedly raised")

    def test_ae_followup_outcome_not_ltfu(self):

        with mock.patch("ambition_ae.action_items.get_offschedule_models") as mocked:
            mocked.return_value = ["ambition_prn.studyterminationconclusion"]

            ae_initial = mommy.make_recipe(
                "ambition_ae.aeinitial", subject_identifier=self.subject_identifier
            )

            ae_followup = mommy.make_recipe(
                "ambition_ae.aefollowup",
                ae_initial=ae_initial,
                subject_identifier=self.subject_identifier,
                report_datetime=get_utcnow(),
                outcome=DEAD,
            )

            try:
                ActionItem.objects.get(
                    parent_action_item=ae_followup.action_item,
                    reference_model="ambition_prn.studyterminationconclusion",
                )
            except ObjectDoesNotExist:
                pass
            else:
                self.fail("ObjectDoesNotExist unexpectedly raised")

    def test_ae_tmg_required_if_g3_and_sae_yes(self):

        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial",
            subject_identifier=self.subject_identifier,
            ae_grade=GRADE3,
            sae=YES,
        )

        try:
            ActionItem.objects.get(
                parent_action_item=ae_initial.action_item,
                reference_model="ambition_ae.aetmg",
            )
        except ObjectDoesNotExist:
            self.fail("ObjectDoesNotExist unexpectedly raised")

    def test_ae_tmg_not_required_if_g3_and_sae_no(self):

        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial",
            subject_identifier=self.subject_identifier,
            ae_grade=GRADE3,
            sae=NO,
        )

        self.assertRaises(
            ObjectDoesNotExist,
            ActionItem.objects.get,
            parent_action_item=ae_initial.action_item,
            reference_model="ambition_ae.aetmg",
        )

    def test_ae_tmg_required_if_g4(self):

        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial",
            subject_identifier=self.subject_identifier,
            ae_grade=GRADE4,
        )

        ActionItem.objects.get(
            parent_action_item=ae_initial.action_item,
            reference_model="ambition_ae.aetmg",
        )

    def test_ae_is_not_sae(self):

        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial",
            subject_identifier=self.subject_identifier,
            ae_grade=GRADE3,
            sae=NO,
        )

        self.assertRaises(
            ObjectDoesNotExist,
            ActionItem.objects.get,
            parent_action_item=ae_initial.action_item,
            reference_model="ambition_ae.aetmg",
        )

    def test_ae_creates_death_report_action(self):

        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial",
            subject_identifier=self.subject_identifier,
            ae_grade=GRADE5,
            sae=NO,
        )

        ActionItem.objects.get(
            parent_action_item=ae_initial.action_item,
            reference_model="ambition_prn.deathreport",
        )

        ActionItem.objects.get(
            parent_action_item=ae_initial.action_item,
            reference_model="ambition_ae.aetmg",
        )

    def test_ae_initial_creates_susar_if_not_reported(self):

        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial",
            subject_identifier=self.subject_identifier,
            susar=YES,
            susar_reported=YES,
            user_created="erikvw",
        )

        self.assertRaises(
            ObjectDoesNotExist,
            ActionItem.objects.get,
            parent_action_item=ae_initial.action_item,
            reference_model="ambition_ae.aesusar",
        )

        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial",
            subject_identifier=self.subject_identifier,
            susar=YES,
            susar_reported=NO,
            user_created="erikvw",
        )

        ActionItem.objects.get(
            parent_action_item=ae_initial.action_item,
            reference_model="ambition_ae.aesusar",
        )

    def test_susar_updates_aeinitial_if_submitted(self):

        # create ae initial
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial",
            subject_identifier=self.subject_identifier,
            susar=YES,
            susar_reported=NO,
            user_created="erikvw",
        )

        # confirm ae susar action item is created
        action_item = ActionItem.objects.get(
            parent_action_item=ae_initial.action_item,
            reference_model="ambition_ae.aesusar",
        )

        self.assertEqual(action_item.status, NEW)

        # create ae susar
        mommy.make_recipe(
            "ambition_ae.aesusar",
            subject_identifier=self.subject_identifier,
            submitted_datetime=get_utcnow(),
            ae_initial=ae_initial,
        )

        # confirm action status is closed
        action_item.refresh_from_db()
        self.assertEqual(action_item.status, CLOSED)

        # confirm susar updates ae_initial (thru signal)
        ae_initial.refresh_from_db()
        self.assertEqual(ae_initial.susar_reported, YES)

    def test_aeinitial_can_close_action_without_susar_model(self):

        # create ae initial
        ae_initial = mommy.make_recipe(
            "ambition_ae.aeinitial",
            subject_identifier=self.subject_identifier,
            susar=YES,
            susar_reported=NO,
            user_created="erikvw",
        )

        # confirm ae susar action item is created
        action_item = ActionItem.objects.get(
            parent_action_item=ae_initial.action_item,
            reference_model="ambition_ae.aesusar",
        )

        # change to YES before submitting an AeSusar
        ae_initial.susar_reported = YES
        ae_initial.save()
        ae_initial.refresh_from_db()

        # confirm AeSusar was created (by signal)
        try:
            AeSusar.objects.get(ae_initial=ae_initial)
        except ObjectDoesNotExist:
            self.fail("AeSusar unexpectedly does not exist")

        # confirm ActionItem is closed
        action_item.refresh_from_db()
        self.assertEqual(action_item.status, CLOSED)

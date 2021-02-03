from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from edc_action_item.models.action_item import ActionItem
from edc_constants.constants import CLOSED, NEW, NO, OTHER, YES
from edc_facility.import_holidays import import_holidays
from edc_list_data.site_list_data import site_list_data
from model_bakery import baker

from edc_adverse_event.constants import DEATH_REPORT_TMG_SECOND_ACTION
from edc_adverse_event.models import CauseOfDeath

from .mixins import DeathReportTestMixin


class TestDeathReportTmg(DeathReportTestMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        site_list_data.autodiscover()
        import_holidays()
        super().setUpClass()

    def test_death(self):
        # create ae initial
        ae_initial = baker.make_recipe(
            "adverse_event_app.aeinitial",
            subject_identifier=self.subject_identifier,
            susar=YES,
            susar_reported=YES,
            ae_grade=5,
            user_created="erikvw",
        )

        ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            parent_action_item=None,
            reference_model="adverse_event_app.aeinitial",
        )

        # confirm death report action item is created
        try:
            action_item = ActionItem.objects.get(
                subject_identifier=self.subject_identifier,
                parent_action_item=ae_initial.action_item,
                reference_model="adverse_event_app.deathreport",
            )
        except ObjectDoesNotExist:
            self.fail("deathreport action unexpectedly does not exist")

        # create death report
        baker.make_recipe(
            "adverse_event_app.deathreport",
            subject_identifier=self.subject_identifier,
            action_identifier=action_item.action_identifier,
            user_created="erikvw",
        )

        # confirm death report action is closed
        action_item = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            parent_action_item=ae_initial.action_item,
            reference_model="adverse_event_app.deathreport",
        )
        self.assertEqual(action_item.status, CLOSED)

    def test_death_tmg_agrees(self):

        death_report = self.get_death_report()

        # confirm death report tmg action item is created
        try:
            action_item = ActionItem.objects.get(
                subject_identifier=self.subject_identifier,
                related_action_item=death_report.action_item,
                parent_action_item=death_report.action_item,
                reference_model="adverse_event_app.deathreporttmg",
            )
        except ObjectDoesNotExist:
            self.fail("deathreport action unexpectedly does not exist")

        # create death report TMG
        death_report_tmg = baker.make_recipe(
            "adverse_event_app.deathreporttmg",
            death_report=death_report,
            subject_identifier=self.subject_identifier,
            action_identifier=action_item.action_identifier,
            cause_of_death=death_report.cause_of_death,
            cause_of_death_agreed=YES,
            report_status=CLOSED,
            user_created="erikvw",
        )

        self.assertEqual(death_report_tmg.report_status, CLOSED)

        action_item.refresh_from_db()
        self.assertEqual(action_item.status, CLOSED)

    def test_death_tmg_disagrees_still_closes(self):

        death_report = self.get_death_report()

        # confirm death report tmg action item is created
        try:
            action_item = ActionItem.objects.get(
                subject_identifier=self.subject_identifier,
                related_action_item=death_report.action_item,
                parent_action_item=death_report.action_item,
                reference_model="adverse_event_app.deathreporttmg",
            )
        except ObjectDoesNotExist:
            self.fail("deathreport action unexpectedly does not exist")

        # create death report TMG
        death_report_tmg = baker.make_recipe(
            "adverse_event_app.deathreporttmg",
            death_report=death_report,
            subject_identifier=self.subject_identifier,
            action_identifier=action_item.action_identifier,
            cause_of_death=death_report.cause_of_death,
            cause_of_death_agreed=NO,
            report_status=CLOSED,
            user_created="erikvw",
        )

        self.assertEqual(death_report_tmg.report_status, CLOSED)

        action_item.refresh_from_db()
        self.assertEqual(action_item.status, CLOSED)

    def test_death_tmg_disagrees_creates_new_second_tmg_action(self):

        death_report = self.get_death_report()

        action_item = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            parent_action_item=death_report.action_item,
            reference_model="adverse_event_app.deathreporttmg",
        )

        # create death report TMG
        causes_qs = CauseOfDeath.objects.exclude(name__in=[OTHER, death_report.cause_of_death])
        baker.make_recipe(
            "adverse_event_app.deathreporttmg",
            death_report=death_report,
            subject_identifier=self.subject_identifier,
            action_identifier=action_item.action_identifier,
            cause_of_death=causes_qs[0],
            cause_of_death_agreed=NO,
            report_status=CLOSED,
            user_created="erikvw",
        )
        action_item.refresh_from_db()
        self.assertEqual(action_item.status, CLOSED)

        # assert second TMG action is created, because they disagree
        try:
            action_item = ActionItem.objects.get(
                subject_identifier=self.subject_identifier,
                reference_model="adverse_event_app.deathreporttmgsecond",
            )
        except ObjectDoesNotExist:
            self.fail("deathreporttmgsecond action item unexpectedly does not exist")

        # assert closed
        self.assertEqual(action_item.status, NEW)

    def test_death_tmg_submit_second_tmg_action(self):
        death_report = self.get_death_report()

        action_item = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            parent_action_item=death_report.action_item,
            reference_model="adverse_event_app.deathreporttmg",
        )

        # create death report TMG
        causes_qs = CauseOfDeath.objects.exclude(name__in=[OTHER, death_report.cause_of_death])
        death_report_tmg = baker.make_recipe(
            "adverse_event_app.deathreporttmg",
            death_report=death_report,
            subject_identifier=self.subject_identifier,
            action_identifier=action_item.action_identifier,
            cause_of_death=causes_qs[0],
            cause_of_death_agreed=NO,
            report_status=CLOSED,
            user_created="erikvw",
        )

        death_report.refresh_from_db()

        second_action_item = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            related_action_item=death_report.action_item,
            parent_action_item=death_report_tmg.action_item,
            reference_model="adverse_event_app.deathreporttmgsecond",
            action_type__name=DEATH_REPORT_TMG_SECOND_ACTION,
        )

        # create 2nd death report TMG
        death_report_tmg_second = baker.make_recipe(
            "adverse_event_app.deathreporttmgsecond",
            death_report=death_report,
            subject_identifier=self.subject_identifier,
            action_identifier=second_action_item.action_identifier,
            cause_of_death=causes_qs[0],
            cause_of_death_agreed=NO,
            report_status=CLOSED,
            user_created="erikvw",
        )

        second_action_item.refresh_from_db()
        death_report_tmg_second.save()
        self.assertEqual(second_action_item.status, CLOSED)

        death_report_tmg_second.save()
        second_action_item.refresh_from_db()
        self.assertEqual(second_action_item.status, CLOSED)

    def test_death_tmg_disagrees_tmg_action_changes(self):
        """Assert changes to death report tmg are safe.

        For example: (cause of death agreed = YES/NO)
        """

        death_report = self.get_death_report()

        action_item = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            parent_action_item=death_report.action_item,
            reference_model="adverse_event_app.deathreporttmg",
        )

        # create death report TMG
        causes_qs = CauseOfDeath.objects.exclude(name__in=[OTHER, death_report.cause_of_death])
        death_report_tmg = baker.make_recipe(
            "adverse_event_app.deathreporttmg",
            death_report=death_report,
            subject_identifier=self.subject_identifier,
            action_identifier=action_item.action_identifier,
            cause_of_death=causes_qs[0],
            cause_of_death_agreed=YES,
            report_status=CLOSED,
            user_created="erikvw",
        )

        self.assertRaises(
            ObjectDoesNotExist,
            ActionItem.objects.get,
            subject_identifier=self.subject_identifier,
            related_action_item=death_report.action_item,
            parent_action_item=death_report_tmg.action_item,
            reference_model="adverse_event_app.deathreporttmgsecond",
            action_type__name=DEATH_REPORT_TMG_SECOND_ACTION,
        )

        death_report_tmg.cause_of_death_agreed = NO
        death_report_tmg.save()

        ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            related_action_item=death_report.action_item,
            parent_action_item=death_report_tmg.action_item,
            reference_model="adverse_event_app.deathreporttmgsecond",
            action_type__name=DEATH_REPORT_TMG_SECOND_ACTION,
        )

        death_report_tmg.cause_of_death_agreed = YES
        death_report_tmg.save()

        self.assertRaises(
            ObjectDoesNotExist,
            ActionItem.objects.get,
            subject_identifier=self.subject_identifier,
            related_action_item=death_report.action_item,
            parent_action_item=death_report_tmg.action_item,
            reference_model="adverse_event_app.deathreporttmgsecond",
            action_type__name=DEATH_REPORT_TMG_SECOND_ACTION,
        )

    def test_tmg_once_closed_does_not_repopen(self):

        death_report = self.get_death_report()

        action_item = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            parent_action_item=death_report.action_item,
            reference_model="adverse_event_app.deathreporttmg",
        )

        causes_qs = CauseOfDeath.objects.exclude(name__in=[OTHER, death_report.cause_of_death])
        death_report_tmg = baker.make_recipe(
            "adverse_event_app.deathreporttmg",
            death_report=death_report,
            subject_identifier=self.subject_identifier,
            action_identifier=action_item.action_identifier,
            cause_of_death=causes_qs[0],
            cause_of_death_agreed=YES,
            report_status=CLOSED,
            user_created="erikvw",
        )

        action_item.refresh_from_db()
        self.assertEqual(action_item.status, CLOSED)

        death_report_tmg.cause_of_death_agreed = NO
        death_report_tmg.save()

        action_item.refresh_from_db()
        self.assertEqual(action_item.status, CLOSED)

    def test_2nd_tmg_once_closed_does_not_repopen(self):

        death_report = self.get_death_report()

        action_item = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            parent_action_item=death_report.action_item,
            reference_model="adverse_event_app.deathreporttmg",
        )

        causes_qs = CauseOfDeath.objects.exclude(name__in=[OTHER, death_report.cause_of_death])
        death_report_tmg = baker.make_recipe(
            "adverse_event_app.deathreporttmg",
            death_report=death_report,
            subject_identifier=self.subject_identifier,
            action_identifier=action_item.action_identifier,
            cause_of_death=causes_qs[0],
            cause_of_death_agreed=NO,
            report_status=CLOSED,
            user_created="erikvw",
        )

        action_item_two = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            related_action_item=death_report.action_item,
            parent_action_item=death_report_tmg.action_item,
            reference_model="adverse_event_app.deathreporttmgsecond",
            action_type__name=DEATH_REPORT_TMG_SECOND_ACTION,
        )

        # create 2nd death report TMG
        death_report_tmg_second = baker.make_recipe(
            "adverse_event_app.deathreporttmgsecond",
            death_report=death_report,
            subject_identifier=self.subject_identifier,
            action_identifier=action_item_two.action_identifier,
            cause_of_death=causes_qs[0],
            cause_of_death_agreed=NO,
            report_status=CLOSED,
            user_created="erikvw",
        )

        action_item_two.refresh_from_db()
        self.assertEqual(action_item_two.status, CLOSED)

        death_report_tmg_second.cause_of_death_agreed = YES
        death_report_tmg_second.save()

        action_item_two.refresh_from_db()
        self.assertEqual(action_item_two.status, CLOSED)

    def test_delete_second_tmg_and_change_agreed_to_yes(self):

        death_report = self.get_death_report()

        action_item_one = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            parent_action_item=death_report.action_item,
            reference_model="adverse_event_app.deathreporttmg",
        )

        causes_qs = CauseOfDeath.objects.exclude(name__in=[OTHER, death_report.cause_of_death])
        death_report_tmg = baker.make_recipe(
            "adverse_event_app.deathreporttmg",
            death_report=death_report,
            subject_identifier=self.subject_identifier,
            action_identifier=action_item_one.action_identifier,
            cause_of_death=causes_qs[0],
            cause_of_death_agreed=NO,
            report_status=CLOSED,
            user_created="erikvw",
        )

        action_item_two = ActionItem.objects.get(
            subject_identifier=self.subject_identifier,
            related_action_item=death_report.action_item,
            parent_action_item=death_report_tmg.action_item,
            reference_model="adverse_event_app.deathreporttmgsecond",
            action_type__name=DEATH_REPORT_TMG_SECOND_ACTION,
        )

        # create 2nd death report TMG
        death_report_tmg_second = baker.make_recipe(
            "adverse_event_app.deathreporttmgsecond",
            death_report=death_report,
            subject_identifier=self.subject_identifier,
            action_identifier=action_item_two.action_identifier,
            cause_of_death=causes_qs[0],
            cause_of_death_agreed=NO,
            report_status=CLOSED,
            user_created="erikvw",
        )

        action_item_one.refresh_from_db()
        self.assertEqual(action_item_one.status, CLOSED)
        action_item_two.refresh_from_db()
        self.assertEqual(action_item_two.status, CLOSED)

        # delete 2nd TMG report
        death_report_tmg_second.delete()

        # assert status for 2nd TMG action item is reset to NEW
        action_item_two.refresh_from_db()
        self.assertEqual(action_item_two.status, NEW)

        # change 1st TMG report to agrees
        death_report_tmg.cause_of_death_agreed = YES
        death_report_tmg.save()

        # action item for 2nd tmg is auto-deleted
        self.assertRaises(
            ObjectDoesNotExist,
            ActionItem.objects.get,
            subject_identifier=self.subject_identifier,
            related_action_item=death_report.action_item,
            parent_action_item=death_report_tmg.action_item,
            reference_model="adverse_event_app.deathreporttmgsecond",
            action_type__name=DEATH_REPORT_TMG_SECOND_ACTION,
        )

from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.test import TestCase

from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_schedule.system_checks import (
    check_form_collections,
    visit_schedule_check,
)
from edc_visit_schedule.visit import CrfCollection, FormsCollectionError, Visit
from edc_visit_schedule.visit.crf import Crf
from edc_visit_schedule.visit_schedule import VisitSchedule
from visit_schedule_app.consents import consent_v1


class TestSystemChecks(TestCase):
    def setUp(self):
        self.visit_schedule = VisitSchedule(
            name="visit_schedule",
            verbose_name="Visit Schedule",
            offstudy_model="visit_schedule_app.subjectoffstudy",
            death_report_model="visit_schedule_app.deathreport",
            locator_model="edc_locator.subjectlocator",
        )

        self.schedule = Schedule(
            name="schedule",
            onschedule_model="visit_schedule_app.onschedule",
            offschedule_model="visit_schedule_app.offschedule",
            appointment_model="edc_appointment.appointment",
            consent_definitions=[consent_v1],
            base_timepoint=1,
        )

    def test_system_check(self):
        site_visit_schedules._registry = {}
        errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "edc_visit_schedule.W001")

    def test_visit_schedule_ok(self):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)
        errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(errors), 0)

    def test_visit_schedule_bad_model(self):
        site_visit_schedules._registry = {}
        visit_schedule = VisitSchedule(
            name="visit_schedule",
            verbose_name="Visit Schedule",
            offstudy_model="blah.subjectoffstudy",
            death_report_model="visit_schedule_app.deathreport",
            locator_model="edc_locator.subjectlocator",
        )
        schedule = Schedule(
            name="schedule",
            onschedule_model="visit_schedule_app.onschedule",
            offschedule_model="visit_schedule_app.offschedule",
            appointment_model="edc_appointment.appointment",
            consent_definitions=[consent_v1],
            base_timepoint=1,
        )
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)
        errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(errors), 1)
        self.assertEqual("edc_visit_schedule.E002", errors[0].id)

    def test_schedule_bad_model(self):
        site_visit_schedules._registry = {}
        visit_schedule = VisitSchedule(
            name="visit_schedule",
            verbose_name="Visit Schedule",
            offstudy_model="visit_schedule_app.subjectoffstudy",
            death_report_model="visit_schedule_app.deathreport",
            locator_model="edc_locator.subjectlocator",
        )
        schedule = Schedule(
            name="schedule",
            onschedule_model="visit_schedule_app.onschedule",
            offschedule_model="visit_schedule_app.offschedule",
            appointment_model="blah.appointment",
            consent_definitions=[consent_v1],
            base_timepoint=1,
        )
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)
        errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(errors), 1)
        self.assertEqual("edc_visit_schedule.E003", errors[0].id)

    def test_schedule_bad_crf_model(self):
        site_visit_schedules._registry = {}
        visit_schedule = VisitSchedule(
            name="visit_schedule",
            verbose_name="Visit Schedule",
            offstudy_model="visit_schedule_app.subjectoffstudy",
            death_report_model="visit_schedule_app.deathreport",
            locator_model="edc_locator.subjectlocator",
        )
        schedule = Schedule(
            name="schedule",
            onschedule_model="visit_schedule_app.onschedule",
            offschedule_model="visit_schedule_app.offschedule",
            appointment_model="edc_appointment.appointment",
            consent_definitions=[consent_v1],
            base_timepoint=1,
        )
        crfs = CrfCollection(
            Crf(show_order=10, model="blah.CrfOne"),
            Crf(show_order=20, model="blah.CrfTwo"),
            Crf(show_order=30, model="blah.CrfThree"),
        )
        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)
        errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(errors), 3)
        self.assertEqual("edc_visit_schedule.E004", errors[0].id)

    def test_visit_with_crfs_and_prns_and_unscheduled_and_missed_crfs_ok(self):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(show_order=10, model="visit_schedule_app.CrfOne"),
            Crf(show_order=20, model="visit_schedule_app.CrfTwo"),
            Crf(show_order=30, model="visit_schedule_app.CrfThree"),
        )
        prns = CrfCollection(
            Crf(show_order=15, model="visit_schedule_app.PrnOne"),
            Crf(show_order=25, model="visit_schedule_app.PrnTwo"),
            Crf(show_order=35, model="visit_schedule_app.PrnThree"),
        )
        unscheduled_crfs = CrfCollection(
            Crf(show_order=20, model="visit_schedule_app.CrfTwo"),
            Crf(show_order=30, model="visit_schedule_app.CrfThree"),
        )
        missed_crfs = CrfCollection(Crf(show_order=30, model="visit_schedule_app.CrfThree"))

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            crfs_unscheduled=unscheduled_crfs,
            crfs_missed=missed_crfs,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertListEqual(fc_errors, [])

    def test_crf_not_required_with_matching_prn_ok(self):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(show_order=10, model="visit_schedule_app.CrfOne", required=False),
            Crf(show_order=20, model="visit_schedule_app.CrfTwo"),
            Crf(show_order=30, model="visit_schedule_app.CrfThree"),
        )
        prns = CrfCollection(
            Crf(show_order=15, model="visit_schedule_app.CrfOne"),
        )
        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertListEqual(fc_errors, [])

    def test_proxy_crf_not_required_with_matching_proxy_prn_ok(
        self,
    ):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(show_order=20, model="visit_schedule_app.CrfTwoProxyOne", required=False),
        )
        prns = CrfCollection(
            Crf(show_order=10, model="visit_schedule_app.CrfTwoProxyOne"),
        )
        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertListEqual(fc_errors, [])

    def test_proxy_crf_not_required_without_shared_proxy_root_and_differing_proxy_prn_raises(
        self,
    ):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(show_order=20, model="visit_schedule_app.CrfTwoProxyOne", required=False),
        )
        prns = CrfCollection(
            Crf(show_order=25, model="visit_schedule_app.CrfTwoProxyOne"),
            Crf(show_order=15, model="visit_schedule_app.CrfTwoProxyTwo"),
        )
        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(fc_errors), 3)
        self.assertEqual("edc_visit_schedule.E007", fc_errors[0].id)
        self.assertIn(
            "Multiple proxies with same proxy root model appear for a visit. ",
            fc_errors[0].msg,
        )
        self.assertIn("Scheduled", fc_errors[0].msg)
        self.assertIn(
            str(
                {
                    "visit_schedule_app.crftwo": [
                        "visit_schedule_app.crftwoproxyone",
                        "visit_schedule_app.crftwoproxyone",
                        "visit_schedule_app.crftwoproxytwo",
                    ]
                }
            ),
            fc_errors[0].msg,
        )
        # Expect only the PRN fields to be flagged for the (undefined)
        # unscheduled and unscheduled visits
        self.assertEqual("edc_visit_schedule.E007", fc_errors[1].id)
        self.assertIn("Unscheduled", fc_errors[1].msg)
        self.assertIn(
            str(
                {
                    "visit_schedule_app.crftwo": [
                        "visit_schedule_app.crftwoproxyone",
                        "visit_schedule_app.crftwoproxytwo",
                    ]
                }
            ),
            fc_errors[1].msg,
        )
        self.assertIn("Missed", fc_errors[2].msg)
        self.assertEqual("edc_visit_schedule.E007", fc_errors[2].id)
        self.assertIn(
            str(
                {
                    "visit_schedule_app.crftwo": [
                        "visit_schedule_app.crftwoproxyone",
                        "visit_schedule_app.crftwoproxytwo",
                    ]
                }
            ),
            fc_errors[2].msg,
        )

    def test_proxy_crf_not_required_with_shared_proxy_root_and_matching_proxy_prn_ok(self):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(
                show_order=20,
                model="visit_schedule_app.CrfTwoProxyOne",
                required=False,
                shares_proxy_root=True,
            ),
        )
        prns = CrfCollection(
            Crf(
                show_order=10,
                model="visit_schedule_app.CrfTwoProxyOne",
                shares_proxy_root=True,
            ),
        )
        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertListEqual(fc_errors, [])

    def test_duplicates_in_crf_collection_raises(self):
        """Duplicate crf/proxy in single collection = BAD."""
        # CRFs
        with self.assertRaises(FormsCollectionError) as cm:
            CrfCollection(
                Crf(show_order=10, model="visit_schedule_app.CrfOne"),
                Crf(show_order=20, model="visit_schedule_app.CrfTwo"),
                Crf(show_order=30, model="visit_schedule_app.CrfTwo"),
            )
        self.assertIn(
            "Expected to be a unique sequence of crf/models.",
            str(cm.exception),
        )
        self.assertIn(
            "Duplicates ['visit_schedule_app.crftwo'].",
            str(cm.exception),
        )

        # Proxy models
        with self.assertRaises(FormsCollectionError) as cm:
            CrfCollection(
                Crf(show_order=10, model="visit_schedule_app.CrfOne"),
                Crf(show_order=20, model="visit_schedule_app.CrfTwoProxyOne"),
                Crf(show_order=30, model="visit_schedule_app.CrfTwoProxyOne"),
            )
        self.assertIn(
            "Expected to be a unique sequence of crf/models.",
            str(cm.exception),
        )
        self.assertIn(
            "Duplicates ['visit_schedule_app.crftwoproxyone'].",
            str(cm.exception),
        )

        # PRNs
        with self.assertRaises(FormsCollectionError) as cm:
            CrfCollection(
                Crf(show_order=15, model="visit_schedule_app.PrnOne"),
                Crf(show_order=25, model="visit_schedule_app.PrnTwo"),
                Crf(show_order=35, model="visit_schedule_app.PrnTwo"),
            )
        self.assertIn(
            "Expected to be a unique sequence of crf/models.",
            str(cm.exception),
        )
        self.assertIn(
            "Duplicates ['visit_schedule_app.prntwo'].",
            str(cm.exception),
        )

    def test_required_crf_in_prns_ok(self):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(show_order=10, model="visit_schedule_app.CrfOne", required=True),
            Crf(show_order=20, model="visit_schedule_app.CrfTwo"),
            Crf(show_order=30, model="visit_schedule_app.CrfThree"),
        )
        prns = CrfCollection(
            Crf(show_order=15, model="visit_schedule_app.CrfOne"),
            Crf(show_order=25, model="visit_schedule_app.PrnOne"),
            Crf(show_order=35, model="visit_schedule_app.PrnTwo"),
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertListEqual(fc_errors, [])

    def test_required_proxy_crf_in_prns_ok(self):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(
                show_order=10,
                model="visit_schedule_app.CrfOneProxyOne",
                required=True,
                shares_proxy_root=True,
            ),
            Crf(show_order=20, model="visit_schedule_app.CrfTwo"),
        )
        prns = CrfCollection(
            Crf(
                show_order=15,
                model="visit_schedule_app.CrfOneProxyOne",
                shares_proxy_root=True,
            ),
            Crf(show_order=25, model="visit_schedule_app.PrnOne"),
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertListEqual(fc_errors, [])

    def test_required_proxy_root_crf_with_required_child_proxy_crf_raises(self):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(show_order=10, model="visit_schedule_app.CrfOne", required=True),
            Crf(show_order=15, model="visit_schedule_app.CrfOneProxyOne", required=True),
            Crf(show_order=20, model="visit_schedule_app.CrfTwo"),
            Crf(show_order=30, model="visit_schedule_app.CrfThree"),
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(fc_errors), 1)
        self.assertEqual("edc_visit_schedule.E006", fc_errors[0].id)
        self.assertIn(
            "Proxy root model class appears alongside associated child proxy for a visit.",
            fc_errors[0].msg,
        )
        self.assertIn("proxy_root_model=visit_schedule_app.crfone", fc_errors[0].msg)
        self.assertIn("proxy_model=visit_schedule_app.crfoneproxyone", fc_errors[0].msg)

    def test_required_proxy_root_crf_with_not_required_child_proxy_crf_raises(self):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(show_order=10, model="visit_schedule_app.CrfOne", required=True),
            Crf(show_order=15, model="visit_schedule_app.CrfOneProxyOne", required=False),
            Crf(show_order=20, model="visit_schedule_app.CrfTwo"),
            Crf(show_order=30, model="visit_schedule_app.CrfThree"),
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(fc_errors), 1)
        self.assertEqual("edc_visit_schedule.E006", fc_errors[0].id)
        self.assertIn(
            "Proxy root model class appears alongside associated child proxy for a visit.",
            fc_errors[0].msg,
        )
        self.assertIn("proxy_root_model=visit_schedule_app.crfone", fc_errors[0].msg)
        self.assertIn("proxy_model=visit_schedule_app.crfoneproxyone", fc_errors[0].msg)

    def test_required_proxy_root_crf_with_child_proxy_prn_raises(self):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(show_order=10, model="visit_schedule_app.CrfOne", required=True),
            Crf(show_order=20, model="visit_schedule_app.CrfTwo"),
        )
        prns = CrfCollection(
            Crf(show_order=15, model="visit_schedule_app.CrfOneProxyOne"),
            Crf(show_order=25, model="visit_schedule_app.PrnOne"),
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(fc_errors), 1)
        self.assertEqual("edc_visit_schedule.E006", fc_errors[0].id)
        self.assertIn(
            "Proxy root model class appears alongside associated child proxy for a visit.",
            fc_errors[0].msg,
        )
        self.assertIn("proxy_root_model=visit_schedule_app.crfone", fc_errors[0].msg)
        self.assertIn("proxy_model=visit_schedule_app.crfoneproxyone", fc_errors[0].msg)

    def test_required_proxy_child_crf_with_proxy_root_prn_raises(self):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(show_order=10, model="visit_schedule_app.CrfOneProxyOne", required=True),
            Crf(show_order=20, model="visit_schedule_app.CrfTwo"),
        )
        prns = CrfCollection(
            Crf(show_order=15, model="visit_schedule_app.CrfOne"),
            Crf(show_order=25, model="visit_schedule_app.PrnOne"),
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(fc_errors), 1)
        self.assertEqual("edc_visit_schedule.E006", fc_errors[0].id)
        self.assertIn(
            "Proxy root model class appears alongside associated child proxy for a visit.",
            fc_errors[0].msg,
        )
        self.assertIn("proxy_root_model=visit_schedule_app.crfone", fc_errors[0].msg)
        self.assertIn("proxy_model=visit_schedule_app.crfoneproxyone", fc_errors[0].msg)

    def test_not_required_crf_also_in_prns_ok(self):
        """e.g. CRF not required (toggled by metadata rule) but
        also available as optional PRN.
        """
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(show_order=10, model="visit_schedule_app.CrfOne", required=False),
            Crf(show_order=20, model="visit_schedule_app.CrfTwo"),
        )
        prns = CrfCollection(
            Crf(show_order=15, model="visit_schedule_app.CrfOne"),
            Crf(show_order=25, model="visit_schedule_app.PrnOne"),
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertListEqual(fc_errors, [])

    def test_not_required_proxy_crf_with_shared_proxy_root_also_in_prns_ok(self):
        """e.g. Proxy CRF not required (toggled by metadata rule) but
        also available as optional PRN.
        """
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(
                show_order=10,
                model="visit_schedule_app.CrfOneProxyOne",
                required=False,
                shares_proxy_root=True,
            ),
            Crf(show_order=20, model="visit_schedule_app.CrfTwo"),
        )
        prns = CrfCollection(
            Crf(
                show_order=15,
                model="visit_schedule_app.CrfOneProxyOne",
                shares_proxy_root=True,
            ),
            Crf(show_order=25, model="visit_schedule_app.PrnOne"),
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertListEqual(fc_errors, [])

    def test_three_crf_proxy_with_shares_root_ok(self):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(
                show_order=10,
                model="visit_schedule_app.CrfOneProxyOne",
                shares_proxy_root=True,
            ),
            Crf(
                show_order=20,
                model="visit_schedule_app.CrfOneProxyTwo",
                shares_proxy_root=True,
            ),
            Crf(
                show_order=30,
                model="visit_schedule_app.CrfOneProxyThree",
                shares_proxy_root=True,
            ),
        )
        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertListEqual(fc_errors, [])

    def test_crf_and_prn_proxies_with_shared_root_ok(self):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(
                show_order=10,
                model="visit_schedule_app.CrfOneProxyOne",
                required=False,
                shares_proxy_root=True,
            ),
            Crf(
                show_order=20,
                model="visit_schedule_app.CrfOneProxyTwo",
                required=False,
                shares_proxy_root=True,
            ),
        )
        prns = CrfCollection(
            Crf(
                show_order=35,
                model="visit_schedule_app.CrfOneProxyThree",
                shares_proxy_root=True,
            ),
            Crf(show_order=25, model="visit_schedule_app.PrnOne"),
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertListEqual(fc_errors, [])

    def test_one_crf_proxy_shares_root_true_with_one_proxy_not_defined_raises(self):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(
                show_order=10,
                model="visit_schedule_app.CrfOneProxyOne",
                shares_proxy_root=True,
            ),
        )
        prns = CrfCollection(
            Crf(show_order=35, model="visit_schedule_app.CrfOneProxyThree"),
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(fc_errors), 1)
        self.assertEqual("edc_visit_schedule.E007", fc_errors[0].id)
        self.assertIn(
            "Multiple proxies with same proxy root model appear for a visit.",
            fc_errors[0].msg,
        )
        self.assertIn(
            str(
                {
                    "visit_schedule_app.crfone": [
                        "visit_schedule_app.crfoneproxyone",
                        "visit_schedule_app.crfoneproxythree",
                    ]
                }
            ),
            fc_errors[0].msg,
        )

    def test_two_crf_proxy_shares_root_true_with_one_proxy_not_defined_raises(self):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(
                show_order=10,
                model="visit_schedule_app.CrfOneProxyOne",
                shares_proxy_root=True,
            ),
            Crf(
                show_order=20,
                model="visit_schedule_app.CrfOneProxyTwo",
            ),
        )
        prns = CrfCollection(
            Crf(
                show_order=35,
                model="visit_schedule_app.CrfOneProxyThree",
                shares_proxy_root=True,
            ),
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(fc_errors), 1)
        self.assertEqual("edc_visit_schedule.E007", fc_errors[0].id)
        self.assertIn(
            "Multiple proxies with same proxy root model appear for a visit.",
            fc_errors[0].msg,
        )
        self.assertIn(
            str(
                {
                    "visit_schedule_app.crfone": [
                        "visit_schedule_app.crfoneproxyone",
                        "visit_schedule_app.crfoneproxythree",
                        "visit_schedule_app.crfoneproxytwo",
                    ]
                }
            ),
            fc_errors[0].msg,
        )

    def test_one_crf_proxy_shares_root_true_with_two_proxy_not_defined_raises(self):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(show_order=10, model="visit_schedule_app.CrfOneProxyOne"),
            Crf(show_order=20, model="visit_schedule_app.CrfOneProxyTwo"),
        )
        prns = CrfCollection(
            Crf(
                show_order=35,
                model="visit_schedule_app.CrfOneProxyThree",
                shares_proxy_root=True,
            ),
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(fc_errors), 1)
        self.assertEqual("edc_visit_schedule.E007", fc_errors[0].id)
        self.assertIn(
            "Multiple proxies with same proxy root model appear for a visit.",
            fc_errors[0].msg,
        )
        self.assertIn(
            str(
                {
                    "visit_schedule_app.crfone": [
                        "visit_schedule_app.crfoneproxyone",
                        "visit_schedule_app.crfoneproxythree",
                        "visit_schedule_app.crfoneproxytwo",
                    ]
                }
            ),
            fc_errors[0].msg,
        )

    def test_proxy_roots_shared_but_not_defined_raises(self):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(show_order=10, model="visit_schedule_app.CrfOneProxyOne"),
            Crf(show_order=12, model="visit_schedule_app.CrfOneProxyTwo"),
            Crf(show_order=20, model="visit_schedule_app.CrfTwoProxyOne"),
        )
        prns = CrfCollection(
            Crf(show_order=15, model="visit_schedule_app.CrfOneProxyOne"),
            Crf(show_order=25, model="visit_schedule_app.CrfTwoProxyTwo"),
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(fc_errors), 1)
        self.assertEqual("edc_visit_schedule.E007", fc_errors[0].id)
        self.assertIn(
            str(
                {
                    "visit_schedule_app.crfone": [
                        "visit_schedule_app.crfoneproxyone",
                        "visit_schedule_app.crfoneproxyone",
                        "visit_schedule_app.crfoneproxytwo",
                    ],
                    "visit_schedule_app.crftwo": [
                        "visit_schedule_app.crftwoproxyone",
                        "visit_schedule_app.crftwoproxytwo",
                    ],
                }
            ),
            fc_errors[0].msg,
        )

    def test_proxy_roots_shared_but_not_defined_case2(self):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(show_order=10, model="visit_schedule_app.CrfOneProxyOne"),
            Crf(show_order=12, model="visit_schedule_app.CrfOneProxyTwo"),
            Crf(show_order=20, model="visit_schedule_app.CrfTwoProxyOne"),
        )
        prns = CrfCollection(
            Crf(show_order=15, model="visit_schedule_app.CrfOneProxyOne"),
            Crf(show_order=25, model="visit_schedule_app.CrfTwoProxyOne"),
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(fc_errors), 1)
        self.assertEqual("edc_visit_schedule.E007", fc_errors[0].id)
        self.assertIn(
            str(
                {
                    "visit_schedule_app.crfone": [
                        "visit_schedule_app.crfoneproxyone",
                        "visit_schedule_app.crfoneproxyone",
                        "visit_schedule_app.crfoneproxytwo",
                    ]
                }
            ),
            fc_errors[0].msg,
        )

    def test_proxy_pair_plus_another_proxy_with_same_parent_raises(self):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(show_order=10, model="visit_schedule_app.CrfOneProxyOne"),
            Crf(show_order=25, model="visit_schedule_app.CrfOneProxyTwo"),
        )
        prns = CrfCollection(Crf(show_order=15, model="visit_schedule_app.CrfOneProxyOne"))

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(fc_errors), 1)
        self.assertEqual("edc_visit_schedule.E007", fc_errors[0].id)
        self.assertIn(
            str(
                {
                    "visit_schedule_app.crfone": [
                        "visit_schedule_app.crfoneproxyone",
                        "visit_schedule_app.crfoneproxyone",
                        "visit_schedule_app.crfoneproxytwo",
                    ]
                }
            ),
            fc_errors[0].msg,
        )

    def test_two_proxy_root_with_child_pairs_raises(self):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(show_order=10, model="visit_schedule_app.CrfOne"),
            Crf(show_order=20, model="visit_schedule_app.CrfTwoProxyOne"),
        )
        prns = CrfCollection(
            Crf(show_order=15, model="visit_schedule_app.CrfOneProxyOne"),
            Crf(show_order=25, model="visit_schedule_app.CrfTwo"),
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(fc_errors), 1)
        self.assertEqual("edc_visit_schedule.E006", fc_errors[0].id)
        self.assertIn("visit_schedule_app.crfone", fc_errors[0].msg)
        self.assertIn("visit_schedule_app.crftwo", fc_errors[0].msg)
        self.assertIn("visit_schedule_app.crfoneproxyone", fc_errors[0].msg)
        self.assertIn("visit_schedule_app.crftwoproxyone", fc_errors[0].msg)

    def test_two_shared_proxy_root_pairs_raises(self):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(show_order=10, model="visit_schedule_app.CrfOneProxyOne"),
            Crf(show_order=20, model="visit_schedule_app.CrfTwoProxyOne"),
        )
        prns = CrfCollection(
            Crf(show_order=15, model="visit_schedule_app.CrfOneProxyTwo"),
            Crf(show_order=25, model="visit_schedule_app.CrfTwoProxyTwo"),
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(fc_errors), 1)
        self.assertEqual("edc_visit_schedule.E007", fc_errors[0].id)
        self.assertIn(
            str(
                {
                    "visit_schedule_app.crfone": [
                        "visit_schedule_app.crfoneproxyone",
                        "visit_schedule_app.crfoneproxytwo",
                    ],
                    "visit_schedule_app.crftwo": [
                        "visit_schedule_app.crftwoproxyone",
                        "visit_schedule_app.crftwoproxytwo",
                    ],
                }
            ),
            fc_errors[0].msg,
        )

    def test_unscheduled_visit_required_crf_in_prns_ok(self):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs_unscheduled = CrfCollection(
            Crf(show_order=10, model="visit_schedule_app.CrfOne", required=True),
            Crf(show_order=20, model="visit_schedule_app.CrfTwo"),
            Crf(show_order=30, model="visit_schedule_app.CrfThree"),
        )
        prns = CrfCollection(
            Crf(show_order=15, model="visit_schedule_app.CrfOne"),
            Crf(show_order=25, model="visit_schedule_app.PrnOne"),
            Crf(show_order=35, model="visit_schedule_app.PrnTwo"),
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs_unscheduled=crfs_unscheduled,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertListEqual(fc_errors, [])

    def test_unscheduled_visit_required_proxy_root_crf_with_child_proxy_prn_raises(self):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs_unscheduled = CrfCollection(
            Crf(show_order=10, model="visit_schedule_app.CrfOne", required=True),
            Crf(show_order=20, model="visit_schedule_app.CrfTwo"),
        )
        prns = CrfCollection(
            Crf(show_order=15, model="visit_schedule_app.CrfOneProxyOne"),
            Crf(show_order=25, model="visit_schedule_app.PrnOne"),
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs_unscheduled=crfs_unscheduled,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(fc_errors), 1)
        self.assertEqual("edc_visit_schedule.E006", fc_errors[0].id)
        self.assertIn(
            "Proxy root model class appears alongside associated child proxy for a visit.",
            fc_errors[0].msg,
        )
        self.assertIn("proxy_root_model=visit_schedule_app.crfone", fc_errors[0].msg)
        self.assertIn("proxy_model=visit_schedule_app.crfoneproxyone", fc_errors[0].msg)

    def test_unscheduled_visit_crf_proxy_shares_root_true_with_proxy_not_defined_raises(
        self,
    ):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs_unscheduled = CrfCollection(
            Crf(
                show_order=10,
                model="visit_schedule_app.CrfOneProxyOne",
                shares_proxy_root=True,
            ),
        )
        prns = CrfCollection(
            Crf(show_order=35, model="visit_schedule_app.CrfOneProxyThree"),
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs_unscheduled=crfs_unscheduled,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(fc_errors), 1)
        self.assertEqual("edc_visit_schedule.E007", fc_errors[0].id)
        self.assertIn(
            str(
                {
                    "visit_schedule_app.crfone": [
                        "visit_schedule_app.crfoneproxyone",
                        "visit_schedule_app.crfoneproxythree",
                    ]
                }
            ),
            fc_errors[0].msg,
        )

    def test_missed_visit_required_crf_in_prns_ok(self):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs_missed = CrfCollection(
            Crf(show_order=10, model="visit_schedule_app.CrfOne", required=True),
            Crf(show_order=20, model="visit_schedule_app.CrfTwo"),
            Crf(show_order=30, model="visit_schedule_app.CrfThree"),
        )
        prns = CrfCollection(
            Crf(show_order=15, model="visit_schedule_app.CrfOne"),
            Crf(show_order=25, model="visit_schedule_app.PrnOne"),
            Crf(show_order=35, model="visit_schedule_app.PrnTwo"),
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs_missed=crfs_missed,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertListEqual(fc_errors, [])

    def test_missed_visit_required_proxy_root_crf_with_required_child_proxy_crf_raises(
        self,
    ):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs_missed = CrfCollection(
            Crf(show_order=10, model="visit_schedule_app.CrfOne", required=True),
            Crf(show_order=15, model="visit_schedule_app.CrfOneProxyOne", required=True),
            Crf(show_order=20, model="visit_schedule_app.CrfTwo"),
            Crf(show_order=30, model="visit_schedule_app.CrfThree"),
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs_missed=crfs_missed,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(fc_errors), 1)
        self.assertEqual("edc_visit_schedule.E006", fc_errors[0].id)
        self.assertIn("proxy_root_model=visit_schedule_app.crfone", fc_errors[0].msg)
        self.assertIn("proxy_model=visit_schedule_app.crfoneproxyone", fc_errors[0].msg)

    def test_missed_visit_crf_proxy_shares_root_true_with_proxy_not_defined_raises(
        self,
    ):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs_missed = CrfCollection(
            Crf(
                show_order=10,
                model="visit_schedule_app.CrfOneProxyOne",
                shares_proxy_root=True,
            )
        )
        prns = CrfCollection(Crf(show_order=35, model="visit_schedule_app.CrfOneProxyThree"))

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs_missed=crfs_missed,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(fc_errors), 1)
        self.assertEqual("edc_visit_schedule.E007", fc_errors[0].id)
        self.assertIn(
            str(
                {
                    "visit_schedule_app.crfone": [
                        "visit_schedule_app.crfoneproxyone",
                        "visit_schedule_app.crfoneproxythree",
                    ]
                }
            ),
            fc_errors[0].msg,
        )

    def test_proxy_model_crf_with_identical_proxy_model_in_prns_ok(self):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(Crf(show_order=10, model="visit_schedule_app.CrfOneProxyOne"))
        prns = CrfCollection(Crf(show_order=15, model="visit_schedule_app.CrfOneProxyOne"))

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertListEqual(fc_errors, [])

    def test_proxy_shares_root_true_crf_with_identical_proxy_not_sharing_root_in_prns_ok(
        self,
    ):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(
                show_order=10,
                model="visit_schedule_app.CrfOneProxyOne",
                shares_proxy_root=True,
            )
        )
        prns = CrfCollection(Crf(show_order=15, model="visit_schedule_app.CrfOneProxyOne"))

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertListEqual(fc_errors, [])

    def test_proxy_crf_not_sharing_root_with_identical_proxy_shares_root_true_in_prns_ok(
        self,
    ):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(Crf(show_order=10, model="visit_schedule_app.CrfOneProxyOne"))
        prns = CrfCollection(
            Crf(
                show_order=15,
                model="visit_schedule_app.CrfOneProxyOne",
                shares_proxy_root=True,
            )
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertListEqual(fc_errors, [])

    def test_one_crf_proxy_shares_root_true_with_another_proxy_prn_not_defined_raises(
        self,
    ):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(
                show_order=10,
                model="visit_schedule_app.CrfOneProxyOne",
                shares_proxy_root=True,
            )
        )
        prns = CrfCollection(
            Crf(
                show_order=10,
                model="visit_schedule_app.CrfOneProxyOne",
                shares_proxy_root=True,
            ),
            Crf(show_order=35, model="visit_schedule_app.CrfOneProxyThree"),
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(fc_errors), 3)
        self.assertEqual("edc_visit_schedule.E007", fc_errors[0].id)
        self.assertIn(
            str(
                {
                    "visit_schedule_app.crfone": [
                        "visit_schedule_app.crfoneproxyone",
                        "visit_schedule_app.crfoneproxyone",
                        "visit_schedule_app.crfoneproxythree",
                    ]
                }
            ),
            fc_errors[0].msg,
        )
        self.assertIn(
            str(
                {
                    "visit_schedule_app.crfone": [
                        "visit_schedule_app.crfoneproxyone",
                        "visit_schedule_app.crfoneproxythree",
                    ]
                }
            ),
            fc_errors[1].msg,
        )
        self.assertIn(
            str(
                {
                    "visit_schedule_app.crfone": [
                        "visit_schedule_app.crfoneproxyone",
                        "visit_schedule_app.crfoneproxythree",
                    ]
                }
            ),
            fc_errors[2].msg,
        )

    def test_multiple_proxy_crfs_prns_some_shared_some_not_raises(
        self,
    ):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(
                show_order=10,
                model="visit_schedule_app.CrfOneProxyOne",
                shares_proxy_root=True,
            ),
            Crf(
                show_order=35,
                model="visit_schedule_app.CrfOneProxyThree",
            ),
        )
        prns = CrfCollection(
            Crf(
                show_order=10,
                model="visit_schedule_app.CrfOneProxyOne",
            ),
            Crf(
                show_order=35,
                model="visit_schedule_app.CrfOneProxyThree",
                shares_proxy_root=True,
            ),
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        # self.assertEqual(len(fc_errors), 3)
        self.assertEqual("edc_visit_schedule.E007", fc_errors[0].id)
        self.assertIn(
            str(
                {
                    "visit_schedule_app.crfone": [
                        "visit_schedule_app.crfoneproxyone",
                        "visit_schedule_app.crfoneproxyone",
                        "visit_schedule_app.crfoneproxythree",
                        "visit_schedule_app.crfoneproxythree",
                    ]
                }
            ),
            fc_errors[0].msg,
        )
        self.assertIn(
            str(
                {
                    "visit_schedule_app.crfone": [
                        "visit_schedule_app.crfoneproxyone",
                        "visit_schedule_app.crfoneproxythree",
                    ]
                }
            ),
            fc_errors[1].msg,
        )
        self.assertIn(
            str(
                {
                    "visit_schedule_app.crfone": [
                        "visit_schedule_app.crfoneproxyone",
                        "visit_schedule_app.crfoneproxythree",
                    ]
                }
            ),
            fc_errors[2].msg,
        )

    def test_multiple_proxy_crfs_shares_proxy_true_with_proxy_prns_not_defined_raises(
        self,
    ):
        site_visit_schedules._registry = {}
        visit_schedule = self.visit_schedule
        schedule = self.schedule
        crfs = CrfCollection(
            Crf(
                show_order=10,
                model="visit_schedule_app.CrfOneProxyOne",
                shares_proxy_root=True,
            ),
            Crf(
                show_order=35,
                model="visit_schedule_app.CrfOneProxyThree",
                shares_proxy_root=True,
            ),
        )
        prns = CrfCollection(
            Crf(
                show_order=10,
                model="visit_schedule_app.CrfOneProxyOne",
            ),
            Crf(
                show_order=35,
                model="visit_schedule_app.CrfOneProxyThree",
            ),
        )

        visit = Visit(
            code="1000",
            rbase=relativedelta(days=0),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            facility_name="default",
            crfs=crfs,
            crfs_prn=prns,
            timepoint=1,
        )
        schedule.add_visit(visit)
        visit_schedule.add_schedule(schedule)
        site_visit_schedules.register(visit_schedule)

        vs_errors = visit_schedule_check(app_configs=django_apps.get_app_configs())
        self.assertListEqual(vs_errors, [])

        fc_errors = check_form_collections(app_configs=django_apps.get_app_configs())
        self.assertEqual(len(fc_errors), 3)
        self.assertEqual("edc_visit_schedule.E007", fc_errors[0].id)
        self.assertIn(
            str(
                {
                    "visit_schedule_app.crfone": [
                        "visit_schedule_app.crfoneproxyone",
                        "visit_schedule_app.crfoneproxyone",
                        "visit_schedule_app.crfoneproxythree",
                        "visit_schedule_app.crfoneproxythree",
                    ]
                }
            ),
            fc_errors[0].msg,
        )
        self.assertIn(
            str(
                {
                    "visit_schedule_app.crfone": [
                        "visit_schedule_app.crfoneproxyone",
                        "visit_schedule_app.crfoneproxythree",
                    ]
                }
            ),
            fc_errors[1].msg,
        )
        self.assertIn(
            str(
                {
                    "visit_schedule_app.crfone": [
                        "visit_schedule_app.crfoneproxyone",
                        "visit_schedule_app.crfoneproxythree",
                    ]
                }
            ),
            fc_errors[2].msg,
        )

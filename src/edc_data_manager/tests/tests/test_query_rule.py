# from django_webtest import WebTest
from data_manager_app.lab_profiles import lab_profile
from data_manager_app.models import Appointment, SubjectVisit, SubjectConsent, CrfOne
from data_manager_app.visit_schedules import visit_schedule
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import tag  # noqa
from edc_constants.constants import OPEN
from edc_data_manager.models import (
    CrfDataDictionary,
    DataQuery,
    QueryRule,
    QueryVisitSchedule,
)
from edc_data_manager.rule import RuleRunner
from edc_facility.import_holidays import import_holidays
from edc_lab.site_labs import site_labs
from edc_metadata.metadata_inspector import MetaDataInspector
from edc_reference.site_reference import site_reference_configs
from edc_utils.date import get_utcnow
from edc_visit_schedule.apps import populate_visit_schedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED
from edc_visit_schedule.constants import HOURS


User = get_user_model()


class TestQueryRules(TestCase):
    def setUp(self):
        import_holidays()
        self.user = User.objects.create_superuser("user_login", "u@example.com", "pass")

        site_labs._registry = {}
        site_labs.loaded = False
        site_labs.register(lab_profile=lab_profile)

        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)

        populate_visit_schedule()

        site_reference_configs.register_from_visit_schedule(
            visit_models={
                "edc_appointment.appointment": "data_manager_app.subjectvisit"
            }
        )

        self.subject_identifier = "092-40990029-4"
        identity = "123456789"
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow() - relativedelta(days=10),
            identity=identity,
            confirm_identity=identity,
            dob=get_utcnow() - relativedelta(years=25),
        )

        # put subject on schedule
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            "data_manager_app.onschedule"
        )
        schedule.put_on_schedule(
            subject_identifier=subject_consent.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )

    def create_subject_visit(self, visit_code, report_datetime=None):
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_schedule_name="visit_schedule",
            schedule_name="schedule",
            visit_code=visit_code,
        )
        return SubjectVisit.objects.create(
            appointment=appointment,
            report_datetime=report_datetime or appointment.appt_datetime,
            subject_identifier=self.subject_identifier,
            reason=SCHEDULED,
            user_created="user_login",
        )

    def test_data_inspector(self):

        for schedule in visit_schedule.schedules.values():
            for visit in schedule.visits.values():
                self.create_subject_visit(visit.code)

        visit_schedule1 = QueryVisitSchedule.objects.get(visit_code="1000")
        visit_schedule2 = QueryVisitSchedule.objects.get(visit_code="2000")
        visit_schedule3 = QueryVisitSchedule.objects.get(visit_code="3000")

        inspector = MetaDataInspector(
            model_cls=CrfOne,
            visit_schedule_name=visit_schedule1.visit_schedule_name,
            schedule_name=visit_schedule1.schedule_name,
            visit_code=visit_schedule1.visit_code,
            timepoint=visit_schedule1.timepoint,
        )
        self.assertEqual(len(inspector.required), 1)
        self.assertEqual(len(inspector.keyed), 0)

        subject_visit1 = SubjectVisit.objects.get(visit_code=visit_schedule1.visit_code)
        CrfOne.objects.create(
            subject_visit=subject_visit1, report_datetime=subject_visit1.report_datetime
        )

        inspector = MetaDataInspector(
            model_cls=CrfOne,
            visit_schedule_name=visit_schedule1.visit_schedule_name,
            schedule_name=visit_schedule1.schedule_name,
            visit_code=visit_schedule1.visit_code,
            timepoint=visit_schedule1.timepoint,
        )
        self.assertEqual(len(inspector.required), 0)
        self.assertEqual(len(inspector.keyed), 1)

        inspector = MetaDataInspector(
            model_cls=CrfOne,
            visit_schedule_name=visit_schedule2.visit_schedule_name,
            schedule_name=visit_schedule2.schedule_name,
            visit_code=visit_schedule2.visit_code,
            timepoint=visit_schedule2.timepoint,
        )
        self.assertEqual(len(inspector.required), 1)
        self.assertEqual(len(inspector.keyed), 0)

        inspector = MetaDataInspector(
            model_cls=CrfOne,
            visit_schedule_name=visit_schedule3.visit_schedule_name,
            schedule_name=visit_schedule3.schedule_name,
            visit_code=visit_schedule3.visit_code,
            timepoint=visit_schedule3.timepoint,
        )
        # not required in 3000, see visit schedule.
        self.assertEqual(len(inspector.required), 0)
        self.assertEqual(len(inspector.keyed), 0)

    def test_crf_rule(self):

        question = CrfDataDictionary.objects.get(
            model="data_manager_app.crfone", field_name="f1"
        )
        visit_schedule1 = QueryVisitSchedule.objects.get(visit_code="1000")
        visit_schedule2 = QueryVisitSchedule.objects.get(visit_code="2000")

        opts = dict(title="test rule", sender=self.user, timing=48, timing_units=HOURS)

        query_rule = QueryRule.objects.create(**opts)
        query_rule.data_dictionaries.add(question)
        query_rule.visit_schedule.add(visit_schedule1)
        query_rule.visit_schedule.add(visit_schedule2)
        query_rule.save()

        # Update DataQueries
        RuleRunner(query_rule).run()

        # assert DataQueries NOT created since no visit reports submitted yet
        self.assertEqual(
            DataQuery.objects.filter(
                rule_generated=True, rule_reference=query_rule.reference
            ).count(),
            0,
        )

        # create visit report
        appointment = Appointment.objects.get(visit_code="1000")
        subject_visit_1000 = self.create_subject_visit(
            "1000", report_datetime=appointment.appt_datetime
        )

        # CRF not keyed => query IMMEDIATELY
        DataQuery.objects.all().delete()
        RuleRunner(query_rule, now=appointment.appt_datetime).run()
        self.assertEqual(
            DataQuery.objects.filter(
                rule_generated=True, rule_reference=query_rule.reference
            ).count(),
            1,
        )

        # create the CRF, field value missing => query when DUE.
        crf_one = CrfOne.objects.create(
            subject_visit=subject_visit_1000,
            report_datetime=subject_visit_1000.report_datetime,
            f1=None,
        )

        for hours in range(-1, 50):
            DataQuery.objects.all().delete()

            RuleRunner(
                query_rule, now=appointment.appt_datetime + relativedelta(hours=hours)
            ).run()

            if hours <= 48:
                # assert CRF not due from 0 to 48 hrs
                self.assertEqual(
                    DataQuery.objects.filter(
                        rule_generated=True, rule_reference=query_rule.reference
                    ).count(),
                    0,
                    msg=hours,
                )
            else:
                # CRF is now due, 48 hrs past
                self.assertEqual(
                    DataQuery.objects.filter(
                        rule_generated=True, rule_reference=query_rule.reference
                    ).count(),
                    1,
                    msg=hours,
                )

        # Update DataQueries
        RuleRunner(query_rule).run()

        # assert DataQuery NOT resolved, field f1 is still None
        self.assertEqual(
            DataQuery.objects.filter(
                rule_generated=True, rule_reference=query_rule.reference, status=OPEN
            ).count(),
            1,
        )

        crf_one.f1 = "erik"
        crf_one.save()

        # Update DataQueries
        RuleRunner(query_rule).run()

        # assert 1 DataQuery changed to resolved
        self.assertEqual(
            DataQuery.objects.filter(
                rule_generated=True, rule_reference=query_rule.reference, status=OPEN
            ).count(),
            0,
        )

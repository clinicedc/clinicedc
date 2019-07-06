# from django_webtest import WebTest
from data_manager_app.lab_profiles import lab_profile
from data_manager_app.models import (
    Appointment,
    SubjectVisit,
    SubjectConsent,
    CrfOne,
    CrfFour,
    CrfSeven,
)
from data_manager_app.visit_schedules import visit_schedule
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import tag  # noqa
from edc_constants.constants import OPEN
from edc_data_manager.models import (
    CrfQueryRule,
    CrfDataDictionary,
    DataQuery,
    QueryVisitSchedule,
)
from edc_data_manager.rule import RuleRunner
from edc_facility.import_holidays import import_holidays
from edc_lab.site_labs import site_labs
from edc_reference.site_reference import site_reference_configs
from edc_utils.date import get_utcnow
from edc_visit_schedule.apps import populate_visit_schedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from ...rule import MetaDataInspector


User = get_user_model()


class TestQueryRules(TestCase):
    def setUp(self):
        import_holidays()
        self.user = User.objects.create_superuser(
            "user_login", "u@example.com", "pass")

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

        for schedule in visit_schedule.schedules.values():
            for visit in schedule.visits.values():
                appointment = Appointment.objects.get(
                    subject_identifier=self.subject_identifier,
                    visit_schedule_name="visit_schedule",
                    schedule_name="schedule",
                    visit_code=visit.code,
                )
                SubjectVisit.objects.create(
                    appointment=appointment,
                    report_datetime=appointment.appt_datetime,
                    subject_identifier=self.subject_identifier,
                    reason=SCHEDULED,
                    user_created="user_login",
                )

    @tag("1")
    def test_data_inspector(self):

        visit_schedule1 = QueryVisitSchedule.objects.get(visit_code="1000")
        visit_schedule2 = QueryVisitSchedule.objects.get(visit_code="2000")
        visit_schedule3 = QueryVisitSchedule.objects.get(visit_code="3000")

        inspector = MetaDataInspector(
            visit_schedule=visit_schedule1, model_cls=CrfOne)
        self.assertEqual(len(inspector.required), 1)
        self.assertEqual(len(inspector.keyed), 0)

        subject_visit1 = SubjectVisit.objects.get(
            visit_code=visit_schedule1.visit_code)
        CrfOne.objects.create(
            subject_visit=subject_visit1,
            report_datetime=subject_visit1.report_datetime)

        inspector = MetaDataInspector(
            visit_schedule=visit_schedule1, model_cls=CrfOne)
        self.assertEqual(len(inspector.required), 0)
        self.assertEqual(len(inspector.keyed), 1)

        inspector = MetaDataInspector(
            visit_schedule=visit_schedule2, model_cls=CrfFour)
        self.assertEqual(len(inspector.required), 1)
        self.assertEqual(len(inspector.keyed), 0)

        inspector = MetaDataInspector(
            visit_schedule=visit_schedule3, model_cls=CrfSeven
        )
        self.assertEqual(len(inspector.required), 1)
        self.assertEqual(len(inspector.keyed), 0)

    def test_crf_rule(self):

        question = CrfDataDictionary.objects.get(
            model="data_manager_app.crfone", field_name="f1"
        )
        visit_schedule1 = QueryVisitSchedule.objects.get(visit_code="1000")
        visit_schedule2 = QueryVisitSchedule.objects.get(visit_code="2000")

        opts = dict(title="test rule", sender=self.user)

        crf_query_rule = CrfQueryRule.objects.create(**opts)
        crf_query_rule.data_dictionaries.add(question)
        crf_query_rule.visit_schedule.add(visit_schedule1)
        crf_query_rule.visit_schedule.add(visit_schedule2)
        crf_query_rule.save()

        # Update DataQueries
        RuleRunner(crf_query_rule).run()

        # assert DataQueries created
        self.assertEqual(
            DataQuery.objects.filter(
                rule_generated=True, rule_reference=crf_query_rule.reference
            ).count(),
            2,
        )

        # create the expected CRF
        subject_visit = SubjectVisit.objects.all().order_by("appointment__visit_code")[
            0
        ]
        crf_one = CrfOne.objects.create(
            subject_visit=subject_visit,
            report_datetime=subject_visit.report_datetime)

        # Update DataQueries
        RuleRunner(crf_query_rule).run()

        # assert 1 DataQuery NOT changed to resolved, field f1 is still
        # None
        self.assertEqual(
            DataQuery.objects.filter(
                rule_generated=True,
                rule_reference=crf_query_rule.reference,
                status=OPEN,
            ).count(),
            2,
        )

        crf_one.f1 = "erik"
        crf_one.save()

        # Update DataQueries
        RuleRunner(crf_query_rule).run()

        # assert 1 DataQuery changed to resolved
        self.assertEqual(
            DataQuery.objects.filter(
                rule_generated=True,
                rule_reference=crf_query_rule.reference,
                status=OPEN,
            ).count(),
            1,
        )

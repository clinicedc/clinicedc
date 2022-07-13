from collections import OrderedDict
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from edc_appointment.constants import IN_PROGRESS_APPT, INCOMPLETE_APPT
from edc_appointment.models import Appointment
from edc_appointment.tests.appointment_test_case_mixin import AppointmentTestCaseMixin
from edc_constants.constants import FEMALE
from edc_facility import import_holidays
from edc_lab.models import Panel
from edc_reference import site_reference_configs
from edc_sites.tests import SiteTestCaseMixin
from edc_utils import get_utcnow
from edc_visit_schedule import site_visit_schedules
from edc_visit_schedule.constants import DAY1
from edc_visit_tracking.constants import SCHEDULED
from model_bakery import baker

from edc_metadata import site_metadata_rules
from edc_metadata.models import CrfMetadata, RequisitionMetadata

from .models import SubjectConsent, SubjectVisit
from .reference_configs import register_to_site_reference_configs


class EdcMetadataTestCaseMixin(AppointmentTestCaseMixin, SiteTestCaseMixin):

    visit_schedule = None
    consent_date_months_ago = 0

    @classmethod
    def setUpTestData(cls):
        import_holidays()

    def setUp(self):
        super().setUp()

        if self.visit_schedule:
            site_visit_schedules._registry = {}
            site_visit_schedules.loaded = False
            site_visit_schedules.register(self.visit_schedule)

        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "edc_metadata.subjectvisit"}
        )

        site_metadata_rules.registry = OrderedDict()
        for rule_cls in self.rule_groups:
            site_metadata_rules.register(rule_cls)

        self.user = User.objects.create(username="erik")

        for name in ["one", "two", "three", "four", "five", "six", "seven", "eight"]:
            Panel.objects.create(name=name)

        self.subject_identifier = "1111111"
        self.assertEqual(CrfMetadata.objects.all().count(), 0)
        self.assertEqual(RequisitionMetadata.objects.all().count(), 0)

        subject_consent = SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow() - relativedelta(months=self.consent_date_months_ago),
        )
        _, self.schedule = site_visit_schedules.get_by_onschedule_model(
            "edc_metadata.onschedule"
        )
        self.schedule.put_on_schedule(
            subject_identifier=self.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )
        self.appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code=self.schedule.visits.first.code,
        )
        self.subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            subject_identifier=self.subject_identifier,
            reason=SCHEDULED,
        )

    @property
    def rule_groups(self) -> list:
        return []

    @staticmethod
    def get_subject_consent(consent_datetime=None, site_id=None, gender=None, initials=None):
        return baker.make_recipe(
            "edc_metadata.tests.subjectconsent",
            user_created="erikvw",
            user_modified="erikvw",
            screening_identifier=uuid4(),
            initials=initials or "XX",
            gender=gender or FEMALE,
            dob=(get_utcnow().date() - relativedelta(years=25)),
            site=Site.objects.get(id=site_id or settings.SITE_ID),
            consent_datetime=consent_datetime,
        )

    def get_subject_visit(
        self,
        visit_code=None,
        visit_code_sequence=None,
        subject_consent=None,
        reason=None,
        appt_datetime=None,
        gender=None,
        initials=None,
    ):
        reason = reason or SCHEDULED
        subject_consent = subject_consent or self.get_subject_consent(
            gender=gender,
            initials=initials,
            consent_datetime=get_utcnow() - relativedelta(day=1),
        )
        options = dict(
            subject_identifier=subject_consent.subject_identifier,
            visit_code=visit_code or DAY1,
            visit_code_sequence=(
                visit_code_sequence if visit_code_sequence is not None else 0
            ),
            reason=reason,
        )
        if appt_datetime:
            options.update(appt_datetime=appt_datetime)
        appointment = self.get_appointment(**options)
        subject_visit = SubjectVisit(
            appointment=appointment,
            reason=SCHEDULED,
            report_datetime=appointment.appt_datetime,
        )
        subject_visit.save()
        subject_visit.refresh_from_db()
        return subject_visit

    @staticmethod
    def get_next_subject_visit(subject_visit):
        appointment = subject_visit.appointment
        appointment.appt_status = INCOMPLETE_APPT
        appointment.save()
        appointment.refresh_from_db()
        next_appointment = appointment.next_by_timepoint
        next_appointment.appt_status = IN_PROGRESS_APPT
        next_appointment.save()
        subject_visit = SubjectVisit(
            appointment=next_appointment,
            reason=SCHEDULED,
            report_datetime=next_appointment.appt_datetime,
            visit_code=next_appointment.visit_code,
            visit_code_sequence=next_appointment.visit_code_sequence,
        )
        subject_visit.save()
        subject_visit.refresh_from_db()
        return subject_visit

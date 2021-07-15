import string
from random import choices

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from edc_appointment.tests.appointment_test_case_mixin import AppointmentTestCaseMixin
from edc_constants.constants import MALE, NO, NOT_APPLICABLE, RANDOM_SAMPLING, YES
from edc_facility.import_holidays import import_holidays
from edc_form_validators import FormValidatorTestCaseMixin
from edc_metadata import REQUIRED
from edc_metadata.models import CrfMetadata
from edc_randomization.randomization_list_importer import RandomizationListImporter
from edc_sites import get_sites_by_country
from edc_sites.tests.site_test_case_mixin import SiteTestCaseMixin
from edc_utils.date import get_utcnow
from edc_visit_schedule.constants import DAY1
from edc_visit_tracking.constants import SCHEDULED, UNSCHEDULED
from model_bakery import baker

from ..constants import HIV_CLINIC
from .forms import SubjectScreeningForm
from .models import SubjectConsent, SubjectScreening, SubjectVisit


class TestCaseMixin(
    AppointmentTestCaseMixin, FormValidatorTestCaseMixin, SiteTestCaseMixin, TestCase
):

    default_sites = get_sites_by_country("uganda")

    site_names = [s.name for s in default_sites]

    import_randomization_list = True

    subject_visit_model_cls = SubjectVisit

    sid_count_for_tests = 1

    @classmethod
    def setUpTestData(cls):
        import_holidays(test=True)
        if cls.import_randomization_list:
            RandomizationListImporter(
                verbose=False,
                name="default",
                sid_count_for_tests=cls.sid_count_for_tests,
            )

    def setUp(self):
        self.user = User.objects.create_superuser("user_login", "u@example.com", "pass")

    def login(self, user=None, superuser=None, groups=None):
        user = self.user if user is None else user
        superuser = True if superuser is None else superuser
        if not superuser:
            user.is_superuser = False
            user.is_active = True
            user.save()
            for group_name in groups:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
        return self.client.force_login(user or self.user)

    def get_subject_screening(self, report_datetime=None, eligibility_datetime=None, **kwargs):
        data = {
            "screening_consent": YES,
            "age_in_years": 25,
            "clinic_type": HIV_CLINIC,
            "gender": MALE,
            "hospital_identifier": "13343322",
            "initials": "".join(choices(string.ascii_uppercase, k=2)),
            "lives_nearby": YES,
            "qualifying_condition": YES,
            "report_datetime": report_datetime or get_utcnow(),
            "requires_acute_care": NO,
            "selection_method": RANDOM_SAMPLING,
            "unsuitable_agreed": NOT_APPLICABLE,
            "unsuitable_for_study": NO,
        }
        data.update(**kwargs)
        form = SubjectScreeningForm(data=data, instance=None)
        form.save()

        subject_screening = SubjectScreening.objects.get(
            screening_identifier=form.instance.screening_identifier
        )

        self.assertTrue(subject_screening.eligible)

        if eligibility_datetime:
            subject_screening.eligibility_datetime = eligibility_datetime
            subject_screening.save()

        return subject_screening

    @staticmethod
    def get_subject_consent(subject_screening, consent_datetime=None, **kwargs):
        dob = (consent_datetime or get_utcnow()).date() - relativedelta(
            years=subject_screening.age_in_years
        )
        consent_datetime = consent_datetime or subject_screening.report_datetime

        options = dict(
            user_created="erikvw",
            user_modified="erikvw",
            screening_identifier=subject_screening.screening_identifier,
            initials=subject_screening.initials,
            dob=dob,
            site=Site.objects.get(id=settings.SITE_ID),
            clinic_type=HIV_CLINIC,
            consent_datetime=consent_datetime,
        )
        options.update(**kwargs)
        return baker.make_recipe("inte_consent.subjectconsent", **options)

    def get_subject_visit(
        self,
        visit_code=None,
        visit_code_sequence=None,
        subject_screening=None,
        subject_consent=None,
        reason=None,
        appointment=None,
        appt_datetime=None,
        report_datetime=None,
    ):
        reason = reason or SCHEDULED
        if not appointment:
            subject_screening = subject_screening or self.get_subject_screening()
            subject_consent = subject_consent or self.get_subject_consent(subject_screening)
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
        try:
            return self.subject_visit_model_cls.objects.get(appointment=appointment)
        except ObjectDoesNotExist:
            return self.subject_visit_model_cls.objects.create(
                appointment=appointment,
                reason=reason,
                report_datetime=report_datetime or appt_datetime or appointment.appt_datetime,
            )

    def get_next_subject_visit(
        self,
        subject_visit=None,
        reason=None,
        appt_datetime=None,
        report_datetime=None,
    ):
        visit_code = (
            subject_visit.appointment.visit_code
            if reason == UNSCHEDULED
            else subject_visit.appointment.next.visit_code
        )
        # visit_code_sequence will increment in get_subject_visit
        visit_code_sequence = (
            subject_visit.appointment.visit_code_sequence if reason == UNSCHEDULED else 0
        )
        return self.get_subject_visit(
            visit_code=visit_code,
            visit_code_sequence=visit_code_sequence,
            reason=reason,
            appt_datetime=appt_datetime,
            subject_screening=SubjectScreening.objects.get(
                subject_identifier=subject_visit.subject_identifier
            ),
            subject_consent=SubjectConsent.objects.get(
                subject_identifier=subject_visit.subject_identifier
            ),
            report_datetime=report_datetime,
        )

    @staticmethod
    def get_crf_metadata(subject_visit):
        return CrfMetadata.objects.filter(
            subject_identifier=subject_visit.subject_identifier,
            visit_code=subject_visit.visit_code,
            visit_code_sequence=subject_visit.visit_code_sequence,
            entry_status=REQUIRED,
        )

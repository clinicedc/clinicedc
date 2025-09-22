from random import shuffle
from tempfile import mkdtemp, mkstemp

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase
from django.test.utils import override_settings, tag
from multisite import SiteID

from edc_constants.constants import FEMALE
from edc_randomization.constants import ACTIVE, PLACEBO
from edc_randomization.decorators import RegisterRandomizerError, register
from edc_randomization.randomization_list_importer import (
    InvalidAssignment,
    RandomizationListAlreadyImported,
    RandomizationListImportError,
)
from edc_randomization.randomization_list_verifier import RandomizationListError
from edc_randomization.randomizer import (
    AllocationError,
    AlreadyRandomized,
    InvalidAssignmentDescriptionMap,
    RandomizationError,
    RandomizationListFileNotFound,
    Randomizer,
)
from edc_randomization.site_randomizers import NotRegistered, site_randomizers
from edc_randomization.utils import (
    RandomizationListExporterError,
    export_randomization_list,
    get_assignment_for_subject,
)
from edc_registration.models import RegisteredSubject
from edc_sites.site import sites as site_sites

from ..models import MyRandomizationList, SubjectConsent
from ..utils import (
    make_randomization_list_for_tests,
    populate_randomization_list_for_tests,
)

tmpdir = mkdtemp()


class MyRandomizer(Randomizer):
    name = "default"
    model = "edc_randomization.myrandomizationlist"
    randomizationlist_folder = tmpdir


@tag("randomization")
@override_settings(
    EDC_AUTH_SKIP_SITE_AUTHS=True,
    EDC_AUTH_SKIP_AUTH_UPDATER=True,
    SITE_ID=SiteID(40),
    EDC_SITES_REGISTER_DEFAULTS=False,
    EDC_RANDOMIZATION_REGISTER_DEFAULT_RANDOMIZER=False,
)
class TestRandomizer(TestCase):
    def setUp(self):
        site_randomizers._registry = {}
        site_randomizers.register(MyRandomizer)
        self.site_names = [s.name for s in site_sites._registry.values()]

    @staticmethod
    def populate_list(randomizer_name=None, per_site=None, overwrite_site=None):
        site_names = [s.name for s in site_sites._registry.values()]
        populate_randomization_list_for_tests(
            randomizer_name=randomizer_name,
            site_names=site_names,
            per_site=per_site,
            overwrite_site=overwrite_site,
        )

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_(self):
        self.populate_list(randomizer_name="default", overwrite_site=True)
        randomizer = site_randomizers.get("default")
        randomizer.import_list()

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_with_consent_insufficient_data(self):
        self.populate_list(randomizer_name="default", overwrite_site=True)
        randomizer = site_randomizers.get("default")
        randomizer.import_list()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", user_created="erikvw"
        )
        self.assertRaises(
            RandomizationError,
            MyRandomizer(
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=subject_consent.consent_datetime,
                site=subject_consent.site,
                user=None,
            ).randomize,
        )

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_with_consent(self):
        self.populate_list(randomizer_name="default", overwrite_site=True)
        randomizer = site_randomizers.get("default")
        randomizer.import_list()
        site = Site.objects.get_current()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", site=site, user_created="erikvw"
        )
        try:
            MyRandomizer(
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=subject_consent.consent_datetime,
                site=subject_consent.site,
                user=subject_consent.user_created,
            ).randomize()
        except Exception as e:
            self.fail(f"Exception unexpectedly raised. Got {e!s}.")

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_with_gender_and_consent(self):
        class RandomizerWithGender(MyRandomizer):
            def __init__(self, gender=None, **kwargs):
                self.gender = gender
                super().__init__(**kwargs)

            @property
            def extra_required_attrs(self):
                return dict(gender=self.gender)

        self.populate_list(randomizer_name="default", overwrite_site=True)
        randomizer = site_randomizers.get("default")
        randomizer.import_list()
        site = Site.objects.get_current()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", site=site, gender=FEMALE, user_created="erikvw"
        )
        try:
            RandomizerWithGender(
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=subject_consent.consent_datetime,
                site=subject_consent.site,
                gender=FEMALE,
                user=subject_consent.user_created,
            ).randomize()
        except Exception as e:
            self.fail(f"Exception unexpectedly raised. Got {e!s}.")

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_with_list_selects_first(self):
        self.populate_list(randomizer_name="default", overwrite_site=True)
        first_obj = MyRandomizationList.objects.all().order_by("sid").first()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", user_created="erikvw"
        )
        randomizer = MyRandomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_created,
        )
        randomizer.randomize()
        self.assertEqual(randomizer.sid, first_obj.sid)

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_updates_registered_subject1(self):
        self.populate_list(randomizer_name="default", overwrite_site=True)
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", user_created="erikvw"
        )
        MyRandomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_created,
        ).randomize()
        first_obj = MyRandomizationList.objects.all().order_by("sid").first()
        rs = RegisteredSubject.objects.get(subject_identifier="12345")
        self.assertEqual(rs.subject_identifier, first_obj.subject_identifier)
        self.assertEqual(rs.sid, str(first_obj.sid))
        self.assertEqual(rs.randomization_datetime, first_obj.allocated_datetime)
        self.assertEqual(rs.randomization_list_model, first_obj._meta.label_lower)

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_updates_list_obj_as_allocated(self):
        self.populate_list(randomizer_name="default", overwrite_site=True)
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", user_created="erikvw"
        )
        MyRandomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_created,
        ).randomize()
        first_obj = MyRandomizationList.objects.all().order_by("sid").first()
        self.assertEqual(first_obj.subject_identifier, "12345")
        self.assertTrue(first_obj.allocated)
        self.assertIsNotNone(first_obj.allocated_user)
        self.assertEqual(first_obj.allocated_user, subject_consent.user_created)
        self.assertEqual(first_obj.allocated_datetime, subject_consent.consent_datetime)
        self.assertGreater(first_obj.modified, subject_consent.created)

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_cannot_rerandomize(self):
        self.populate_list(randomizer_name="default", overwrite_site=True)
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", user_created="erikvw"
        )
        first_obj = MyRandomizationList.objects.all().order_by("sid").first()
        randomizer = MyRandomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_created,
        )
        randomizer.randomize()
        self.assertEqual(randomizer.sid, first_obj.sid)
        self.assertRaises(
            AlreadyRandomized,
            MyRandomizer(
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=subject_consent.consent_datetime,
                site=subject_consent.site,
                user=subject_consent.user_created,
            ).randomize,
        )

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_error_condition1(self):
        """Assert raises if RegisteredSubject not updated correctly."""
        self.populate_list(randomizer_name="default", overwrite_site=True)
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", user_created="erikvw"
        )
        randomizer = MyRandomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_created,
        )
        randomizer.randomize()
        randomizer.registration_obj.sid = ""
        randomizer.registration_obj.save()
        with self.assertRaises(AlreadyRandomized) as cm:
            MyRandomizer(
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=subject_consent.consent_datetime,
                site=subject_consent.site,
                user=subject_consent.user_created,
            ).randomize()
        self.assertEqual(cm.exception.code, "edc_randomization.myrandomizationlist")

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_error_condition2(self):
        """Assert raises if RandomizationList not updated correctly."""
        self.populate_list(randomizer_name="default", overwrite_site=True)
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", user_created="erikvw"
        )
        randomizer = MyRandomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_created,
        )
        randomizer.randomize()
        randomizer.registration_obj.sid = ""
        randomizer.registration_obj.save()
        with self.assertRaises(AlreadyRandomized) as cm:
            MyRandomizer(
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=subject_consent.consent_datetime,
                site=subject_consent.site,
                user=subject_consent.user_created,
            ).randomize()
        self.assertEqual(cm.exception.code, "edc_randomization.myrandomizationlist")

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_error_condition3(self):
        """Assert raises if RandomizationList not updated correctly."""
        self.populate_list(randomizer_name="default", overwrite_site=True)
        site = Site.objects.get_current()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", site=site, user_created="erikvw"
        )
        MyRandomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_created,
        ).randomize()
        MyRandomizationList.objects.update(subject_identifier=None)
        with self.assertRaises(AlreadyRandomized) as cm:
            MyRandomizer(
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=subject_consent.consent_datetime,
                site=subject_consent.site,
                user=subject_consent.user_created,
            ).randomize()
        self.assertEqual(cm.exception.code, "edc_registration.registeredsubject")

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_subject_does_not_exist(self):
        self.populate_list(randomizer_name="default", overwrite_site=True)
        site = Site.objects.get_current()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", site=site, user_created="erikvw"
        )
        RegisteredSubject.objects.all().delete()
        self.assertRaises(
            RandomizationError,
            MyRandomizer(
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=subject_consent.consent_datetime,
                site=subject_consent.site,
                user=subject_consent.user_modified,
            ).randomize,
        )

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_get_subject_assignment(self):
        self.populate_list(randomizer_name="default", overwrite_site=True)
        first_assignment = MyRandomizationList.objects.all().order_by("sid").first().assignment
        second_assignment = MyRandomizationList.objects.all().order_by("sid")[1].assignment
        site = Site.objects.get_current()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", site=site, user_created="erikvw"
        )
        MyRandomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_created,
        ).randomize()
        self.assertEqual(get_assignment_for_subject("12345", "default"), first_assignment)

        subject_consent = SubjectConsent.objects.create(
            subject_identifier="54321", site=site, user_created="erikvw"
        )
        MyRandomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_created,
        ).randomize()
        self.assertEqual(get_assignment_for_subject("54321", "default"), second_assignment)

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_valid_assignment_description_maps(self):
        self.populate_list(randomizer_name="default", overwrite_site=True)
        site = Site.objects.get_current()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", site=site, user_created="erikvw"
        )

        class ValidRandomizer(MyRandomizer):
            assignment_description_map = {ACTIVE: "blah", PLACEBO: "blahblah"}

        try:
            ValidRandomizer(
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=subject_consent.consent_datetime,
                site=subject_consent.site,
                user=subject_consent.user_created,
            )
        except InvalidAssignmentDescriptionMap as e:
            self.fail(f"InvalidAssignmentDescriptionMap unexpectedly raised. Got {e}")

        # Test still ok with dict items in opposite order
        class ValidRandomizerMapOrderDifferent(MyRandomizer):
            assignment_description_map = {PLACEBO: "blah", ACTIVE: "blahblah"}

        try:
            ValidRandomizerMapOrderDifferent(
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=subject_consent.consent_datetime,
                site=subject_consent.site,
                user=subject_consent.user_created,
            )
        except InvalidAssignmentDescriptionMap as e:
            self.fail(f"InvalidAssignmentDescriptionMap unexpectedly raised. Got {e}")

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_invalid_assignment_description_map(self):
        self.populate_list(randomizer_name="default", overwrite_site=True)
        site = Site.objects.get_current()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", site=site, user_created="erikvw"
        )

        class BadRandomizer(MyRandomizer):
            assignment_description_map = {"A": "blah", "B": "blahblah"}

        self.assertRaises(
            InvalidAssignmentDescriptionMap,
            BadRandomizer,
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_created,
        )

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_invalid_path(self):
        self.populate_list(randomizer_name="default", overwrite_site=True)
        site = Site.objects.get_current()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", site=site, user_created="erikvw"
        )

        class BadRandomizer(MyRandomizer):
            randomizationlist_folder = "bert"
            filename = "backarach.cvs"

        self.assertRaises(
            RandomizationListFileNotFound,
            BadRandomizer,
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_created,
        )

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_empty_csv_file(self):
        site = Site.objects.get_current()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", site=site, user_created="erikvw"
        )
        tmppath = mkstemp(suffix=".csv")

        class BadRandomizer(MyRandomizer):
            name = "bad_dog"
            randomizationlist_folder = "/".join(tmppath[1].split("/")[:-1])
            filename = tmppath[1].split("/")[-1:][0]

        site_randomizers.register(BadRandomizer)

        self.assertRaises(
            RandomizationListImportError,
            BadRandomizer,
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_created,
        )

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_wrong_csv_file(self):
        site = Site.objects.get_current()
        SubjectConsent.objects.create(
            subject_identifier="12345", site=site, user_created="erikvw"
        )
        tmppath = mkstemp(suffix=".csv", text=True)
        with open(tmppath[1], "w", encoding="utf8") as f:
            f.write("asdasd,sid,assignment,site_name,adasd,adasd\n")

        class BadRandomizer(MyRandomizer):
            name = "bad_bad_dog"
            randomizationlist_folder = "/".join(tmppath[1].split("/")[:-1])
            filename = tmppath[1].split("/")[-1:][0]

        site_randomizers.register(BadRandomizer)
        self.assertRaises(
            RandomizationListImportError, BadRandomizer.import_list, overwrite=True
        )

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_str(self):
        self.populate_list(randomizer_name="default", overwrite_site=True)
        site = Site.objects.get_current()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", site=site, user_created="erikvw"
        )
        MyRandomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_created,
        ).randomize()
        obj = MyRandomizationList.objects.all().order_by("sid").first()
        self.assertTrue(str(obj))

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_for_sites(self):
        """Assert that allocates by site correctly."""

        site_randomizers._registry = {}
        site_randomizers.register(MyRandomizer)

        model_cls = MyRandomizer.model_cls()
        model_cls.objects.all().delete()
        self.populate_list(randomizer_name=MyRandomizer.name, per_site=5)
        site_names = [obj.site_name for obj in model_cls.objects.all()]
        shuffle(site_names)
        self.assertEqual(len(site_names), len(self.site_names * 5))
        # consent and randomize 5 for each site
        for index, site_name in enumerate(site_names):
            site_obj = Site.objects.get(name=site_name)
            subject_consent = SubjectConsent.objects.create(
                subject_identifier=f"12345{index}", site=site_obj, user_created="erikvw"
            )
            MyRandomizer(
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=subject_consent.consent_datetime,
                site=subject_consent.site,
                user=subject_consent.user_created,
            ).randomize()
        # assert consented subjects were allocated SIDs in the
        # correct order per site.
        for site_name in site_names:
            randomized_subjects = [
                (obj.subject_identifier, str(obj.sid))
                for obj in model_cls.objects.filter(
                    allocated_site__name=site_name, subject_identifier__isnull=False
                ).order_by("sid")
            ]
            for index, obj in enumerate(
                SubjectConsent.objects.filter(site__name=site_name).order_by(
                    "consent_datetime"
                )
            ):
                rs = RegisteredSubject.objects.get(subject_identifier=obj.subject_identifier)
                self.assertEqual(obj.subject_identifier, randomized_subjects[index][0])
                self.assertEqual(rs.sid, randomized_subjects[index][1])

        # clear out any unallocated
        model_cls.objects.filter(subject_identifier__isnull=True).delete()

        # assert raises on next attempt to randomize
        site_obj = Site.objects.get_current()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="ABCDEF",
            site=site_obj,
            user_created="erikvw",
            user_modified="erikvw",
        )
        self.assertRaises(
            AllocationError,
            MyRandomizer(
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=subject_consent.consent_datetime,
                site=subject_consent.site,
                user=subject_consent.user_modified,
            ).randomize,
        )

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_not_loaded(self):
        randomizer_cls = site_randomizers.get("default")
        try:
            randomizer_cls.verify_list()
        except RandomizationListError as e:
            self.assertIn("Randomization list has not been loaded", str(e))
        else:
            self.fail("RandomizationListError unexpectedly NOT raised")

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_cannot_overwrite(self):
        site_randomizers._registry = {}
        site_randomizers.register(MyRandomizer)
        make_randomization_list_for_tests(
            full_path=MyRandomizer.get_randomizationlist_path(),
            site_names=self.site_names,
            count=5,
        )
        randomizer_cls = site_randomizers.get(MyRandomizer.name)
        randomizer_cls.import_list()
        importer = randomizer_cls.importer_cls(
            randomizer_model_cls=randomizer_cls.model_cls(),
            randomizer_name=randomizer_cls.name,
            randomizationlist_path=randomizer_cls.get_randomizationlist_path(),
            assignment_map=randomizer_cls.assignment_map,
        )
        self.assertRaises(RandomizationListAlreadyImported, importer.import_list)

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_can_overwrite_explicit(self):
        site_randomizers._registry = {}
        site_randomizers.register(MyRandomizer)
        make_randomization_list_for_tests(
            full_path=MyRandomizer.get_randomizationlist_path(),
            site_names=self.site_names,
            count=5,
        )
        randomizer_cls = site_randomizers.get(MyRandomizer.name)
        try:
            randomizer_cls.import_list(overwrite=True)
        except RandomizationListAlreadyImported:
            self.fail("RandomizationListImportError unexpectedly raised")

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_invalid_assignment(self):
        site_randomizers._registry = {}
        site_randomizers.register(MyRandomizer)

        MyRandomizer.get_randomizationlist_path()
        make_randomization_list_for_tests(
            full_path=MyRandomizer.get_randomizationlist_path(),
            site_names=self.site_names,
            # change to a different assignments
            assignments=[100, 101],
            count=5,
        )
        self.assertRaises(InvalidAssignment, MyRandomizer.import_list)

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_invalid_sid(self):
        self.populate_list(randomizer_name="default")
        # change to a different starting SID
        obj = MyRandomizationList.objects.all().order_by("sid").first()
        obj.sid = 99999
        obj.save()
        randomizer_cls = site_randomizers.get("default")

        with self.assertRaises(RandomizationListError) as cm:
            randomizer_cls.verify_list()
        self.assertIn("Randomization file has an invalid SID", str(cm.exception))

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_invalid_count(self):
        randomizer_cls = site_randomizers.get("default")
        site = Site.objects.get_current()
        # change number of SIDs in DB
        self.populate_list(randomizer_name="default")
        MyRandomizationList.objects.create(sid=100, assignment=ACTIVE, site_name=site.name)
        self.assertEqual(MyRandomizationList.objects.all().count(), 51)
        with self.assertRaises(RandomizationListError) as cm:
            randomizer_cls.verify_list()
        self.assertIn("Randomization list count is off", str(cm.exception))

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_get_randomizer_cls(self):
        site_randomizers._registry = {}
        self.assertRaises(NotRegistered, site_randomizers.get, MyRandomizer.name)
        site_randomizers.register(MyRandomizer)
        try:
            site_randomizers.get(MyRandomizer.name)
        except NotRegistered:
            self.fail("NotRegistered unexpectedly raised")

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_randomization_list_importer(self):
        randomizer_cls = site_randomizers.get("default")

        make_randomization_list_for_tests(
            full_path=randomizer_cls.get_randomizationlist_path(),
            site_names=self.site_names,
        )
        randomizer_cls.import_list()
        self.assertEqual(randomizer_cls.model_cls().objects.all().count(), 50)
        importer = randomizer_cls.importer_cls(
            randomizer_model_cls=randomizer_cls.model_cls(),
            randomizer_name=randomizer_cls.name,
            randomizationlist_path=randomizer_cls.get_randomizationlist_path(),
            assignment_map=randomizer_cls.assignment_map,
            verbose=True,
        )
        self.assertRaises(RandomizationListAlreadyImported, importer.import_list)
        self.assertEqual(randomizer_cls.model_cls().objects.all().count(), 50)

    @override_settings(EXPORT_FOLDER=tmpdir, ETC_DIR=tmpdir, DEBUG=False)
    def test_randomization_list_exporter(self):
        user = get_user_model().objects.create(
            username="me", is_superuser=False, is_staff=True
        )
        randomizer_cls = site_randomizers.get("default")
        make_randomization_list_for_tests(
            full_path=randomizer_cls.get_randomizationlist_path(),
            site_names=self.site_names,
        )
        randomizer_cls.import_list()
        self.assertRaises(RandomizationListExporterError, export_randomization_list, "default")
        self.assertRaises(
            RandomizationListExporterError,
            export_randomization_list,
            "default",
            username=user.username,
        )
        user = get_user_model().objects.create(
            username="you", is_superuser=True, is_staff=True
        )
        path = export_randomization_list("default", username=user.username)
        with open(path) as f:
            n = 0
            for line in f:
                n += 1
                if "str" in line:
                    break
        self.assertEqual(n, 51)

    @override_settings(ETC_DIR=tmpdir, DEBUG=False)
    def test_decorator(self):
        @register()
        class MeRandomizer(MyRandomizer):
            name = "me"

        self.assertEqual(site_randomizers.get("me"), MeRandomizer)

        try:

            @register()
            class NotARandomizer:
                name = "not_me"

        except RegisterRandomizerError:
            pass
        else:
            self.fail("RegisterRandomizerError not raised")

        self.assertRaises(NotRegistered, site_randomizers.get, "not_me")

from dateutil.relativedelta import relativedelta
from django import forms
from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.contrib.messages import get_messages
from django.contrib.sites.models import Site
from django.test import Client, RequestFactory, TestCase
from django.test.utils import override_settings
from edc_constants.constants import OTHER
from edc_utils import get_utcnow
from multisite import SiteID
from multisite.models import Alias

from edc_sites import (
    InvalidSiteError,
    get_all_sites,
    get_current_country,
    get_language_choices_for_site,
    get_site_id,
    get_sites_by_country,
)
from edc_sites.add_or_update_django_sites import add_or_update_django_sites
from edc_sites.forms import SiteModelFormMixin
from edc_sites.models import SiteProfile
from edc_sites.single_site import SingleSite, SiteLanguagesError
from edc_sites.sites import all_sites

from ...auths import codename
from ...permissions import has_permissions_for_extra_sites, site_ids_with_permissions
from ...permissions.site_ids_with_permissions import (
    InvalidSiteForUser,
    successmsg,
    warnmsg,
)
from ..models import TestModelWithSite
from ..site_test_case_mixin import SiteTestCaseMixin
from ..sites import all_test_sites


class TestForm(SiteModelFormMixin, forms.ModelForm):
    class Meta:
        model = TestModelWithSite
        fields = "__all__"


@override_settings(
    EDC_PROTOCOL_STUDY_OPEN_DATETIME=get_utcnow() - relativedelta(years=5),
    EDC_PROTOCOL_STUDY_CLOSE_DATETIME=get_utcnow() + relativedelta(years=1),
    EDC_AUTH_SKIP_SITE_AUTHS=True,
    EDC_AUTH_SKIP_AUTH_UPDATER=True,
)
class TestSites(SiteTestCaseMixin, TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = User.objects.create_superuser("user_login", "u@example.com", "pass")
        self.user.is_active = True
        self.user.is_staff = True
        self.user.save()
        self.user.refresh_from_db()

    @override_settings(SITE_ID=SiteID(default=20))
    def test_20(self):
        add_or_update_django_sites(sites=self.default_sites, verbose=False)
        obj = TestModelWithSite.objects.create()
        self.assertEqual(obj.site.pk, 20)
        self.assertEqual(obj.site.pk, Site.objects.get_current().pk)

    @override_settings(SITE_ID=SiteID(default=30))
    def test_30(self):
        add_or_update_django_sites(sites=self.default_sites, verbose=False)
        obj = TestModelWithSite.objects.create()
        self.assertEqual(obj.site.pk, 30)
        self.assertEqual(obj.site.pk, Site.objects.get_current().pk)

    @override_settings(SITE_ID=SiteID(default=30))
    def test_override_current(self):
        add_or_update_django_sites(sites=self.default_sites, verbose=False)
        site = Site.objects.get(pk=40)
        obj = TestModelWithSite.objects.create(site=site)
        self.assertEqual(obj.site.pk, 40)
        self.assertNotEqual(obj.site.pk, Site.objects.get_current().pk)

    @override_settings(LANGUAGES=[("en", "English"), ("sw", "Swahili"), ("tn", "Setswana")])
    def test_get_language_choices_for_site(self):
        add_or_update_django_sites(
            sites=[
                SingleSite(
                    99,
                    "amana",
                    title="Amana",
                    country="tanzania",
                    country_code="tz",
                    language_codes=["en", "sw"],
                    fqdn="clinicedc.org",
                )
            ],
            verbose=False,
        )
        site = Site.objects.get(pk=99)
        obj = TestModelWithSite.objects.create(site=site)
        self.assertEqual(obj.site.pk, 99)

        language_choices = get_language_choices_for_site(site)
        self.assertTupleEqual(language_choices, (("en", "English"), ("sw", "Swahili")))

        language_choices = get_language_choices_for_site(site, other=True)
        self.assertTupleEqual(
            language_choices,
            (("en", "English"), ("sw", "Swahili"), (OTHER, "Other")),
        )

    def test_get_site_id_by_name(self):
        add_or_update_django_sites(sites=self.default_sites)
        self.assertEqual(get_site_id("mochudi"), 10)

    def test_get_site_id_by_title(self):
        add_or_update_django_sites(sites=self.default_sites)
        self.assertEqual(get_site_id("Mochudi"), 10)

    def test_get_site_id_invalid(self):
        add_or_update_django_sites(sites=self.default_sites)
        self.assertRaises(InvalidSiteError, get_site_id, "blahblah")

    def test_get_site_id_without_sites(self):
        add_or_update_django_sites(sites=self.default_sites)
        self.assertEqual(get_site_id("mochudi"), 10)

    @override_settings(SITE_ID=SiteID(default=30))
    def test_site_profile(self):
        add_or_update_django_sites(sites=self.default_sites, verbose=False)
        obj = TestModelWithSite.objects.create()
        site_profile = SiteProfile.objects.get(site=obj.site)
        self.assertEqual(obj.site.siteprofile, site_profile)

    def test_updates_sites(self):
        add_or_update_django_sites(sites=self.default_sites)
        for site in self.default_sites:
            self.assertIn(site.site_id, [obj.id for obj in Site.objects.all()])
        self.assertNotIn("example.com", str([str(obj) for obj in Site.objects.all()]))
        self.assertEqual(len(self.default_sites), Site.objects.all().count())

    def test_domain(self):
        add_or_update_django_sites(sites=self.default_sites)
        obj = Site.objects.get(name="molepolole")
        self.assertEqual("molepolole.clinicedc.org", obj.domain)
        obj = Site.objects.get(name="mochudi")
        self.assertEqual("mochudi.bw.clinicedc.org", obj.domain)

    @override_settings(EDC_SITES_UAT_DOMAIN=True)
    def test_uat_domain(self):
        self.assertTrue(settings.EDC_SITES_UAT_DOMAIN)
        add_or_update_django_sites(sites=self.default_sites)
        obj = Site.objects.get(name="molepolole")
        self.assertEqual("molepolole.uat.clinicedc.org", obj.domain)
        obj = Site.objects.get(name="mochudi")
        self.assertEqual("mochudi.uat.bw.clinicedc.org", obj.domain)

    @override_settings(SITE_ID=SiteID(default=10))
    def test_country(self):
        for sites in self.default_all_sites.values():
            add_or_update_django_sites(sites=sites)
        self.assertEqual("mochudi", Site.objects.get_current().name)
        self.assertEqual("botswana", Site.objects.get_current().siteprofile.country)
        self.assertEqual("botswana", get_current_country())
        self.assertEqual(
            self.default_all_sites.get("botswana"), get_sites_by_country("botswana")
        )
        self.assertEqual(self.default_all_sites.get("botswana"), get_sites_by_country())
        self.assertEqual(
            self.default_all_sites.get("botswana"),
            get_sites_by_country(all_sites=self.default_all_sites),
        )

        self.assertEqual(
            self.default_all_sites.get("botswana"),
            get_sites_by_country(country="botswana", all_sites=self.default_all_sites),
        )

    @override_settings(EDC_SITES_MODULE_NAME=None)
    def test_default_sites_module_domain(self):
        self.assertEqual(get_all_sites(), all_sites)
        for sites in get_all_sites().values():
            add_or_update_django_sites(sites=sites, verbose=False)
        site = Site.objects.get(id=1)
        self.assertEqual(Alias.objects.get(site=site).domain, "localhost")

    @override_settings(
        EDC_SITES_MODULE_NAME="edc_sites.tests.sites", EDC_SITES_UAT_DOMAIN=False
    )
    def test_custom_sites_module_domain(self):
        self.assertEqual(get_all_sites(), all_test_sites)
        self.assertEqual(settings.SITE_ID, 10)
        for sites in get_all_sites().values():
            add_or_update_django_sites(sites=sites, verbose=False)
        site = Site.objects.get(id=10)
        self.assertEqual(get_current_country(), "botswana")
        self.assertEqual(Alias.objects.get(site=site).domain, "mochudi.bw.clinicedc.org")

    @override_settings(LANGUAGES={"xx": "XXX"})
    def test_site_language_code_not_found_raises(self):
        self.assertRaises(
            SiteLanguagesError,
            SingleSite,
            10,
            "mochudi",
            title="Mochudi",
            country="botswana",
            country_code="bw",
            language_codes=["tn"],
            domain="mochudi.bw.xxx",
        ),

    @override_settings(LANGUAGES=[])
    def test_site_language_code_and_no_settings_languages_raises(self):
        self.assertRaises(
            SiteLanguagesError,
            SingleSite,
            10,
            "mochudi",
            title="Mochudi",
            country="botswana",
            country_code="bw",
            language_codes=["sw"],
            domain="mochudi.bw.xxx",
        ),

    @override_settings(LANGUAGES={"en": "English", "tn": "Setswana"})
    def test_site_languages_codes_ok(self):
        try:
            obj = SingleSite(
                10,
                "mochudi",
                title="Mochudi",
                country="botswana",
                country_code="bw",
                language_codes=["tn"],
                domain="mochudi.bw.xxx",
            )
        except SiteLanguagesError:
            self.fail("SiteLanguagesError unexpectedly raised")

        self.assertDictEqual(obj.languages, {"tn": "Setswana"})

    @override_settings(LANGUAGES=[("en", "English"), ("sw", "Swahili")])
    def test_no_site_language_codes_defaults_to_settings_languages_ok(self):
        try:
            obj = SingleSite(
                10,
                "mochudi",
                title="Mochudi",
                country="botswana",
                country_code="bw",
                domain="mochudi.bw.xxx",
            )
        except SiteLanguagesError:
            self.fail("SiteLanguagesError unexpectedly raised")
        self.assertDictEqual(obj.languages, {"en": "English", "sw": "Swahili"})

        try:
            obj = SingleSite(
                10,
                "mochudi",
                title="Mochudi",
                country="botswana",
                country_code="bw",
                language_codes=[],
                domain="mochudi.bw.xxx",
            )
        except SiteLanguagesError:
            self.fail("SiteLanguagesError unexpectedly raised")
        self.assertDictEqual(obj.languages, {"en": "English", "sw": "Swahili"})

    @override_settings(LANGUAGES=[])
    def test_no_site_language_codes_and_no_settings_languages_ok(self):
        try:
            obj = SingleSite(
                10,
                "mochudi",
                title="Mochudi",
                country="botswana",
                country_code="bw",
                domain="mochudi.bw.xxx",
            )
        except SiteLanguagesError:
            self.fail("SiteLanguagesError unexpectedly raised")
        self.assertDictEqual(obj.languages, {})

    @override_settings(SITE_ID=SiteID(default=30))
    def test_permissions_no_sites(self):
        rf = RequestFactory()
        request = rf.get("/")
        request.site = Site.objects.get(id=30)
        request.user = User.objects.get(username="user_login")
        self.assertRaises(InvalidSiteForUser, has_permissions_for_extra_sites, request)

    @override_settings(SITE_ID=SiteID(default=30))
    def test_permissions_sites(self):
        rf = RequestFactory()
        request = rf.get("/")
        request.site = Site.objects.get(id=30)
        request.user = User.objects.get(username="user_login")
        request.user.userprofile.sites.add(request.site)

        request.user.user_permissions.clear()

        self.assertFalse(has_permissions_for_extra_sites(request))

        rf = RequestFactory()
        request = rf.get("/")
        request.site = Site.objects.get(id=30)
        request.user = User.objects.get(username="user_login")
        permission = Permission.objects.get(codename=codename)

        request.user.user_permissions.add(permission)

        self.assertFalse(has_permissions_for_extra_sites(request))

        rf = RequestFactory()
        request = rf.get("/")
        request.site = Site.objects.get(id=30)
        request.user = User.objects.get(username="user_login")
        request.user.userprofile.sites.add(Site.objects.get(id=40))
        self.assertTrue(has_permissions_for_extra_sites(request))
        self.assertEqual(site_ids_with_permissions(request), [30, 40])

        rf = RequestFactory()
        request = rf.get("/")
        request.site = Site.objects.get(id=30)
        request.user = User.objects.get(username="user_login")
        request.user.user_permissions.clear()
        self.assertFalse(has_permissions_for_extra_sites(request))

    @override_settings(SITE_ID=SiteID(default=30))
    def test_permissions_sites_not_in_userprofile(self):
        rf = RequestFactory()
        request = rf.get("/admin")
        request.site = Site.objects.get(id=30)
        request.user = User.objects.get(username="user_login")

        # only add 40 to user profile
        request.user.userprofile.sites.add(Site.objects.get(id=40))
        request.user.user_permissions.clear()
        permission = Permission.objects.get(codename=codename)
        request.user.user_permissions.add(permission)

        self.assertRaises(InvalidSiteForUser, has_permissions_for_extra_sites, request)

    @override_settings(SITE_ID=SiteID(default=30))
    def test_permissions_messages(self):
        c = Client()
        c.login(username="user_login", password="pass")  # nosec B106
        response = c.get("/admin/")

        # only add 40 to user profile
        response.wsgi_request.user.userprofile.sites.add(Site.objects.get(id=40))
        response.wsgi_request.user.user_permissions.clear()
        permission = Permission.objects.get(codename=codename)
        response.wsgi_request.user.user_permissions.add(permission)
        self.assertRaises(
            InvalidSiteForUser, has_permissions_for_extra_sites, response.wsgi_request
        )

        # user profile has 30 and 40
        response.wsgi_request.user.userprofile.sites.add(Site.objects.get(id=30))
        response.wsgi_request.user.userprofile.sites.add(Site.objects.get(id=40))
        response.wsgi_request.user.user_permissions.clear()
        permission = Permission.objects.get(codename=codename)
        response.wsgi_request.user.user_permissions.add(permission)
        has_permissions_for_extra_sites(response.wsgi_request)
        self.assertIn(
            successmsg, [msg_obj.message for msg_obj in get_messages(response.wsgi_request)]
        )

        # add a permission with add_, expect a warning
        permission = Permission.objects.get(codename="add_site")
        response = c.get("/admin/")
        response.wsgi_request.user.user_permissions.add(permission)
        has_permissions_for_extra_sites(response.wsgi_request)
        self.assertIn(
            warnmsg, [msg_obj.message for msg_obj in get_messages(response.wsgi_request)]
        )

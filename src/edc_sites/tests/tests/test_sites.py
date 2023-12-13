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

from edc_sites.forms import SiteModelFormMixin
from edc_sites.models import SiteProfile
from edc_sites.single_site import SingleSite
from edc_sites.single_site.get_languages import SiteLanguagesError
from edc_sites.site import (
    AlreadyRegistered,
    AlreadyRegisteredDomain,
    AlreadyRegisteredName,
    SiteDoesNotExist,
    sites,
)
from edc_sites.utils import add_or_update_django_sites

from ...auths import codename
from ...permissions import has_permissions_for_extra_sites, site_ids_with_permissions
from ...permissions.site_ids_with_permissions import (
    InvalidSiteForUser,
    successmsg,
    warnmsg,
)
from ..models import TestModelWithSite
from ..site_test_case_mixin import SiteTestCaseMixin


class TestForm(SiteModelFormMixin, forms.ModelForm):
    class Meta:
        model = TestModelWithSite
        fields = "__all__"


def sites_factory():
    pass


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
        add_or_update_django_sites(single_sites=self.default_sites, verbose=False)
        obj = TestModelWithSite.objects.create()
        self.assertEqual(obj.site.pk, 20)
        self.assertEqual(obj.site.pk, Site.objects.get_current().pk)

    @override_settings(SITE_ID=SiteID(default=30))
    def test_30(self):
        add_or_update_django_sites(single_sites=self.default_sites, verbose=False)
        obj = TestModelWithSite.objects.create()
        self.assertEqual(obj.site.pk, 30)
        self.assertEqual(obj.site.pk, Site.objects.get_current().pk)

    @override_settings(SITE_ID=SiteID(default=30))
    def test_override_current(self):
        add_or_update_django_sites(single_sites=self.default_sites, verbose=False)
        site = Site.objects.get(pk=40)
        obj = TestModelWithSite.objects.create(site=site)
        self.assertEqual(obj.site.pk, 40)
        self.assertNotEqual(obj.site.pk, Site.objects.get_current().pk)

    @override_settings(LANGUAGES=[("en", "English"), ("sw", "Swahili"), ("tn", "Setswana")])
    def test_get_language_choices_for_site(self):
        sites.register(
            SingleSite(
                99,
                "amana",
                title="Amana",
                country="tanzania",
                country_code="tz",
                language_codes=["en", "sw"],
                domain="amana.clinicedc.org",
            )
        )
        add_or_update_django_sites(verbose=False)
        site = Site.objects.get(pk=99)
        obj = TestModelWithSite.objects.create(site=site)
        self.assertEqual(obj.site.pk, 99)

        language_choices = sites.get_language_choices_tuple(site)
        self.assertTupleEqual(language_choices, (("en", "English"), ("sw", "Swahili")))

        language_choices = sites.get_language_choices_tuple(site, other=True)
        self.assertTupleEqual(
            language_choices,
            (("en", "English"), ("sw", "Swahili"), (OTHER, "Other")),
        )

    def test_get_site_id_by_name(self):
        sites.initialize()
        sites.register(*self.default_sites)
        add_or_update_django_sites()
        self.assertEqual(sites.get_by_attr("name", "mochudi").site_id, 10)

    def test_get_site_id_by_description(self):
        sites.initialize()
        sites.register(*self.default_sites)
        add_or_update_django_sites()
        self.assertEqual(sites.get_by_attr("description", "Mochudi").site_id, 10)

    def test_get_site_id_invalid(self):
        sites.initialize()
        sites.register(*self.default_sites)
        add_or_update_django_sites()
        self.assertRaises(SiteDoesNotExist, sites.get_by_attr, "name", "blahblah")

    def test_get_site_id_without_sites(self):
        sites.initialize()
        sites.register(*self.default_sites)
        add_or_update_django_sites()
        self.assertEqual(sites.get_by_attr("name", "mochudi").site_id, 10)

    @override_settings(SITE_ID=SiteID(default=30))
    def test_site_profile(self):
        sites.initialize()
        sites.register(*self.default_sites)
        add_or_update_django_sites()
        obj = TestModelWithSite.objects.create()
        site_profile = SiteProfile.objects.get(site=obj.site)
        self.assertEqual(obj.site.siteprofile, site_profile)

    def test_updates_sites(self):
        sites.initialize()
        sites.register(*self.default_sites)
        add_or_update_django_sites()
        for single_site in self.default_sites:
            self.assertIn(single_site.site_id, [obj.id for obj in Site.objects.all()])
        self.assertNotIn("example.com", str([str(obj) for obj in Site.objects.all()]))
        self.assertEqual(len(self.default_sites), Site.objects.all().count())

    @override_settings(EDC_SITES_UAT_DOMAIN=False)
    def test_domain(self):
        sites.initialize(initialize_site_model=True)
        sites.register(*self.default_sites)
        add_or_update_django_sites()
        obj = Site.objects.get(name="molepolole")
        self.assertEqual("molepolole.bw.clinicedc.org", obj.domain)
        obj = Site.objects.get(name="mochudi")
        self.assertEqual("mochudi.bw.clinicedc.org", obj.domain)

    @override_settings(EDC_SITES_UAT_DOMAIN=True)
    def test_uat_domain(self):
        self.assertTrue(settings.EDC_SITES_UAT_DOMAIN)
        sites.initialize()
        sites.register(*self.default_sites)
        add_or_update_django_sites()
        self.assertEqual(sites.get(10).domain, "mochudi.uat.bw.clinicedc.org")
        add_or_update_django_sites()
        obj = Site.objects.get(name="molepolole")
        self.assertEqual("molepolole.uat.bw.clinicedc.org", obj.domain)
        obj = Site.objects.get(name="mochudi")
        self.assertEqual("mochudi.uat.bw.clinicedc.org", obj.domain)

    @override_settings(SITE_ID=SiteID(default=10))
    def test_country(self):
        sites.initialize()
        sites.register(*self.default_sites)
        add_or_update_django_sites()
        self.assertEqual("mochudi", Site.objects.get_current().name)
        self.assertEqual("botswana", Site.objects.get_current().siteprofile.country)
        self.assertEqual("botswana", sites.get_current_country())
        self.assertEqual(
            [s for s in self.default_sites if s.country == "botswana"],
            sites.get_by_country("botswana", aslist=True),
        )

    @override_settings(EDC_SITES_UAT_DOMAIN=False)
    def test_register_sites(self):
        sites.initialize()
        site1 = SingleSite(site_id=1, name="site1", domain="site1.clinicedc.org")
        site2 = SingleSite(site_id=2, name="site2", domain="site2.clinicedc.org")
        site_bad1 = SingleSite(site_id=1, name="site3", domain="site3.clinicedc.org")
        site_bad2 = SingleSite(site_id=3, name="site1", domain="site3.clinicedc.org")
        site_bad3 = SingleSite(site_id=3, name="site3", domain="site1.clinicedc.org")

        sites.register(site1, site2)

        self.assertEqual(site1.domain, "site1.clinicedc.org")
        self.assertEqual(site2.domain, "site2.clinicedc.org")

        self.assertRaises(AlreadyRegistered, sites.register, site1)
        self.assertRaises(AlreadyRegistered, sites.register, site_bad1)
        self.assertRaises(AlreadyRegisteredName, sites.register, site_bad2)
        self.assertRaises(AlreadyRegisteredDomain, sites.register, site_bad3)

        sites._registry = {}

        site1 = SingleSite(
            site_id=1, name="site1", domain="site1.clinicedc.org", country="tanzania"
        )
        site2 = SingleSite(
            site_id=2, name="site2", domain="site2.clinicedc.org", country="uganda"
        )
        sites.register(site1, site2)

        self.assertEqual(sites.get_by_country("tanzania"), {1: site1})
        self.assertEqual(sites.get_by_country("uganda"), {2: site2})

    @override_settings(EDC_SITES_UAT_DOMAIN=True)
    def test_register_inserts_uat_in_site_domains(self):
        sites.initialize()
        site1 = SingleSite(site_id=1, name="site1", domain="site1.clinicedc.org")
        site2 = SingleSite(site_id=2, name="site2", domain="site2.clinicedc.org")

        sites.register(site1, site2)
        self.assertEqual(sites.get(site1.site_id).domain, "site1.uat.clinicedc.org")
        self.assertEqual(sites.get(site2.site_id).domain, "site2.uat.clinicedc.org")

    @override_settings(EDC_SITES_REGISTER_DEFAULT=True)
    def test_register_default_site_domain(self):
        sites.initialize()
        for single_site in sites.all().values():
            sites.register(single_site)
        add_or_update_django_sites()
        site = Site.objects.get(id=1)
        self.assertEqual(Alias.objects.get(site=site).domain, "localhost")

    def test_alias_model(self):
        sites.initialize()
        sites.register(*self.default_sites)
        add_or_update_django_sites()
        self.assertEqual(settings.SITE_ID, 10)
        site = Site.objects.get(id=10)
        self.assertEqual(Alias.objects.get(site=site).domain, "mochudi.bw.clinicedc.org")

    @override_settings(EDC_SITES_UAT_DOMAIN=True)
    def test_alias_model_for_uat(self):
        sites.initialize()
        sites.register(*self.default_sites)
        add_or_update_django_sites()
        self.assertEqual(settings.SITE_ID, 10)
        site = Site.objects.get(id=10)
        self.assertEqual(Alias.objects.get(site=site).domain, "mochudi.uat.bw.clinicedc.org")

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
        sites.initialize()
        sites.register(*self.default_sites)
        add_or_update_django_sites()
        rf = RequestFactory()
        request = rf.get("/")
        request.site = Site.objects.get(id=30)
        request.user = User.objects.get(username="user_login")
        self.assertRaises(InvalidSiteForUser, has_permissions_for_extra_sites, request)

    @override_settings(SITE_ID=SiteID(default=30))
    def test_permissions_sites(self):
        sites.initialize()
        sites.register(*self.default_sites)
        add_or_update_django_sites()
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
        sites.initialize()
        sites.register(*self.default_sites)
        add_or_update_django_sites()
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
        sites.initialize()
        sites.register(*self.default_sites)
        add_or_update_django_sites()
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

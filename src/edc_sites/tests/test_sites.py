from django import forms
from django.conf import settings
from django.contrib.sites.models import Site
from django.test import TestCase
from django.test.utils import override_settings
from multisite import SiteID
from multisite.models import Alias

from edc_sites import get_all_sites, get_current_country, get_sites_by_country
from edc_sites.models import SiteProfile
from edc_sites.sites import all_sites

from ..add_or_update_django_sites import add_or_update_django_sites
from ..forms import SiteModelFormMixin
from ..get_site_id import InvalidSiteError, get_site_id
from ..single_site import SingleSite, SiteLanguagesError
from .models import TestModelWithSite
from .site_test_case_mixin import SiteTestCaseMixin
from .sites import all_test_sites


class TestForm(SiteModelFormMixin, forms.ModelForm):
    class Meta:
        model = TestModelWithSite
        fields = "__all__"


class TestSites(SiteTestCaseMixin, TestCase):
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
    def test_languages_not_found(self):
        self.assertRaises(
            SiteLanguagesError,
            SingleSite,
            10,
            "mochudi",
            title="Mochudi",
            country="botswana",
            country_code="bw",
            languages={"tn": "Tswana"},
            domain="mochudi.bw.xxx",
        ),

    @override_settings(LANGUAGES={"tn": "Setswana"})
    def test_languages_ok(self):
        try:
            SingleSite(
                10,
                "mochudi",
                title="Mochudi",
                country="botswana",
                country_code="bw",
                languages={"tn": "Setswana"},
                domain="mochudi.bw.xxx",
            )
        except SiteLanguagesError:
            self.fail("SiteLanguagesError unexpectedly raised")

    @override_settings(LANGUAGES={})
    def test_languages_ok_default(self):
        try:
            SingleSite(
                10,
                "mochudi",
                title="Mochudi",
                country="botswana",
                country_code="bw",
                domain="mochudi.bw.xxx",
            )
        except SiteLanguagesError:
            self.fail("SiteLanguagesError unexpectedly raised")

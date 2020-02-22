from django.apps import apps as django_apps
from django.contrib.auth import get_user_model
from django.test import TestCase, tag
from django.test.client import RequestFactory
from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch

from edc_auth import get_default_codenames_by_group
from edc_auth.group_permissions_updater import GroupPermissionsUpdater
from edc_dashboard import url_names

from ...navbar import Navbar
from ...navbar_item import NavbarItem, NavbarItemError
from ...site_navbars import site_navbars, AlreadyRegistered

User = get_user_model()


class TestNavbar(TestCase):
    @classmethod
    def setUpClass(cls):
        url_names.register("dashboard_url", "dashboard_url", "edc_dashboard")
        GroupPermissionsUpdater(
            codenames_by_group=get_default_codenames_by_group(), verbose=True
        )
        # GroupPermissionsUpdater(
        #     verbose=True,
        #     apps=django_apps,
        #     create_codename_tuples={
        #         "edc_navbar.navbar": [
        #             ("edc_navbar.navbar_one", "Can access One")
        #         ]
        #     },
        # )
        return super().setUpClass()

    def setUp(self):
        site_navbars._registry = {}
        self.user = User.objects.create_superuser("user_login", "u@example.com", "pass")
        rf = RequestFactory()
        self.request = rf.request()
        self.request.user = self.user

    def create_navbar(self):
        testnavbar = Navbar(name="pharmacy_dashboard")
        testnavbar.append_item(
            NavbarItem(
                name="navbar1",
                title="Navbar1",
                label="one",
                codename="edc_navbar.navbar1",
                url_name="navbar_one_url",
            )
        )

        testnavbar.append_item(
            NavbarItem(
                name="navbar2",
                title="Navbar2",
                label="two",
                codename="edc_navbar.navbar2",
                url_name="navbar_two_url",
            )
        )
        return testnavbar

    def test_urls(self):
        reverse("navbar_one_url")
        reverse("navbar_two_url")

    def test_site_navbar_register(self):
        navbar = self.create_navbar()
        site_navbars.register(navbar)
        self.assertTrue(navbar.name in site_navbars.registry)
        self.assertRaises(AlreadyRegistered, site_navbars.register, navbar)

    def test_navbar_item_raises_missing_url(self):
        self.assertRaises(
            NavbarItemError,
            NavbarItem,
            name="navbar_item_one",
            label="Navbar Item One",
            title="navbar_item_one",
            url_name=None,
        )

    def test_navbar_item_raises_bad_url(self):
        self.assertRaises(
            NoReverseMatch,
            NavbarItem,
            name="navbar_item_one",
            label="Navbar Item One",
            title="navbar_item_one",
            url_name="blahblahblah",
        )

    def test_navbar_item_ok(self):
        navbar_item = NavbarItem(
            name="navbar_item_one",
            label="Navbar Item One",
            title="navbar_item_one",
            url_name="navbar_one_url",
            codename="edc_navbar.nav_one",
        )
        self.assertEqual(navbar_item.name, "navbar_item_one")
        self.assertEqual(navbar_item.title, "navbar_item_one")
        self.assertEqual(navbar_item.label, "Navbar Item One")

    def test_render_navbar_item_to_string(self):
        navbar_item_selected = "navbar_item_one"
        navbar_item = NavbarItem(
            name="navbar_item_one",
            label="Navbar Item One",
            title="navbar_item_one",
            url_name="navbar_one_url",
            codename="edc_navbar.nav_one",
        )
        template_string = navbar_item.render(
            request=self.request, navbar_item_selected=navbar_item_selected
        )
        self.assertIn(navbar_item.name, template_string)
        self.assertIn(navbar_item.title, template_string)
        self.assertIn(navbar_item.reversed_url, template_string)
        self.assertIn(navbar_item.label, template_string)

    def test_navbar_repr(self):
        navbar = Navbar(name="default")
        self.assertTrue(repr(navbar))

    def test_render_navbar_item_to_string_fa_icon(self):
        navbar_item_selected = "navbar_item_one"
        navbar_item = NavbarItem(
            name="navbar_item_one",
            label="Navbar Item One",
            title="navbar_item_one",
            url_name="navbar_one_url",
            fa_icon="far fa-user-circle",
            codename="edc_navbar.nav_one",
        )
        template_string = navbar_item.render(
            self.request, navbar_item_selected=navbar_item_selected
        )
        self.assertIn(navbar_item.fa_icon, template_string)

    def test_render_navbar_item_to_string_icon(self):
        navbar_item_selected = "navbar_item_one"
        navbar_item = NavbarItem(
            name="navbar_item_one",
            label="Navbar Item One",
            title="navbar_item_one",
            url_name="navbar_one_url",
            icon="medicine.png",
            codename="edc_navbar.nav_one",
        )
        template_string = navbar_item.render(
            self.request, navbar_item_selected=navbar_item_selected
        )
        self.assertIn(navbar_item.icon, template_string)

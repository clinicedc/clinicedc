from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls.base import reverse
from edc_dashboard.url_names import url_names

from ...navbar import Navbar
from ...navbar_item import NavbarItem
from ...site_navbars import AlreadyRegistered, site_navbars

User = get_user_model()


class TestNavbar(TestCase):
    @classmethod
    def setUpClass(cls):
        url_names.register("dashboard_url", "dashboard_url", "edc_dashboard")
        return super().setUpClass()

    def setUp(self):
        site_navbars._registry = {}
        self.user = User.objects.create_superuser("user_login", "u@example.com", "pass")
        rf = RequestFactory()
        self.request = rf.request()
        self.request.user = self.user

    def create_navbar(self) -> Navbar:
        testnavbar = Navbar(name="pharmacy_dashboard")
        testnavbar.register(
            NavbarItem(
                name="navbar1",
                title="Navbar1",
                label="one",
                codename="edc_navbar.navbar1",
                url_name="navbar_one_url",
            )
        )

        testnavbar.register(
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

    def test_navbar_set_active(self):
        navbar = self.create_navbar()
        navbar.set_active("navbar2")
        self.assertTrue(navbar.get("navbar2").active)
        self.assertFalse(navbar.get("navbar1").active)
        navbar.set_active("navbar1")
        self.assertFalse(navbar.get("navbar2").active)
        self.assertTrue(navbar.get("navbar1").active)

    def test_navbar_urls(self):
        navbar = self.create_navbar()
        for navbar_item in navbar.navbar_items:
            self.assertIsNotNone(navbar_item.get_url())

    def test_navbar_disabled(self):
        navbar = self.create_navbar()
        for navbar_item in navbar.navbar_items:
            navbar_item.set_disabled(self.user)
            self.assertEqual(navbar_item.disabled, "")

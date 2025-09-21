from clinicedc_tests.sites import all_sites
from clinicedc_tests.utils import login
from django.contrib.auth.models import User
from django.test import override_settings, tag
from django.urls import reverse
from django.utils import timezone
from django_webtest import WebTest

from edc_auth.auth_updater.group_updater import GroupUpdater, PermissionsCodenameError
from edc_facility.auths import codenames
from edc_facility.import_holidays import import_holidays
from edc_facility.models import HealthFacility, HealthFacilityTypes
from edc_sites.site import sites as site_sites
from edc_sites.utils import add_or_update_django_sites


@tag("facility")
@override_settings(SITE_ID=10)
class TestAdmin(WebTest):
    @classmethod
    def setUpTestData(cls):
        import_holidays()
        site_sites._registry = {}
        site_sites.loaded = False
        site_sites.register(*all_sites)
        add_or_update_django_sites()

    def setUp(self) -> None:
        super().setUp()
        self.user = User.objects.create_superuser("user_login", "u@example.com", "pass")
        self.user.is_active = True
        self.user.is_staff = True
        self.user.save()
        self.user.refresh_from_db()

    def login(self):
        form = self.app.get(reverse("admin:index")).maybe_follow().form
        form["username"] = self.user.username
        form["password"] = "pass"  # noqa: S105
        return form.submit()

    @staticmethod
    def get_obj(**kwargs):
        health_facility_type = HealthFacilityTypes.objects.all()[0]
        opts = dict(
            report_datetime=timezone.now(),
            name="HealthFacility",
            health_facility_type=health_facility_type,
            mon=False,
            tue=False,
            wed=False,
            thu=False,
            fri=False,
            sat=False,
            sun=False,
        )
        opts.update(**kwargs)
        return HealthFacility.objects.create(**opts)

    def test_admin_ok(self):
        login(self, superuser=True, redirect_url="admin:index")
        obj = self.get_obj(mon=False, tue=False)
        url = reverse("edc_facility_admin:edc_facility_healthfacility_changelist")
        url = f"{url}?q={obj.name}"
        response = self.app.get(url, user=self.user)
        self.assertNotIn(
            '<td class="field-clinic_days"><span style="white-space:nowrap;">Mon',
            response.text,
        )
        self.assertIn(
            '<td class="field-clinic_days"><span style="white-space:nowrap;"></span></td>',
            response.text,
        )
        obj.mon = True
        obj.tue = True
        obj.wed = True
        obj.save()
        url = reverse("edc_facility_admin:edc_facility_healthfacility_changelist")
        url = f"{url}?q={obj.name}"
        response = self.app.get(url, user=self.user)
        self.assertIn(">Mon,Tue,Wed<", response.text)

        obj.thu = True
        obj.fri = True
        obj.sat = True
        obj.sun = True
        obj.save()
        url = reverse("edc_facility_admin:edc_facility_healthfacility_changelist")
        url = f"{url}?q={obj.name}"
        response = self.app.get(url, user=self.user)
        self.assertIn(">Mon,Tue,Wed,Thu,Fri,Sat,Sun<", response.text)

    def test_auth(self):
        group_updater = GroupUpdater(groups={})
        for codename in codenames:
            try:
                group_updater.get_from_dotted_codename(codename)
            except PermissionsCodenameError as e:
                self.fail(f"PermissionsCodenameError raised unexpectedly. Got {e}")

from unittest.mock import patch

from django.contrib.auth.models import User
from django.urls import reverse
from django_webtest import WebTest
from edc_auth.auth_updater.group_updater import GroupUpdater, PermissionsCodenameError
from edc_test_utils.webtest import login
from edc_utils import get_utcnow

from edc_facility.auths import codenames
from edc_facility.models import HealthFacility, HealthFacilityTypes


class TestAdmin(WebTest):
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
        form["password"] = "pass"  # nosec B105
        return form.submit()

    @staticmethod
    def get_obj(**kwargs):
        health_facility_type = HealthFacilityTypes.objects.all()[0]
        opts = dict(
            report_datetime=get_utcnow(),
            name="HealthFacility",
            health_facility_type=health_facility_type,
            mon=True,
            tue=True,
            wed=False,
            thu=False,
            fri=False,
            sat=False,
            sun=False,
        )
        opts.update(**kwargs)
        return HealthFacility.objects.create(**opts)

    @patch(
        "edc_subject_dashboard.templatetags.edc_subject_dashboard_extras."
        "get_appointment_model_cls"
    )
    def test_admin_ok(self, mock_appointment_type):
        login(self, user=self.user)
        obj = self.get_obj(mon=False, tue=False)
        url = reverse("edc_facility_admin:edc_facility_healthfacility_changelist")
        url = f"{url}?q={obj.name}"
        response = self.app.get(url, user=self.user)
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
        self.assertIn(">MTW<", response.text)

        obj.thu = True
        obj.fri = True
        obj.sat = True
        obj.sun = True
        obj.save()
        url = reverse("edc_facility_admin:edc_facility_healthfacility_changelist")
        url = f"{url}?q={obj.name}"
        response = self.app.get(url, user=self.user)
        self.assertIn(">MTWThFSSu<", response.text)

    def test_auth(self):
        group_updater = GroupUpdater(groups={})
        for codename in codenames:
            try:
                group_updater.get_from_dotted_codename(codename)
            except PermissionsCodenameError as e:
                self.fail(f"PermissionsCodenameError raised unexpectedly. Got {e}")

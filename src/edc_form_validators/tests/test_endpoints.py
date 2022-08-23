from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from django_webtest import WebTest


def login(testcase, user=None, redirect_url=None):
    user.is_superuser = True
    user.is_active = True
    user.is_staff = True
    user.save()
    user.refresh_from_db()
    form = (
        testcase.app.get(reverse(redirect_url or settings.LOGIN_REDIRECT_URL))
        .maybe_follow()
        .form
    )
    form["username"] = user.username
    form["password"] = "pass"  # nosec B105
    return form.submit()


class AdminSiteTest(WebTest):
    def setUp(self):
        self.user = User.objects.create(  # nosec B106
            username="user_login",
            email="u@example.com",
            is_active=True,
            is_staff=True,
        )
        self.user.set_password("pass")

    def test_ok(self):
        """Assert default rule handler names on queryrule ADD form"""
        login(self, user=self.user, redirect_url="admin:index")
        url = reverse("admin:form_validators_app_testmodel_add")
        response = self.app.get(url, user=self.user, status=200)
        self.assertIn("Test model", response)

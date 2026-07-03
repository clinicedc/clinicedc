from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends.db import SessionStore
from django.test import RequestFactory, TestCase, override_settings, tag
from django.urls import reverse

from edc_lab_results.forms import OrderUpdateForm
from edc_lab_results.models import Result
from edc_lab_results.views import OrderDetailView
from edc_registration.models import RegisteredSubject


@tag("lab_results")
@override_settings(SITE_ID=10)
class TestOrderUpdateFormValidation(TestCase):
    """subject_identifier and screening_identifier are validated against
    RegisteredSubject."""

    def setUp(self):
        RegisteredSubject.objects.create(
            subject_identifier="123-0001",
            screening_identifier="S-0001",
        )

    def test_screening_identifier_valid(self):
        form = OrderUpdateForm(data={"screening_identifier": "S-0001"})
        form.is_valid()
        self.assertNotIn("screening_identifier", form.errors)

    def test_screening_identifier_unknown_rejected(self):
        form = OrderUpdateForm(data={"screening_identifier": "S-NOPE"})
        form.is_valid()
        self.assertIn("screening_identifier", form.errors)
        self.assertIn("not found", str(form.errors["screening_identifier"]))

    def test_screening_identifier_blank_ok(self):
        form = OrderUpdateForm(data={"screening_identifier": ""})
        form.is_valid()
        self.assertNotIn("screening_identifier", form.errors)

    def test_subject_identifier_valid(self):
        form = OrderUpdateForm(data={"subject_identifier": "123-0001"})
        form.is_valid()
        self.assertNotIn("subject_identifier", form.errors)

    def test_subject_identifier_unknown_rejected(self):
        form = OrderUpdateForm(data={"subject_identifier": "999-9999"})
        form.is_valid()
        self.assertIn("subject_identifier", form.errors)


@tag("lab_results")
@override_settings(ROOT_URLCONF="edc_lab_results.tests.tests.review_urls")
class TestOrderDetailNext(TestCase):
    """The Back button and post-save redirect honor a safe `next` param."""

    def _view(self, request, order_no="DG-1"):
        view = OrderDetailView()
        view.request = request
        view.kwargs = {"order_no": order_no}
        return view

    @staticmethod
    def _post_request(data):
        request = RequestFactory().post("/x/", data)
        request.session = SessionStore()
        request._messages = FallbackStorage(request)
        return request

    def test_safe_next_accepts_local_path(self):
        request = RequestFactory().get(
            "/x/", {"next": "/results/review/?category=no_match"}
        )
        self.assertEqual(
            self._view(request)._safe_next(), "/results/review/?category=no_match"
        )

    def test_safe_next_rejects_external_host(self):
        request = RequestFactory().get("/x/", {"next": "https://evil.example/x"})
        self.assertEqual(self._view(request)._safe_next(), "")

    def test_safe_next_rejects_protocol_relative(self):
        request = RequestFactory().get("/x/", {"next": "//evil.example/x"})
        self.assertEqual(self._view(request)._safe_next(), "")

    def test_safe_next_empty_when_absent(self):
        request = RequestFactory().get("/x/")
        self.assertEqual(self._view(request)._safe_next(), "")

    def test_back_url_uses_next(self):
        request = RequestFactory().get("/x/")
        first = Result(subject_identifier="123-0001")
        self.assertEqual(
            self._view(request)._back_url(first, "/results/review/?category=no_match"),
            "/results/review/?category=no_match",
        )

    def test_back_url_defaults_to_subject_results(self):
        request = RequestFactory().get("/x/")
        first = Result(subject_identifier="123-0001")
        url = self._view(request)._back_url(first, "")
        self.assertEqual(
            url, reverse("edc_lab_results:subject-results") + "?identifier=123-0001"
        )

    def test_post_redirect_preserves_next(self):
        request = self._post_request({"next": "/results/review/?category=no_match"})
        response = self._view(request).post(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn("next=", response.url)
        self.assertTrue(
            response.url.startswith(
                reverse("edc_lab_results:order-detail", kwargs={"order_no": "DG-1"})
            )
        )

    def test_post_redirect_without_next_has_no_query(self):
        request = self._post_request({})
        response = self._view(request).post(request)
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("next=", response.url)

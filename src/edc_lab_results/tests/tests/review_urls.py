"""Minimal URLconf for OrderDetailView `next` round-trip tests.

Provides just the two named routes the view reverses, so tests can exercise
back-url / redirect logic without wiring the navbar/dashboard/admin.

The routes are included under the ``edc_lab_results`` application namespace so
``reverse("edc_lab_results:...")`` resolves. Setting ``app_name`` at the root
urlconf level does NOT register a namespace -- the namespace is only created
when patterns are ``include()``-ed with an app namespace.
"""

from django.http import HttpResponse
from django.urls import include, path


def _noop(request, *args, **kwargs):
    return HttpResponse()


app_patterns = [
    path("results/", _noop, name="subject-results"),
    path("results/order/<str:order_no>/", _noop, name="order-detail"),
]

urlpatterns = [
    path("", include((app_patterns, "edc_lab_results"))),
]

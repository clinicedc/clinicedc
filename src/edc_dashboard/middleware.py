from django.conf import settings
from edc_constants.constants import MALE, FEMALE, OTHER, YES, NO
from edc_constants.constants import NEW, OPEN, CLOSED
from edc_constants.constants import NOT_APPLICABLE, CANCELLED

from .dashboard_templates import dashboard_templates
from .utils import insert_bootstrap_version


class DashboardMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            request.url_name_data
        except AttributeError:
            request.url_name_data = {}
        try:
            request.template_data
        except AttributeError:
            request.template_data = {}
        request.template_data = insert_bootstrap_version(
            **request.template_data)
        response = self.get_response(request)
        return response

    def process_view(self, request, *args):
        template_data = dashboard_templates
        try:
            template_data.update(settings.DASHBOARD_BASE_TEMPLATES)
        except AttributeError:
            pass
        template_data = insert_bootstrap_version(**template_data)
        request.template_data.update(**template_data)

    def process_template_response(self, request, response):
        try:
            reviewer_site_id = settings.REVIEWER_SITE_ID
        except AttributeError:
            reviewer_site_id = None
        if response.context_data:
            response.context_data.update(
                CANCELLED=CANCELLED,
                CLOSED=CLOSED,
                FEMALE=FEMALE,
                MALE=MALE,
                NEW=NEW,
                NO=NO,
                NOT_APPLICABLE=NOT_APPLICABLE,
                OPEN=OPEN,
                OTHER=OTHER,
                YES=YES,
                reviewer_site_id=reviewer_site_id)
        return response

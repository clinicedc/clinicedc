from django.conf import settings
from edc_constants.constants import MALE, FEMALE, OTHER, YES, NO, NOT_APPLICABLE
from edc_constants.constants import NEW, OPEN, CLOSED


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
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        try:
            reviewer_site_id = settings.REVIEWER_SITE_ID
        except AttributeError:
            reviewer_site_id = None
        response.context_data.update(
            OPEN=OPEN,
            CLOSED=CLOSED,
            FEMALE=FEMALE,
            MALE=MALE,
            NEW=NEW,
            NO=NO,
            NOT_APPLICABLE=NOT_APPLICABLE,
            OTHER=OTHER,
            YES=YES,
            reviewer_site_id=reviewer_site_id)
        return response

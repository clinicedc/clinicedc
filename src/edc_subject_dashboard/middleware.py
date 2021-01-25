from django.conf import settings
from edc_appointment.constants import (
    COMPLETE_APPT,
    IN_PROGRESS_APPT,
    INCOMPLETE_APPT,
    NEW_APPT,
)
from edc_dashboard import insert_bootstrap_version, url_names
from edc_visit_tracking.constants import MISSED_VISIT

from .dashboard_templates import dashboard_templates


class DashboardMiddleware:

    """Declare in settings:

    For example:

        DASHBOARD_URL_NAMES = {
            'subject_models_url': 'subject_models_url',
            'subject_listboard_url': 'myapp:subject_listboard_url',
            'subject_dashboard_url': 'myapp:subject_dashboard_url',
        }

        DASHBOARD_BASE_TEMPLATES = {
            'listboard_base_template': 'myapp/base.html',
            'dashboard_base_template': 'myapp/base.html',
            'subject_listboard_template': 'myapp/listboard.html',
            'subject_dashboard_template': 'myapp/dashboard.html',
        }


    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, *args):
        """Adds/Updates references to urls and templates.
        """

        try:
            settings.DASHBOARD_URL_NAMES
        except AttributeError:
            pass
        else:
            url_names.register_from_dict(**settings.DASHBOARD_URL_NAMES)
        request.url_name_data = url_names.registry

        try:
            template_data = settings.DASHBOARD_BASE_TEMPLATES
        except AttributeError:
            template_data = dashboard_templates
        template_data = insert_bootstrap_version(**template_data)
        request.template_data.update(**template_data)

    def process_template_response(self, request, response):
        if response.context_data:
            response.context_data.update(**request.url_name_data)
            response.context_data.update(**request.template_data)
            response.context_data.update(
                COMPLETE_APPT=COMPLETE_APPT,
                INCOMPLETE_APPT=INCOMPLETE_APPT,
                IN_PROGRESS_APPT=IN_PROGRESS_APPT,
                MISSED_VISIT=MISSED_VISIT,
                NEW_APPT=NEW_APPT,
            )
        return response

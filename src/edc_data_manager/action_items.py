from django.conf import settings
from django.template.loader import render_to_string
from edc_action_item import Action, site_action_items
from edc_constants.constants import RESOLVED, FEEDBACK

from .constants import RESOLVED_WITH_ACTION


DATA_QUERY_ACTION = "data_query_action"


class DataQueryAction(Action):
    name = DATA_QUERY_ACTION
    display_name = "Data query"
    reference_model = "edc_data_manager.dataquery"
    create_by_user = True
    show_link_to_changelist = True
    show_on_dashboard = True
    admin_site_name = "edc_data_manager_admin"
    instructions = "Review and respond to the query"
    delete_with_reference_object = True

    def close_action_item_on_save(self):
        if self.reference_obj and self.reference_obj.status in [
            RESOLVED,
            RESOLVED_WITH_ACTION,
        ]:
            return True
        return False

    @property
    def site_response_status(self):
        try:
            site_response_status = self.reference_obj.site_response_status
        except AttributeError:
            site_response_status = None
        return site_response_status

    def get_color_style(self):
        color_style = "danger"
        if self.site_response_status in [FEEDBACK, RESOLVED]:
            color_style = "info"
        return color_style

    def get_display_name(self):
        template_name = (
            f"edc_data_manager/bootstrap{settings.EDC_BOOTSTRAP}/"
            f"action_item_display_name.html"
        )
        category = (
            "TCC" if self.site_response_status in [FEEDBACK, RESOLVED] else "Query"
        )
        title = getattr(self.reference_obj, "title", "")
        auto = "auto" if getattr(self.reference_obj, "rule_generated", False) else ""
        context = dict(category=category, title=title, auto=auto)
        return render_to_string(template_name, context=context)


site_action_items.register(DataQueryAction)

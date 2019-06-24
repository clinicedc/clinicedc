from edc_action_item import ActionWithNotification, site_action_items
from edc_constants.constants import RESOLVED, FEEDBACK
from edc_data_manager.constants import RESOLVED_WITH_ACTION


DATA_QUERY_ACTION = "data_query_action"


class DataQueryAction(ActionWithNotification):
    name = DATA_QUERY_ACTION
    display_name = "Data query"
    notification_display_name = "Data query"
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
        display_name = "Site data query"
        if self.site_response_status in [FEEDBACK, RESOLVED]:
            display_name = "TCC data query"
        return display_name


site_action_items.register(DataQueryAction)

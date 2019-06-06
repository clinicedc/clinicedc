from edc_action_item import ActionWithNotification, site_action_items
from edc_constants.constants import YES


DATA_QUERY_ACTION = "data_query_action"


class DataQueryAction(ActionWithNotification):
    name = DATA_QUERY_ACTION
    display_name = "Data query"
    notification_display_name = "Data query"
    reference_model = "edc_data_manager.datamanagerquery"
    create_by_user = True
    show_link_to_changelist = True
    show_on_dashboard = True
    singleton = True
    admin_site_name = "edc_data_manager_admin"
    instructions = "Review and respond to the query"

    def close_action_item_on_save(self):
        if self.reference_obj and self.reference_obj.resolved == YES:
            return True
        return False


site_action_items.register(DataQueryAction)

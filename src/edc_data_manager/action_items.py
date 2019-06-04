from edc_action_item import ActionWithNotification, site_action_items


DATA_QUERY_ACTION = "data_query_action"


class DataQueryAction(ActionWithNotification):
    name = DATA_QUERY_ACTION
    display_name = "Data manager query"
    notification_display_name = "Data manager query"
    # parent_action_names = [AE_INITIAL_ACTION]
    reference_model = "edc_data_manager.datamanagerquery"
    # related_reference_model = "edc_data_manager.dataquery"
    # related_reference_fk_attr = "ae_initial"
    create_by_user = True
    show_link_to_changelist = True
    show_on_dashboard = False
    singleton = True
    admin_site_name = "edc_data_manager_admin"
    instructions = "Review and respond to the query"


site_action_items.register(DataQueryAction)

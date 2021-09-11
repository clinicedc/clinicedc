ACTION_ITEM = "ACTION_ITEM"
ACTION_ITEM_VIEW_ONLY = "ACTION_ITEM_VIEW_ONLY"
action_items_codenames = [
    "edc_action_item.add_actionitem",
    "edc_action_item.add_reference",
    "edc_action_item.change_actionitem",
    "edc_action_item.change_reference",
    "edc_action_item.delete_actionitem",
    "edc_action_item.delete_reference",
    "edc_action_item.view_actionitem",
    "edc_action_item.view_actiontype",
    "edc_action_item.view_historicalactionitem",
    "edc_action_item.view_historicalreference",
    "edc_action_item.view_reference",
    "edc_navbar.nav_action_item_section",
]


action_items_view_only_codenames = [
    c for c in action_items_codenames if "view_" in c or "edc_navbar" in c
]

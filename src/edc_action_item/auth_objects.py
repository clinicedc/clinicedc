ACTION_ITEM = "ACTION_ITEM"
ACTION_ITEM_EXPORT = "ACTION_ITEM_EXPORT"
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
]

navbar_codenames = [
    "edc_action_item.nav_action_item_section",
]

navbar_tuples = []
for codename in navbar_codenames:
    navbar_tuples.append((codename, f"Can access {codename.split('.')[1]}"))

action_items_codenames.extend(navbar_codenames)

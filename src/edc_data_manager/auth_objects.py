from edc_dashboard.auth_objects import dashboard_tuples

# group names
DATA_MANAGER = "DATA_MANAGER"
DATA_MANAGER_SUPER = "DATA_MANAGER_SUPER"
DATA_MANAGER_EXPORT = "DATA_MANAGER_EXPORT"
DATA_QUERY = "DATA_QUERY"
DATA_QUERY_VIEW = "DATA_QUERY_VIEW"
SITE_DATA_MANAGER = "SITE_DATA_MANAGER"

# role names
SITE_DATA_MANAGER_ROLE = "site_data_manager"
DATA_MANAGER_ROLE = "data_manager"

# codenames
data_manager = [
    "edc_data_manager.add_dataquery",
    "edc_data_manager.add_queryrule",
    "edc_data_manager.change_dataquery",
    "edc_data_manager.change_queryrule",
    "edc_data_manager.delete_dataquery",
    "edc_data_manager.delete_queryrule",
    "edc_data_manager.view_crfdatadictionary",
    "edc_data_manager.view_datadictionary",
    "edc_data_manager.view_datamanageractionitem",
    "edc_data_manager.view_datamanageruser",
    "edc_data_manager.view_dataquery",
    "edc_data_manager.view_historicaldatadictionary",
    "edc_data_manager.view_historicaldataquery",
    "edc_data_manager.view_historicalqueryrule",
    "edc_data_manager.view_queryrule",
    "edc_data_manager.view_querysubject",
    "edc_data_manager.view_queryuser",
    "edc_data_manager.view_queryvisitschedule",
    "edc_data_manager.view_requisitiondatadictionary",
    "edc_data_manager.view_requisitionpanel",
    "edc_data_manager.view_visitdatadictionary",
    "edc_metadata.view_crfmetadata",
    "edc_metadata.view_requisitionmetadata",
]

custom_codenames = [
    "edc_data_manager.nav_data_manager_section",
]

data_manager.extend(custom_codenames)

data_manager.extend([tpl[0] for tpl in dashboard_tuples])

data_query = [c for c in data_manager if ("view_" in c or "navbar" in c)]

custom_codename_tuples = []
for codename in custom_codenames:
    custom_codename_tuples.append((codename, f"Can access {codename.split('.')[1]}"))

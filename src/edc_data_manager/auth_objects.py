from edc_adverse_event.auth_objects import AE, TMG
from edc_auth import (
    ADMINISTRATION,
    CELERY_MANAGER,
    CLINIC,
    EVERYONE,
    PII,
    REVIEW,
    SCREENING,
)
from edc_dashboard.auth_objects import dashboard_tuples

# group names
DATA_MANAGER = "DATA_MANAGER"
DATA_QUERY = "DATA_QUERY"
SITE_DATA_MANAGER = "SITE_DATA_MANAGER"

# codenames
data_manager = [
    "edc_crf.view_crfstatus",
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
    "edc_navbar.nav_data_manager_section",
]

data_manager.extend([tpl[0] for tpl in dashboard_tuples])


data_query = [
    "edc_crf.view_crfstatus",
    "edc_data_manager.change_dataquery",
    "edc_data_manager.view_crfdatadictionary",
    "edc_data_manager.view_queryrule",
    "edc_data_manager.view_datadictionary",
    "edc_data_manager.view_datamanageractionitem",
    "edc_data_manager.view_datamanageruser",
    "edc_data_manager.view_dataquery",
    "edc_data_manager.view_historicalqueryrule",
    "edc_data_manager.view_historicaldatadictionary",
    "edc_data_manager.view_historicaldataquery",
    "edc_data_manager.view_querysubject",
    "edc_data_manager.view_queryuser",
    "edc_data_manager.view_queryvisitschedule",
    "edc_data_manager.view_requisitiondatadictionary",
    "edc_data_manager.view_requisitionpanel",
    "edc_data_manager.view_visitdatadictionary",
    "edc_navbar.nav_data_manager_section",
]

# role names
SITE_DATA_MANAGER_ROLE = "site_data_manager"
DATA_MANAGER_ROLE = "data_manager"

# roles
data_manager_role_group_names = [
    ADMINISTRATION,
    AE,
    TMG,
    CELERY_MANAGER,
    CLINIC,
    DATA_MANAGER,
    EVERYONE,
    PII,
    REVIEW,
    SCREENING,
]

site_data_manager_role_group_names = [ADMINISTRATION, EVERYONE, REVIEW, SITE_DATA_MANAGER]

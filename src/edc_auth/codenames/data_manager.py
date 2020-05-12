from .dashboard import dashboard

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

data_manager.extend(dashboard)

from .action_items import action_items

clinic = [
    "edc_appointment.add_appointment",
    "edc_appointment.change_appointment",
    "edc_appointment.view_appointment",
    "edc_appointment.view_historicalappointment",
    "edc_crf.view_crfstatus",
    "edc_dashboard.view_subject_listboard",
    "edc_dashboard.view_subject_review_listboard",
    "edc_navbar.nav_subject_section",
    "edc_offstudy.add_subjectoffstudy",
    "edc_offstudy.change_subjectoffstudy",
    "edc_offstudy.delete_subjectoffstudy",
    "edc_offstudy.view_historicalsubjectoffstudy",
    "edc_offstudy.view_subjectoffstudy",
]

clinic.extend(action_items)

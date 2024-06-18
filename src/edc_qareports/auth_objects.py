# group names
QA_REPORTS = "QA_REPORTS"

# role names
QA_REPORTS_ROLE = "qa_reports_role"

qa_reports_codenames = [
    "edc_qareports.add_qareportnote",
    "edc_qareports.change_qareportnote",
    "edc_qareports.delete_qareportnote",
    "edc_qareports.view_qareportnote",
]


custom_codenames = [
    "edc_qareports.nav_qareports_section",
]

qa_reports_codenames.extend(custom_codenames)

custom_codename_tuples = []
for codename in custom_codenames:
    custom_codename_tuples.append((codename, f"Can access {codename.split('.')[1]}"))

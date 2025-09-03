from edc_lab import LabProfile
from edc_lab_panel.panels import (
    blood_glucose_panel,
    fbc_panel,
    hba1c_panel,
    hba1c_poc_panel,
    lft_panel,
    lipids_panel,
    rft_panel,
)

lab_profile = LabProfile(
    name="lab_profile",
    requisition_model="tests.subjectrequisition",
    reference_range_collection_name="my_reportables",
)

lab_profile.add_panel(fbc_panel)
lab_profile.add_panel(blood_glucose_panel)
lab_profile.add_panel(hba1c_panel)
lab_profile.add_panel(hba1c_poc_panel)
lab_profile.add_panel(lipids_panel)
lab_profile.add_panel(lft_panel)
lab_profile.add_panel(rft_panel)

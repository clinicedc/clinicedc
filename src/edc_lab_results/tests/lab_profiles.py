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

subject_lab_profile = LabProfile(
    name="subject_lab_profile",
    requisition_model="edc_metadata.subjectrequisition",
    reference_range_collection_name="my_reportables",
)

subject_lab_profile.add_panel(fbc_panel)
subject_lab_profile.add_panel(blood_glucose_panel)
subject_lab_profile.add_panel(hba1c_panel)
subject_lab_profile.add_panel(hba1c_poc_panel)
subject_lab_profile.add_panel(lipids_panel)
subject_lab_profile.add_panel(lft_panel)
subject_lab_profile.add_panel(rft_panel)

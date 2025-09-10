from edc_lab import LabProfile
from edc_lab_panel.panels import rft_panel

lab_profile = LabProfile(
    name="my_lab_profile",
    requisition_model="egfr_app.subjectrequisition",
    reference_range_collection_name="my_reference_list",
)

lab_profile.add_panel(rft_panel)

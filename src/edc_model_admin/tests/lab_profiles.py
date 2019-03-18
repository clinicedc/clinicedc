from edc_lab import LabProfile, RequisitionPanel, AliquotType
from edc_lab import ProcessingProfile

wb = AliquotType(name="Whole Blood", alpha_code="WB", numeric_code="02")


fbc_processing = ProcessingProfile(name="FBC", aliquot_type=wb)

panel_one = RequisitionPanel(
    name="one", verbose_name="One", processing_profile=fbc_processing
)

panel_two = RequisitionPanel(
    name="two", verbose_name="Two", processing_profile=fbc_processing
)

lab_profile = LabProfile(
    name="lab_profile", requisition_model="edc_model_admin.requisition"
)

lab_profile.add_panel(panel_one)
lab_profile.add_panel(panel_two)

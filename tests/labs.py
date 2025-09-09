from django.conf import settings

from edc_lab import bc, LabProfile, pl, Process, site_labs
from edc_lab_panel.panels import fbc_panel, lft_panel, rft_panel, vl_panel

lab_profile = LabProfile(
    name="lab_profile",
    requisition_model=settings.SUBJECT_REQUISITION_MODEL,
    reference_range_collection_name="my_reportables",
)

lab_profile.add_panel(fbc_panel)
lab_profile.add_panel(lft_panel)
lab_profile.add_panel(rft_panel)

vl_pl_process = Process(aliquot_type=pl, aliquot_count=4)
vl_bc_process = Process(aliquot_type=bc, aliquot_count=2)
vl_panel.processing_profile.add_processes(vl_pl_process, vl_bc_process)
lab_profile.add_panel(vl_panel)

site_labs.register(lab_profile)

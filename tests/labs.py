from django.conf import settings

from edc_lab import LabProfile, site_labs
from edc_lab_panel.panels import fbc_panel, lft_panel, rft_panel

lab_profile = LabProfile(
    name="lab_profile",
    requisition_model=settings.SUBJECT_REQUISITION_MODEL,
    reference_range_collection_name="my_reportables",
)

lab_profile.add_panel(fbc_panel)
lab_profile.add_panel(lft_panel)
lab_profile.add_panel(rft_panel)

site_labs.register(lab_profile)

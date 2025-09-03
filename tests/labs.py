from django.conf import settings

from edc_lab import LabProfile
from edc_lab_panel.panels import fbc_panel

lab_profile = LabProfile(
    name="subject_lab_profile",
    requisition_model=settings.SUBJECT_REQUISITION_MODEL,
    reference_range_collection_name="effect",
)

lab_profile.add_panel(fbc_panel)

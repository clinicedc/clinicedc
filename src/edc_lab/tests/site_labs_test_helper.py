from edc_lab.lab import (
    AliquotType,
    RequisitionPanel,
    Process,
    ProcessingProfile,
    LabProfile,
)
from edc_lab.site_labs import site_labs


class SiteLabsTestHelper:
    def __init__(self):
        self.profile_aliquot_count = None
        self.panel = None
        self.lab_profile = None

    requisition_model = "edc_lab.subjectrequisition"

    def setup_site_labs(self):
        """Sets up the site_lab global.
        """
        site_labs._registry = {}
        site_labs.loaded = False

        self.profile_aliquot_count = 3

        # create aliquots and their relationship
        a = AliquotType(name="aliquot_a", numeric_code="55", alpha_code="AA")
        b = AliquotType(name="aliquot_b", numeric_code="66", alpha_code="BB")
        a.add_derivatives(b)

        # set up processes
        process = Process(aliquot_type=b, aliquot_count=self.profile_aliquot_count)
        processing_profile = ProcessingProfile(name="process", aliquot_type=a)
        processing_profile.add_processes(process)

        # create a panel
        self.panel = RequisitionPanel(
            name="panel", processing_profile=processing_profile
        )

        # lab profile
        self.lab_profile = LabProfile(
            name="lab_profile", requisition_model=self.requisition_model
        )
        self.lab_profile.add_panel(self.panel)

        # register with site
        site_labs.register(lab_profile=self.lab_profile)

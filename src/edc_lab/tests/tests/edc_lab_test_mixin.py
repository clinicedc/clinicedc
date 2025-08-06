from edc_lab import RequisitionPanelGroup
from edc_lab.lab import AliquotType, Process, ProcessingProfile, RequisitionPanel


class EdcLabTestMixin:
    @staticmethod
    def get_panel_group():
        a = AliquotType(name="aliquot_a", numeric_code="55", alpha_code="AA")
        b = AliquotType(name="aliquot_b", numeric_code="66", alpha_code="BB")
        a.add_derivatives(b)
        process = Process(aliquot_type=b, aliquot_count=3)
        processing_profile = ProcessingProfile(name="process", aliquot_type=a)
        processing_profile.add_processes(process)
        rft_panel = RequisitionPanel(
            name="chemistry_rft",
            verbose_name="Chemistry: Renal Function Tests",
            abbreviation="RFT",
            processing_profile=processing_profile,
            utest_ids=["urea", "creatinine", "uric_acid", "egfr"],
        )

        lipids_panel = RequisitionPanel(
            name="chemistry_lipids",
            verbose_name="Chemistry: Lipids",
            abbreviation="LIPIDS",
            processing_profile=processing_profile,
            utest_ids=["ldl", "hdl", "trig"],
        )

        lft_panel = RequisitionPanel(
            name="chemistry_lft",
            verbose_name="Chemistry: Liver Function Tests",
            abbreviation="LFT",
            processing_profile=processing_profile,
            utest_ids=["ast", "alt", "alp", "amylase", "ggt", "albumin"],
        )

        return RequisitionPanelGroup(
            lft_panel,
            rft_panel,
            lipids_panel,
            name="chemistry",
            verbose_name="Chemistry: LFT, RFT, Lipids",
            reference_range_collection_name="default",
        )

from typing import Optional

from .processing_profile import ProcessingProfile
from .requisition_panel import RequisitionPanel


class RequisitionPanelGroupError(Exception):
    pass


class RequisitionPanelGroup(RequisitionPanel):
    def __init__(
        self,
        *panels,
        name: Optional[str] = None,
        verbose_name: Optional[str] = None,
        abbreviation: Optional[str] = None,
        is_poc: Optional[bool] = None,
        reference_range_collection_name: Optional[str] = None,
    ):
        processing_profile = ProcessingProfile(
            name=f"{name} group", aliquot_type=panels[0].aliquot_type
        )
        utest_ids = []
        for panel in panels:
            utest_ids.extend(panel.utest_ids)
            if (
                panel.reference_range_collection_name
                and reference_range_collection_name != panel.reference_range_collection_name
            ):
                raise RequisitionPanelGroupError(
                    "Panels in a panel group must use the same reference range "
                    f"collection name. Got "
                    f"{reference_range_collection_name} != "
                    f"{panel.reference_range_collection_name}. "
                    f"See {self}."
                )
            if panel.aliquot_type and panel.aliquot_type != processing_profile.aliquot_type:
                raise RequisitionPanelGroupError(
                    "Panels in a panel group must use the same aliquot_type "
                    f"Got {panel.aliquot_type} != "
                    f"{panel.processing_profile.aliquot_type}. "
                    f"See {self}."
                )
        super().__init__(
            utest_ids=utest_ids,
            processing_profile=processing_profile,
            name=name,
            verbose_name=verbose_name,
            abbreviation=abbreviation,
            is_poc=is_poc,
            reference_range_collection_name=reference_range_collection_name,
        )

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    def __str__(self):
        return self.verbose_name or self.name

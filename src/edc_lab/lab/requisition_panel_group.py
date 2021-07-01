class RequisitionPanelGroupError(Exception):
    pass


class RequisitionPanelGroup:
    requisition_model = None
    lab_profile_name = None

    def __init__(
        self,
        *panels,
        name: str = None,
        verbose_name: str = None,
        reference_range_collection_name=None,
    ):
        self.aliquot_type = None
        self.reference_range_collection_name = None
        self.utest_ids = []

        self.name = name
        self.panels = panels
        self.reference_range_collection_name = reference_range_collection_name
        self.verbose_name = verbose_name
        if not reference_range_collection_name:
            raise RequisitionPanelGroupError(
                "Expected `reference_range_collection_name`. Got None"
            )
        for panel in panels:
            self.utest_ids.extend(panel.utest_ids)
            if (
                panel.reference_range_collection_name
                and self.reference_range_collection_name
                != panel.reference_range_collection_name
            ):
                raise RequisitionPanelGroupError(
                    "Panels in a panel group must use the same reference range "
                    f"collection name. Got "
                    f"{self.reference_range_collection_name} != "
                    f"{panel.reference_range_collection_name}. "
                    f"See {self}."
                )
            panel.reference_range_collection_name = self.reference_range_collection_name
            if not self.aliquot_type:
                self.aliquot_type = panel.processing_profile.aliquot_type
            else:
                if self.aliquot_type != panel.processing_profile.aliquot_type:
                    raise RequisitionPanelGroupError(
                        "Panels in a panel group must use the same aliquot_type "
                        f"Got {self.aliquot_type} != "
                        f"{panel.processing_profile.aliquot_type}. "
                        f"See {self}."
                    )

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    def __str__(self):
        return self.verbose_name or self.name

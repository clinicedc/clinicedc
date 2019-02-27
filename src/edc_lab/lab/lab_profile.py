class PanelAlreadyRegistered(Exception):
    pass


class LabProfileRequisitionModelError(Exception):
    pass


class LabProfile:

    """A container class for aliquot types, panels and processing.
    """

    site_model = "sites.site"

    def __init__(self, name=None, requisition_model=None):
        self.aliquot_types = {}
        self.processing_profiles = {}
        self.panels = {}
        self.name = name
        if not requisition_model:
            raise LabProfileRequisitionModelError("Invalid requisition model. Got None")
        self.requisition_model = requisition_model

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"

    def __str__(self):
        return self.name

    def add_panel(self, panel=None):
        """Adds a panel instance to the profile.

        If site_id specified, will only add if site_id matches
        the current site_id.
        """
        panel.requisition_model = self.requisition_model
        panel.lab_profile_name = self.name
        if panel.name in self.panels:
            raise PanelAlreadyRegistered(f"Panel already registered. Got {panel.name}")
        self.panels.update({panel.name: panel})
        self.processing_profiles.update(
            {panel.processing_profile.name: panel.processing_profile}
        )
        self.aliquot_types.update({panel.name: panel})
        self.aliquot_types.update({panel.numeric_code: panel})
        self.aliquot_types.update({panel.alpha_code: panel})

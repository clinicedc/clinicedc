from .get_model_cls import GetModelCls, GetModelError


class PanelAlreadyRegistered(Exception):
    pass


class LabProfileRequisitionModelError(Exception):
    pass


class LabProfile:

    """A container class for panels.

    Added panels must have a matching requisition_model.
    """
    model_cls = GetModelCls

    def __init__(self, name=None, requisition_model=None):
        self._get_requisition_model = self.model_cls(
            model=requisition_model).get_model
        self.name = name
        self.aliquot_types = {}
        self.processing_profiles = {}
        self.panels = {}

    def __repr__(self):
        return f'{self.__class__.__name__}(name={self.name})'

    def __str__(self):
        return self.name

    @property
    def requisition_model(self):
        try:
            return self._get_requisition_model()
        except GetModelError as e:
            raise LabProfileRequisitionModelError(e) from e

    def add_panel(self, panel=None):
        """Adds a panel instance to the profile.
        """
        if panel.model != self.requisition_model:
            raise LabProfileRequisitionModelError(
                f'Invalid requisition model when adding panel {panel} '
                f'to {repr(self)}. Got  {panel.model}')
        if panel.name in self.panels:
            raise PanelAlreadyRegistered(
                f'Panel already registered. Got {panel.name}')
        self.panels.update({panel.name: panel})
        self.processing_profiles.update(
            {panel.processing_profile.name: panel.processing_profile})
        self.aliquot_types.update({panel.name: panel})
        self.aliquot_types.update({panel.numeric_code: panel})
        self.aliquot_types.update({panel.alpha_code: panel})

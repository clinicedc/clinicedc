from ..exceptions import AlreadyRegistered


class LabProfile:

    def __init__(self, name):
        self.name = name
        self.aliquot_types = {}
        self.processing_profiles = {}
        self.panels = {}

    def add_aliquot_type(self, aliquot_type):
        if aliquot_type.name in self.aliquot_types:
            raise AlreadyRegistered(
                'Aliquot type already registered. Got {}'.format(
                    aliquot_type.name))
        self.aliquot_types.update({aliquot_type.name: aliquot_type})
        self.aliquot_types.update({aliquot_type.numeric_code: aliquot_type})
        self.aliquot_types.update({aliquot_type.alpha_code: aliquot_type})

    def add_processing_profile(self, processing_profile):
        if processing_profile.name in self.processing_profiles:
            raise AlreadyRegistered(
                'Processing profile already registered. '
                'Got {}'.format(processing_profile.name))
        self.processing_profiles.update(
            {processing_profile.name: processing_profile})

    def add_panel(self, panel):
        if panel.name in self.panels:
            raise AlreadyRegistered(
                'Panel already registered. Got {}'.format(panel.name))
        self.panels.update({panel.name: panel})

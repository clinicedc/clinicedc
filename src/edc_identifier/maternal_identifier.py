from .infant_identifier import InfantIdentifier
from .subject_identifier import SubjectIdentifier


class MaternalIdentifier(SubjectIdentifier):

    def __init__(self, *args, **kwargs):
        self.infants = []
        super(MaternalIdentifier, self).__init__(*args, **kwargs)

    @property
    def name(self):
        return 'maternalidentifier'

    def deliver(self, live_infants, model):
        for n in range(0, live_infants):
            self.infants.append(
                InfantIdentifier(
                    maternal_identifier=self.identifier,
                    model=model,
                    birth_order=n,
                    live_infants=live_infants))

from .infant_identifier import InfantIdentifier
from .subject_identifier import SubjectIdentifier
from .models import IdentifierModel


class MaternalIdentifierError(Exception):
    pass


class MaternalIdentifier(SubjectIdentifier):

    def __init__(self, **kwargs):
        self.infants = []
        super(MaternalIdentifier, self).__init__(**kwargs)
        for obj in IdentifierModel.objects.filter(linked_identifier=self.identifier):
            self.infants.append(InfantIdentifier(identifier=obj.identifier))

    @property
    def name(self):
        return 'maternalidentifier'

    def deliver(self, live_infants, model, create_registration=None, **kwargs):
        if self.infants:
            raise MaternalIdentifierError('Infant identifiers already created for this mother. Got \'{}\''.format(
                '\', \''.join([infant_identifier.identifier for infant_identifier in self.infants])))
        else:
            for n in range(0, live_infants):
                self.infants.append(
                    InfantIdentifier(
                        maternal_identifier=self.identifier,
                        model=model,
                        birth_order=n,
                        live_infants=live_infants,
                        create_registration=create_registration,
                        **kwargs))

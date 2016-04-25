from django.db.models import get_model

from ...exceptions import IdentifierError
from ...models import SubjectIdentifier

from .base_subject_identifier import BaseSubjectIdentifier


class InfantIdentifier(BaseSubjectIdentifier):

    """ Creates an infant identifier derived from the maternal identifier, considers the number of infants
    during this registration session and their birth order and returns a dictionary {infant order: identifier}.

    Usage::
        >>>    if obj.live_infants_to_register > 0:
        >>>        #Allocate Infant Identifier
        >>>        infant_identifier = InfantIdentifier()
        >>>        for self.infant_order in range(0, obj.live_infants_to_register):
        >>>            infant_identifier.get_identifier(
        >>>                add_check_digit=False,
        >>>                is_derived=True,
        >>>                maternal_identifier=obj.maternal_visit.appointment.registered_subject.subject_identifier,
        >>>                maternal_study_site=obj.maternal_visit.appointment.registered_subject.study_site,
        >>>                user=request.user,
        >>>                birth_order=self.infant_order,
        >>>                live_infants=obj.live_infants,
        >>>                live_infants_to_register=obj.live_infants_to_register)
    """

    def __init__(self, maternal_identifier, study_site, birth_order,
                 live_infants, live_infants_to_register, user=None):
        self.birth_order = birth_order
        self.live_infants = live_infants
        self.live_infants_to_register = live_infants_to_register
        self.study_site = study_site
        self.subject_type = 'infant'
        self.user = user
        template = "{maternal_identifier}-{suffix}"
        self.maternal_identifier = maternal_identifier
        try:
            SubjectIdentifier.objects.get(identifier=self.maternal_identifier)
        except SubjectIdentifier.DoesNotExist:
            raise IdentifierError(
                'Maternal_identifier {0} does not exist. See model SubjectIdentifier'.format(
                    self.maternal_identifier))
        if self.live_infants_to_register == 0:
            raise IdentifierError("Number of live_infants_to_register may not be 0!.")
        if self.live_infants_to_register > self.live_infants:
            raise IdentifierError(
                'Number of infants to register ({0}) may not exceed '
                'number of live infants ({1}).'.format(self.live_infants_to_register, self.live_infants))
        if self.birth_order > self.live_infants:
            raise IdentifierError("Invalid birth order if number of live infants is {0}.".format(self.live_infants))
        super(InfantIdentifier, self).__init__(
            template=template, site_code=study_site,
            is_derived=True, add_check_digit=False)

    def format_options(self, **kwargs):
        format_options = super(InfantIdentifier, self).format_options(**kwargs)
        format_options.update(
            maternal_identifier=self.maternal_identifier,
            suffix=self.suffix())
        return format_options

    def suffix(self):
        """ Return a two digit suffix based on the number of live infants.

        In the case of twins, triplets, ... will be incremented by 10's
        during registration for each subsequent infant registered.
        """

        if self.live_infants == 1:
            suffix = 10  # singlet 10
        elif self.live_infants == 2:
            suffix = 25  # twins 25,26
        elif self.live_infants == 3:
            suffix = 36  # triplets 36,37,38
        elif self.live_infants == 4:
            suffix = 47  # quadruplets 47,48,49,50
        else:
            raise TypeError(
                'Ensure number of infants is greater than 0 and less than '
                'or equal to 4. You wrote %s' % (self.live_infants))
        suffix += (self.birth_order) * 10
        return suffix

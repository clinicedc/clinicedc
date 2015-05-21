from datetime import datetime

from django.apps import apps

from ..exceptions import IdentifierError
from ..models import SubjectIdentifier

from . import BaseIdentifier


class InfantIdentifier(BaseIdentifier):

    """ Creates an infant edc_identifier derived from the maternal edc_identifier.

    - considers the number of infants during this registration session and
      their birth order and returns a dictionary {infant order: edc_identifier}.

    Usage::
        >>> if not change:
        >>>    obj.user_created = request.user
        >>>    obj.save()
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
        >>>                live_infants_to_register=obj.live_infants_to_register,
        >>>                subject_type='infant')
    """

    def __init__(self, maternal_identifier, study_site, birth_order, live_infants,
                 live_infants_to_register, user=None):
        self.subject_type = 'infant'
        self.birth_order = birth_order
        self.live_infants = live_infants
        self.live_infants_to_register = live_infants_to_register
        self.maternal_identifier = maternal_identifier
        self.study_site = study_site
        self.user = user
        identifier_format = "{maternal_identifier}-{suffix}"
        super(InfantIdentifier, self).__init__(
            identifier_format=identifier_format, site_code=study_site.site_code, is_derived=True,
            add_check_digit=False)

    def consent_required(self):
        return False

    def get_identifier_prep(self, **kwargs):
        """Prepares to create an edc_identifier consisting of the the maternal edc_identifier and a
        suffix determined by the number of live infants from this delivery.

        For example:
          maternal_identifier=056-19800001-3 -> 2 live infants -> 056-19800001-3-
          """
        options = {}
#         birth_order = kwargs.get('birth_order')
#         live_infants = kwargs.get('live_infants')
#         live_infants_to_register = kwargs.get('live_infants_to_register')
        # maternal edc_identifier should exist in SubjectIdentifier
        if not SubjectIdentifier.objects.filter(identifier=self.maternal_identifier):
            raise IdentifierError('Unknown maternal_identifier {0}.'.format(self.maternal_identifier))
        # some checks on logic of live and live to register
        if self.live_infants_to_register == 0:
            raise IdentifierError("Number of live_infants_to_register may not be 0!.")
        if self.live_infants_to_register > self.live_infants:
            raise IdentifierError(
                'Number of infants to register ({0}) may not exceed '
                'number of live infants ({1}).'.format(
                    self.live_infants_to_register, self.live_infants))
        if self.birth_order > self.live_infants:
            raise IdentifierError(
                "Invalid birth order if number of live infants is {0}.".format(self.live_infants))
        options.update(
            maternal_identifier=self.maternal_identifier,
            suffix=self._get_suffix())
        return options

    def get_identifier_post(self, new_identifier, **kwargs):
        """ Updates registered subject after a new subject edc_identifier is created."""
        RegisteredSubject = apps.get_model('registration', 'registeredsubject')
        RegisteredSubject.objects.using(self.using).create(
            subject_identifier=new_identifier,
            registration_datetime=datetime.now(),
            subject_type=self.subject_type,
            user_created=self.user,
            created=datetime.now(),
            first_name='',
            initials='',
            registration_status='registered',
            relative_identifier=self.maternal_identifier,
            study_site=self.study_site)
        return new_identifier

    def _get_suffix(self):
        """ Returns a suffix for the edc_identifier."""
        suffix = self._get_base_suffix()
        suffix += (self.birth_order) * 10
        return suffix

    def _get_base_suffix(self):
        """ Return a two digit suffix based on the number of live infants.

        In the case of twins, triplets, ... will be incremented
        by 10's during registration for each subsequent infant registered.
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
                'Ensure number of infants is greater than 0 and less than or '
                'equal to 4. You wrote %s' % (self.live_infants))
        return suffix

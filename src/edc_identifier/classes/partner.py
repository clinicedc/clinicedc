from datetime import datetime

from django.apps import apps
from django.forms import ValidationError

from ..models import SubjectIdentifier, DerivedSubjectIdentifier


class Partner(object):
    """ Create the subject edc_identifier for a partner by calling get_identifier() with the index subject edc_identifier. """
    def __init__(self):
        raise TypeError('This class is broken')

    def get_identifier_prep(self, index_identifier, subject_type="partner", **kwargs):
        """ Just add a -10 to the index edc_identifier and register.

        * Probably not creating the edc_identifier because of a consent
        * Subject Identifier is derived from the index edc_identifier so the

        SubjectIdentifier model is referenced but not updated."""

        if not SubjectIdentifier.objects.filter(identifier=index_identifier):
            raise ValidationError('Unknown index_identifier {0}.'.format(index_identifier))
        subject_identifier = "{0}-10".format(index_identifier)
        # create/save to DerivedSubjectIdentifier
        DerivedSubjectIdentifier.objects.create(subject_identifier=subject_identifier,
                                                base_identifier=index_identifier)
        RegisteredSubject = apps.get_model('registration', 'registeredsubject')
        if not RegisteredSubject.objects.filter(relative_identifier=index_identifier):
#            RegisteredSubject.objects.update_with(consent, )
            RegisteredSubject.objects.create(
                relative_identifier=index_identifier,
                subject_identifier=subject_identifier,
                registration_datetime=datetime.now(),
                subject_type=subject_type,
                created=datetime.now(),
                first_name=kwargs.get('first_name'),
                initials=kwargs.get('initials'),
                registration_status='not_contacted',
                study_site=kwargs.get('site'),
                )
        else:
            ValidationError('A partner has already been registered for index {}'.format(index_identifier))

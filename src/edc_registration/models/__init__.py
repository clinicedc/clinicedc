from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .base_registered_subject_model import BaseRegisteredSubjectModel
from .base_registration_model import BaseRegistrationModel
from .registered_subject import RegisteredSubject
from .subject_identifier_audit_trail import SubjectIdentifierAuditTrail


if 'MAX_SUBJECTS' not in dir(settings):
    raise ImproperlyConfigured(
        'Missing settings attribute MAX_SUBJECTS. Please add settings attribute '
        'MAX_SUBJECTS = to your settings file.')

import re

from edc_base.model.models import BaseUuidModel

from django.core.validators import RegexValidator
from django.db import models
from django_crypto_fields.fields import FirstnameField, LastnameField, EncryptedCharField

from edc_base.model.fields import IsDateEstimatedField
from edc_base.model.validators import dob_not_future, MinConsentAge, MaxConsentAge
from edc_constants.choices import GENDER_UNDETERMINED

from ..managers import BaseSubjectManager


#  
# from uuid import uuid4
#  
# from django.conf import settings
# from django.db.models import get_model
# from django.utils.translation import ugettext_lazy as _
#  
#  
# if 'edc.device.dispatch' in settings.INSTALLED_APPS:
#     from edc.device.dispatch.models import BaseDispatchSyncUuidModel as BaseSyncUuidModel
# else:
#      
# 
# from edc.choices.common import GENDER_UNDETERMINED
# 
# 
# from edc.core.crypto_fields.fields import (EncryptedFirstnameField, EncryptedLastnameField,
#                                            EncryptedCharField)
# from edc_subject.consent.exceptions import ConsentError
# from edc.core.identifier.exceptions import IdentifierError
# 


class BaseSubject (BaseUuidModel):
    """Base for consent and registered subject models.

    .. note:: the field subject_identifier_as_pk is in both
              models but the values are independent; that
              is, consent.subject_identifier_as_pk !=
              registered_subject.subject_identifier_as_pk.
    """

    # a signal changes subject identifier which messes up bhp_sync
    # this field is always available and is unique
    subject_identifier_as_pk = models.CharField(
        verbose_name="Subject Identifier as pk",
        max_length=50,
        null=True,
        db_index=True,
        )

    subject_identifier_aka = models.CharField(
        verbose_name="Subject Identifier a.k.a",
        max_length=50,
        null=True,
        editable=False,
        help_text='track a previously allocated identifier.'
        )

    dm_comment = models.CharField(
        verbose_name="Data Management comment",
        max_length=150,
        null=True,
        editable=False,
        help_text='see also edc.data manager.'
        )

    # may not be available when instance created (e.g. infants prior to birth report)
    first_name = FirstnameField(
        null=True,
        )

    # may not be available when instance created (e.g. infants or household subject before consent)
    last_name = LastnameField(
        verbose_name="Last name",
        null=True,
        )

    # may not be available when instance created (e.g. infants)
    initials = EncryptedCharField(
        validators=[RegexValidator(regex=r'^[A-Z]{2,3}$',
                                   message=('Ensure initials consist of letters '
                                            'only in upper case, no spaces.')), ],
        null=True,
        )

    dob = models.DateField(
        verbose_name=_("Date of birth"),
        validators=[
            dob_not_future,
            MinConsentAge,
            MaxConsentAge,
            ],
        null=True,
        blank=False,
        help_text=_("Format is YYYY-MM-DD"),
        )

    is_dob_estimated = IsDateEstimatedField(
        verbose_name=_("Is date of birth estimated?"),
        null=True,
        blank=False,
        )

    gender = models.CharField(
        verbose_name="Gender",
        choices=GENDER_UNDETERMINED,
        max_length=1,
        null=True,
        blank=False,
        )

    subject_type = models.CharField(
        max_length=25,
        null=True,
        )
 
    objects = BaseSubjectManager()
 
#     def get_subject_identifier(self):
#         return self.subject_identifier
# 
#     def is_registered_subject(self):
#         if self._meta.object_name == 'RegisteredSubject':
#             return True
#         return False
# 
# #     def _get_or_created_registered_subject(self, using):
# #         registered_subject = None
# #         if 'registered_subject' in dir(self):
# #             if self.registered_subject:
# #                 registered_subject = self.registered_subject
# #         if not registered_subject:
# #             RegisteredSubject = get_model('registration', 'registeredsubject')
# #             try:
# #                 registered_subject = RegisteredSubject.objects.using(using).get(
# #                     subject_identifier=self.subject_identifier)
# #                 self._update_registered_subject(using, registered_subject)
# #             except RegisteredSubject.DoesNotExist:
# #                 options = self._get_registered_subject_options()
# #                 registered_subject = RegisteredSubject.objects.using(using).create(
# #                     subject_identifier=self.subject_identifier, **options)
# #         return registered_subject
# 
#     def post_save_get_or_create_registered_subject(self, **kwargs):
#         """Creates or \'gets and updates\' the registered
#         subject instance for this subject.
# 
#         Called by a post save signal.
# 
#         ..note:: RegisteredSubject also inherits from BaseSubject.
#                  This method does nothing if \'self\' is an
#                  instance of RegisteredSubject.
#         ..note:: 'self' may not have an attribute registered_subject
#                  or the attribute may not be set.
#         """
#         using = kwargs.get('using')
#         updated = False
#         registered_subject = None
#         # skip if self is an instance of RegisteredSubject
#         if not self.is_registered_subject():
#             if 'registered_subject' in dir(self):
#                 if not self.registered_subject:
#                     registered_subject = self._get_or_created_registered_subject(using)
#                     self.registered_subject = registered_subject
#                     updated = True
#                 else:
#                     registered_subject = self._update_registered_subject(using)
#             else:
#                 # self does not have a foreign key to RegisteredSubject but RegisteredSubject
#                 # still needs to be created or updated
#                 registered_subject = self._get_or_created_registered_subject(using)
#         return registered_subject, updated
# 
#     def get_subject_type(self):
#         """Returns a subject type.
#         Usually overridden.
# 
#         ..note:: this is important for the link between
#                  dashboard and membership form category."""
# 
#         return self.subject_type
# 
#     def save(self, *args, **kwargs):
#         using = kwargs.get('using')
#         self.subject_type = self.get_subject_type()
#         self.insert_dummy_identifier()
#         self._check_if_duplicate_subject_identifier(using)
#         self.check_if_may_change_subject_identifier(using)
#         # if editing, confirm that identifier fields are not changed
#         if self.id:
#             if self.get_user_provided_subject_identifier_attrname():
#                 if not self.subject_identifier == getattr(
#                         self, self.get_user_provided_subject_identifier_attrname()):
#                     raise IdentifierError('Identifier field {0} cannot be changed.'.format(
#                         self.get_user_provided_subject_identifier_attrname()))
#         if not self.id:
#             if self.get_user_provided_subject_identifier_attrname():
#                 # if user_provided_subject_identifier is None, set it to the same value as subject_identifier
#                 if not getattr(self, self.get_user_provided_subject_identifier_attrname()):
#                     setattr(self, self.get_user_provided_subject_identifier_attrname(), self.subject_identifier)
#         super(BaseSubject, self).save(*args, **kwargs)
# 
#     def __unicode__(self):
#         return "{0} {1}".format(self.mask_unset_subject_identifier(), self.subject_type)
# 
#     def natural_key(self):
#         return (self.subject_identifier_as_pk, )
# 
#     def mask_unset_subject_identifier(self):
#         subject_identifier = self.subject_identifier
#         re_pk = re.compile('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}')
#         if re_pk.match(subject_identifier):
#             subject_identifier = '<identifier not set>'
#         return subject_identifier
# 
#     def _get_user_provided_subject_identifier(self):
#         """Return a user provided subject_identifier.
# 
#         Do not override."""
#         if self.get_user_provided_subject_identifier_attrname() in dir(self):
#             return getattr(self, self.get_user_provided_subject_identifier_attrname())
#         else:
#             return None
# 
#     def get_user_provided_subject_identifier_attrname(self):
#         """Override to return the attribute name of the user provided subject_identifier."""
#         return None
# 
#     def include_for_dispatch(self):
#         return True
# 
#     def check_if_may_change_subject_identifier(self, using):
#         if self.id:
#             if not self.__class__.objects.get(pk=self.id).subject_identifier == self.subject_identifier:
#                 raise IdentifierError('Subject Identifier cannot be changed. '
#                                       'Got {0} != {1}'.format(
#                                           self.__class__.objects.get(pk=self.id).subject_identifier,
#                                           self.subject_identifier))
# 
#     def _check_if_duplicate_subject_identifier(self, using):
#         """Checks if the subject identifier is in use, for new and existing instances."""
#         if not self.pk and self.subject_identifier:
#             if self.__class__.objects.using(using).filter(subject_identifier=self.subject_identifier):
#                 raise IdentifierError('Attempt to insert duplicate value for '
#                                       'subject_identifier {0} when saving {1} '
#                                       'on add.'.format(self.subject_identifier, self))
#         else:
#             if self.__class__.objects.using(using).filter(
#                     subject_identifier=self.subject_identifier).exclude(pk=self.pk):
#                 raise IdentifierError('Attempt to insert duplicate value for '
#                                       'subject_identifier {0} when saving {1} '
#                                       'on change.'.format(self.subject_identifier, self))
#         self.check_for_duplicate_subject_identifier()
# 
#     def check_for_duplicate_subject_identifier(self):
#         """Users may override to add an additional strategy to detect duplicate identifiers."""
#         pass
# 
#     def insert_dummy_identifier(self):
#         """Inserts a random uuid as a dummy identifier for a new instance.
# 
#         Model uses subject_identifier_as_pk as a natural key for
#         serialization/deserialization. Value must not change once set."""
# 
#         # set to uuid if new and not specified
#         if not self.id:
#             subject_identifier_as_pk = str(uuid4())
#             self.subject_identifier_as_pk = subject_identifier_as_pk  # this will never change
#             if not self.subject_identifier:
#                 # this will be changed when allocated a subject_identifier on consent
#                 self.subject_identifier = subject_identifier_as_pk
#         # never allow subject_identifier as None
#         if not self.subject_identifier:
#             raise ConsentError('Subject Identifier may not be left blank.')
#         # never allow subject_identifier_as_pk as None
#         if not self.subject_identifier_as_pk:
#             raise ConsentError('Attribute subject_identifier_as_pk on model '
#                                '{0} may not be left blank. Expected to be set '
#                                'to a uuid already.'.format(self._meta.object_name))


    class Meta:
        abstract = True

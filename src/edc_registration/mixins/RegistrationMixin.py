import re

from edc_identifier.exceptions import IdentifierError


class RegistrationMixin:

    def change_subject_identifier(self, *args, **kwargs):
        using = kwargs.get('using')
        self.check_if_may_change_subject_identifier(using)
        if self.get_user_provided_subject_identifier_attrname():
            if not self.subject_identifier == getattr(
                    self, self.get_user_provided_subject_identifier_attrname()):
                raise IdentifierError('Identifier field {0} cannot be changed.'.format(
                    self.get_user_provided_subject_identifier_attrname()))
            # if user_provided_subject_identifier is None, set it to the same value as subject_identifier
            if not getattr(self, self.get_user_provided_subject_identifier_attrname()):
                setattr(self, self.get_user_provided_subject_identifier_attrname(), self.subject_identifier)

    def mask_unset_subject_identifier(self):
        subject_identifier = self.subject_identifier
        re_pk = re.compile('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}')
        if re_pk.match(subject_identifier):
            subject_identifier = '<identifier not set>'
        return subject_identifier

    def _get_user_provided_subject_identifier(self):
        """Return a user provided subject_identifier.

        Do not override."""
        if self.get_user_provided_subject_identifier_attrname() in dir(self):
            return getattr(self, self.get_user_provided_subject_identifier_attrname())
        else:
            return None

    def get_user_provided_subject_identifier_attrname(self):
        """Override to return the attribute name of the user provided subject_identifier."""
        return None

    def include_for_dispatch(self):
        return True

    def check_if_may_change_subject_identifier(self, using):
        if not self.__class__.objects.get(pk=self.id).subject_identifier == self.subject_identifier:
            raise IdentifierError('Subject Identifier cannot be changed. '
                                  'Got {0} != {1}'.format(
                                      self.__class__.objects.get(pk=self.id).subject_identifier,
                                      self.subject_identifier))

    def _check_if_duplicate_subject_identifier(self, using):
        """Checks if the subject identifier is in use, for new and existing instances."""
        if self.subject_identifier:
            if self.__class__.objects.using(using).filter(subject_identifier=self.subject_identifier):
                raise IdentifierError('Attempt to insert duplicate value for '
                                      'subject_identifier {0} when saving {1} '
                                      'on add.'.format(self.subject_identifier, self))
        else:
            if self.__class__.objects.using(using).filter(
                    subject_identifier=self.subject_identifier).exclude(pk=self.pk):
                raise IdentifierError('Attempt to insert duplicate value for '
                                      'subject_identifier {0} when saving {1} '
                                      'on change.'.format(self.subject_identifier, self))
        self.check_for_duplicate_subject_identifier()

    def check_for_duplicate_subject_identifier(self):
        """Users may override to add an additional strategy to detect duplicate identifiers."""
        pass

    def dummy_subject_identifier(self):
        """Inserts a random uuid as a dummy identifier for a new instance.

        Model uses subject_identifier_as_pk as a natural key for
        serialization/deserialization. Value must not change once set."""

        # set to uuid if new and not specified
        if not self.subject_identifier:
            # this will be changed when allocated a subject_identifier on consent
            self.subject_identifier = self.subject_identifier_as_pk
        # never allow subject_identifier as None
        if not self.subject_identifier:
            raise IdentifierError('Subject Identifier may not be left blank.')

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

    def post_save_get_or_create_registered_subject(self, **kwargs):
        """Creates or \'gets and updates\' the registered
        subject instance for this subject.

        Called by a post save signal.

        ..note:: RegisteredSubject also inherits from BaseSubject.
                 This method does nothing if \'self\' is an
                 instance of RegisteredSubject.
        ..note:: 'self' may not have an attribute registered_subject
                 or the attribute may not be set.
        """
        using = kwargs.get('using')
        updated = False
        registered_subject = None
        # skip if self is an instance of RegisteredSubject
        if not self.is_registered_subject():
            if 'registered_subject' in dir(self):
                if not self.registered_subject:
                    registered_subject = self._get_or_created_registered_subject(using)
                    self.registered_subject = registered_subject
                    updated = True
                else:
                    registered_subject = self._update_registered_subject(using)
            else:
                # self does not have a foreign key to RegisteredSubject but RegisteredSubject
                # still needs to be created or updated
                registered_subject = self._get_or_created_registered_subject(using)
        return registered_subject, updated

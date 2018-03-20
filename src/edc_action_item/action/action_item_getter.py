from copy import deepcopy
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from uuid import uuid4


class ActionItemGetterError(Exception):
    pass


class ActionItemObjectDoesNotExist(ObjectDoesNotExist):
    pass


class ActionItemParentDoesNotExist(ObjectDoesNotExist):
    pass


class ActionItemMismatch(Exception):
    pass


class ParentReferenceModelDoesNotExist(Exception):
    pass


class ActionItemGetter:

    model = 'edc_action_item.actionitem'

    def __init__(self, action_cls,
                 action_identifier=None,
                 subject_identifier=None,
                 reference_identifier=None,
                 parent_reference_identifier=None,
                 allow_create=None):

        self._model_options = None
        self._model_obj = None
        self.action_cls = action_cls
        self.action_identifier = action_identifier
        self.allow_create = allow_create
        self.parent_reference_identifier = parent_reference_identifier
        self.reference_identifier = reference_identifier
        self.subject_identifier = subject_identifier

        # subject identifier is required if no action_identifier.
        if not action_identifier and not self.subject_identifier:
            raise ActionItemGetterError(
                f'Subject identifier cannot be None if '
                f'action_identifier not provided. See {self.action_cls}.')

        # if fk_attr, parent_reference model instance must exist
        if self.action_cls.parent_reference_model_fk_attr:
            try:
                self.action_cls.parent_reference_model_cls().objects.get(
                    subject_identifier=self.subject_identifier,
                    tracking_identifier=parent_reference_identifier or uuid4())
            except ObjectDoesNotExist as e:
                raise ParentReferenceModelDoesNotExist(
                    f'Actions parent reference model does not exist. '
                    f'{repr(action_cls)} fk is '
                    f'{self.action_cls.parent_reference_model_fk_attr}'
                    f'tracking identifier=\'{parent_reference_identifier}\'. '
                    f'Got {e}.')

        if not self.model_obj:
            raise ActionItemObjectDoesNotExist(
                f'Action item does not exists. Got action_cls='
                f'{repr(self.action_cls)} using '
                f'\n(action_identifier={self.action_identifier},\n'
                f'subject_identifier={self.subject_identifier},\n'
                f'reference_identifier={self.reference_identifier},\n'
                f'action_type={self.action_cls.action_type()}).\n')

        self.action_identifier = self.model_obj.action_identifier
        if not self.model_obj.reference_identifier and self.reference_identifier:
            self.model_obj.reference_identifier = self.reference_identifier
            self.model_obj.save()

    @classmethod
    def model_cls(cls):
        """Returns the ActionItem model class.
        """
        return django_apps.get_model(cls.model)

    @property
    def model_obj(self):
        """Returns an ActionItem model instance.
        """
        if not self._model_obj:
            if self.action_identifier:
                self._model_obj = self._get_by_action_identifier_only()
            else:
                self._model_obj = self._get_by_subject_identifier_with_options()
            if not self._model_obj:
                if not self.action_cls.parent_reference_model_fk_attr:
                    self._model_obj = self._create_model_obj()
                else:
                    raise ActionItemObjectDoesNotExist(
                        'Expected ActionItem to exist for action class with FK attr. '
                        f'Got {self.action_cls} '
                        f'where {self.action_cls.parent_reference_model_fk_attr}='
                        f'{self.parent_reference_identifier} (tracking identifier).')
        return self._model_obj

    def _get_by_action_identifier_only(self):
        """Returns an ActionItem model instance by attempting
        to get by action_identifier only.

        This will be tried first.
        """
        try:
            model_obj = self.model_cls().objects.get(
                action_identifier=self.action_identifier)
        except ObjectDoesNotExist as e:
            raise ActionItemObjectDoesNotExist(e)
        return model_obj

    def _get_by_subject_identifier_with_options(self):
        """Returns an ActionItem model instance by attempting
        to get by subject_identifier and additional model options.

        This will be tried if action_identifier is None.
        """

        try:
            model_obj = self.model_cls().objects.get(**self.model_options)
        except ObjectDoesNotExist:

            # attempt to get a NEW ActionItem
            # where reference_identifier to None
            opts = deepcopy(self.model_options)
            try:
                del opts['reference_identifier']
            except KeyError:
                pass
            opts.update(reference_identifier__isnull=True)

            try:
                model_obj = self.model_cls().objects.get(**opts)
            except ObjectDoesNotExist:
                model_obj = None
            except MultipleObjectsReturned:
                try:
                    del opts['parent_reference_identifier']
                except KeyError:
                    pass
                opts.update(parent_reference_identifier__isnull=True)
                model_obj = self.model_cls().objects.filter(**opts).first()
        return model_obj

    def _create_model_obj(self):
        """Returns a new ActionItem instance, if allowed, or None.
        """
        model_obj = None
        if self.allow_create:
            model_obj = self.model_cls().objects.create(
                subject_identifier=self.subject_identifier,
                action_type=self.action_cls.action_type(),
                reference_identifier=self.reference_identifier,
                parent_reference_identifier=self.parent_reference_identifier)
        return model_obj

    @property
    def model_options(self):
        """Returns a dictionary of options to query the ActionItem.
        """
        if not self._model_options:
            self._model_options = dict(
                subject_identifier=self.subject_identifier,
                action_type=self.action_cls.action_type())
            if self.reference_identifier:
                self._model_options.update(
                    reference_identifier=self.reference_identifier)
            if self.parent_reference_identifier:
                self._model_options.update(
                    parent_reference_identifier=self.parent_reference_identifier)
        return self._model_options

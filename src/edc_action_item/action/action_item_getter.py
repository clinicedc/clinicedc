from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from uuid import uuid4
from edc_action_item.action.utils import SingletonActionItemError


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


class RelatedReferenceModelDoesNotExist(Exception):
    pass


class ActionItemGetter:

    model = 'edc_action_item.actionitem'

    def __init__(self, action_cls,
                 action_identifier=None,
                 related_reference_identifier=None,
                 parent_reference_identifier=None,
                 reference_identifier=None,
                 subject_identifier=None,
                 allow_create=None):

        self._model_options = None
        self._action_item = None
        self.action_cls = action_cls
        self.action_identifier = action_identifier
        self.allow_create = allow_create
        self.parent_reference_identifier = parent_reference_identifier
        self.related_reference_identifier = related_reference_identifier
        self.reference_identifier = reference_identifier
        self.subject_identifier = subject_identifier
        # subject identifier is required if no action_identifier.
        if not action_identifier and not self.subject_identifier:
            raise ActionItemGetterError(
                f'Subject identifier cannot be None if '
                f'action_identifier not provided. See {self.action_cls}.')

        # if fk_attr, related reference model instance must exist
        if self.action_cls.related_reference_model_fk_attr:
            try:
                self.action_cls.related_reference_model_cls().objects.get(
                    subject_identifier=self.subject_identifier,
                    tracking_identifier=self.related_reference_identifier or uuid4())
            except ObjectDoesNotExist as e:
                raise RelatedReferenceModelDoesNotExist(
                    f'Actions "related" reference model instance does not exist. '
                    f'{repr(action_cls)} fk is '
                    f'\'{self.action_cls.related_reference_model_fk_attr}\' where '
                    f'related tracking identifier=\'{self.related_reference_identifier}\'. '
                    f'Got {e}.')
        elif self.related_reference_identifier:
            try:
                self.action_cls.related_reference_model_cls().objects.get(
                    subject_identifier=self.subject_identifier,
                    tracking_identifier=self.related_reference_identifier or uuid4())
            except ObjectDoesNotExist as e:
                raise RelatedReferenceModelDoesNotExist(
                    f'Actions "related" reference model does not exist. '
                    f'{repr(action_cls)} with {self.related_reference_model}. '
                    f'tracking identifier=\'{self.related_reference_identifier}\'. '
                    f'Got {e}.')

#         if self.parent_reference_identifier:
#             try:
#                 self.action_cls.parent_reference_model_cls.objects.get(
#                     subject_identifier=self.subject_identifier,
#                     tracking_identifier=self.parent_reference_identifier or uuid4())
#             except ObjectDoesNotExist as e:
#                 raise ParentReferenceModelDoesNotExist(
#                     f'Actions "parent" reference model does not exist. '
#                     f'{repr(action_cls)} with {self.parent_reference_model}. '
#                     f'tracking identifier=\'{self.parent_reference_identifier}\'. '
#                     f'Got {e}.')

        if not self.action_item:
            raise ActionItemObjectDoesNotExist(
                f'Action item does not exists. Got action_cls='
                f'{repr(self.action_cls)} using '
                f'\n(action_identifier={self.action_identifier},\n'
                f'subject_identifier={self.subject_identifier},\n'
                f'reference_identifier={self.reference_identifier},\n'
                f'action_type={self.action_cls.action_type()}).\n')

        self.action_identifier = self.action_item.action_identifier
        if not self.action_item.reference_identifier and self.reference_identifier:
            self.action_item.reference_identifier = self.reference_identifier
            self.action_item.save()

    @classmethod
    def action_item_model_cls(cls):
        """Returns the ActionItem model class.
        """
        return django_apps.get_model(cls.model)

    @property
    def action_item(self):
        """Returns an ActionItem model instance.
        """
        if not self._action_item:
            if self.action_identifier:
                self._action_item = self._get_by_action_identifier_only()
            elif (self.action_cls.related_reference_model_fk_attr
                  and self.related_reference_identifier
                  and self.parent_reference_identifier):
                self._action_item = self._get_by_reference_identifiers()
            else:
                self._action_item = self._get_by_subject_identifier_with_options()
            if not self._action_item:
                if not self.action_cls.related_reference_model_fk_attr:
                    self._action_item = self._create_action_item()
                else:
                    # if has fk_attr, action item should have been created
                    # by a parent.
                    raise ActionItemObjectDoesNotExist(
                        'Expected ActionItem to exist for action class with FK attr. '
                        f'Got {self.action_cls} '
                        f'where {self.action_cls.related_reference_model_fk_attr}='
                        f'{self.related_reference_identifier} (tracking identifier).')
        return self._action_item

    def _get_by_action_identifier_only(self):
        """Returns an ActionItem model instance by attempting
        to get by action_identifier only.

        This will be tried first.
        """
        try:
            action_item = self.action_item_model_cls().objects.get(
                action_identifier=self.action_identifier)
        except ObjectDoesNotExist as e:
            raise ActionItemObjectDoesNotExist(e)
        return action_item

    def _get_by_reference_identifiers(self):
        try:
            action_item = self.action_item_model_cls().objects.get(
                action_type__name=self.action_cls.name,
                parent_reference_identifier=self.parent_reference_identifier,
                related_reference_identifier=self.related_reference_identifier)
        except ObjectDoesNotExist as e:
            raise ActionItemObjectDoesNotExist(e)
        return action_item

    def _get_by_subject_identifier_with_options(self):
        """Returns an ActionItem model instance by attempting
        to get by subject_identifier and additional model options.

        This will be tried if action_identifier is None.
        """
        opts = dict(
            subject_identifier=self.subject_identifier,
            action_type=self.action_cls.action_type())
        if self.reference_identifier:
            opts.update(
                reference_identifier=self.reference_identifier)
        if self.parent_reference_identifier:
            opts.update(
                parent_reference_identifier=self.parent_reference_identifier)

        try:
            action_item = self.action_item_model_cls().objects.get(**opts)
        except ObjectDoesNotExist:

            # attempt to get a NEW ActionItem
            # where reference_identifier to None
            try:
                del opts['reference_identifier']
            except KeyError:
                pass
            opts.update(reference_identifier__isnull=True)
            try:
                action_item = self.action_item_model_cls().objects.get(**opts)
            except ObjectDoesNotExist:
                action_item = None
            except MultipleObjectsReturned:
                try:
                    del opts['parent_reference_identifier']
                except KeyError:
                    pass
                opts.update(parent_reference_identifier__isnull=True)
                action_item = self.action_item_model_cls().objects.filter(
                    **opts).first()
        return action_item

    @property
    def singleton_action_item(self):
        action_item = None
        if self.action_cls.singleton:
            try:
                action_item = self.action_item_model_cls().objects.get(
                    action_type=self.action_cls.action_type(),
                    subject_identifier=self.subject_identifier)
            except ObjectDoesNotExist:
                pass
        return action_item

    def _create_action_item(self):
        """Returns a new ActionItem instance, if allowed, or None.
        """
        action_item = None
        if self.allow_create:
            if self.singleton_action_item:
                raise SingletonActionItemError(
                    f'Action {self.action_cls.name} can only be created once per subject.')
            else:
                action_item = self.action_item_model_cls().objects.create(
                    subject_identifier=self.subject_identifier,
                    action_type=self.action_cls.action_type(),
                    reference_identifier=self.reference_identifier,
                    related_reference_identifier=self.related_reference_identifier,
                    parent_reference_identifier=self.parent_reference_identifier)
        return action_item

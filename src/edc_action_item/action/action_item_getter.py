from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from .utils import SingletonActionItemError


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
                 parent_reference_identifier=None,
                 related_reference_identifier=None,
                 subject_identifier=None,
                 allow_create=None):
        self._model_options = None
        self._action_item = None
        self.action_cls = action_cls
        self.action_identifier = action_identifier
        self.allow_create = allow_create
        self.parent_reference_identifier = parent_reference_identifier
        self.related_reference_identifier = related_reference_identifier
        self.subject_identifier = subject_identifier

        # always need subject_identifier
        if not self.subject_identifier:
            raise ActionItemGetterError('Subject identifier is required.')

        self.verify_parent_reference_identifier()
        self.verify_related_reference_identifier()

        if not self.action_item:
            raise ActionItemObjectDoesNotExist(
                f'Action item does not exists. Got action_cls='
                f'{repr(self.action_cls)} using '
                f'\n(action_identifier={self.action_identifier},\n'
                f'subject_identifier={self.subject_identifier},\n'
                f'action_type={self.action_cls.action_type()}).\n')

        self.action_identifier = self.action_item.action_identifier

    @classmethod
    def action_item_model_cls(cls):
        """Returns the ActionItem model class.
        """
        return django_apps.get_model(cls.model)

    @property
    def action_item(self):
        """Returns an ActionItem model instance.

        Creates a new one if one does not exist.
        """
        if not self._action_item:
            if self.action_identifier:
                self._action_item = self._get_by_action_identifier_only()
            elif (self.action_cls.related_reference_fk_attr
                  and self.related_reference_identifier
                  and self.parent_reference_identifier):
                self._action_item = self._get_by_reference_identifiers()
            else:
                self._action_item = self._get_by_subject_identifier_with_options()
            if not self._action_item:
                if not self.action_cls.related_reference_fk_attr:
                    self._action_item = self._create_action_item()
                else:
                    # if has fk_attr, action item should have been created
                    # by a parent.
                    raise ActionItemObjectDoesNotExist(
                        'Expected ActionItem to exist for action class with FK attr. '
                        f'Got {self.action_cls} '
                        f'where {self.action_cls.related_reference_fk_attr}='
                        f'{self.related_reference_identifier}.')
        return self._action_item

    def _get_by_action_identifier_only(self):
        """Returns an ActionItem model instance by attempting
        to get by action_identifier only.

        This will be tried first.
        """
        try:
            action_item = self.action_item_model_cls().objects.get(
                subject_identifier=self.subject_identifier,
                action_identifier=self.action_identifier)
        except ObjectDoesNotExist as e:
            raise ActionItemObjectDoesNotExist(e)
        return action_item

    def _get_by_reference_identifiers(self):
        """Returns an existing ActionItem queried on the
        parent and related reference.

        If you are here, you want to link to an available
        ActionItem.
        """
        try:
            action_item = self.action_item_model_cls().objects.get(
                subject_identifier=self.subject_identifier,
                action_type__name=self.action_cls.name,
                parent_reference_identifier=self.parent_reference_identifier,
                related_reference_identifier=self.related_reference_identifier,
                linked_to_reference=False)
        except ObjectDoesNotExist as e:
            raise ActionItemObjectDoesNotExist(e)
        return action_item

    def _get_by_subject_identifier_with_options(self):
        """Returns an ActionItem model instance by attempting
        to get by subject_identifier and additional model options.

        This will be tried if action_identifier is None.

        If you are here, you want to link to an available
        ActionItem.
        """
        action_item = None
        if not self.action_identifier:
            if self.action_cls.singleton:
                action_item = self.singleton_action_item
            else:
                opts = dict(
                    subject_identifier=self.subject_identifier,
                    action_type=self.action_cls.action_type(),
                    linked_to_reference=False)
                if self.parent_reference_identifier:
                    opts.update(
                        parent_reference_identifier=self.parent_reference_identifier)
                if self.related_reference_identifier:
                    opts.update(
                        related_reference_identifier=self.related_reference_identifier)
                try:
                    action_item = self.action_item_model_cls().objects.get(**opts)
                except (ObjectDoesNotExist, MultipleObjectsReturned):
                    # attempt to get the first NEW unlinked ActionItem
                    action_item = self.action_item_model_cls().objects.filter(**opts).first()
        return action_item

    @property
    def singleton_action_item(self):
        """Returns the "singleton" action item, if it exists.
        """
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
        """Returns a newly created ActionItem instance, if allowed, or None.

        A new ActionItem is not allowed if the parent is a
        singleton.
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
                    action_identifier=self.action_identifier,
                    linked_to_reference=True,
                    parent_reference_identifier=self.parent_reference_identifier,
                    related_reference_identifier=self.related_reference_identifier,
                    related_reference_model=self.action_cls.related_reference_model)
        return action_item

    def verify_parent_reference_identifier(self):
        """Assert if parent_reference_identifier then
        parent model and action item exist.
        """
        if self.action_cls.parent_reference_model:
            try:
                action_item = self.action_item_model_cls().objects.get(
                    action_identifier=self.parent_reference_identifier)
            except ObjectDoesNotExist:
                raise ParentReferenceModelDoesNotExist(
                    f'Actions "parent" action item does not exist. '
                    f'parent reference identifier=\'{self.parent_reference_identifier}\'. '
                    f'See {repr(self.action_cls)}.')
            try:
                action_item.reference_model_cls.objects.get(
                    action_identifier=action_item.action_identifier)
            except ObjectDoesNotExist:
                raise ParentReferenceModelDoesNotExist(
                    f'Actions "parent" reference model instance does not exist. '
                    f'parent reference identifier=\'{self.parent_reference_identifier}\'. '
                    f'See {repr(self.action_cls)}.')

    def verify_related_reference_identifier(self):
        """Assert if related_reference_identifier then
        related model and action item exist.

        Note: if related_reference_fk_attr is specified on the
        action class, related_reference_identifier MUST exist.
        """

        if (self.action_cls.related_reference_fk_attr
                and not self.related_reference_identifier):
            raise ActionItemGetterError(
                'Action has a related_reference_fk_attr specified but '
                'related_reference_identifier is None')

        if self.action_cls.related_reference_model:
            try:
                action_item = self.action_item_model_cls().objects.get(
                    action_identifier=self.related_reference_identifier)
            except ObjectDoesNotExist:
                raise RelatedReferenceModelDoesNotExist(
                    f'Actions "related" action item does not exist. '
                    f'related reference identifier=\'{self.related_reference_identifier}\'. '
                    f'See {repr(self.action_cls)}.')
            try:
                action_item.reference_model_cls.objects.get(
                    action_identifier=action_item.action_identifier)
            except ObjectDoesNotExist:
                raise RelatedReferenceModelDoesNotExist(
                    f'Actions "related" reference model instance does not exist. '
                    f'related reference identifier=\'{self.related_reference_identifier}\'. '
                    f'See {repr(self.action_cls)}.')

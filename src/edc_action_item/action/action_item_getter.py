from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned,\
    ValidationError
from edc_constants.constants import NEW

from ..get_action_type import get_action_type


class ActionItemGetterError(ValidationError):
    pass


class ActionItemGetter:

    """A class that gets an ActionItem.
    """

    model = 'edc_action_item.actionitem'

    def __init__(self, action_cls,
                 action_identifier=None,
                 parent_action_identifier=None,
                 related_action_identifier=None,
                 subject_identifier=None):
        self._action_item = None
        self._model_options = None
        self._parent_reference_obj = None
        self._related_action_item = None
        self._related_reference_obj = None

        self.action_cls = action_cls
        self.action_identifier = action_identifier
        self.parent_action_identifier = parent_action_identifier
        self.related_action_identifier = related_action_identifier
        self.subject_identifier = subject_identifier

        # always need subject_identifier
        if not self.subject_identifier:
            raise ActionItemGetterError(
                'Subject identifier is required.',
                code='subject_identifier')
        self.action_item = self.get_action_item()
        self.action_identifier = self.action_item.action_identifier

    def get_action_item(self):
        # get by action identifier only
        action_item = None
        try:
            action_item = self.action_item_model_cls().objects.get(
                subject_identifier=self.subject_identifier,
                action_identifier=self.action_identifier)
        except ObjectDoesNotExist as e:
            if self.action_identifier:
                raise ObjectDoesNotExist(
                    f'{e}. Got action_identifier=\'{self.action_identifier}\'')
        # get using refernce identifiers
        if (not action_item
                and self.action_cls.related_reference_fk_attr
                and self.related_action_identifier
                and self.parent_action_identifier):
            try:
                action_item = self._get_by_action_identifiers()
            except ObjectDoesNotExist:
                pass
        if not action_item:
            action_item = self._get_by_subject_identifier_with_options()
        return action_item

    @classmethod
    def action_item_model_cls(cls):
        """Returns the ActionItem model class.
        """
        return django_apps.get_model(cls.model)

    def _get_by_action_identifiers(self):
        """Returns an existing ActionItem queried on the
        parent and related reference.

        If you are here, you want to link to an available
        ActionItem.
        """
        action_item = self.action_item_model_cls().objects.get(
            subject_identifier=self.subject_identifier,
            action_type__name=self.action_cls.name,
            parent_action_identifier=self.parent_action_identifier,
            related_action_identifier=self.related_action_identifier,
            linked_to_reference=False)
        return action_item

    def _get_by_subject_identifier_with_options(self):
        """Returns an ActionItem model instance by attempting
        to get by subject_identifier and additional model options.

        This will be tried if action_identifier is None.

        If you are here, you want to link to any available
        ActionItem of the correct type.
        """
        action_item = None
        if not self.action_identifier:
            action_type = get_action_type(self.action_cls)
            if self.action_cls.singleton:
                action_item = self.action_item_model_cls().objects.get(
                    action_type=get_action_type(self.action_cls),
                    subject_identifier=self.subject_identifier)
            else:
                opts = dict(
                    subject_identifier=self.subject_identifier,
                    action_type=action_type,
                    linked_to_reference=False,
                    status=NEW)
                if self.parent_action_identifier:
                    opts.update(
                        parent_action_identifier=self.parent_action_identifier)
                if self.related_action_identifier:
                    opts.update(
                        related_action_identifier=self.related_action_identifier)
                try:
                    action_item = self.action_item_model_cls().objects.get(**opts)
                except (ObjectDoesNotExist, MultipleObjectsReturned):
                    # attempt to get the first NEW unlinked ActionItem
                    action_item = self.action_item_model_cls().objects.filter(
                        **opts).first()
            if not action_item:
                raise ObjectDoesNotExist(
                    f'ActionItem does not exist. Got {action_type.name} '
                    f'for {self.subject_identifier}.')
        return action_item

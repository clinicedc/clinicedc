from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Q
from django.utils.formats import localize
from edc_base.constants import DEFAULT_BASE_FIELDS
from edc_constants.constants import CLOSED, NEW, OPEN
from urllib.parse import urlencode, unquote

from ..create_action_item import create_action_item
from ..get_action_type import get_action_type
from ..site_action_items import site_action_items
from .action_item_getter import ActionItemGetter

REFERENCE_MODEL_ERROR_CODE = 'reference_model'


class ActionError(ValidationError):
    pass


class RelatedReferenceObjectDoesNotExist(ObjectDoesNotExist):
    pass


class Action:

    action_item_getter = ActionItemGetter

    admin_site_name = None
    color_style = 'danger'
    create_by_action = None
    create_by_user = None
    display_name = None
    email_recipients = None
    email_sender = None
    help_text = None
    instructions = None
    name = None
    parent_reference_model = None
    priority = None
    reference_model = None
    related_reference_fk_attr = None
    related_reference_model = None
    show_link_to_add = False
    show_link_to_changelist = False
    show_on_dashboard = None
    singleton = False

    action_item_model = 'edc_action_item.actionitem'
    action_type_model = 'edc_action_item.actiontype'
    next_actions = None  # a list of Action classes which may include 'self'

    def __init__(self,
                 action_item=None, reference_obj=None,
                 subject_identifier=None,
                 action_identifier=None,
                 parent_action_identifier=None,
                 related_action_identifier=None):

        self._reference_obj = reference_obj

        self.messages = {}

        self.action_registered_or_raise()

        self.action_identifier = action_identifier
        try:
            self.action_item = reference_obj.action_item
        except AttributeError:
            self.action_item = action_item

        self.parent_action_identifier = parent_action_identifier
        self.related_action_identifier = related_action_identifier
        self.subject_identifier = subject_identifier

        if self.action_item:
            if self.action_item.action_cls != self.__class__:
                raise ActionError(
                    f'Action class mismatch for given ActionItem. '
                    f'{self.action_item.action_cls} incorrectly passed '
                    f'to Action {self.__class__}',
                    code='class type mismatch')
            self.action_identifier = self.action_item.action_identifier
            self.subject_identifier = self.action_item.subject_identifier
            self.parent_action_identifier = self.action_item.parent_action_identifier
            self.related_action_identifier = self.action_item.related_action_identifier
        else:
            if self.reference_obj:
                self.subject_identifier = self.reference_obj.subject_identifier
                self.parent_action_identifier = (
                    self.reference_obj.parent_action_identifier)
                self.related_action_identifier = (
                    self.reference_obj.related_action_identifier)
            self.action_item = self.get_or_create_action_item()
            self.action_identifier = self.action_item.action_identifier
            self.subject_identifier = self.action_item.subject_identifier
            self.parent_action_identifier = self.action_item.parent_action_identifier
            self.related_action_identifier = (
                self.action_item.related_action_identifier)

        self.linked_to_reference = self.action_item.linked_to_reference

        if self.reference_obj:
            self.close_and_create_next()

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name})'

    def __str__(self):
        return self.name

    @property
    def reference_obj(self):
        if not self._reference_obj:
            try:
                self._reference_obj = self.reference_model_cls().objects.get(
                    action_identifier=self.action_identifier)
            except ObjectDoesNotExist:
                if (self.action_identifier and self.action_item
                        and self.action_item.status == CLOSED):
                    raise ActionError(
                        'Reference model instance not found. '
                        f'Got action_identifier=\'{self.action_identifier}\' '
                        f'for reference_model '
                        f'\'{self.reference_model}\'. See {repr(self)}',
                        code=REFERENCE_MODEL_ERROR_CODE)
        return self._reference_obj

    def get_or_create_action_item(self):
        try:
            getter = self.action_item_getter(
                self, action_identifier=self.action_identifier,
                subject_identifier=self.subject_identifier,
                related_action_identifier=self.related_action_identifier,
                parent_action_identifier=self.parent_action_identifier)
        except ObjectDoesNotExist:
            action_item = create_action_item(
                self, subject_identifier=self.subject_identifier,
                action_identifier=self.action_identifier,
                parent_action_identifier=self.parent_action_identifier,
                related_action_identifier=self.related_action_identifier)
        else:
            action_item = getter.action_item
        return action_item

    @classmethod
    def action_item_model_cls(cls):
        """Returns the ActionItem model class.
        """
        return django_apps.get_model(cls.action_item_model)

    @classmethod
    def action_type_model_cls(cls):
        """Returns the ActionType model class.
        """
        return django_apps.get_model(cls.action_type_model)

    @classmethod
    def reference_model_cls(cls):
        """Returns the reference model class.
        """
        return django_apps.get_model(cls.reference_model)

    @classmethod
    def related_reference_model_cls(cls):
        """Returns the related reference model class
        """
        return django_apps.get_model(cls.related_reference_model)

    @classmethod
    def action_registered_or_raise(cls):
        """Raises if this is not a registered action class.
        """
        registered_cls = site_action_items.get(cls.name)
        if registered_cls is not cls:
            raise ActionError(
                f'Inconsistent action name or class. Got '
                f'{registered_cls} for {cls.name}.')
        return True

    @classmethod
    def as_dict(cls):
        """Returns select class attrs as a dictionary.
        """
        dct = {k: v for k, v in cls.__dict__.items() if not k.startswith('_')}
        try:
            dct.update(reference_model=cls.reference_model.lower())
        except AttributeError:
            pass
        try:
            dct.update(
                related_reference_model=cls.related_reference_model.lower())
        except AttributeError:
            pass
        dct.update(
            name=cls.name,
            display_name=cls.display_name,
            show_on_dashboard=(
                True if cls.show_on_dashboard is None else cls.show_on_dashboard),
            show_link_to_changelist=(
                True if cls.show_link_to_changelist is None
                else cls.show_link_to_changelist),
            create_by_user=(True if cls.create_by_user is None
                            else cls.create_by_user),
            create_by_action=(True if cls.create_by_action is None
                              else cls.create_by_action),
            instructions=cls.instructions)
        return dct

    def get_next_actions(self):
        """Returns a list of action classes to be created
        again by this model if the first has been closed on post_save.
        """
        return self.next_actions or []

    def close_action_item_on_save(self):
        """Returns True if action item for \'action_identifier\'
        is to be closed on post_save.
        """
        return True

    def close_and_create_next(self):
        """Attempt to close the action item and
        create new ones, if required.
        """
        self.reopen_action_items_on_changed()
        status = CLOSED if self.close_action_item_on_save() else OPEN
        self.action_item.status = status
        self.action_item.save()
        self.action_item = self.action_item_model_cls().objects.get(
            action_identifier=self.action_identifier)
        if status == CLOSED:
            self.create_next_action_items()

    def create_next_action_items(self):
        """Creates any next action items if they do not
        already exist.
        """
        next_actions = self.get_next_actions()
        for action_cls in next_actions:
            action_cls = self.__class__ if action_cls == 'self' else action_cls
            action_type = get_action_type(action_cls)
            if action_type.related_reference_model:
                related_action_identifier = (
                    self.action_item.related_action_identifier
                    or self.action_item.action_identifier)
            else:
                related_action_identifier = None
            opts = dict(
                subject_identifier=self.subject_identifier,
                action_type=action_type,
                parent_action_item=self.action_item,
                parent_action_identifier=self.action_item.action_identifier,
                parent_reference_model=get_action_type(
                    self.__class__).reference_model,
                related_action_identifier=related_action_identifier,
                related_reference_model=action_type.related_reference_model,
                reference_model=action_type.reference_model,
                instructions=self.instructions)
            try:
                self.action_item_model_cls().objects.get(**opts)
            except ObjectDoesNotExist:
                self.action_item_model_cls().objects.create(**opts)

    @property
    def reference_obj_has_changed(self):
        """Returns True if the reference object has changed
        since the last save.

        References the objects "history" (historical)
        """
        changed_message = {}
        try:
            history = self.reference_obj.history.all().order_by(
                '-history_date')[1]
        except IndexError:
            pass
        except AttributeError:
            # suppressed here but is reviewed in system checks
            pass
        else:
            field_names = [
                field.name for field in self.reference_obj._meta.get_fields()
                if field.name not in DEFAULT_BASE_FIELDS]
            for field_name in field_names:
                try:
                    if getattr(history, field_name) != getattr(self.reference_obj, field_name):
                        changed_message.update(
                            {field_name: getattr(self.reference_obj, field_name)})
                except AttributeError:
                    pass
        return changed_message

    def reopen_action_items_on_changed(self):
        """Reopen the action_item and child action items for this
        reference object if reference object was changed since
        the last save.
        """
        if self.reference_obj_has_changed:
            for action_item in self.action_item_model_cls().objects.filter(
                    (Q(action_identifier=self.reference_obj.action_identifier) |
                     Q(parent_action_identifier=self.reference_obj.action_identifier) |
                     Q(related_action_identifier=self.reference_obj.action_identifier)),
                    status=CLOSED):
                action_item.status = OPEN
                action_item.save()
                self.messages.update(
                    {action_item: (
                        f'{self.reference_obj._meta.verbose_name.title()} '
                        f'{self.reference_obj} was changed on '
                        f'{localize(self.reference_obj.modified)} '
                        f'({settings.TIME_ZONE})')})

    def append_to_next_if_required(self, next_actions=None,
                                   action_cls=None, required=None):
        """Returns next actions where the given action_cls is
        appended if required.

        `required` can be anything that evaluates to a boolean.

        Will not append if the ActionItem for the next action
        already exists.
        """
        next_actions = next_actions or []
        required = True if required is None else required
        try:
            self.action_item_model_cls().objects.get(
                subject_identifier=self.subject_identifier,
                parent_action_identifier=self.action_identifier,
                parent_reference_model=self.reference_model,
                action_type__name=action_cls.name)
        except ObjectDoesNotExist:
            if required:
                next_actions.append(action_cls)
        return next_actions

    def delete_children_if_new(self, parent_action_identifier=None):
        """Deletes the action item instance where status
        is NEW, use with caution.

        Since some actions are created by an event, this method
        could mess up the state.
        """
        index = 0
        opts = dict(
            subject_identifier=self.subject_identifier,
            parent_action_identifier=parent_action_identifier,
            status=NEW)
        for index, obj in enumerate(self.action_item_model_cls().objects.filter(**opts)):
            obj.delete()
        return index

    @classmethod
    def reference_url(cls, action_item=None, reference_obj=None, **kwargs):
        """Returns a relative add URL with querystring that can
        get back to the subject dashboard on save.
        """
        if cls.related_reference_fk_attr:
            obj = cls.related_reference_model_cls().objects.get(
                action_identifier=action_item.related_action_identifier)
            kwargs.update({
                cls.related_reference_fk_attr: str(obj.pk)})
        query = unquote(urlencode(kwargs))
        if reference_obj:
            path = reference_obj.get_absolute_url()
        else:
            path = cls.reference_model_cls()().get_absolute_url()
        if query:
            return '?'.join([path, query])
        return path

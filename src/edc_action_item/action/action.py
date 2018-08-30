from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured,\
    ValidationError
from edc_constants.constants import CLOSED, NEW, OPEN
from urllib.parse import urlencode, unquote

from ..site_action_items import site_action_items
from .action_item_getter import ActionItemGetter

REFERENCE_MODEL_ERROR_CODE = 'reference_model'


class ActionError(ValidationError):
    pass


class ReferenceModelObjectDoesNotExist(ObjectDoesNotExist):
    pass


class Action:

    action_item_getter = ActionItemGetter

    _updated_action_type = False

    admin_site_name = None
    color_style = 'danger'
    create_by_action = None
    create_by_user = None
    display_name = None
    help_text = None
    instructions = None
    name = None
    parent_reference_model = None
    related_reference_model = None
    related_reference_fk_attr = None
    priority = None
    reference_model = None
    show_link_to_add = False
    show_link_to_changelist = False
    show_on_dashboard = None
    singleton = False

    action_type_model = 'edc_action_item.actiontype'
    next_actions = None  # a list of Action classes which may include 'self'

    def __init__(self, subject_identifier=None, action_identifier=None,
                 parent_reference_identifier=None,
                 related_reference_identifier=None):

        self.action_item_obj = None

        self.action_registered_or_raise()

        if not self.reference_model:
            raise ImproperlyConfigured(
                f'Reference model not declared. See {repr(self)}')

        try:
            reference_obj = self.reference_model_cls().objects.get(
                action_identifier=action_identifier)
        except ObjectDoesNotExist:
            if action_identifier:
                raise ActionError(
                    'Reference model instance not found. '
                    f'Got action_identifier=\'{action_identifier}\' for reference_model '
                    f'\'{self.reference_model}\'. See {repr(self)}',
                    code=REFERENCE_MODEL_ERROR_CODE)
            reference_obj = None
            self.action_identifier = action_identifier
            self.subject_identifier = subject_identifier
            self.parent_reference_identifier = parent_reference_identifier
            self.related_reference_identifier = related_reference_identifier
        else:
            self.action_identifier = reference_obj.action_identifier
            self.subject_identifier = reference_obj.subject_identifier
            self.parent_reference_identifier = reference_obj.parent_reference_identifier
            self.related_reference_identifier = reference_obj.related_reference_identifier

        getter = self.action_item_getter(
            self, action_identifier=self.action_identifier,
            subject_identifier=self.subject_identifier,
            related_reference_identifier=self.related_reference_identifier,
            parent_reference_identifier=self.parent_reference_identifier,
            allow_create=True)
        self.action_item_obj = getter.action_item
        self.linked_to_reference = self.action_item_obj.linked_to_reference

        if not self.action_identifier:
            self.action_identifier = self.action_item_obj.action_identifier

        if reference_obj:
            self.close_and_create_next()

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name})'

    def __str__(self):
        return self.name

    @property
    def reference_obj(self):
        return self.reference_model_cls().objects.get(
            action_identifier=self.action_identifier)

    @classmethod
    def action_item_model_cls(cls):
        """Returns the ActionItem model class.
        """
        return cls.action_item_getter.action_item_model_cls()

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
                f'Inconsistent action name or class. Got {registered_cls} for {cls.name}.')
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
                True if cls.show_link_to_changelist is None else cls.show_link_to_changelist),
            create_by_user=True if cls.create_by_user is None else cls.create_by_user,
            create_by_action=True if cls.create_by_action is None else cls.create_by_action,
            instructions=cls.instructions)
        return dct

    @classmethod
    def action_type(cls):
        """Returns a model instance of ActionType.

        Gets or creates the ActionType on first pass.

        If model instance exists, updates.
        """
        opts = {}
        action_type_model_cls = django_apps.get_model(cls.action_type_model)
        fields = [
            f.name for f in action_type_model_cls._meta.fields if f.name != 'name']
        for attr, value in cls.as_dict().items():
            if attr in fields:
                opts.update({attr: value})
        try:
            action_type = action_type_model_cls.objects.get(name=cls.name)
        except ObjectDoesNotExist:
            action_type = action_type_model_cls.objects.create(
                name=cls.name, **opts)
        else:
            if not cls._updated_action_type:
                for k, v in opts.items():
                    setattr(action_type, k, v)
                action_type.save()
                action_type = action_type_model_cls.objects.get(name=cls.name)
                cls._updated_action_type = True
        return action_type

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
        status = CLOSED if self.close_action_item_on_save() else OPEN
        self.action_item_obj.status = status
        self.action_item_obj.save()
        self.action_item_obj = self.action_item_model_cls().objects.get(
            action_identifier=self.action_identifier)
        if status == CLOSED:
            self.create_next()

    def create_next(self):
        """Creates any next action items if they do not already exist.
        """
        next_actions = self.get_next_actions()
        for action_cls in next_actions:
            action_cls = self.__class__ if action_cls == 'self' else action_cls
            action_type = action_cls.action_type()
            if action_type.related_reference_model:
                related_reference_identifier = (
                    self.action_item_obj.related_reference_identifier
                    or self.action_item_obj.action_identifier)
            else:
                related_reference_identifier = None
            opts = dict(
                subject_identifier=self.subject_identifier,
                action_type=action_type,
                parent_action_item=self.action_item_obj,
                parent_reference_identifier=self.action_item_obj.action_identifier,
                parent_reference_model=self.action_type().reference_model,
                related_reference_identifier=related_reference_identifier,
                related_reference_model=action_type.related_reference_model,
                reference_model=action_type.reference_model,
                instructions=self.instructions)
            try:
                self.action_item_model_cls().objects.get(**opts)
            except ObjectDoesNotExist:
                self.action_item_model_cls().objects.create(**opts)

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
        self.delete_if_new(action_cls)
        try:
            self.action_item_model_cls().objects.get(
                subject_identifier=self.subject_identifier,
                parent_reference_identifier=self.action_identifier,
                reference_model=action_cls.reference_model)
        except ObjectDoesNotExist:
            if required:
                next_actions.append(action_cls)
        return next_actions

    def delete_if_new(self, action_cls=None):
        """Deletes the action item instance where status
        is NEW, use with caution.

        Since some actions are created by an event, this method
        could mess up the state.
        """
        opts = dict(
            subject_identifier=self.subject_identifier,
            parent_reference_identifier=self.action_identifier,
            reference_model=action_cls.reference_model,
            status=NEW)
        return self.action_item_model_cls().objects.filter(**opts).delete()

    @classmethod
    def reference_url(cls, action_item=None, reference_obj=None, **kwargs):
        """Returns a relative add URL with querystring that can
        get back to the subject dashboard on save.
        """
        if cls.related_reference_fk_attr:
            try:
                obj = cls.related_reference_model_cls().objects.get(
                    action_identifier=action_item.related_reference_identifier)
            except ObjectDoesNotExist:
                pass
            else:
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

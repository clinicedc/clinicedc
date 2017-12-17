from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import CLOSED
from urllib.parse import urlencode, unquote
from uuid import uuid4


class ActionError(Exception):
    pass


class Action:

    _updated_action_type = False

    name = None
    display_name = None
    model = None
    show_on_dashboard = None
    show_link_to_changelist = False
    create_by_action = None
    create_by_user = None
    instructions = None
    priority = None
    help_text = None

    parent_model_fk_attr = None
    action_item_model = 'edc_action_item.actionitem'
    action_type_model = 'edc_action_item.actiontype'
    next_actions = None  # a list of Action classes or 'self'

    def __init__(self, model_obj=None, subject_identifier=None, tracking_identifier=None):

        self.model_obj = model_obj
        if not self.model_obj:
            self.subject_identifier = subject_identifier
            self.tracking_identifier = tracking_identifier or str(uuid4())
        else:
            self.subject_identifier = self.model_obj.subject_identifier
            self.tracking_identifier = self.model_obj.tracking_identifier
            if (self.model and self.model_obj) or (self.model and not self.model_obj):
                if self.model_obj._meta.label_lower != self.model.lower():
                    raise ActionError(
                        f'Invalid model for {repr(self)}. Expected {self.model}. '
                        f'Got \'{self.model_obj._meta.label_lower}\'.')
        self.object = self.get_or_create_action_item()
        self.action_identifier = self.object.action_identifier
        if self.model_obj:
            self.model_obj.action_identifier = self.action_identifier
            self.model_obj.save(update_fields=['action_identifier'])
            self.close_and_create_next()

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name})'

    def __str__(self):
        return self.name

    @classmethod
    def as_dict(cls):
        """Returns select attrs as a dictionary.
        """
        try:
            cls.model = cls.model.lower()
        except AttributeError:
            pass
        return dict(
            name=cls.name,
            display_name=cls.display_name,
            model=cls.model,
            show_on_dashboard=(
                False if cls.show_on_dashboard is None else cls.show_on_dashboard),
            show_link_to_changelist=(
                True if cls.show_link_to_changelist is None else cls.show_link_to_changelist),
            create_by_user=True if cls.create_by_user is None else cls.create_by_user,
            create_by_action=True if cls.create_by_action is None else cls.create_by_action,
            instructions=cls.instructions)

    @property
    def action_item_model_cls(self):
        return django_apps.get_model(self.action_item_model)

    @classmethod
    def reference_model(cls):
        return cls.model

    @classmethod
    def reference_model_cls(cls):
        return django_apps.get_model(cls.model)

    @classmethod
    def action_type(cls):
        """Returns a model instance of the action type.

        Creates or updates the model instance on first pass.
        """
        action_type_model_cls = django_apps.get_model(
            cls.action_type_model)
        try:
            action_type = action_type_model_cls.objects.get(
                name=cls.name)
        except ObjectDoesNotExist:
            action_type = action_type_model_cls.objects.create(
                **cls.as_dict())
        else:
            if not cls._updated_action_type:
                for attr, value in cls.as_dict().items():
                    if attr != 'name':
                        setattr(action_type, attr, value)
                action_type.save()
        cls._updated_action_type = True
        return action_type

    def get_or_create_action_item(self):
        """Returns the action item model instance represented by this
        Action.
        """
        opts = dict(
            subject_identifier=self.subject_identifier,
            action_type=self.action_type())
        try:
            action_item = self.action_item_model_cls.objects.get(
                reference_identifier=self.tracking_identifier, **opts)
        except ObjectDoesNotExist:
            action_item = self.action_item_model_cls.objects.filter(
                reference_identifier__isnull=True,
                **opts).order_by('created').first()
            if action_item:
                action_item.reference_identifier = self.tracking_identifier
                action_item.save()
                action_item = self.action_item_model_cls.objects.get(
                    pk=action_item.pk)
            else:
                action_item = self.action_item_model_cls.objects.create(
                    reference_identifier=self.tracking_identifier,
                    instructions=self.instructions, **opts)
        return action_item

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
        if self.close_action_item_on_save():
            self.object.status = CLOSED
            self.object.save(update_fields=['status'])
            self.create_next()

    def create_next(self):
        """Creates any next action items if they do not already exist.
        """
        next_actions = self.get_next_actions()
        for action_cls in next_actions:
            action_cls = self.__class__ if action_cls == 'self' else action_cls
            action_type = action_cls.action_type()
            opts = dict(
                subject_identifier=self.subject_identifier,
                action_type=action_type,
                parent_reference_identifier=self.tracking_identifier,
                parent_model=self.reference_model(),
                parent_action_item=self.object,
                reference_model=action_type.model,
                reference_identifier=None,
                instructions=self.instructions)
            try:
                self.action_item_model_cls.objects.get(**opts)
            except ObjectDoesNotExist:
                self.action_item_model_cls.objects.create(**opts)

    @classmethod
    def reference_model_url(cls, action_item=None, model_obj=None, **kwargs):
        """Returns a relative add URL with querystring that can
        get back to the subject dashboard on save.
        """
        if cls.parent_model_fk_attr and action_item.parent_object:
            try:
                value = getattr(action_item.parent_object,
                                cls.parent_model_fk_attr)
            except AttributeError:
                value = action_item.parent_object
            kwargs.update({cls.parent_model_fk_attr: str(value.pk)})
        query = unquote(urlencode(kwargs))
        if model_obj:
            path = model_obj.get_absolute_url()
        else:
            path = cls.reference_model_cls()().get_absolute_url()
        return '?'.join([path, query])

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from urllib.parse import urlencode, unquote

from .site_action_items import site_action_items


class ActionError(Exception):
    pass


class Action:

    _updated_action_type = False

    name = None
    display_name = None
    model = None
    show_on_dashboard = None
    prn_form_action = None
    instructions = None
    priority = None

    parent_model_fk_attr = None
    action_item_model = 'edc_action_item.actionitem'
    action_type_model = 'edc_action_item.actiontype'
    create_actions = None
    next_actions = None  # a list of Action classes or 'self'

    def __init__(self, model_obj=None, subject_identifier=None, tracking_identifier=None):
        site_action_items.populate_action_type()
        self.model_obj = model_obj
        if (self.model and self.model_obj) or (self.model and not self.model_obj):
            # raise if not correct model type
            if model_obj._meta.label_lower != self.model.lower():
                raise ActionError(
                    f'Invalid model for {repr(self)}. Expected {self.model}. '
                    f'Got \'{model_obj._meta.label_lower}\'.')
            self.model_obj = model_obj
            self.subject_identifier = self.model_obj.subject_identifier

            # require tracking_identifier
            # for example, from TrackingIdentifierModelMixin
            self.tracking_identifier = self.model_obj.tracking_identifier
        else:
            self.subject_identifier = subject_identifier
            self.tracking_identifier = tracking_identifier
        self.object = self.get_or_create_object()
        if model_obj:
            # require action_identifier from model mixin
            self.model_obj.action_identifier = self.object.action_identifier
            self.model_obj.save(update_fields=['action_identifier'])

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name}>'

    def __str__(self):
        return self.name

    @classmethod
    def as_dict(cls):
        """Returns attrs as a dictionary for the list data module
        class.
        """
        try:
            cls.model = cls.model.lower()
        except AttributeError:
            pass
        return dict(
            name=cls.name,
            display_name=cls.display_name,
            model=cls.model,
            show_on_dashboard=cls.show_on_dashboard or False,
            prn_form_action=cls.prn_form_action or False,
            instructions=cls.instructions)

    @classmethod
    def action_item_model_cls(cls):
        return django_apps.get_model(cls.action_item_model)

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

    @property
    def action_identifier(self):
        return self.object.action_identifier

    def get_or_create_object(self):
        """Returns the action item model instance represented by this
        Action.
        """
        opts = dict(
            reference_identifier=self.tracking_identifier,
            subject_identifier=self.subject_identifier,
            reference_model=self.reference_model(),
            action_type=self.action_type())
        try:
            action_item = self.action_item_model_cls().objects.get(**opts)
        except ObjectDoesNotExist:
            action_item = self.action_item_model_cls().objects.create(
                instructions=self.instructions, **opts)
        return action_item

    def get_create_actions(self):
        """Returns a list of action classes to create action items
        once on post_save.
        """
        return self.create_actions or []

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

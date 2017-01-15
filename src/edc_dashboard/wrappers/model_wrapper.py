from django.db.models.fields.reverse_related import ForeignObjectRel

from .utils import model_name_as_attr
from .wrapper import Wrapper


class ModelWrapperError(Exception):
    pass


class ModelWrapper(Wrapper):

    """A class to set attrs, flatten relations, adds admin and next urls,
    onto a model object to be used in views and templates.

    Common model and url attrs are added onto self so you can avoid
    accessing the model instance directly.
    For example:
        instead of this:
            model_wrapper._original_object.created  # not allowed in templates
            model_wrapper.wrapped_object.created
            model_wrapper.<my model name>.created
        this:
            model_wrapper.created

    * wrapped_object: The wrapped model instance. Will include URLs
        and any other attrs that the wrapper is configured to add.
    * """

    model_name = None
    url_namespace = None
    admin_site_name = 'admin'

    def __init__(self, obj):
        super().__init__(obj)
        if not hasattr(obj, '_meta'):
            raise ModelWrapperError(
                'Only model objects can be wrapped by {}. Got {}'.format(
                    self.__class__.__name__, obj))
        try:
            assert not obj._wrapped
        except AttributeError:
            pass
        except AssertionError:
            raise ModelWrapperError(
                'Object is already wrapped. Got {}'.format(obj))
        self.wrapped_object = self.model_url_wrapper(obj)
        self.wrap_me()

    def wrap_me(self):
        """Sets additional attrs onto self."""
        try:
            self.add_model_audit_fields()
        except AttributeError:
            pass
        else:
            self.id = str(self._original_object.id)
            model_name = model_name_as_attr(self._original_object)
            setattr(self, model_name, self.wrapped_object)
        self.add_from_wrapped_model()

    def add_model_audit_fields(self):
        """Adds a models audit fields to self."""
        self.created = self._original_object.created
        self.modified = self._original_object.modified
        self.user_created = self._original_object.user_created
        self.user_modified = self._original_object.user_modified
        self.hostname_created = self._original_object.hostname_created
        self.hostname_modified = self._original_object.hostname_modified
        self.revision = self._original_object.revision

    def add_from_wrapped_model(self):
        """Add field attrs from the wrapped object to self."""
        print(self)
        for field in self.wrapped_object._meta.get_fields():
            if not hasattr(self, field.name) and not isinstance(field, ForeignObjectRel):
                setattr(self, field.name, getattr(self.wrapped_object, field.name))

        self.verbose_name = self.wrapped_object._meta.verbose_name
        self.verbose_name_plural = self.wrapped_object._meta.verbose_name_plural
        # add admin urls.
        self.add_url_name = self.wrapped_object.add_url_name
        self.change_url_name = self.wrapped_object.change_url_name
        self.get_absolute_url = self.wrapped_object.get_absolute_url
        # add next url after save of model in admin
        self.next_url = self.wrapped_object.next_url
        # add any extra querystring paramters, e.g. a foreign key value
        # to filter a select list
        self.extra_querystring = self.wrapped_object.extra_querystring

    def model_url_wrapper(self, obj):
        """Add urls to obj, wrapped object."""
        obj = self.object_url_wrapper(
            key=obj._meta.label_lower, obj=obj)
        return obj

    def admin_urls_wrapper(self, obj=None, label_lower=None):
        """Adds the admin urls with namespace to the model.

        Template may access `add_url_name` and `change_url_name`."""
        admin_url_name = '{namespace}:{admin}:{label_lower}'.format(
            namespace=self.url_namespace,
            admin=self.admin_site_name,
            label_lower='_'.join(label_lower.split('.')))
        obj.add_url_name = admin_url_name + '_add'
        obj.change_url_name = admin_url_name + '_change'
        return obj

    def object_url_wrapper(self, key=None, obj=None):
        """Override to add admin urls to the model instance."""
        obj = super().object_url_wrapper(key=key, obj=obj)
        obj = self.admin_urls_wrapper(obj=obj, label_lower=key)
        return obj

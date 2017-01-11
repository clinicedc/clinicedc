from django.utils.text import camel_case_to_spaces

from .wrapper import Wrapper


def model_name_as_attr(model):
    """Returns the a model name like PlotLogEntry as plot_log_entry."""
    return camel_case_to_spaces(
        model._meta.label.split('.')[1]).replace(' ', '_')


class ModelWrapperError(Exception):
    pass


class ModelWrapper(Wrapper):

    """A class to set attrs, flatten relations, adds admin and next urls,
    onto a model object to be used in views."""

    model_name = None
    url_namespace = None
    admin_site_name = 'admin'

    def __init__(self, obj):
        super().__init__(obj)
        try:
            assert not obj._wrapped
        except AttributeError:
            self.wrapped_object = self.model_url_wrapper(obj)
            self.wrap_me()
        else:
            raise ModelWrapperError(
                'Object is already wrapped. Got {}'.format(obj))

    def wrap_me(self):
        """Sets additional attrs onto self."""
        try:
            self.created = self._original_object.created
            self.modified = self._original_object.modified
            self.user_created = self._original_object.user_created
            self.user_modified = self._original_object.user_modified
            self.hostname_created = self._original_object.hostname_created
            self.hostname_modified = self._original_object.hostname_modified
            self.revision = self._original_object.revision
        except AttributeError:
            pass
        else:
            self.id = str(self._original_object.id)
            model_name = model_name_as_attr(self._original_object)
            setattr(self, model_name, self.wrapped_object)
        self.add_url_name = self.wrapped_object.add_url_name
        self.change_url_name = self.wrapped_object.change_url_name
        self.next_url = self.wrapped_object.next_url
        self.extra_querystring = self.wrapped_object.extra_querystring

    def model_url_wrapper(self, obj):
        """Add urls to obj, wrapped object."""
        obj = self.object_url_wrapper(
            key=obj._meta.label_lower, obj=obj)
        return obj

    def admin_urls_wrapper(self, obj=None, label_lower=None):
        admin_url_name = '{namespace}:{admin}:{label_lower}'.format(
            namespace=self.url_namespace,
            admin=self.admin_site_name,
            label_lower='_'.join(label_lower.split('.')))
        obj.add_url_name = admin_url_name + '_add'
        obj.change_url_name = admin_url_name + '_change'
        return obj

    def object_url_wrapper(self, key=None, obj=None):
        obj = super().object_url_wrapper(key=key, obj=obj)
        obj = self.admin_urls_wrapper(obj=obj, label_lower=key)
        return obj

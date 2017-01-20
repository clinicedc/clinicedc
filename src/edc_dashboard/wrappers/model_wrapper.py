from django.core.exceptions import ObjectDoesNotExist
from django.db.models.fields.related import ManyToManyField, ForeignKey, OneToOneField
from django.db.models.fields.reverse_related import ForeignObjectRel

from .utils import model_name_as_attr
from .wrapper import Wrapper


class ModelWrapperError(Exception):
    pass


class ModelWrapper(Wrapper):

    """A wrapper for model instances or classes.

    Set attrs, flatten relations, adds admin and next urls,
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

    key = None  # key attr for dictionaires for next_url and extra_querystring
    model_name = None  # label lower

    def __init__(self, obj, **kwargs):
        super().__init__(obj, **kwargs)

        self.model_name = kwargs.get('model_name', self.model_name)
        self.key = kwargs.get('key', self.key)
        self.key = self.key if self.key else self.model_name

        if not hasattr(obj, '_meta'):
            raise ModelWrapperError(
                'Only model objects can be wrapped by {}. Got {}'.format(
                    self.__class__.__name__, obj))
        if self.model_name != obj._meta.label_lower:
            raise ModelWrapperError(
                'Expected {}. Got {}'.format(
                    self.model_name, obj._meta.label_lower))
        try:
            assert not obj._wrapped
        except AttributeError:
            pass
        except AssertionError:
            raise ModelWrapperError(
                'Object is already wrapped. Got {}'.format(obj))
        self.validate_properties()
        self.add_extra_attributes_before(obj, **kwargs)
        self.wrapped_object = self.model_url_wrapper(obj)
        self.add_extra_attributes_after()

    def __repr__(self):
        return '{0}(<{1}: {2} id={3}>)'.format(
            self.__class__.__name__,
            self._original_object.__class__.__name__,
            self._original_object, self._original_object.id)

    def __bool__(self):
        return True if self.id else False

    def validate_properties(self):
        """Raises an exception if a property is set that returns a ModelWrapper."""
        for key, value in self.__dict__.items():
            if hasattr(value, '_wrapped'):
                raise ModelWrapperError(
                    'Invalid property. Property may not return a wrapped object. '
                    'Got {}, {}'.format(key, value))

    def add_extra_attributes_after(self, **kwargs):
        """Called after the model is wrapped."""
        model_name = model_name_as_attr(self._original_object)
        setattr(self, model_name, self.wrapped_object)
        self.next_url = self.wrapped_object.next_url
        self.extra_querystring = self.wrapped_object.extra_querystring
        return None

    def add_extra_attributes_before(self, obj, **kwargs):
        """Called before the model is wrapped."""
        self.add_model_fields(obj)
        self.str_pk = str(obj.id)
        for key, value in kwargs.items():
            try:
                setattr(self, key, value)
            except AttributeError as e:
                raise ModelWrapper(
                    'An exception was raised when trying to set kwargs onto '
                    '{}. Got {} Using key={} value={}'.format(
                        self.__class__, str(e), key, value))
        return None

    def add_model_fields(self, obj):
        """Add field attrs to self before the model is wrapped.

        Skips foreign keys"""
        for field in obj._meta.get_fields():
            if (not hasattr(self, field.name) and
                    not isinstance(field, (
                        ManyToManyField, ForeignKey, OneToOneField, ForeignObjectRel))):
                try:
                    setattr(self, field.name, getattr(obj, field.name))
                except ObjectDoesNotExist:
                    pass
                except ValueError:
                    pass

        self.verbose_name = obj._meta.verbose_name
        self.verbose_name_plural = obj._meta.verbose_name_plural
        self.label_lower = obj._meta.label_lower
        self.get_absolute_url = obj.get_absolute_url

    def model_url_wrapper(self, obj):
        """Add urls to obj, wrapped object."""
        obj = self.object_url_wrapper(
            key=self.key, obj=obj)
        return obj

    @property
    def href(self):
        return '{0.absolute_url}?next={0.next_url}&{0.extra_querystring}'.format(self)

    @property
    def absolute_url(self):
        return self.get_absolute_url()

from django.apps import apps as django_apps

from edc_base.utils import get_utcnow

from .model_wrapper import ModelWrapper
from .utils import model_name_as_attr
from .wrapper import Wrapper
from edc_dashboard.wrappers.model_wrapper import ModelWrapperError


class ModelWithLogWrapperError(Exception):
    pass


class ModelWithLogWrapper(Wrapper):

    """A model wrapper that expects the given model instance to
    follow the LogEntry relational schema.

    For example:
        Plot->PlotLog->PlotLogEntry where Plot is the model that the
        class is instantiated with."""

    model_wrapper_class = None
    log_entry_model_wrapper_class = None
    log_model_names = []  # default is xxx_log, xxx_log_entry

    # if model and parent to the log model are not the same, define parent here.
    # for example, model = HouseholdStructure but parent to HouseholdLog
    #   is Household, not HousholdStructure.
    # Note: parent and model must be related
    parent_model_wrapper_class = None
    parent_lookup = None
    log_model_attr_prefix = None
    log_model_app_label = None  # if different from parent

    def __init__(self, obj, report_datetime=None):
        super().__init__(obj)
        self._parent = None
        self.log = None
        self.log_entry = None
        self.log_entries = None

        if not obj:
            raise ModelWithLogWrapperError('Null objects cannot be wrapped.')
        if self._original_object._meta.label_lower != self.model_wrapper_class.model_name:
            raise ModelWithLogWrapperError('\'{}\' expected \'{}\'. Got \'{}\' instead.'.format(
                self.__class__.__name__,
                self.model_wrapper_class.model_name,
                self._original_object._meta.label_lower))

        # generate rel names, label_lower, assuming we
        # followed <parent>_log, <parent>_log_entry naming
        # in the model classes
        if not self.log_model_names:
            log_model_app_label = self.log_model_app_label or obj._meta.app_label
            log_model_attr_prefix = self.log_model_attr_prefix or self.parent._original_object._meta.model_name
            self.log_model_names = [
                '{}.{}log'.format(log_model_app_label, log_model_attr_prefix),
                '{}.{}logentry'.format(log_model_app_label, log_model_attr_prefix)]

        # lookup log and log entry models using the
        # assumed "label_lower" from above
        try:
            self.log_model = django_apps.get_model(*self.log_model_names[0].split('.'))
            self.log_entry_model = django_apps.get_model(*self.log_model_names[1].split('.'))
        except LookupError as e:
            raise ModelWithLogWrapperError(
                '{} Assumed \'{}\' has a foreignkey to the log model. '
                'Using {} to generate model names. log_model_attr_prefix={}'.format(
                    e, self.parent._original_object._meta.label_lower,
                    self.log_model_attr_prefix or self.parent._original_object._meta.label_lower,
                    self.log_model_attr_prefix))

        # get the log instance from parent instance.
        # log instance must exist. usually created in
        # signal on parent post_save
        try:
            self.log = ModelWrapper(
                getattr(self.parent._original_object, self.log_model._meta.model_name),
                model_name=self.log_model._meta.label_lower)
        except AttributeError as e:
            raise ModelWithLogWrapperError(
                'Could not get Log instance from parent. Got {} '
                'Using parent=\'{}\', log field name=\'{}\', '
                'parent_lookup={}.'.format(
                    e, self.parent._original_object._meta.label_lower,
                    self.log_model._meta.model_name,
                    self.parent_lookup))

        setattr(self, model_name_as_attr(obj), self.model_wrapper_class(obj).wrapped_object)
        self.prepare_log_entries(report_datetime=report_datetime)
        # self.wrap_log_entry_objects()

    def __repr__(self):
        return '{0}(<{1}: {2} id={3}>)'.format(
            self.__class__.__name__,
            self._original_object.__class__.__name__,
            self._original_object, self._original_object.id)

    @property
    def parent(self):
        """Returns a wrapped original_object or parent model.

        parent_lookup follows Django style lookup"""
        if not self._parent:
            if self.parent_lookup:
                for attrname in self.parent_lookup.split('__'):
                    parent = getattr(self._original_object, attrname)
                self._parent = parent
            else:
                self._parent = self._original_object  # e.g. Plot
                parent_model_wrapper_class = (
                    self.parent_model_wrapper_class or self.model_wrapper_class)
            self._parent = parent_model_wrapper_class(self._parent)
        return self._parent

    @property
    def log_rel_attrs(self):
        """Converts model instance names to there reverse relation names."""
        # remove 'app_label'
        fields = [f.split('.')[1] for f in self.log_model_names]
        # last is a queryset
        fields = fields[:-1] + [fields[-1:][0] + '_set']
        return fields

    def wrap_log_entries(self):
        """Wraps the log entry and all instances in log_entries."""
        # wrap the log entries, if there are any
        objs = []
        for obj in self.log_entries.all().order_by('-report_datetime'):
            objs.append(self.log_entry_model_wrapper_class(obj))
        self.log_entries = objs

    def get_current_log_entry(self, report_datetime=None):
        report_datetime = report_datetime or get_utcnow()
        return self.log_entries.filter(
            report_datetime__date=report_datetime.date()).order_by(
                'report_datetime').last()

    def prepare_log_entries(self, report_datetime=None):
        """Sets attrs on self for model, log, log_entry.

        For example, self.plot, self.log, self.log_entries, self.log_entry."""
        log_field_attr = model_name_as_attr(self.log._original_object)

        self.log_entries = getattr(
            self.log._original_object,
            self.log_entry_model._meta.model_name + '_set')

        if self.log_entries.all().count() == 0:

            self.log_entries = []
            self.log_entry = self.new_wrapped_log_entry(log_field_attr)

        else:

            log_entry = self.get_current_log_entry(report_datetime=report_datetime)
            if log_entry:
                # wrap the current log entry
                self.log_entry = self.log_entry_model_wrapper_class(log_entry)
            else:
                self.log_entry = self.new_wrapped_log_entry(log_field_attr)

            log_entries = []
            for log_entry in self.log_entries.all().order_by('report_datetime'):
                log_entries.append(self.log_entry_model_wrapper_class(log_entry))
            self.log_entries = log_entries

    def new_wrapped_log_entry(self, log_field_attr):
        """Returns a wrapped log entry, un-saved and disabled."""
        new_obj = self.log_entry_model(**{log_field_attr: self.log._original_object})
        new_obj.save = ModelWrapperError
        new_obj.save_base = ModelWrapperError
        return self.log_entry_model_wrapper_class(new_obj)

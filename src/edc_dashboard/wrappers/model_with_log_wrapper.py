from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from edc_base.utils import get_utcnow

from .utils import model_name_as_attr
from .wrapper import Wrapper


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
    parent_alias = None  # label_lower, if name prefix to log, log_entry is not model_name of parent

    def __init__(self, obj, report_datetime=None):
        super().__init__(obj)
        if not obj:
            raise ModelWithLogWrapperError('Null objects cannot be wrapped.')
        if self._original_object._meta.label_lower != self.model_wrapper_class.model_name:
            raise ModelWithLogWrapperError('\'{}\' expected \'{}\'. Got \'{}\' instead.'.format(
                self.__class__.__name__,
                self.model_wrapper_class.model_name,
                self._original_object._meta.label_lower))
        if self.parent_lookup:
            self.parent = self.lookup_parent(obj)
        else:
            self.parent = obj  # e.g. Plot
        self.log = None
        self.log_entry = None
        self.log_entry_set = None
        if not self.log_model_names:
            self.log_model_names = [
                (self.parent_alias or self.parent._meta.label_lower) + 'log',
                (self.parent_alias or self.parent._meta.label_lower) + 'logentry']
        self.log_model = django_apps.get_model(*self.log_model_names[0].split('.'))
        self.log_entry_model = django_apps.get_model(*self.log_model_names[1].split('.'))
        setattr(self, model_name_as_attr(obj), self.model_wrapper_class(obj).wrapped_object)
        try:
            getattr(self.parent, self.log_model._meta.label_lower.split('.')[1])
        except ObjectDoesNotExist:
            # nothing to do, no log model
            pass
        else:
            self.prepare(report_datetime=report_datetime)
            self.wrap_log_entry_objects()
            parent_model_wrapper_class = self.parent_model_wrapper_class or self.model_wrapper_class
            self.parent = parent_model_wrapper_class(self.parent)

    def lookup_parent(self, obj):
        instance = obj
        for attr in self.parent_lookup.split('__'):
            instance = getattr(instance, attr)
        return instance

    @property
    def log_rel_attrs(self):
        """Converts model instance names to there reverse relation names."""
        # remove 'app_label'
        fields = [f.split('.')[1] for f in self.log_model_names]
        # last is a queryset
        fields = fields[:-1] + [fields[-1:][0] + '_set']
        return fields

    @property
    def mock_log_entry(self):
        # TODO: can we do away with this????
        class MockLogEntry:
            def get_absolute_url(self):
                return self.log_entry_model.get_absolute_url

            class Meta:
                label_lower = self.log_entry_model._meta.label_lower
                label = self.log_entry_model._meta.label
                verbose_name = 'Mock'
                verbose_name_plural = 'Mock'

                def get_fields(self):
                    return []
            _mocked_object = True
            _meta = Meta()
        mock_log_entry = MockLogEntry()
        setattr(mock_log_entry, model_name_as_attr(self.log), self.log)
        return mock_log_entry

    def wrap_log_entry_objects(self):
        """Wraps the log entry and all instances in log_entry_set."""
        self.log_entry = self.log_entry_model_wrapper_class(self.log_entry).wrapped_object
        # wrap the log entries, if there are any
        objs = []
        for obj in self.log_entry_set.all().order_by('-report_datetime'):
            objs.append(self.log_entry_model_wrapper_class(obj).wrapped_object)
        self.log_entry_set = objs

    def get_current_log_entry(self, report_datetime=None):
        report_datetime = report_datetime or get_utcnow()
        return self.log_entry_set.filter(
            report_datetime__date=report_datetime.date()).order_by(
                'report_datetime').last()

    def prepare(self, report_datetime=None):
        """Sets attrs on self for model, log, log_entry.

        For example, self.plot, self.log, self.log_entry_set, self.log_entry."""
        value = self.parent
        # set attrs, e.g. log, log_entry
        for attr, rel_attr in zip(['log', 'log_entry_set'], self.log_rel_attrs):
            try:
                value = getattr(value, rel_attr)
                setattr(self, attr, value)
            except AttributeError:
                setattr(self, attr, None)
        # set log_entry to its queryset or None
        if self.log_entry_set.all().count() == 0:
            self.log_entry_set = self.log_entry_model.objects.none()
            self.log_entry = self.mock_log_entry
        else:
            # get the current log entry
            self.log_entry = self.log_entry_set.filter(
                report_datetime__date=get_utcnow().date()).order_by(
                    'report_datetime').last()
            self.log_entry = self.get_current_log_entry(
                report_datetime=report_datetime) or self.mock_log_entry

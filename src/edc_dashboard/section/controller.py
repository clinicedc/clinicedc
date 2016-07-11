import copy

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_module
from django.utils.module_loading import module_has_submodule

from .base_section_view import BaseSectionView
from .helpers import SectionNamedTpl


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class Controller(object):

    """ Main controller of :class:`Section` objects. """

    def __init__(self):
        self.registry = {}
        self.is_autodiscovered = False
        self._section_tuples = []
        self._section_names = []
        self._section_display_names = []
        self._section_display_indexes = []
        self._indexed_section_tuples = []
        self._indexed_section_display_names = []

    def reset_controller(self):
        """Resets everything except the registry."""
        self._section_tuples = None
        self._section_names = None
        self._section_display_names = None
        self._section_display_indexes = None
        self._indexed_section_tuples = None
        self._indexed_section_display_names = None

    def register(self, section_view_cls, replaces=None):
        """Registers section_view_classes to the registry dictionary
        as {section_view_cls.sectionname: section_view_cls}.

        Adds the class to the registry by section_name.

        Kwargs:
          * replaces: dictionary key of class to replace if it exists. Default(None)
        """
        if not isinstance(section_view_cls(), BaseSectionView):
            raise AlreadyRegistered('Expected an instance of BaseSectionView. Got {0}.'.format(section_view_cls))
        if (section_view_cls().section_name in self.registry and
                section_view_cls().section_name != replaces):
            raise AlreadyRegistered('A section view class of type {1} is already '
                                    'registered ({0})'.format(section_view_cls, section_view_cls().section_name))
        if 'DENIED_SECTIONS_FOR_GROUP' in dir(settings) and 'LOGGED_IN_USER_GROUP' in dir(settings):
            logged_in_user_group = settings.LOGGED_IN_USER_GROUP  # settings.LOGGED_IN_USER_GROUP must be changed.
            # FIXME: Only temporary until i figure out how to get logged in USER from within a class properly.
            if settings.DENIED_SECTIONS_FOR_GROUP.get(logged_in_user_group, None):
                # denied_sections_for_user should be a tuple of section names
                denied_sections_for_user = settings.DENIED_SECTIONS_FOR_GROUP.get(logged_in_user_group)
                if not section_view_cls().get_section_name() in denied_sections_for_user:
                    self.registry[section_view_cls().section_name] = section_view_cls()
        else:
            self.registry[section_view_cls().section_name] = section_view_cls()

    def all(self):
        """Returns the registry as a dcitionary."""
        return self.registry

    @property
    def section_names(self):
        """Sets to a list of the internal section names, the same as the _registry keys."""
        if not self._section_names:
            self._section_names = [tpl.section_name for tpl in self.section_tuples]
            self._section_names.sort()
        return self._section_names

    @property
    def indexed_section_tuples(self):
        """Returns a list of section tuples in order of display index."""
        if not self._indexed_section_tuples:
            for index in self.section_display_indexes:
                for section_tpl in self.section_tuples:
                    if section_tpl.display_index == index:
                        self._indexed_section_tuples.append(section_tpl)
                        break
        return self._indexed_section_tuples

    @property
    def indexed_section_display_names(self):
        if not self._indexed_section_display_names:
            self._indexed_section_display_names = [tpl.display_name for tpl in self.indexed_section_tuples]
        return self._indexed_section_display_names

    @property
    def section_display_names(self):
        if not self._section_display_names:
            self._section_display_names = [tpl.display_name for tpl in self.section_tuples]
            self._section_display_names.sort()
        return self._section_display_names

    @property
    def section_display_indexes(self):
        """Returns an ordered list of section display indexes."""
        if not self._section_display_indexes:
            self._section_display_indexes = [tpl.display_index for tpl in self.section_tuples]
            self._section_display_indexes.sort()
            # check for duplicates
            lst = list(set(self._section_display_indexes))
            lst.sort()
            if lst != self._section_display_indexes:
                raise ImproperlyConfigured(
                    'Section classes must have a unique section_display_index. '
                    'Got {0} from site_sections {1}. Check the section cls in '
                    'each app. Section tuples are {2}'.format(
                        self._section_display_indexes, site_sections.get_section_names,
                        site_sections.section_tuples))
        return self._section_display_indexes

    @property
    def section_tuples(self):
        """Returns a list of named tuples (section_name, display_name, display_index)."""
        """Sets to a list of named tuples with section information
        of the format (section_name, display_name, display_index)."""
        if not self._section_tuples:
            self._section_tuples = []
            for inst in self.registry.values():
                tpl = SectionNamedTpl(
                    section_name=inst.section_name,
                    display_name=inst.section_display_name,
                    display_index=inst.section_display_index)
                if tpl not in self._section_tuples:
                    self._section_tuples.append(tpl)
        return self._section_tuples

    @property
    def section_list(self):
        """Wrapper for :func:`get_section_tuples`."""
        return self.section_tuples

    def update_section_lists(self):
        for section in self.registry.values():
            section.section_list = self.registry.keys()

    def unregister(self, section_name):
        if section_name in self.registry:
            del self.registry[section_name]
        self.reset_controller()

    def autodiscover(self):
        before_import_registry = None
        module_name = 'section'
        if not self.is_autodiscovered:
            for app in django_apps.app_configs:
                try:
                    mod = import_module(app)
                    try:
                        before_import_registry = copy.copy(site_sections.registry)
                        import_module('{}.{}'.format(app, module_name))
                        #sys.stdout.write(' * registered visit schedules from application \'{}\'\n'.format(app))
                    except:
                        site_sections.registry = before_import_registry
                        if module_has_submodule(mod, module_name):
                            raise
                except ImportError:
                    pass
            self.is_autodiscovered = True
        #if not self.is_autodiscovered:
        #    for app in settings.INSTALLED_APPS:
        #        mod = import_module(app)
        #        try:
        #            before_import_registry = copy.copy(site_sections.registry)
        #            import_module('%s.section' % app)
        #        except:
        #            site_sections.registry = before_import_registry
        #            if module_has_submodule(mod, 'section'):
        #                raise
        #    self.is_autodiscovered = True

site_sections = Controller()

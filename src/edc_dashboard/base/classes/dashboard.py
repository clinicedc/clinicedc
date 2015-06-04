import copy
import re

from django.conf import settings
from django.shortcuts import render
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils import translation
from django.views.generic import TemplateView

from edc_dashboard.section.classes import site_sections


class Dashboard(TemplateView):

    dashboard_name = None
    dashboard_url_name = None
    urlpattern_view = None
    urlpatterns = [
        '^(?P<dashboard_type>{dashboard_type})/(?P<dashboard_model>{dashboard_model})/(?P<dashboard_id>{pk})/$',
    ]
    urlpattern_options = {
        'pk': '[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}',
        'dashboard_model': '*',
        'dashboard_type': '*'}

    def __init__(self, **kwargs):
        super(Dashboard, self).__init__(**kwargs)
        self._extra_url_context = None
        self.context = None
        self.dashboard_model = None
        self.dashboard_models = {}

    def get_context_data(self, **kwargs):
        """Returns the TemplateView.context after first adding additional items."""
        self.context = super(Dashboard, self).get_context_data(**kwargs)
        self.dashboard_model = self.dashboard_models.get(self.context.get('dashboard_model'))
        self.dashboard_model_name = self.context.get('dashboard_model')
        self.context.update(
            template=self.template_name,
            dashboard_model_name=self.context.get('dashboard_model'),
            dashboard_model_instance=self.dashboard_model_instance,
            dashboard_name=self.dashboard_name,
            dashboard_url_name=self.dashboard_url_name,
            home_url=self.home_url)
        return self.context

    def post(self, request, *args, **kwargs):
        """Allows a POST -- without the class returns a 405 error."""
        return render(request, self.template_name, self.get_context_data(**kwargs))

    @classmethod
    def get_urlpatterns(cls):
        """Returns a list of urlpattern strings for the urls.py."""
        cls.validate_urlpattern_with_options()
        return map(lambda s: s.format(**cls.urlpattern_options), cls.urlpatterns)

    @property
    def dashboard_type(self):
        if self.context.get('dashboard_type') not in self.dashboard_type_list:
            raise TypeError('Invalid edc_dashboard type. Expected one of {0}. Got \'{1}\''.format(
                self.dashboard_type_list, self.context.get('dashboard_type')))
        return self.context.get('dashboard_type')

    @property
    def dashboard_id(self):
        re_pk = re.compile('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}')
        if not re_pk.match(self.context.get('dashboard_id') or ''):
            raise TypeError('Dashboard id must be a uuid (pk). Got {0}'.format(self.context.get('dashboard_id')))
        return self.context.get('dashboard_id')

    @property
    def dashboard_model_instance(self):
        try:
            dashboard_model_instance = self.dashboard_model.objects.get(pk=self.dashboard_id)
        except AttributeError:
            dashboard_model_instance = None
        except self.dashboard_model.DoesNotExist:
            dashboard_model_instance = None
        return dashboard_model_instance

    @property
    def home_url(self):
        """Returns a home url."""
        try:
            return reverse(
                self.dashboard_url_name,
                kwargs={
                    'dashboard_type': self.dashboard_type,
                    'dashboard_model': self.dashboard_model_name,
                    'dashboard_id': self.dashboard_id}
            )
        except NoReverseMatch:
            pass

    @property
    def search_type(self):
        return self.section.get_search_type(self.get_section_name())

    @property
    def section(self):
        return self._section

    @section.setter
    def section(self, section_name):
        """Sets the instance of the section class for the edc_dashboard."""
        section = site_sections.get(section_name)
        if not section:
            if site_sections.get_section_names() == []:
                raise TypeError('class site_sections is not set up. Call autodoscover first.')
            section = site_sections.get(section_name)
        if not section:
            raise TypeError(
                'Could not find section \'{0}\' in site_sections. You need to '
                'define a section class for this name in section.py.'.format(section_name))
        self._section = section()

    @property
    def section_name(self):
        return self.section.get_section_name()

    @property
    def extra_url_context(self):
        return self._extra_url_context

    @extra_url_context.setter
    def extra_url_context(self, value):
        self._extra_url_context = value
        default_value = '&form_language_code={0}'.format(self.language)
        if default_value not in self._extra_url_context:
            self._extra_url_context = '{0}{1}'.format(
                self._extra_url_context, '&form_language_code={0}'.format(self.language))

    @property
    def language(self):
        """Returns the language of consent.

        If the consent has not been defined for this edc_dashboard, just take the settings LANGUAGE attribute."""
        if self.consent:
            self.consent.language
            translation.activate(self.consent.language)
            self._language = translation.get_language()
        else:
            self._language = settings.LANGUAGE_CODE
        return self._language

    @classmethod
    def validate_urlpattern_with_options(cls):
        """Returns True if all keywords in the cls.urlpatterns have matching keywords from
        the urlpattern_options dictionary or raises an error."""
        p = re.compile('\{\w+\}')
        for urlpattern in cls.urlpatterns:
            matches = p.findall(urlpattern)
            not_found = copy.copy(matches)
            for match in matches:
                if not cls.urlpattern_options.get(match.strip('{}')):
                    raise ImproperlyConfigured('Keyword not found for placeholder in urlpattern. Got \'{}\'.'.format(match.strip('{}')))
                not_found.remove(match)
            if not_found:
                raise ImproperlyConfigured('Unexpected placeholder(s) in urlpattern. No matching key in urlpattern_options. Got placeholders {}.'.format(not_found))
        return True

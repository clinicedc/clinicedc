from datetime import date, time, datetime, timedelta
from decimal import Decimal

from django.conf.urls import patterns, url
from django.db import models
from django.db.models import Q
from django.core.exceptions import ImproperlyConfigured

from edc_base.encrypted_fields import BaseEncryptedField

from ..exceptions import SearchError
from ..forms import SearchForm


class BaseSearcher(object):

    """ Base search class. """

    name = None
    search_model = None
    search_form = None
    search_form_field_name = None
    template = None
    order_by = ['-modified', '-created']

    def __init__(self):
        self._search_value = None
        self._search_form_field_name = None
        self.search_result_include_template = self.template or '{0}_include.html'.format(
            self.search_model._meta.object_name.lower())
        self.search_form = self.search_form or SearchForm
        self.search_form_data = {}  # set in the view, only access through a form
        self.search_form_field_name = self.search_form_field_name or 'search_term'

    def contribute_to_context(self, context):
        context.update({'search_form': self.search_form(self.search_form_data)})
        return context

    @property
    def search_value(self):
        """Returns the search value."""
        return self._search_value

    @search_value.setter
    def search_value(self, value):
        """Sets the value after striping.

        The search value is assigned in the view from the form."""
        self._search_value = value.strip()

    @property
    def search_form_field_name(self):
        return self._search_form_field_name

    @search_form_field_name.setter
    def search_form_field_name(self, field_name):
        """Sets the search field after confirming the field exists on the search Form Class."""
        try:
            [field.name for field in SearchForm().visible_fields()].index(field_name)
            self._search_form_field_name = field_name
        except ValueError:
            raise ImproperlyConfigured(
                'Search form field \'{}\' is not a visible field of search_form \'{}\''.format(
                    field_name, self.search_form))

    @property
    def search_result(self):
        try:
            return self.search_model.objects.filter(self.qset).order_by(*self.order_by)
        except TypeError:
            return []

    @property
    def qset(self):
        """Builds and returns a qset, Q(), based on a single search value against any text or integer fields.

        If the field is an Encrypted field, the search value is hashed using the models fields
        field_cryptor.

        If the form is not valid, nothing is returned."""
        qset = None
        form = self.search_form(self.search_form_data)
        if form.is_valid():
            search_value = form.data.get(self.search_form_field_name)
            qset = Q()
            for field in self.search_model._meta.fields:
                if isinstance(field, BaseEncryptedField):
                    qset.add(Q(**{'{0}__exact'.format(field.name): search_value}), Q.OR)
                elif isinstance(field, (models.CharField, models.TextField)):
                    qset.add(Q(**{'{0}__icontains'.format(field.name): search_value}), Q.OR)
                elif isinstance(field, (models.IntegerField, models.FloatField, models.DecimalField)):
                    try:
                        search_value = int(search_value)
                    except ValueError:
                        try:
                            search_value = float(search_value)
                        except ValueError:
                            search_value = Decimal(search_value)
                    finally:
                        qset.add(Q(**{'{0}'.format(field.name): search_value}), Q.OR)
                elif isinstance(field, (models.DateTimeField, models.DateField)):
                    pass
                elif isinstance(field, (models.ForeignKey, models.OneToOneField, models.ManyToManyField,
                                        models.ImageField, models.NullBooleanField, models.BooleanField)):
                    pass
                else:
                    raise SearchError('model contains a field type not handled. '
                                      'Got {0} from model {1}.'.format(field, self.search_model_cls))
        return qset

    def url_patterns(self, view, section_name=None):
        """Returns a url pattern which includes the section prefix of the url pattern.

        This is called by the section class."""
        # TODO: can section be removed from this??
        if section_name:
            return patterns(
                '',
                url(
                    (r'^(?P<section_name>{section_name})/(?P<search_name>{search_name})/'
                     '(?P<search_term>[\d\w\ \-\<\>]+)/$'.format(section_name=section_name, search_name=self.name)),
                    view,
                    name="section_search_{name}_url".format(name=self.name)),
                url(
                    r'^(?P<section_name>{section_name})/(?P<search_name>{search_name})/$'.format(
                        section_name=section_name, search_name=self.name),
                    view,
                    name="section_search_{name}_url".format(name=self.name)))
        return patterns(
            '',
            url(
                r'^(?P<search_name>{search_name})/(?P<search_term>{search_term})/$'.format(
                    search_name=self.name, search_term=self.search_form_field_name),
                view,
                name="search_{name}_url".format(name=self.name)),
            url(r'^(?P<search_name>{search_name})/$'.format(search_name=self.name),
                view,
                name="search_{name}_url".format(name=self.name)))

    def hash_value(self, field, value):
        """ Returns a hash if this is an encrypted field """
        try:
            value = field.field_cryptor.get_hash_with_prefix(value)
        except AttributeError:
            pass
        return value

    @property
    def special_keyword_queryset(self):
        if self.search_value.lower() == '?':
            queryset = self.search_model.objects.all().order_by('-modified')[0:15]
        elif self.search_value.lower().startswith('?last'):
            limit = self.search_value.lower().split('?last')[1] or 15
            queryset = self.search_model.objects.all().order_by('-modified')[0:limit]
        elif self.search_value.lower().startswith('?first'):
            limit = self.search_value.lower().split('?first')[1] or 15
            queryset = self.search_model.objects.all().order_by('modified')[0:limit]
        elif self.search_value.lower() == '?today':
            queryset = self.search_model.objects.filter(
                modified__gte=datetime.combine(date.today(), time.min)).order_by('modified')
        elif self.search_value.lower() == '?yesterday':
            queryset = self.search_model.objects.filter(
                modified__gte=datetime.combine(date.today() - timedelta(days=1), time.min)).order_by('modified')
        elif self.search_value.lower() == '?lastweek':
            queryset = self.search_model.objects.filter(
                modified__gte=datetime.combine(date.today() - timedelta(days=7), time.min)).order_by('modified')
        else:
            queryset = None
        return queryset

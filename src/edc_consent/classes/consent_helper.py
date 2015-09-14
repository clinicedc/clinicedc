import copy

from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.apps import apps

from edc_base.model.models import BaseModel

from ..exceptions import ConsentError, ConsentDoesNotExist


class ConsentHelper(object):
    """Provides methods to help manage subject consents and the data models covered by edc_consent.

    May be subclassed at the protocol module to override :func:`clean_versioned_field` to add more detailed
    data checks for versioned fields than the default. For example, from mpepu_maternal::

        from edc.subject.edc_consent.classes import ConsentHelper

        class MaternalEligibilityConsentHelper(ConsentHelper):
            def clean_versioned_field(self, field_value, field, start_datetime, consent_version):
                if getattr(self.subject_instance, 'feeding_choice') == 'Yes':
                    if field.name == 'maternal_haart' and getattr(self.subject_instance, 'is_cd4_low'):
                        if  field_value == 'No' and getattr(self.subject_instance, 'is_cd4_low') < 250:
                            raise self.get_exception_cls()('Mother must be willing to '
                                                           'initiate HAART if feeding choice is BF and '
                                                           'CD4 < 250 for data captured during or after '
                                                           'version {2}. [{3}]'.format(field.name, start_datetime,
                                                           consent_version, field.verbose_name[0:50]))

    """

    def __init__(self, subject_instance, exception_cls=None, **kwargs):
        self._report_datetime = None
        self._subject_identifier = None
        self._current_consent_version = None
        self._exception_cls = None
        self._consent_models = []
        self._suppress_exception = kwargs.get('suppress_exception', False)
        self.exception_cls = exception_cls
        self.subject_instance = subject_instance

    @property
    def subject_instance(self):
        return self._subject_instance

    @subject_instance.setter
    def subject_instance(self, subject_instance):
        """Sets the subject instance after confirming model is listed and active in AttachedModels.

        You can add to the model a method :func:`get_requires_consent`
        returning False, to bypass, or True to force.

        Args:
            subject_instance: a model instance or tuple of (model_cls, cleaned_data)

        .. seealso:: Results may not be as expected.
        See comment on :class:`base_consented_model_form.BaseConsentedModelForm`
        :func:`check_attached`.
        """
        try:
            subject_instance = self.unpack_subject_instance_tuple(subject_instance)
        except ValueError:
            AttachedModel = apps.get_model('edc_consent', 'AttachedModel')
            if not AttachedModel.objects.filter(
                    content_type_map__model=subject_instance._meta.object_name.lower(), is_active=True).exists():
                raise self.exception_cls(
                    'Subject Model must be listed, and active, in AttachedModel of '
                    'the ConsentCatalogue. Model {0} not found or not active.'.format(
                        subject_instance._meta.object_name.lower()))
        self._subject_instance = subject_instance

    def unpack_subject_instance_tuple(self, tpl):
        """Receives a tuple of model class and cleaned data to initialize an instance of the model_class.

            Args:
                tpl: tuple of (model_cls, cleaned_data).

        ..note:: Removes the many to many fields before initializing the Model class."""
        # unpack subject_instance
        subject_model_cls, cleaned_data = tpl
        # deep copy because we are manipulating cleaned data in order to initiate the model class
        cleaned_data = copy.deepcopy(cleaned_data)
        if not issubclass(subject_model_cls, BaseModel):
            raise TypeError(
                'The first item of the subject instance tuple, (model_cls, cleaned_data), '
                'must be a subclass of BaseModel.')
        if not isinstance(cleaned_data, dict):
            raise TypeError(
                'The second item of the subject instance tuple, (model_cls, cleaned_data), '
                'must be a dictionary.')
        # check to remove m2m fields from cleaned data, assuming
        # field names listed in cleaned data and not in
        # fields are ManyToMany fields
        field_names = [field.name for field in subject_model_cls._meta.local_many_to_many]
        del_keys = [k for k in cleaned_data.iterkeys() if k in field_names]
        for k in del_keys:
            del cleaned_data[k]
        if 'DELETE' in cleaned_data:
            del cleaned_data['DELETE']
        return subject_model_cls(**cleaned_data)

    @property
    def report_datetime(self):
        """Sets and returns the datetime field to use to compare with the start and end dates
        of consents listed in the edc_consent catalogue.

        The report_datetime comes from the subject_instance."""
        return self.subject_instance.report_datetime

    @property
    def subject_identifier(self):
        """Sets and Gets the subject_identifier from the instance."""
        return self.subject_instance.subject_identifier

    @property
    def consent_models(self):
        """Sets edc_consent models for this instance by querying the AttachedModel class."""
        if not self._consent_models:
            AttachedModel = apps.get_model('edc_consent', 'AttachedModel')
            # find if any edc_consent models listed in the catalogue cover this report_datetime
            attached_models = AttachedModel.objects.filter(
                content_type_map__model=self.subject_instance._meta.object_name.lower())
            for attached_model in attached_models:
                if (self.report_datetime >= attached_model.consent_catalogue.start_datetime and
                        self.report_datetime < attached_model.consent_catalogue.end_datetime):
                    self._consent_models.append(
                        attached_model.consent_catalogue.content_type_map.content_type.model_class())
            if not self._consent_models:
                if not self._suppress_exception:
                    raise self.exception_cls(
                        'Data collection not permitted. Subject has no edc_consent '
                        'to cover form \'{0}\' with date {1}.'.format(
                            self.subject_instance._meta.verbose_name, self.report_datetime))
                else:
                    pass
        return self._consent_models

    def get_current_consent_version(self):
        """Returns the current edc_consent version relative to the given
        subject_instance report_datetime and subject_identifier."""
        ConsentCatalogue = apps.get_model('edc_consent', 'ConsentCatalogue')
        current_consent_version = None
        consent_model_names = [consent_model._meta.object_name.lower() for consent_model in self.consent_models]
        catalogues = ConsentCatalogue.objects.filter(
            content_type_map__model__in=consent_model_names)
        for consent_catalogue in catalogues:
            end_date = consent_catalogue.end_datetime or datetime.today() + relativedelta(days=1)
            if (self.report_datetime >= consent_catalogue.start_datetime and
                    self.report_datetime < end_date):
                current_consent_version = consent_catalogue.version
        if not current_consent_version:
            if not self._suppress_exception:
                raise self.exception_cls(
                    'Cannot determine the version of edc_consent '
                    '\'{0}\' using \'{1}\''.format(self.subject_instance, self.report_datetime))
            else:
                pass
        return current_consent_version

    def is_off_study(self):
        from edc_subject.off_study.models import BaseOffStudy
        if not isinstance(self.subject_instance, BaseOffStudy):
            if self.subject_instance.is_off_study():
                raise self.exception_cls(
                    'Data collection not allowed after off study date. Subject was taken '
                    'off study before this form\'s report datetime \'{0}\'. '
                    '(ConsentHelper)'.format(self.subject_instance.get_report_datetime()))

    def clean_versioned_field(self, field_value, field, start_datetime, consent_version):
        """Runs checks on a versioned field.

        Users may override."""
        if not field_value:
            # require a user provided value
            raise self.exception_cls(
                'Field \'{0}\' cannot be blank for data captured during'
                'or after version {2}. [{3}]'.format(
                    field.name,
                    start_datetime,
                    consent_version,
                    field.verbose_name[0:50]
                )
            )

    def validate_versioned_fields(self):
        """Validate fields under edc_consent version control to be set to the default value or not (None).

        This validation logic should also be applied in the forms.py along with more field
        specific validation logic."""
        ConsentCatalogue = apps.get_model('edc_consent', 'ConsentCatalogue')
        current_consent_version = self.get_current_consent_version()
        # cycle through all versions in the edc_consent catalogue
        for consent_catalogue in ConsentCatalogue.objects.all().order_by('start_datetime', 'version'):
            consent_version = consent_catalogue.version
            start_datetime = consent_catalogue.start_datetime
            if not start_datetime:
                raise TypeError('Cannot determine edc_consent version start date. Check the Consent Catalogue')
            if self.subject_instance.get_versioned_field_names(consent_version):
                for field in self.subject_instance._meta.fields:
                    if field.name in self.subject_instance.get_versioned_field_names(consent_version):
                        field_value = getattr(self.subject_instance, field.name)
                        if self.report_datetime < start_datetime and field_value:
                            # enforce None / default
                            raise self.exception_cls(
                                'Field \'{0}\' must be left blank for data captured prior to version {2}. [{3}]'
                                .format(field.name, start_datetime, consent_version, field.verbose_name[0:50]))
                        if self.report_datetime >= start_datetime:
                            self.clean_versioned_field(field_value, field, start_datetime, consent_version)
        return current_consent_version

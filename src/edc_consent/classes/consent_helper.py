import copy
from datetime import datetime
from django.db.models import get_model
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from edc.base.model.models import BaseModel
from edc_consent import ConsentError, ConsentDoesNotExist


class ConsentHelper(object):
    """Provides methods to help manage subject consents and the data models covered by edc_consent.

    May be subclassed at the protocol module to override :func:`clean_versioned_field` to add more detailed
    data checks for versioned fields than the default. For example, from mpepu_maternal::

        from edc.subject.edc_consent.classes import ConsentHelper

        class MaternalEligibilityConsentHelper(ConsentHelper):
            def clean_versioned_field(self, field_value, field, start_datetime, consent_version):
                if getattr(self.get_subject_instance(), 'feeding_choice') == 'Yes':
                    if field.name == 'maternal_haart' and getattr(self.get_subject_instance(), 'is_cd4_low'):
                        if  field_value == 'No' and getattr(self.get_subject_instance(), 'is_cd4_low') < 250:
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
        self._set_exception_cls(exception_cls)
        self._set_subject_instance(subject_instance)

    def _set_exception_cls(self, cls=None):
        self._exception_cls = cls or ValidationError

    def _get_exception_cls(self):
        return self._exception_cls

    def _set_subject_instance(self, subject_instance):
        """Sets the subject instance after confirming model is listed and active in AttachedModels.

        You can add to the model a method :func:`get_requires_consent` returning False, to bypass, or True to force.

        Args:
            subject_instance: a model instance or tuple of (model_cls, cleaned_data)

        .. seealso:: Results may not be as expected.
        See comment on :class:`base_consented_model_form.BaseConsentedModelForm` :func:`check_attached`.
        """
        if isinstance(subject_instance, tuple):
            subject_instance = self.unpack_subject_instance_tuple(subject_instance)
        RegisteredSubject = get_model('registration', 'RegisteredSubject')
        if not isinstance(subject_instance, RegisteredSubject):
            AttachedModel = get_model('edc_consent', 'AttachedModel')
            if not AttachedModel.objects.filter(content_type_map__model=subject_instance._meta.object_name.lower(), is_active=True).exists():
                raise self._get_exception_cls()('Subject Model must be listed, and active, in AttachedModel of the ConsentCatalogue. Model {0} not found or not active.'.format(subject_instance._meta.object_name.lower()))
        self._subject_instance = subject_instance

    def get_subject_instance(self):
        return self._subject_instance

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
            raise TypeError('The first item of the subject instance tuple, (model_cls, cleaned_data), must be a subclass of BaseModel.')
        if not isinstance(cleaned_data, dict):
            raise TypeError('The second item of the subject instance tuple, (model_cls, cleaned_data), must be a dictionary.')
        # check to remove m2m fields from cleaned data, assuming field names listed in cleaned data and not in
        # fields are ManyToMany fields
        field_names = [field.name for field in subject_model_cls._meta.local_many_to_many]
        del_keys = [k for k in cleaned_data.iterkeys() if k in field_names]
        for k in del_keys:
            del cleaned_data[k]
        if 'DELETE' in cleaned_data:
            del cleaned_data['DELETE']
        return subject_model_cls(**cleaned_data)

    def _set_report_datetime(self):
        """Sets the datetime field to use to compare with the start and end dates of consents listed in the edc_consent catalogue.

        The report_datetime comes from the subject_instance."""

        self._report_datetime = None
        if 'get_report_datetime' in dir(self.get_subject_instance()):
            self._report_datetime = self.get_subject_instance().get_report_datetime()
        elif 'get_visit' in dir(self.get_subject_instance()):
            self._report_datetime = self.get_subject_instance().get_visit().report_datetime
        elif 'report_datetime' in dir(self.get_subject_instance()):
            self._report_datetime = self.get_subject_instance().report_datetime
        elif 'registration_datetime' in dir(self.get_subject_instance()):
            self._report_datetime = self.get_subject_instance().registration_datetime
        elif 'get_registration_datetime' in dir(self.get_subject_instance()):
            self._report_datetime = self.get_subject_instance().get_registration_datetime()
        else:
            raise self._get_exception_cls()('Cannot determine datetime to use for model {0} to compare with the edc_consent catalogue. Add get_report_datetime() to the model.'.format(self.get_subject_instance()._meta.object_name))

    def _get_report_datetime(self):
        if not self._report_datetime:
            self._set_report_datetime()
        return self._report_datetime

    def _set_subject_identifier(self):
        """Gets the subject_identifier from the instance."""
        self._subject_identifier = None
        if 'get_subject_identifier' in dir(self.get_subject_instance()):
            self._subject_identifier = self.get_subject_instance().get_subject_identifier()
        elif 'subject_identifier' in dir(self.get_subject_instance()):
            self._subject_identifier = self.get_subject_instance().subject_identifier
        elif 'get_visit' in dir(self.get_subject_instance()):
            self._subject_identifier = self.get_subject_instance().get_visit().get_subject_identifier()
        else:
            raise self._get_exception_cls()('Cannot determine the subject_identifier for model {0} needed to lookup the edc_consent. Perhaps add method get_subject_identifier() to the model.'.format(self.get_subject_instance()._meta.object_name))

    def _get_subject_identifier(self):
        if not self._subject_identifier:
            self._set_subject_identifier()
        return self._subject_identifier

    def _set_consent_models(self):
        """Sets edc_consent models for this instance by querying the AttachedModel class."""
        self._consent_models = []
        AttachedModel = get_model('edc_consent', 'AttachedModel')
        # find if any edc_consent models listed in the catalogue cover this report_datetime
        for attached_model in AttachedModel.objects.filter(content_type_map__model=self.get_subject_instance()._meta.object_name.lower()):
            if self._get_report_datetime() >= attached_model.consent_catalogue.start_datetime and self._get_report_datetime() < attached_model.consent_catalogue.end_datetime:
                self._consent_models.append(attached_model.consent_catalogue.content_type_map.content_type.model_class())
        if not self._consent_models:
            if not self._suppress_exception:
                raise self._get_exception_cls()('Data collection not permitted. Subject has no edc_consent to cover form \'{0}\' with date {1}.'.format(self.get_subject_instance()._meta.verbose_name, self._get_report_datetime()))
            else:
                pass

    def _get_consent_models(self):
        """Gets edc_consent models for this subject_instance."""
        if not self._consent_models:
            self._set_consent_models()
        return self._consent_models

    def get_current_consent_version(self):
        """Returns the current edc_consent version relative to the given subject_instance report_datetime and subject_identifier."""
        ConsentCatalogue = get_model('edc_consent', 'ConsentCatalogue')
        current_consent_version = None
        catalogues = ConsentCatalogue.objects.filter(content_type_map__model__in=[consent_model._meta.object_name.lower() for consent_model in self._get_consent_models()])
        for consent_catalogue in catalogues:
            end_date = consent_catalogue.end_datetime or datetime.today() + relativedelta(days=1)
            if self._get_report_datetime() >= consent_catalogue.start_datetime and self._get_report_datetime() < end_date:
                current_consent_version = consent_catalogue.version
        if not current_consent_version:
            if not self._suppress_exception:
                raise self._get_exception_cls()('Cannot determine the version of edc_consent \'{0}\' using \'{1}\''.format(self.get_subject_instance(), self._get_report_datetime()))
            else:
                pass
        return current_consent_version

    def is_off_study(self):
        from edc.subject.off_study.models import BaseOffStudy
        if not isinstance(self.get_subject_instance(), BaseOffStudy):
            if self.get_subject_instance().is_off_study():
                raise self._get_exception_cls()('Data collection not allowed after off study date. Subject was taken off study before this form\'s report datetime \'{0}\'. (ConsentHelper)'.format(self.get_subject_instance().get_report_datetime()))

    def is_consented_for_subject_instance(self):
        """Searches for a valid edc_consent instance for this subject for the possible edc_consent models.

        If model class of the subject instance is listed in the edc_consent catalogue under the edc_consent of a different subject, such
        as with mother and their infants, get the other subject's identifier from the :func:`get_consent_subject_identifier`. """
        from edc.subject.consent.models import BaseConsent
        consent_models = []
        consent_subject_identifier = None
        if 'get_consenting_subject_identifier' in dir(self.get_subject_instance()):
            consent_subject_identifier = self.get_subject_instance().get_consenting_subject_identifier()
        else:
            consent_subject_identifier = self._get_subject_identifier()
        if not consent_subject_identifier:
            raise ConsentError('Cannot determine the subject_identifier of the edc_consent covering data entry for model {0}'.format(self.get_subject_instance()._meta.object_name))
        for consent_model in self._get_consent_models():
            if not issubclass(consent_model, BaseConsent):
                raise TypeError('Consent models must be subclasses of BaseConsent. Got {0}.'.format(consent_model))
            if consent_model.objects.filter(subject_identifier=consent_subject_identifier):
                # confirm what version covers either from edc_consent model or consent_update_model_cls
                # does the catalogue return only the MaternalConsent, ??
                consent_models.append(consent_model.objects.get(subject_identifier=consent_subject_identifier))
                # look for an updated edc_consent attached to this model
                # TODO: look up in consent_update_model_cls ??
                # retval = True
        if not consent_models:
            raise ConsentDoesNotExist(
                ('Cannot determine the instance of edc_consent {0} to cover data entry for model {1} '
                 'instance {2} given the consenting identifier={3}, report_datetime={4}').format(
                    self._get_consent_models(),
                    self.get_subject_instance()._meta.object_name,
                    self.get_subject_instance(),
                    consent_subject_identifier,
                    self.get_subject_instance().get_report_datetime()
                )
            )
        return consent_models

    def clean_versioned_field(self, field_value, field, start_datetime, consent_version):
        """Runs checks on a versioned field.

        Users may override."""
        if not field_value:
            # require a user provided value
            raise self._get_exception_cls()('Field \'{0}\' cannot be blank for data captured during'
                                            'or after version {2}. [{3}]'.
                                            format(
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
        ConsentCatalogue = get_model('edc_consent', 'ConsentCatalogue')
        current_consent_version = self.get_current_consent_version()
        # cycle through all versions in the edc_consent catalogue
        for consent_catalogue in ConsentCatalogue.objects.all().order_by('start_datetime', 'version'):
            consent_version = consent_catalogue.version
            start_datetime = consent_catalogue.start_datetime
            if not start_datetime:
                raise TypeError('Cannot determine edc_consent version start date. Check the Consent Catalogue')
            if self.get_subject_instance().get_versioned_field_names(consent_version):
                for field in self.get_subject_instance()._meta.fields:
                    if field.name in self.get_subject_instance().get_versioned_field_names(consent_version):
                        field_value = getattr(self.get_subject_instance(), field.name)
                        if self._get_report_datetime() < start_datetime and field_value:
                            # enforce None / default
                            raise self._get_exception_cls()(
                                'Field \'{0}\' must be left blank for data captured prior to version {2}. [{3}]'
                                .format(field.name, start_datetime, consent_version, field.verbose_name[0:50]))
                        if self._get_report_datetime() >= start_datetime:
                            self.clean_versioned_field(field_value, field, start_datetime, consent_version)
        return current_consent_version

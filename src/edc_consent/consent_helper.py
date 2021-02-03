from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from .exceptions import ConsentVersionSequenceError
from .site_consents import site_consents


class ConsentHelper:

    """A class to get the consent configuration object and to
    validate version numbers if this consent is an update
    of a previous.
    """

    def __init__(
        self,
        model_cls=None,
        update_previous=None,
        subject_identifier=None,
        identity=None,
        first_name=None,
        consent_datetime=None,
        dob=None,
        last_name=None,
        subject_identifier_as_pk=None,
        subject_identifier_aka=None,
        **kwargs,
    ):
        self._previous_consent = None
        self.model_cls = model_cls
        self.dob = dob
        self.first_name = first_name
        self.identity = identity
        self.last_name = last_name
        self.subject_identifier = subject_identifier
        self.update_previous = True if update_previous is None else update_previous

        self.consent_object = site_consents.get_consent_for_period(
            model=self.model_cls._meta.label_lower,
            consent_group=self.model_cls._meta.consent_group,
            report_datetime=consent_datetime,
        )

        # these to be set on the model
        self.version = self.consent_object.version
        self.updates_versions = self.consent_object.updates_versions

        # if updates a previous, validate version sequence
        # and update the subject_identifier_as_pk, etc
        if self.updates_versions and update_previous:
            self.previous_consent.subject_identifier_as_pk = subject_identifier_as_pk
            self.previous_consent.subject_identifier_aka = subject_identifier_aka
            self.previous_consent.save(
                update_fields=["subject_identifier_as_pk", "subject_identifier_aka"]
            )

    @property
    def previous_consent(self):
        """Returns the previous consent or raises if does
        not exist or is out of sequence with the current.
        """
        if not self._previous_consent:
            opts = dict(
                subject_identifier=self.subject_identifier,
                identity=self.identity,
                version__in=self.consent_object.updates_versions,
            )
            opts = {k: v for k, v in opts.items() if v is not None}
            try:
                self._previous_consent = self.model_cls.objects.get(**opts)
            except ObjectDoesNotExist:
                updates_versions = ", ".join(self.consent_object.updates_versions)
                raise ConsentVersionSequenceError(
                    f"Failed to update previous version. A previous consent "
                    f"with version in {updates_versions} for {self.subject_identifier} "
                    f"was not found. Consent version '{self.version}' is "
                    "configured to update a previous version."
                )
            except MultipleObjectsReturned:
                previous_consents = self.model_cls.objects.filter(**opts).order_by("-version")
                self._previous_consent = previous_consents[0]
        return self._previous_consent

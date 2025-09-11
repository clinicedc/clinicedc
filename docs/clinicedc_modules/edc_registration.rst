edc-registration
================

The model ``RegisteredSubject`` is used by the Edc as the master subject registration table. Only one record may exist per individual. The table has space for PII so typically a ``RegisteredSubject`` instance is created or updated on completion of the informed consent. As always, PII in the Edc is encrypted at rest using ``django-crypto-field``.


For the model and signal to be registered you need to add the AppConfig to your INSTALLED_APPS:

.. code-block:: python

    INSTALLED_APPS = (
        # ....
        'edc_registration.apps.AppConfig',
        # ....
    )


**UpdatesOrCreatesRegistrationModelMixin**

``RegisteredSubject`` is never edited directly by the user. Instead some other model with the needed attributes is used as a proxy. To have a model perform the task of creating or updating  ``RegisteredSubject``, declare it with the ``UpdatesOrCreatesRegistrationModelMixin``.

For example, a model, ``SubjectEligibility`` or a screening model creates or updates ``RegisteredSubject`` without a subject identifier then a model such as the ``SubjectConsent`` in ``tests.models``, also creates or updates a subject's ``RegisteredSubject`` instance on save. For this to happen, both models are declared with the ``UpdatesOrCreatesRegistrationModelMixin``:

.. code-block:: python

    class SubjectEligibility(
        UniqueSubjectIdentifierModelMixin,
        UpdatesOrCreatesRegistrationModelMixin,
        BaseUuidModel,
    ):

        screening_identifier = models.CharField(
            max_length=36,
            null=True,
            unique=True)

        @property
        def registration_unique_field(self):
            return 'screening_identifier'

        def update_subject_identifier_on_save(self):
            """Overridden to not set the subject identifier on save.
            """
            if not self.subject_identifier:
                self.subject_identifier = self.subject_identifier_as_pk.hex
                self.subject_identifier_aka = self.subject_identifier_as_pk.hex
            return self.subject_identifier

    class SubjectConsent(
        ConsentModelMixin, UpdatesOrCreatesRegistrationModelMixin,
        CreateAppointmentsMixin, IdentityFieldsMixin, ReviewFieldsMixin,
        PersonalFieldsMixin, CitizenFieldsMixin, VulnerabilityFieldsMixin,
        BaseUuidModel):

        @property
        def registration_unique_field(self):
            return 'screening_identifier'

        class Meta:
            app_label = 'my_app'


The property ``registration_unique_field`` returns a model attribute that is used to set a registration identifier on ``RegisteredSubject``.

A subject's ``RegisteredSubject`` instance is created and updated in a ``post_save`` signal. As mentioned, it is never edited directly by the user.

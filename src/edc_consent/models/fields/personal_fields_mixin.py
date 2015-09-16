from django.core.validators import RegexValidator
from django.conf import settings
from django.db import models

from edc_consent.plain_fields import IsDateEstimatedField
from edc_consent.validators import dob_not_future, ConsentAgeValidator
from edc_constants.choices import GENDER_UNDETERMINED
from edc_consent.encrypted_fields import FirstnameField, LastnameField, EncryptedCharField

from ...validators import SubjectTypeValidator


class PersonalFieldsMixin(models.Model):

    class Constants:
        SUBJECT_TYPES = ['subject']
        GENDER_OF_CONSENT = ['M', 'F']
        AGE_IS_ADULT = 18
        MIN_AGE_OF_CONSENT = 16
        MAX_AGE_OF_CONSENT = 64

    # may not be available when instance created (e.g. infants prior to birth report)
    first_name = FirstnameField(
        null=True,
    )

    # may not be available when instance created (e.g. infants or household subject before consent)
    last_name = LastnameField(
        verbose_name="Last name",
        null=True,
    )

    # may not be available when instance created (e.g. infants)
    initials = EncryptedCharField(
        validators=[RegexValidator(regex=r'^[A-Z]{2,3}$',
                                   message=('Ensure initials consist of letters '
                                            'only in upper case, no spaces.')), ],
        null=True,
    )

    dob = models.DateField(
        verbose_name="Date of birth",
        validators=[
            dob_not_future,
            ConsentAgeValidator(Constants.MIN_AGE_OF_CONSENT, Constants.MAX_AGE_OF_CONSENT),
        ],
        null=True,
        blank=False,
        help_text="Format is YYYY-MM-DD",
    )

    is_dob_estimated = IsDateEstimatedField(
        verbose_name="Is date of birth estimated?",
        null=True,
        blank=False,
    )

    gender = models.CharField(
        verbose_name="Gender",
        choices=GENDER_UNDETERMINED,
        max_length=1,
        null=True,
        blank=False,
    )

    guardian_name = LastnameField(
        verbose_name=("Guardian\'s Last and first name (minors only)"),
        validators=[
            RegexValidator(
                '^[A-Z]{1,50}\, [A-Z]{1,50}$',
                'Invalid format. Format is \'LASTNAME, FIRSTNAME\'. All uppercase separated by a comma')],
        blank=True,
        null=True,
        help_text=(
            'Required only if subject is a minor. Format is \'LASTNAME, FIRSTNAME\'. '
            'All uppercase separated by a comma then followe by a space.'),
    )

    subject_type = models.CharField(
        max_length=25,
        validators=[SubjectTypeValidator(Constants.SUBJECT_TYPES)],
    )

    def additional_filter_options(self):
        """Additional kwargs to filter the consent when looking for the previous consent in base save."""
        options = super(PersonalFieldsMixin, self).additional_filter_options()
        options.update({'first_name': self.first_name, 'dob': self.dob, 'last_name': self.last_name})
        return options

    class Meta:
        abstract = True

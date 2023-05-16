from django.db import models
from django.utils.html import format_html
from django_crypto_fields.fields import EncryptedCharField, EncryptedTextField
from edc_constants.choices import YES_NO
from edc_model.validators import cell_number, telephone_number


class SubjectIndirectContactFieldsMixin(models.Model):
    may_contact_indirectly = models.CharField(
        max_length=25,
        choices=YES_NO,
        verbose_name=format_html(
            "Has the participant given permission for study staff "
            "<b>to contact anyone else</b> for follow-up purposes during the study?"
        ),
        help_text="For example a partner, spouse, family member, neighbour ...",
    )

    indirect_contact_name = EncryptedCharField(
        verbose_name="Full names of the contact person", blank=True, null=True
    )

    indirect_contact_relation = EncryptedCharField(
        verbose_name="Relationship to participant", blank=True, null=True
    )

    indirect_contact_physical_address = EncryptedTextField(
        verbose_name="Full physical address ", max_length=500, blank=True, null=True
    )

    indirect_contact_cell = EncryptedCharField(
        verbose_name="Cell number", validators=[cell_number], blank=True, null=True
    )

    indirect_contact_cell_alt = EncryptedCharField(
        verbose_name="Cell number (alternative)",
        validators=[cell_number],
        blank=True,
        null=True,
    )

    indirect_contact_phone = EncryptedCharField(
        verbose_name="Telephone number",
        validators=[telephone_number],
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True

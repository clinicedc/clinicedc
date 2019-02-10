from django.db import models


class SiteFieldsMixin(models.Model):

    site_code = models.CharField(
        verbose_name="Site",
        max_length=25,
        help_text=(
            "This refers to the site or 'clinic area' where the "
            "subject is being consented."
        ),
    )

    class Meta:
        abstract = True

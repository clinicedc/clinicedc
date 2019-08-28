from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django_crypto_fields.fields import EncryptedTextField

from ..randomizer import RandomizationError
from ..models import RandomizationListMixin, RandomizationListModelError

CONTROL = "control"
CONTROL_NAME = "Control: Some control treatment."
SINGLE_DOSE = "single_dose"
SINGLE_DOSE_NAME = "Single-dose: Some treatment"


class RandomizationList(RandomizationListMixin):

    assignment = EncryptedTextField(
        choices=((SINGLE_DOSE, SINGLE_DOSE_NAME), (CONTROL, CONTROL_NAME))
    )

    def save(self, *args, **kwargs):
        self.validate_or_raise()
        try:
            Site.objects.get(name=self.site_name)
        except ObjectDoesNotExist:
            site_names = [obj.name for obj in Site.objects.all()]
            raise RandomizationListModelError(
                f"Invalid site name. Got {self.site_name}. "
                f"Expected one of {site_names}."
            )
        super().save(*args, **kwargs)

    @property
    def short_label(self):
        return f"{self.assignment} SID:{self.site_name}.{self.sid}"

    @property
    def assignment_description(self):
        if self.assignment == CONTROL:
            return CONTROL_NAME
        elif self.assignment == SINGLE_DOSE:
            return SINGLE_DOSE_NAME
        raise RandomizationError(
            f"Invalid drug assignment. Got {self.assignment}")

    class Meta(RandomizationListMixin.Meta):
        pass

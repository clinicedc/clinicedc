from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import ContextMixin
from edc_identifier.utils import is_subject_identifier_or_raise
from edc_randomization.randomizer import RandomizationError
from edc_randomization.site_randomizers import site_randomizers


class RandomizationListViewMixin(ContextMixin):

    randomizer_name = "default"

    @property
    def assignment_description(self):
        randomizer_cls = site_randomizers.get(self.randomizer_name)
        subject_identifier = is_subject_identifier_or_raise(
            self.kwargs.get("subject_identifier")
        )
        try:
            obj = randomizer_cls.model_cls().objects.get(
                subject_identifier=subject_identifier
            )
        except ObjectDoesNotExist as e:
            current_site = Site.objects.get_current()
            total = (
                randomizer_cls.model_cls()
                .objects.filter(site_name=current_site.name)
                .count()
            )
            available = (
                randomizer_cls.model_cls()
                .objects.filter(site_name=current_site.name, allocated=False)
                .count()
            )
            raise RandomizationError(
                f"Subject {subject_identifier}. "
                f"Found {available}/{total} available records for {current_site}. Got {e}"
            )
        return obj.assignment_description

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(assignment_description=self.assignment_description)
        return context

from django.contrib.sites.models import Site
from django_pylabels.models import LabelSpecification
from edc_sites.site import sites as site_sites
from edc_visit_schedule.models import VisitSchedule as BaseVisitSchedule


class VisitSchedule(BaseVisitSchedule):
    class Meta:
        proxy = True


class SiteProxy(Site):

    def __str__(self):
        single_site = site_sites.get(self.id)
        return single_site.description

    class Meta:
        proxy = True
        verbose_name = "Site"
        verbose_name_plural = "Sites"


class LabelSpecificationProxy(LabelSpecification):
    class Meta:
        proxy = True
        verbose_name = "Label Sheet Specification"
        verbose_name_plural = "Label Sheet Specifications"

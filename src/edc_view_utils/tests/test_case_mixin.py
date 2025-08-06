from django.core.exceptions import ObjectDoesNotExist
from edc_sites import site_sites
from edc_sites.utils import add_or_update_django_sites, get_site_model_cls
from edc_test_utils.get_user_for_tests import get_user_for_tests
from edc_visit_schedule.models import VisitSchedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from dashboard_app.sites import all_sites
from dashboard_app.visit_schedule import visit_schedule1


class TestCaseMixin:
    @classmethod
    def setUpTestData(cls):
        for obj in get_site_model_cls().objects.all():
            try:
                obj.siteprofile.delete()
            except ObjectDoesNotExist:
                pass
            obj.delete()
        get_site_model_cls().objects.all().delete()
        site_sites._registry = {}
        site_sites.register(*all_sites)
        add_or_update_django_sites(verbose=False)
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule1)
        VisitSchedule.objects.update(active=False)
        site_visit_schedules.to_model(VisitSchedule)
        cls.user = get_user_for_tests()

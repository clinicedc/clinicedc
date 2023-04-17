from django.contrib.sites.models import Site
from edc_constants.constants import NOT_APPLICABLE, YES
from model_bakery.recipe import Recipe

from dx_app.models import (
    ClinicalReviewBaseline,
    DmInitialReview,
    HivInitialReview,
    HtnInitialReview,
)

clinicalreviewbaseline = Recipe(
    ClinicalReviewBaseline,
    site=Site.objects.get_current(),
    hiv_dx=YES,
    htn_dx=NOT_APPLICABLE,
    dm_dx=NOT_APPLICABLE,
)


hivinitialreview = Recipe(HivInitialReview, dx_ago=None, dx_date=None)
htninitialreview = Recipe(HtnInitialReview, dx_ago=None, dx_date=None)
dminitialreview = Recipe(DmInitialReview, dx_ago=None, dx_date=None)

from django.contrib.sites.models import Site
from edc_constants.constants import NO, NOT_APPLICABLE, YES
from model_bakery.recipe import Recipe

from .models import (
    CholInitialReview,
    ClinicalReview,
    ClinicalReviewBaseline,
    DmInitialReview,
    HivInitialReview,
    HtnInitialReview,
)

clinicalreviewbaseline = Recipe(
    ClinicalReviewBaseline,
    site=Site.objects.get_current(),
    hiv_test=YES,
    hiv_test_ago="5y",
    hiv_dx=YES,
    htn_test=NO,
    htn_test_ago=None,
    hypertension=NOT_APPLICABLE,
    dm_test=NO,
    dm_test_ago=None,
    diabetes=NOT_APPLICABLE,
)

clinicalreview = Recipe(
    ClinicalReview,
    site=Site.objects.get_current(),
    hiv_test=NOT_APPLICABLE,
    hiv_test_date=None,
    hiv_dx=NOT_APPLICABLE,
    htn_test=NO,
    htn_test_date=None,
    htn_dx=NOT_APPLICABLE,
    dm_test=NO,
    dm_test_date=None,
    dm_dx=NOT_APPLICABLE,
    health_insurance=YES,
    patient_club=YES,
)

hivinitialreview = Recipe(HivInitialReview, dx_ago=None, dx_date=None)
htninitialreview = Recipe(HtnInitialReview, dx_ago=None, dx_date=None)
dminitialreview = Recipe(DmInitialReview, dx_ago=None, dx_date=None)
cholinitialreview = Recipe(CholInitialReview, dx_ago=None, dx_date=None)

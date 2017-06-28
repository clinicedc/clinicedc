from collections import OrderedDict
from django.test import TestCase, tag
from faker import Faker

from edc_constants.constants import MALE, FEMALE
from edc_registration.models import RegisteredSubject
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from ..constants import NOT_REQUIRED, REQUIRED
from ..models import CrfMetadata
from ..rules import RuleGroup, RequisitionRule, CrfRule, Logic, P, PF, site_metadata_rules
from ..rules import RuleEvaluatorRegisterSubjectError, RuleGroupModelConflict
from ..rules import TargetModelConflict, PredicateError, RuleEvaluatorError
from ..rules import TargetModelLookupError, TargetModelMissingManagerMethod
from .models import Appointment, SubjectVisit, Enrollment, CrfOne
from .visit_schedule import visit_schedule
from pprint import pprint

fake = Faker()


class RequisitionRuleGroup(RuleGroup):
    """Specifies source model.
    """
    class RequisitionPanel:
        def __init__(self, name):
            self.name = name

    viral_load_panel = RequisitionPanel('viral_load')
    crfs_male = RequisitionRule(
        logic=Logic(
            predicate=P('f1', 'eq', 'car'),
            consequence=REQUIRED,
            alternative=NOT_REQUIRED),
        target_model='subjectrequisition',
        target_panels=[viral_load_panel])

    class Meta:
        app_label = 'edc_metadata'
        source_model = 'edc_metadata.crfone'
